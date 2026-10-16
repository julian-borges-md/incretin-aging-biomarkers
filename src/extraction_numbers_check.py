#!/usr/bin/env python3
"""
extraction_numbers_check.py

Provenance check of an extraction against the packet texts: every number an extractor wrote
must occur in the text the study was read from. A number that does not occur is either a
transcription error, an arithmetic the brief forbids, or a value taken from outside the packet;
each case is reported, none is corrected here.

Matching: the absolute value as written (27.32), with and without trailing zeros (7.8 / 7.80),
with the decimal comma variant (27,32); signs are ignored because papers print reductions as
positive magnitudes and the extraction records them as signed changes. Numbers below 10 with no
decimals (n of 5, dose of 1) match too easily and are reported as "weak" rather than found.

Usage
  python3 -I src/extraction_numbers_check.py GROUP [EXTRACTOR] [--text FILE ...]   (default extractor A)
  exit 1 when any number is missing

--text adds a text outside the packet (a companion paper fetched by epmc_fetch_one.py, a baseline
table) to the texts searched; the files used are printed so the provenance is on record.
"""
import csv
import json
import os
import re
import sys

ROOT = os.getcwd()
NUMERIC = ("yi_reported", "ci_lb_reported", "ci_ub_reported", "se_reported", "p_reported", "mean_tx", "sem_tx",
           "sd_tx", "mean_ctrl", "sem_ctrl", "sd_ctrl", "base_mean_tx", "base_sd_tx", "final_mean_tx",
           "final_sd_tx", "base_mean_ctrl", "base_sd_ctrl", "final_mean_ctrl", "final_sd_ctrl", "events_tx",
           "events_ctrl", "n_tx", "n_ctrl", "pct_weight_change", "dose_mg", "duration_weeks")


def variants(v):
    s = str(v).strip().replace("−", "-").replace("–", "-").lstrip("-+")
    if not s:
        return []
    out = {s}
    if "." in s:
        out.add(s.rstrip("0").rstrip("."))
        out.add(s + "0")
        out.add(s.replace(".", ","))
        out.add(s.replace(".", "·"))  # Lancet house style prints the decimal point as a middle dot
        if s.startswith("0."):
            out.add(s[1:])
    return [x for x in out if x]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    group = argv[0]
    extra = []
    rest = []
    i = 1
    while i < len(argv):
        if argv[i] == "--text" and i + 1 < len(argv):
            extra.append(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    ext = rest[0] if rest else "A"
    d = os.path.join(ROOT, "work", "extraction", "staging", group)
    pk = json.load(open(os.path.join(ROOT, "work", "extraction", "packets", group, "packet.json")))
    text = ""
    files = [t["file"] for t in pk["texts"]] + extra
    for f in files:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            text += open(p, errors="replace").read() + "\n"
        else:
            print(f"  text not found: {f}")
    if extra:
        print("texts searched: " + ", ".join(files))
    text = text.replace("−", "-").replace("–", "-")
    rows = list(csv.DictReader(open(os.path.join(d, f"{ext}.csv"), newline="")))
    missing = 0
    for r in rows:
        for c in NUMERIC:
            v = (r.get(c) or "").strip()
            if v in ("", "NA", "TRUE", "FALSE"):
                continue
            vs = variants(v)
            found = any(re.search(r"(?<![\d.])" + re.escape(x) + r"(?![\d])", text) for x in vs)
            if not found:
                try:
                    weak = float(v.replace(",", ".")) < 10 and "." not in v
                except ValueError:
                    weak = False
                tag = "weak" if weak else "MISSING"
                if tag == "MISSING":
                    missing += 1
                print(f"  {tag:8} {r['biomarker']:16} dose {r.get('dose_mg', ''):>5}  {c:16} = {v}")
    print(f"group {group} extractor {ext}: {len(rows)} rows checked, {missing} number(s) not found in the packet texts")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
