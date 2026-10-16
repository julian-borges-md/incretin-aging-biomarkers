#!/usr/bin/env python3
"""Adjudication of full text screening disagreements by the session's reviewer.

The two local reviewers screen every record (src/fulltext_screen.py). When
search/screening/ADJUDICATOR.txt exists, the adjudication of their disagreements is
delegated to the reviewer it names, who reads exactly the text the two reviewers received
and records a decision in the same adjudication file and schema. Three commands:

  python3 -I src/session_adjudicate.py list
      the pending disagreements (screened by both, decisions differ, not yet adjudicated)
  python3 -I src/session_adjudicate.py show KEY [KEY ...] [--max N]
      the package for each key: both decisions with their reasons, then the text as the
      reviewers saw it (cut at N characters, default the full text)
  python3 -I src/session_adjudicate.py write KEY decision failed "reason" duration comparator "biomarkers"
      appends one adjudication row; decision is include or exclude, failed is letters among
      DPIOT or "-", duration is weeks or "null"; refused when KEY is not a pending disagreement

Rows carry the adjudicator's identity in the reason prefix and seconds = 0 (no model call).
"""
import csv
import os
import sys

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
ARGS = sys.argv[1:]
sys.argv = [sys.argv[0]]
import fulltext_screen as fs  # noqa: E402

FIELDS = ["key", "pool", "n", "source", "decision_A", "decision_B", "decision", "failed", "reason",
          "duration_weeks", "comparator", "biomarkers_reported", "seconds"]


def pending(items):
    A, B, ADJ = fs.read_dec(fs.dec_path("A")), fs.read_dec(fs.dec_path("B")), fs.read_dec(fs.ADJ_PATH)
    out = []
    for it in items:
        k = it["key"]
        if k in A and k in B and A[k]["decision"] != B[k]["decision"] and k not in ADJ:
            out.append((it, A[k], B[k]))
    return out


def main():
    if not ARGS or ARGS[0] not in ("list", "show", "write"):
        print(__doc__)
        sys.exit(2)
    if not os.path.exists(fs.ADJUDICATOR_FILE):
        print("FAIL: ADJUDICATOR.txt absent; adjudication is not delegated")
        sys.exit(1)
    items = fs.load_items()
    by_key = {it["key"]: it for it in items}
    cmd = ARGS[0]
    if cmd == "list":
        rows = pending(items)
        print(f"{len(rows)} pending disagreements")
        for it, a, b in rows:
            print(f"{it['key']:7s} {it['source']:19s} {len(it['text']):6d} chars  A={a['decision']}({a['failed'] or '-'})  B={b['decision']}({b['failed'] or '-'})  {it['title'][:70]}")
        return
    if cmd == "show":
        cap = int(ARGS[ARGS.index("--max") + 1]) if "--max" in ARGS else None
        skip = {ARGS.index("--max") + 1} if "--max" in ARGS else set()
        keys = [x for i, x in enumerate(ARGS) if i > 0 and i not in skip and not x.startswith("--")]
        pend = {it["key"]: (it, a, b) for it, a, b in pending(items)}
        for k in keys:
            if k not in pend:
                print(f"=== {k}: not a pending disagreement")
                continue
            it, a, b = pend[k]
            print(f"=== {k} | {it['source']} | {len(it['text'])} chars | known relevant: {it['matched_known']}")
            print(f"Reviewer A: {a['decision']} ({a['failed'] or 'none'}) {a['reason']} | duration {a['duration_weeks']} | comparator {a['comparator']} | biomarkers {a['biomarkers_reported']}")
            print(f"Reviewer B: {b['decision']} ({b['failed'] or 'none'}) {b['reason']} | duration {b['duration_weeks']} | comparator {b['comparator']} | biomarkers {b['biomarkers_reported']}")
            print("--- text as the reviewers received it ---")
            print(it["text"][:cap] if cap else it["text"])
            print(f"=== end {k}\n")
        return
    if cmd == "write":
        if len(ARGS) != 8:
            print("FAIL: write needs KEY decision failed reason duration comparator biomarkers")
            sys.exit(2)
        key, decision, failed, reason, duration, comparator, biomarkers = ARGS[1:]
        pend = {it["key"]: (it, a, b) for it, a, b in pending(items)}
        if key not in pend:
            print(f"FAIL: {key} is not a pending disagreement (already adjudicated, agreed, or not screened by both)")
            sys.exit(1)
        if decision not in ("include", "exclude"):
            print("FAIL: decision must be include or exclude")
            sys.exit(1)
        failed = "" if failed == "-" else failed
        if any(c not in "DPIOT" for c in failed):
            print("FAIL: failed letters must be among DPIOT")
            sys.exit(1)
        if decision == "exclude" and not failed:
            print("FAIL: an exclusion names at least one failed criterion")
            sys.exit(1)
        it, a, b = pend[key]
        new_file = not os.path.exists(fs.ADJ_PATH)
        with open(fs.ADJ_PATH, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            if new_file:
                w.writeheader()
            w.writerow(dict(key=key, pool=it["pool"], n=it["n"], source=it["source"], decision_A=a["decision"], decision_B=b["decision"],
                            decision=decision, failed=failed, reason="[session adjudicator] " + reason,
                            duration_weeks="" if duration == "null" else duration, comparator=comparator,
                            biomarkers_reported=biomarkers, seconds="0"))
        print(f"written: {key} {decision} {failed or '-'}")


if __name__ == "__main__":
    main()
