#!/usr/bin/env python3
"""
arm_orientation_check.py

Fourth provenance gate. The numbers check asks whether a row's numbers occur in its source; the
attachment check asks whether they sit next to the right biomarker; the p value gate asks whether a
row's interval and its p value reconcile. None of them can see a swapped treatment and control arm.
A swap leaves every number present, attached and internally consistent, and inverts the finding.

What this does, per row of the master
  1. keep the rows that carry BOTH a reported effect and both printed arm values, which is the only
     configuration in which the two can be compared at all
  2. recompute the between group contrast from the arm values on the row's own scale
  3. compare it with the reported effect and classify
       HARD   the two have opposite signs, both being distinguishable from zero at the printed
              precision, which is the signature of a swapped arm; or they differ by more than
              rounding and model adjustment together can explain, which is the signature of a value
              read from the wrong row of a table
       SOFT   they differ by more than rounding alone but less than the hard threshold
       OK     they agree within the rounding bound of the three printed numbers
  4. report, separately and without failing, the rows whose gap exceeds the rounding bound, because
     those are the rows whose reported effect is model adjusted rather than the raw arm difference,
     and therefore the rows whose arm values must not be used to re derive the effect

The contrast form depends on the measure, and this is the part that is easy to get wrong.
  MD    the contrast is the arithmetic difference, mean_tx minus mean_ctrl
  PCT   a percent change is on the ratio scale, so the contrast of two percent changes is NOT their
        arithmetic difference but (1 + tx/100) / (1 + ctrl/100) - 1. The four PCT rows in scope
        match the ratio form to the last printed digit and none of them match the arithmetic form;
        the largest discrepancy under the arithmetic form is 8.4 percentage points on a 42 per cent
        effect. The self test injects the arithmetic contrast into each PCT row and reports how many
        the gate rejects: at present one of four. That is the honest limit and not a defect. The two
        forms diverge in proportion to how far the comparator arm moved, so on a row whose
        comparator barely changed they agree to within a few per cent and no numerical check can
        separate them. The gate catches the error on rows where it changes the answer.

Tolerance. The rounding bound is built from the printed precision of the three numbers rather than
assumed: a value printed to one decimal carries a half width of 0.05, and the bound is the sum over
the two arm values and the effect. On top of rounding, a reported effect is usually an ANCOVA or
MMRM estimate with covariates, so it does not have to equal the raw arm difference; the hard
threshold is set well above that gap and the soft band carries it.

Scope limits, stated so the green result is not read as more than it is.
  - Rows whose effect was DERIVED from the arm values cannot be checked here. A swap flips the
    derived effect too, so the two agree by construction and the comparison is empty. The script
    counts these rows rather than passing them silently.
  - Rows with no printed arm values are out of scope entirely.
  - The gate cannot tell an adjusted estimate from a raw difference, which is why a gap inside the
    soft band is information and not a defect.

Nothing is corrected here. HARD rows are the verifier's reading list.

Usage
  python3 -I src/arm_orientation_check.py                  all rows, summary plus the lists
  python3 -I src/arm_orientation_check.py TRIAL_SUBSTRING  one trial
  python3 -I src/arm_orientation_check.py --self-test      mutate known good rows, prove it fires
  exit 1 when any HARD row is not written up in docs/ARM_ORIENTATION_TRIAGE.md, or when the self
  test fails to detect an injected swap
"""
import csv
import os
import re
import sys

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
TRIAGE = os.path.join(ROOT, "docs", "ARM_ORIENTATION_TRIAGE.md")

RATIO_MEASURES = {"PCT"}      # percent change: contrast is a ratio of ratios, not a difference
HARD_RB = 4.0                 # multiples of the rounding bound
HARD_REL = 0.60               # fraction of the implied contrast
SOFT_RB = 2.0
SOFT_REL = 0.20
# Ceiling on the relative escape. The relative clause exists to absorb the gap between an adjusted
# estimate and the raw arm difference, which is real but bounded; it is not a licence for any gap at
# all provided the effect is large. A gap of twenty rounding bounds is no longer explicable as
# printed precision, and the second condition keeps a very high precision row, whose bound is tiny,
# from tripping on an absolutely negligible gap. Every row of the present corpus sits below 1.7
# rounding bounds and the injected errors of the self test sit above 500, so the margin either side
# of twenty is more than an order of magnitude; the figure is a round choice inside that gap and not
# a derived quantity.
CEIL_RB = 20.0
CEIL_REL = 0.05


def raw(r, k):
    return (r.get(k) or "").strip().replace("−", "-")


def num(r, k):
    x = raw(r, k)
    if x in ("", "NA"):
        return None
    try:
        return float(x)
    except ValueError:
        return None


KEYS = ("mean_tx", "mean_ctrl", "yi_reported")


def decimals(x):
    """Decimal places carried by a printed number, or None when it has no decimal point."""
    if "e" in x.lower():
        return None
    return len(x.split(".")[1]) if "." in x else None


def half_widths(r):
    """
    Half widths of the rounding intervals of the three numbers, per row.

    The master CSV does not preserve trailing zeros: a source that printed -1.0 is stored as -1, and
    read literally that claims a half width of 0.5 rather than 0.05, overstating the bound tenfold
    and disarming the gate on precisely the rows where the arms are close. So a value that carries a
    decimal point is taken at its own precision, which is evidence, and a value that carries none
    inherits the finest precision seen elsewhere in the same row, which is an inference from the
    convention that a journal does not mix precision within one column family. The convention has
    counterexamples: a table may print an effect to one more decimal than the arm values it came
    from, and under that counterexample this bound is too tight. Too tight produces a flag on the
    verifier's reading list, while too loose produces a swapped arm that nobody sees, so the error
    is taken in the direction that is visible. A row whose three numbers all lack a decimal point
    offers no evidence at all; it keeps the literal half width of 0.5 and is reported as a row the
    gate cannot protect rather than as a row that passed.
    """
    obs = {k: decimals(raw(r, k)) for k in KEYS}
    known = [d for d in obs.values() if d is not None]
    fine = max(known) if known else None
    out = {}
    for k, d in obs.items():
        if d is None:
            d = fine if fine is not None else 0
        out[k] = 0.5 * (10.0 ** -d)
    return out, (fine is None)


def contrast(measure, tx, ctrl):
    """The between group contrast implied by the two arm values, on the row's own scale."""
    if measure in RATIO_MEASURES:
        den = 1.0 + ctrl / 100.0
        if abs(den) < 1e-9:
            return None
        return ((1.0 + tx / 100.0) / den - 1.0) * 100.0
    return tx - ctrl


def rounding_bound(r, measure, tx, ctrl):
    """Propagate the printed precision of the three numbers into a bound on the gap."""
    h, no_evidence = half_widths(r)
    h_tx, h_ct, h_y = h["mean_tx"], h["mean_ctrl"], h["yi_reported"]
    if measure in RATIO_MEASURES:
        # d(contrast)/d(tx) = 100/(100+ctrl), d/d(ctrl) = -(100+tx)*100/(100+ctrl)^2
        den = 100.0 + ctrl
        if abs(den) < 1e-9:
            return h_tx + h_ct + h_y
        g_tx = abs(100.0 / den)
        g_ct = abs((100.0 + tx) * 100.0 / (den * den))
        return g_tx * h_tx + g_ct * h_ct + h_y
    return h_tx + h_ct + h_y


def classify(r):
    """
    Return (verdict, implied_contrast, gap, rounding_bound, blind) or None when out of scope.

    blind is True when a swapped arm on this row would not have been detected: either the row offers
    no printed precision at all, or the two arms sit within the rounding bound of each other, so the
    swap changes a quantity that is indistinguishable from zero either way. A blind row is not a
    passing row and the report keeps the two apart.
    """
    measure = raw(r, "measure")
    y, tx, ctrl = num(r, "yi_reported"), num(r, "mean_tx"), num(r, "mean_ctrl")
    if y is None or tx is None or ctrl is None:
        return None
    d = contrast(measure, tx, ctrl)
    if d is None:
        return None
    rb = rounding_bound(r, measure, tx, ctrl)
    gap = abs(y - d)
    swapped = y * d < 0 and abs(y) > rb and abs(d) > rb
    beyond_precision = gap > CEIL_RB * rb and gap > CEIL_REL * abs(d)
    if swapped or beyond_precision or (gap > HARD_RB * rb and gap > HARD_REL * abs(d)):
        v = "HARD"
    elif gap > SOFT_RB * rb and gap > SOFT_REL * abs(d):
        v = "SOFT"
    else:
        v = "OK"
    # Blindness is decided by the comparison, not by whether the precision had to be assumed. When
    # a row offers no printed decimals at all the bound already defaults to the most conservative
    # value available, so a contrast that clears even that bound is still a contrast a swap would
    # have inverted visibly. Treating unknown precision as blindness would have reported the 4B
    # adiponectin row, whose arms differ by 160 pg/mL, as a row the gate cannot see.
    _, no_evidence = half_widths(r)
    return v, d, gap, rb, abs(d) <= rb, no_evidence


def triaged():
    if not os.path.exists(TRIAGE):
        return set()
    out = set()
    for ln in open(TRIAGE, errors="replace"):
        m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z0-9_]+)\s*\|", ln)
        if m and m.group(2).lower() != "marker":
            out.add((m.group(1).strip(), m.group(2).strip()))
    return out


def self_test(rows):
    """Prove the gate fires. A gate that has never flagged anything has not been shown to work."""
    ok = [r for r in rows if (classify(r) or ("",))[0] == "OK"]
    if not ok:
        print("self test: no OK row to mutate")
        return False
    failures = []
    # 1. swap the arms of every OK row and require HARD, except where the two arms are so close
    #    that a swap is not detectable at the printed precision, which is an honest limit
    swap_hard = swap_blind = 0
    for r in ok:
        m = dict(r)
        m["mean_tx"], m["mean_ctrl"] = r["mean_ctrl"], r["mean_tx"]
        v = (classify(m) or ("",))[0]
        if classify(r)[4]:
            swap_blind += 1
        elif v == "HARD":
            swap_hard += 1
        else:
            failures.append(f"swap of {r['trial_id'][:30]} {r['biomarker']} classified {v}, not HARD")
    # 2. move one printed digit of the treatment arm and require HARD
    shift_hard = 0
    for r in ok[:12]:
        m = dict(r)
        tx = num(r, "mean_tx")
        if tx is None or abs(tx) < 1e-9:
            continue
        m["mean_tx"] = f"{tx * 10.0:.{len(raw(r, 'mean_tx').split('.')[1]) if '.' in raw(r, 'mean_tx') else 0}f}"
        if (classify(m) or ("",))[0] == "HARD":
            shift_hard += 1
        else:
            failures.append(f"tenfold shift of {r['trial_id'][:30]} {r['biomarker']} not HARD")
    # 3. a PCT row subtracted arithmetically instead of ratio wise must not pass as OK
    pct_caught = pct_seen = 0
    for r in rows:
        if raw(r, "measure") not in RATIO_MEASURES:
            continue
        c = classify(r)
        if not c or c[0] != "OK":
            continue
        pct_seen += 1
        tx, ctrl = num(r, "mean_tx"), num(r, "mean_ctrl")
        m = dict(r)
        m["yi_reported"] = f"{tx - ctrl:.2f}"          # the arithmetic contrast, which is wrong here
        if (classify(m) or ("",))[0] != "OK":
            pct_caught += 1
    print(f"self test: arm swap detected on {swap_hard} row(s), undetectable on {swap_blind} "
          f"(arms within rounding of each other)")
    print(f"self test: tenfold digit shift detected on {shift_hard} row(s)")
    print(f"self test: arithmetic contrast on a ratio scale row rejected on {pct_caught} of "
          f"{pct_seen} PCT row(s)")
    for f in failures:
        print("  FAIL " + f)
    return not failures


def main(argv):
    selftest = "--self-test" in argv
    argv = [a for a in argv if not a.startswith("--")]
    want = argv[0].lower() if argv else None
    rows = list(csv.DictReader(open(MASTER, newline="")))
    if want:
        rows = [r for r in rows if want in r["trial_id"].lower()]
    counts = {"OK": 0, "SOFT": 0, "HARD": 0}
    out_of_scope_derived = out_of_scope_noarms = assumed = 0
    flagged, adjusted, blind = [], [], []
    for r in rows:
        c = classify(r)
        if c is None:
            if raw(r, "mean_tx") not in ("", "NA") and raw(r, "mean_ctrl") not in ("", "NA"):
                out_of_scope_derived += 1          # arm values present, effect derived from them
            else:
                out_of_scope_noarms += 1
            continue
        v, d, gap, rb, is_blind, no_evidence = c
        counts[v] += 1
        if no_evidence:
            assumed += 1
        rec = (r["trial_id"], r["biomarker"], raw(r, "dose_mg"), raw(r, "measure"),
               num(r, "yi_reported"), num(r, "mean_tx"), num(r, "mean_ctrl"), d, gap, rb,
               raw(r, "se_route"))
        if v != "OK":
            flagged.append((v, rec))
        elif is_blind:
            blind.append(rec)
        elif gap > rb:
            adjusted.append(rec)
    done = triaged()
    untriaged = [rec for v, rec in flagged if v == "HARD" and (rec[0], rec[1]) not in done]
    print(f"arm orientation over {len(rows)} row(s)")
    print(f"  in scope, effect and both arms printed   {sum(counts.values())}")
    for k in ("OK", "SOFT", "HARD"):
        print(f"    {k:6} {counts[k]}")
    print(f"      of the OK rows, a swap would not have shown on {len(blind)}")
    print(f"  precision assumed, no decimals printed in the master  {assumed}")
    print(f"  out of scope, effect derived from arms   {out_of_scope_derived}")
    print(f"  out of scope, no printed arm values      {out_of_scope_noarms}")

    def show(title, recs, gating=True):
        if not recs:
            return
        print(f"\n{title}")
        for t, b, dose, meas, y, tx, ct, d, gap, rb, route in sorted(recs, key=lambda x: -x[8]):
            # The allowlist governs HARD rows only, so an informational row gets no triage tag.
            tag = ("triaged  " if (t, b) in done else "UNTRIAGED") if gating else "info     "
            print(f"  {tag} {t[:32]:34} {b:18} dose {dose[:5]:>5} {meas:4} "
                  f"reported {y:>9.3f}  arms {tx:>9.3f} / {ct:>9.3f}  implied {d:>9.3f}  "
                  f"gap {gap:>7.3f} bound {rb:>6.3f} {route}")

    show("HARD rows: the arms and the reported effect do not reconcile",
         [rec for v, rec in flagged if v == "HARD"])
    show("SOFT rows: a gap beyond rounding but short of the hard threshold",
         [rec for v, rec in flagged if v == "SOFT"])
    show("Reported effect is model adjusted, not the raw arm difference (information only)",
         adjusted, gating=False)
    show("Rows the gate cannot protect: the arms sit within the rounding bound of each other, "
         "so a swap would change an effect that is indistinguishable from zero either way",
         blind, gating=False)
    bad = False
    if selftest:
        print()
        bad = not self_test(rows)
    sys.exit(1 if (untriaged or bad) else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
