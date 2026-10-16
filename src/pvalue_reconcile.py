#!/usr/bin/env python3
"""
pvalue_reconcile.py

Third provenance gate, and the part of the amendment A5 verifier pass that scales. The numbers check
asks whether each number occurs in the source; the attachment check asks whether it is attached to
the right biomarker. Neither asks whether the row's numbers are consistent WITH EACH OTHER. A row
whose interval and p value disagree is either a transcription error or a paper whose statistics do
not hold together, and both of the integrity exclusions of this corpus were found by exactly that
comparison, by hand, one row at a time.

What this does, per row of the harmonised master
  1. keep the rows that carry a printed exact p value (p_is_bound FALSE) and a computable effect
     with a standard error
  2. compute the two sided p implied by the effect and its standard error on the row's own scale,
     from the normal approximation, which is what the pipeline's weights assume anyway
  3. compare it with the printed p and classify
       OK        the two agree within the tolerance below
       SOFT      they differ by more than tenfold but agree on which side of 0.05 they fall
       HARD      they fall on opposite sides of 0.05, or differ by more than a hundredfold
  4. print the HARD rows first, because those are where a paper's own statistics do not reconcile

Tolerance and its justification. Printed p values come from ANCOVA, MMRM or t tests with finite
degrees of freedom, while the implied p here is normal; with the smallest arms in this corpus (about
20 per group) that difference moves a p of 0.05 by roughly a factor of two, not ten. Rows whose
printed and implied p are both below 0.001 are not compared, because both are then floors rather
than values, and a printed p of exactly 0.05 is treated as agreeing with anything in [0.01, 0.2].

Nothing is corrected here. HARD rows are the verifier's reading list, in order.

Usage
  python3 -I src/pvalue_reconcile.py                  all rows, summary plus the lists
  python3 -I src/pvalue_reconcile.py TRIAL_SUBSTRING  one trial
  exit 1 when any HARD row is not written up in docs/PVALUE_TRIAGE.md
"""
import csv
import math
import os
import re
import sys

ROOT = os.getcwd()
HARMONISED = os.path.join(ROOT, "analysis", "data", "extraction_master_harmonised.csv")
TRIAGE = os.path.join(ROOT, "docs", "PVALUE_TRIAGE.md")
FLOOR = 0.001          # below this both numbers are floors, not values
SOFT_RATIO = 10.0      # order of magnitude disagreement
HARD_RATIO = 100.0


def norm_sf(z):
    """Upper tail of the standard normal, via the error function."""
    return 0.5 * math.erfc(abs(z) / math.sqrt(2.0))


def implied_p(yi, se):
    if se is None or se <= 0:
        return None
    return 2.0 * norm_sf(yi / se)


def num(x):
    x = (x or "").strip().replace("−", "-")
    if x in ("", "NA"):
        return None
    try:
        return float(x)
    except ValueError:
        return None


def triaged():
    if not os.path.exists(TRIAGE):
        return set()
    out = set()
    for ln in open(TRIAGE, errors="replace"):
        m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z0-9_]+)\s*\|", ln)
        if m and m.group(2).lower() != "marker":
            out.add((m.group(1).strip(), m.group(2).strip()))
    return out


def main(argv):
    want = argv[0].lower() if argv else None
    rows = list(csv.DictReader(open(HARMONISED, newline="")))
    if want:
        rows = [r for r in rows if want in r["trial_id"].lower()]
    counts = {"OK": 0, "SOFT": 0, "HARD": 0, "skipped": 0}
    soft, hard = [], []
    for r in rows:
        p_print = num(r.get("p_reported"))
        bound = (r.get("p_is_bound") or "").strip().upper() == "TRUE"
        yi, se = num(r.get("yi")), num(r.get("se"))
        if p_print is None or bound or yi is None or se is None or se <= 0:
            counts["skipped"] += 1
            continue
        p_imp = implied_p(yi, se)
        if p_imp is None:
            counts["skipped"] += 1
            continue
        if p_print < FLOOR and p_imp < FLOOR:
            counts["OK"] += 1
            continue
        lo, hi = sorted((max(p_print, 1e-12), max(p_imp, 1e-12)))
        ratio = hi / lo
        crosses = (p_print < 0.05) != (p_imp < 0.05)
        # Dead band around the conventional threshold. A printed 0.0504 against an implied 0.0482 is
        # the same number twice and crosses 0.05 only because the line is drawn there; flagging it
        # teaches the reader to ignore the gate. Both values inside [0.02, 0.10] is agreement.
        if 0.02 <= p_print <= 0.10 and 0.02 <= p_imp <= 0.10:
            crosses = False
        if abs(p_print - 0.05) < 1e-9 and 0.01 <= p_imp <= 0.2:
            crosses = False
        rec = (r["trial_id"], r["biomarker"], r.get("dose_mg", ""), p_print, p_imp, ratio,
               r.get("se_source", ""), yi, se)
        if crosses or ratio > HARD_RATIO:
            counts["HARD"] += 1
            hard.append(rec)
        elif ratio > SOFT_RATIO:
            counts["SOFT"] += 1
            soft.append(rec)
        else:
            counts["OK"] += 1
    done = triaged()
    untriaged = [h for h in hard if (h[0], h[1]) not in done]
    print(f"p value reconciliation over {len(rows)} row(s)")
    for k in ("OK", "SOFT", "HARD", "skipped"):
        print(f"  {k:8} {counts[k]}")
    def show(title, recs):
        if not recs:
            return
        print(f"\n{title}")
        for t, b, d, pp, pi, ratio, route, yi, se in sorted(recs, key=lambda x: -x[5]):
            tag = "triaged  " if (t, b) in done else "UNTRIAGED"
            print(f"  {tag} {t[:34]:36} {b:16} dose {str(d)[:5]:>5} printed p {pp:<9.4g} "
                  f"implied p {pi:<9.4g} ratio {ratio:>8.1f}  yi {yi:>9.3f} se {se:>8.3f} {route}")
    show("HARD rows: the printed p and the printed interval do not reconcile", hard)
    show("SOFT rows: an order of magnitude apart, same side of 0.05", soft)
    sys.exit(1 if untriaged else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
