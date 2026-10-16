#!/usr/bin/env python3
"""
packet_grouping_check.py

Audits the study grouping of the extraction packets. src/extraction_packets.py groups the included
records into one packet per study by title and registry identifier, so that a trial with a
conference abstract, a register entry and a full text is extracted once. When that grouping is
wrong and two UNRELATED studies land in one packet, the extractor reads one of them, the ledger
closes the group, and the other study leaves the review without ever being assessed. That is a
silent loss of evidence, not a visible error, and it happened: group 219 bundles the SCALE obesity
and prediabetes 3 year abstract with an unrelated exenatide, metformin and glibenclamide
adipocytokine abstract; the SCALE record was extracted and the exenatide record was never read.

The check, per packet with two or more records
  1. read each record's Title line (the packet texts keep it) and the packet's identifiers
  2. find which molecules each title names, over the admitted and the non admitted vocabulary
  3. flag the packet when two records name disjoint, non empty molecule sets, which no single
     study can do unless it is a head to head trial that names both in both records
  4. report the flagged packets with their ledger status first, because a packet closed as
     extracted or already_extracted is where a dropped study hides

Nothing is regrouped here. The output is a reading list.

Usage
  python3 -I src/packet_grouping_check.py
  exit 1 when any packet is flagged
"""
import csv
import glob
import json
import os
import re
import sys

ROOT = os.getcwd()
PACKETS = os.path.join(ROOT, "work", "extraction", "packets")
LEDGER = os.path.join(ROOT, "analysis", "data", "EXTRACTION_LEDGER.csv")
# Groups whose records have been read one by one and whose verdicts are written up. The file is the
# audit record and the allowlist at once: a flagged group that appears as a table row there is
# triaged, and the gate fails only on a group that is flagged and not yet in it, which is what a
# later packet rebuild would produce.
TRIAGE = os.path.join(ROOT, "docs", "PACKET_GROUPING_TRIAGE.md")


def triaged_groups():
    if not os.path.exists(TRIAGE):
        return set()
    out = set()
    for ln in open(TRIAGE, errors="replace"):
        m = re.match(r"\s*\|\s*(\d+)\s*\|", ln)
        if m:
            out.add(m.group(1))
    return out

MOLECULES = [
    "semaglutide", "liraglutide", "tirzepatide", "survodutide", "mazdutide", "pemvidutide",
    "cotadutide", "retatrutide", "amycretin", "cagrilintide", "cagrisema", "exenatide",
    "dulaglutide", "lixisenatide", "albiglutide", "efpeglenatide", "orforglipron", "danuglipron",
    "beinaglutide", "taspoglutide", "ecnoglutide", "supaglutide", "noiiglutide", "insulin degludec",
]
# words that name an intervention of a different class; two records naming only these are not
# necessarily different studies, so they are not used to flag, only to describe
TITLE = re.compile(r"^Title:\s*(.+)$", re.M)


def molecules_in(text):
    low = text.lower()
    return {m for m in MOLECULES if m in low}


def main():
    status = {}
    titles = {}
    with open(LEDGER, newline="") as fh:
        for r in csv.DictReader(fh):
            status[r["study_group"]] = r["status"]
            titles[r["study_group"]] = r.get("title", "")
    flagged = []
    checked = 0
    for pj in sorted(glob.glob(os.path.join(PACKETS, "*", "packet.json"))):
        g = os.path.basename(os.path.dirname(pj))
        d = json.load(open(pj))
        texts = d.get("texts", [])
        if len(texts) < 2:
            continue
        checked += 1
        recs = []
        for t in texts:
            p = os.path.join(ROOT, t["file"])
            if not os.path.exists(p):
                continue
            head = open(p, errors="replace").read(1200)
            m = TITLE.search(head)
            title = m.group(1).strip() if m else os.path.basename(p)
            recs.append((t["source"], title, molecules_in(title)))
        named = [(s, ti, ms) for s, ti, ms in recs if ms]
        if len(named) < 2:
            continue
        disjoint = False
        for i in range(len(named)):
            for j in range(i + 1, len(named)):
                if named[i][2].isdisjoint(named[j][2]):
                    disjoint = True
        if disjoint:
            flagged.append((g, status.get(g, "?"), recs))
    order = {"extracted": 0, "already_extracted": 1, "held_pending_decision": 2,
             "no_usable_contrast": 3, "excluded_at_extraction": 4}
    flagged.sort(key=lambda x: (order.get(x[1], 9), int(x[0])))
    done = triaged_groups()
    untriaged = [f for f in flagged if f[0] not in done]
    print(f"packets with two or more records: {checked}; flagged: {len(flagged)}; "
          f"triaged in {os.path.relpath(TRIAGE, ROOT)}: {len(flagged) - len(untriaged)}; "
          f"untriaged: {len(untriaged)}")
    for g, st, recs in flagged:
        tag = "triaged" if g in done else "UNTRIAGED"
        print(f"\ngroup {g} [{st}] {tag}")
        for s, ti, ms in recs:
            print(f"   {s:20} {','.join(sorted(ms)) or '-':28} {ti[:96]}")
    sys.exit(1 if untriaged else 0)


if __name__ == "__main__":
    main()
