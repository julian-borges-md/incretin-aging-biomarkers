#!/usr/bin/env python3
"""
results_numbers_check.py

Checks every pooled figure written in the Results narrative against the table the pipeline
generated, so that a manuscript sentence cannot drift away from the corpus it claims to describe.
The Results draft is edited by hand after each extraction pass; the figures in it are not generated,
and the failure mode this script exists to catch is a paragraph left at the previous commit's
numbers while the table moved under it.

What is checked
  1. Every occurrence in the narrative of the shape
         <magnitude> per cent (<lo> to <hi>, k <n>)
     is matched against analysis/output/table2_pooled_by_biomarker.csv.
  2. Added 2026-10-22: every Markdown table row whose first cell names a biomarker is matched
     against that biomarker's row of the same table. A pooled quantity written into a table cell
     was invisible to check 1, because check 1 reads prose: the Discussion's own summary table of
     the unfavourable axis cited five markers with their estimates and intervals and no gate read
     any of them. A table is where a number is most likely to be copied by hand and least likely to
     be reread. An occurrence matches a row of
  that table when k is identical and the three magnitudes agree with the row's estimate and
  interval bounds to one decimal place, signs ignored (the narrative prints reductions as "minus
  31.1 per cent" and as "31.1 per cent" depending on the sentence). An occurrence that matches no
  row is reported; so is a row of the table whose k is unique in the table and which the narrative
  never cites, because that is where a new marker silently fails to reach the text.

The sign is deliberately not checked here: the narrative's direction words are checked by the
direction column of the generated table, which make_tables.py writes from the same CSV.

Usage
  python3 -I src/results_numbers_check.py manuscript/RESULTS_2026-10-16.md
  python3 -I src/results_numbers_check.py --self-test
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


INVENTORY = os.path.join(ROOT, "analysis", "data", "biomarker_inventory.csv")
NUM = re.compile(r"(?:minus|plus)?\s*(\d+(?:\.\d+)?)")


def marker_aliases():
    """Map a folded display name or key to the biomarker key the pooled table uses.

    Both spellings are accepted because the manuscript prints the inventory's display name, Liver
    fat (MRI-PDFF), while the table and the data carry the key, liver_fat_pdff.
    """
    out = {}
    if not os.path.exists(INVENTORY):
        return out
    with open(INVENTORY, newline="") as fh:
        for r in csv.DictReader(fh):
            key = r["biomarker"]
            for name in (key, r.get("table1_name") or ""):
                if name:
                    out[fold_name(name)] = key
    return out


def fold_name(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def check_tables(text, rows, aliases):
    """Pooled quantities written into Markdown table rows.

    A row is checked when its first cell names a biomarker and the row carries at least three
    numbers, which is the shape of an estimate with an interval. The row passes when the pooled
    estimate and both interval bounds for that biomarker appear among the row's numbers, to one
    decimal place and ignoring sign, which is the same tolerance check 1 applies.

    Rows that name no biomarker are not checked: the manuscript's tables also carry dose arms,
    framework conditions and coverage tiers, none of which are pooled quantities.

    Two further conditions keep the check on the tables that claim to carry overall pooled
    estimates, and both were added after the first version misfired.

    The table's header row must name a change or estimate column and a prediction interval column.
    Only a table of overall pooled estimates carries all three quantities; the receptor class table,
    the meta-regression tables and the coverage counts do not, and they name the same markers while
    carrying different quantities by design. Without this condition the check read all of them and
    reported 54 mismatches against 34 real rows, which is a gate manufacturing its own defects.

    The row must also carry the biomarker's pooled trial count, which is what distinguishes a claim
    about the overall pool from a claim about a subgroup that happens to share the layout. Without
    it, a coverage table whose cells hold small integers matched markers whose k is 1 or 2.

    A table that quotes a pooled estimate with neither a prediction interval column nor the trial
    count is therefore not checked. That is a stated limit rather than a silent one, and the remedy
    is to print the k, which such a table should carry in any case.
    """
    by_marker = {r["biomarker"]: r for r in rows}
    problems, checked = [], 0
    header_ok = False
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            header_ok = False
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        low = " ".join(c.lower() for c in cells)
        # The prediction interval column must BE one, not merely mention one. The correlation
        # sensitivity table heads a column "Prediction interval excludes no effect", a yes or no
        # flag, and its rows carry three estimates at three assumed correlations: admitting it on a
        # substring match put ten legitimate rows in front of a check that compares them with a
        # quantity they are not.
        if any(fold_name(c) == "predictioninterval" for c in cells) and (
                "change" in low or "estimate" in low):
            header_ok = True
            continue
        if not header_ok:
            continue
        key = aliases.get(fold_name(cells[0]))
        if key is None or key not in by_marker:
            continue
        nums = [one_dp(m.group(1)) for c in cells[1:] for m in NUM.finditer(c)]
        if len(nums) < 3:
            continue
        r = by_marker[key]
        if float(r["k"]) not in nums:
            continue
        checked += 1
        missing = [name for name, v in (("estimate", r["est"]), ("lower bound", r["lo"]),
                                       ("upper bound", r["hi"])) if v not in nums]
        if missing:
            problems.append("table row for %s does not carry its %s (table 2 has %s, %s to %s, k %d)"
                            % (key, " or its ".join(missing), r["est"], r["lo"], r["hi"], r["k"]))
    return checked, problems


def self_test():
    rows = [dict(biomarker="lean_mass", k=2, est=5.0, lo=29.8, hi=19.7),
            dict(biomarker="hsCRP", k=36, est=31.1, lo=36.7, hi=25.5)]
    aliases = {"leanmass": "lean_mass", "totalleanmass": "lean_mass", "hscrp": "hsCRP"}
    HEAD = "| Marker | Trials | Change (%) | 95 per cent CI | Prediction interval | Reading |\n"
    good = HEAD + "| Total lean mass | 2 | minus 5.0 | minus 29.8 to 19.7 | n/a | reading |"
    stale = HEAD + "| Total lean mass | 2 | minus 4.2 | minus 29.8 to 19.7 | n/a | reading |"
    wrong_ci = HEAD + "| hsCRP | 36 | minus 31.1 | minus 36.7 to 22.0 | n/a | reading |"
    not_a_marker = HEAD + "| Primary endpoint | 12 | minus 82.7 | week 24 | n/a | note |"
    short = HEAD + "| hsCRP | 36 |"

    cases = [
        ("a correct table row passes", check_tables(good, rows, aliases) == (1, [])),
        ("a stale estimate in a table row is caught",
         any("does not carry its estimate" in m for m in check_tables(stale, rows, aliases)[1])),
        ("a wrong interval bound is caught",
         any("upper bound" in m for m in check_tables(wrong_ci, rows, aliases)[1])),
        ("a row naming no biomarker is not checked",
         check_tables(not_a_marker, rows, aliases) == (0, [])),
        ("a row with too few numbers is not checked",
         check_tables(short, rows, aliases) == (0, [])),
        # The receptor class and meta-regression tables name the same markers and carry different
        # quantities by design. Without the trial count condition this check read all of them.
        ("a per class row with its own k is not checked",
         check_tables(HEAD + "| hsCRP | 4 | minus 44.0 | minus 60.1 to minus 27.9 | n/a | x |",
                      rows, aliases) == (0, [])),
        ("a row quoting the pooled estimate without its k is not checked",
         check_tables(HEAD + "| hsCRP | minus 31.1 | minus 36.7 to minus 25.5 | n/a | x |",
                      rows, aliases) == (0, [])),
        # A table without a prediction interval column is a different quantity, whatever it names.
        ("a table with no prediction interval column is not checked",
         check_tables("| Biomarker | Trials | I2 | Egger |\n| hsCRP | 36 | 91 | no |",
                      rows, aliases) == (0, [])),
        ("a column that only mentions a prediction interval is not one",
         check_tables("| Biomarker | Trials | Prediction interval excludes no effect | "
                      "Estimate at r 0.3 | r 0.5 | r 0.7 |\n"
                      "| hsCRP | 36 | yes | minus 29.0 | minus 31.1 | minus 33.4 |",
                      rows, aliases) == (0, [])),
    ]
    print("SELF TEST")
    ok = True
    for name, passed in cases:
        print("  %-46s %s" % (name, passed))
        ok = ok and passed
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
        if rc != 0:
            sys.exit(rc)
        argv = [a for a in argv if a != "--self-test"]
        if not argv:
            sys.exit(0)
        print()
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
    t_checked, t_problems = check_tables(text, rows, marker_aliases())
    for m in t_problems:
        print("  MISMATCH  " + m)
    bad += len(t_problems)
    print(f"{os.path.relpath(path, ROOT)}: {n} pooled figure(s) cited in prose and {t_checked} in "
          f"table rows, {bad} not matching the table "
          f"({len(rows)} rows in {os.path.relpath(POOLED, ROOT)})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
