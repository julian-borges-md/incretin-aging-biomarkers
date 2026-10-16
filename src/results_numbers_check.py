#!/usr/bin/env python3
"""
results_numbers_check.py

Checks every pooled figure written in the Results narrative against the table the pipeline
generated, so that a manuscript sentence cannot drift away from the corpus it claims to describe.
The Results draft is edited by hand after each extraction pass; the figures in it are not generated,
and the failure mode this script exists to catch is a paragraph left at the previous commit's
numbers while the table moved under it.

What is checked
  Every occurrence in the narrative of the shape
      <magnitude> per cent (<lo> to <hi>, k <n>)
  is matched against analysis/output/table2_pooled_by_biomarker.csv. An occurrence matches a row of
  that table when k is identical and the three magnitudes agree with the row's estimate and
  interval bounds to one decimal place, signs ignored (the narrative prints reductions as "minus
  31.1 per cent" and as "31.1 per cent" depending on the sentence). An occurrence that matches no
  row is reported; so is a row of the table whose k is unique in the table and which the narrative
  never cites, because that is where a new marker silently fails to reach the text.

The sign is deliberately not checked here: the narrative's direction words are checked by the
direction column of the generated table, which make_tables.py writes from the same CSV.

Usage
  python3 -I src/results_numbers_check.py manuscript/RESULTS_2026-10-16.md
  exit 1 when any cited figure matches no row of the pooled table
"""
import csv
import os
import re
import sys

ROOT = os.getcwd()
POOLED = os.path.join(ROOT, "analysis", "output", "table2_pooled_by_biomarker.csv")
SIGN = r"(?:minus\s+|plus\s+)?"
# The narrative writes a pooled figure in four shapes that all have to be checked:
#   31.1 per cent (95 per cent CI 25.5 to 36.7, k 36, I squared 91 per cent)
#   18.8 per cent (4.5 to 33.1, k 10)
#   minus 1.5 per cent, minus 30.3 to plus 27.4, k 6
#   3.2 per cent, 2.1 to 4.4, k 26, I squared 53 per cent
# so the opening bracket is optional, the "95 per cent CI" prefix is optional, and the trailing
# bracket is not required (a figure may continue into an I squared clause before it closes).
CITE = re.compile(
    SIGN + r"(\d+\.\d)\s*per\s+cent\s*[(,]\s*(?:95\s*per\s*cent\s*CI\s*)?"
    + SIGN + r"(\d+\.\d)\s*to\s*" + SIGN + r"(\d+\.\d)\s*,\s*k\s*(\d+)\b",
    re.I,
)


def one_dp(x):
    return round(abs(float(x)), 1)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    path = argv[0]
    rows = []
    with open(POOLED, newline="") as fh:
        for r in csv.DictReader(fh):
            if not r["est"] or r["est"] == "NA":
                continue
            rows.append(dict(biomarker=r["biomarker"], k=int(r["k"]), est=one_dp(r["est"]),
                             lo=one_dp(r["lo"]), hi=one_dp(r["hi"])))
    text = open(path).read()
    cited_k = set()
    bad = 0
    n = 0
    for m in CITE.finditer(text):
        est, a, b, k = one_dp(m.group(1)), one_dp(m.group(2)), one_dp(m.group(3)), int(m.group(4))
        n += 1
        cited_k.add(k)
        hit = [r for r in rows if r["k"] == k and r["est"] == est and {r["lo"], r["hi"]} == {a, b}]
        if hit:
            continue
        near = [r for r in rows if r["k"] == k and r["est"] == est]
        bad += 1
        print(f"  MISMATCH  {est} ({a} to {b}, k {k})  "
              + (f"-> {near[0]['biomarker']} has interval {near[0]['lo']} to {near[0]['hi']}"
                 if near else "no row with that estimate and k"))
    uncited = sorted(r["biomarker"] for r in rows
                     if sum(1 for q in rows if q["k"] == r["k"]) == 1 and r["k"] not in cited_k)
    if uncited:
        print("  not cited in the narrative (k unique in the table):", ", ".join(uncited))
    print(f"{os.path.relpath(path, ROOT)}: {n} pooled figure(s) cited, {bad} not matching the table "
          f"({len(rows)} rows in {os.path.relpath(POOLED, ROOT)})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
