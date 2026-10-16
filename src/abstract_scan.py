#!/usr/bin/env python3
"""
abstract_scan.py

Deterministic screen of the included study groups that have no full text (conference abstracts,
register entries, ClinicalTrials.gov entries, partial captures): does any text of the group carry
the statistics a contrast needs (a dispersion or an interval or an exact p)? A group without any
such mark cannot yield a poolable row, so it is closed in the ledger as no_usable_contrast with
this scan as the reason, without an agent read; a group with marks goes to a single extractor.

Patterns (case insensitive, counted per group over the packet texts):
  dispersion   ±, +/-, "SD", "S.D.", "standard deviation", "SEM", "standard error", "(SE)"
  interval     "95% CI", "95%CI", "95% confidence", "CI:", "CI ["
  exact p      "p = 0.0x" or "p=0.0x" with at least two decimals (bounds "p < " are not counted)
  arm numbers  "n = " or "n=" followed by digits (a weak mark, reported but not decisive)

Outputs
  work/extraction/abstract_scan.csv   per group: texts, chars, marks per pattern, verdict
  stdout                              counts

Usage
  python3 -I src/abstract_scan.py
"""
import csv
import json
import os
import re

ROOT = os.getcwd()
PACKETS = os.path.join(ROOT, "work", "extraction", "packets")
INDEX = os.path.join(ROOT, "work", "extraction", "PACKET_INDEX.csv")
OUT = os.path.join(ROOT, "work", "extraction", "abstract_scan.csv")
FULLTEXT = ("epmc_fulltext", "direct_fulltext", "proxy_fulltext")
PATTERNS = {
    "dispersion": re.compile(r"(±|\+/-|\+/−|\bS\.?D\.?\b|standard deviation|\bSEM\b|standard error|\(SE\))", re.I),
    "interval": re.compile(r"(95\s?%\s?CI|95\s?%\s?confidence|\bCI\s?[:\[(]|confidence interval)", re.I),
    "exact_p": re.compile(r"\bp\s?=\s?0?\.\d{2,}", re.I),
    "arm_n": re.compile(r"\bn\s?=\s?\d+", re.I),
}


def main():
    rows = []
    with open(INDEX, newline="") as fh:
        for r in csv.DictReader(fh):
            g = r["study_group"]
            d = json.load(open(os.path.join(PACKETS, g, "packet.json")))
            texts = d["texts"]
            if any(t["source"] in FULLTEXT for t in texts):
                continue  # full text groups go to the extractor regardless
            counts = {k: 0 for k in PATTERNS}
            chars = 0
            for t in texts:
                p = os.path.join(ROOT, t["file"])
                if not os.path.exists(p):
                    continue
                txt = open(p, errors="replace").read()
                chars += len(txt)
                for k, rx in PATTERNS.items():
                    counts[k] += len(rx.findall(txt))
            decisive = counts["dispersion"] + counts["interval"] + counts["exact_p"]
            verdict = "to_extractor" if decisive > 0 else "no_variance_marks"
            rows.append(dict(study_group=g, texts=len(texts), sources=";".join(sorted({t["source"] for t in texts})),
                             chars=chars, **counts, decisive=decisive, verdict=verdict, title=d["title"][:120]))
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n_to = sum(1 for r in rows if r["verdict"] == "to_extractor")
    print(f"groups without a full text: {len(rows)}; with variance marks (to an extractor): {n_to}; "
          f"without any mark (closed as no_usable_contrast): {len(rows) - n_to}")
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
