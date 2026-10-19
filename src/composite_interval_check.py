#!/usr/bin/env python3
"""
composite_interval_check.py

Chain gate, run after the fifteen provenance gates. Asks whether every composite interval
contains the estimate it belongs to.

The gates are not numbered in these docstrings. Numbering them means stating the order in two
places, the chain script and every script in it, and this repository has been bitten three times by
a rule stated twice. scripts/run_gates.sh is the order; its log records what ran.

Why this gate exists. The first implementation of the Net Biological Age Impact Score passed a
stochastic statistic to boot::boot and asked for the bias corrected and accelerated interval.
BCa is defined for a statistic that is a deterministic function of the resample; this one draws
from each pooled estimate's sampling distribution inside the resample, so t0 was one random draw
and the bias correction constant was computed against it. The printed result for GLP1_GCGR under
equal weighting was 15.97 (19.51 to 39.73): an estimate outside its own confidence interval. The
figure built from that table would have drawn error bars that did not reach the top of their own
bar, and the Results would have quoted an interval that excludes the number it qualifies.

Nothing in the fifteen gate chain could see it. The pipeline ran to completion, the numbers were
finite and plausibly signed, and every other gate checks extraction and provenance rather than the
internal coherence of a computed interval. This gate closes that class: an interval that does not
contain its own point estimate is arithmetically impossible for a percentile interval and
indefensible for any other, so it stops the chain.

What it checks, per row of analysis/output/table5_nbais.csv:
  1. ci_lb <= ci_ub
  2. ci_lb <= nbais <= ci_ub          the defect above
  3. ci_type is declared, not blank   an undeclared interval method cannot be reported
  4. the BCa columns are either a computed pair or an explicit not_computable status, never a
     silent NA, and when computed the pair is reported if it excludes the point, as information
     rather than as a failure, because BCa is the secondary interval here
and, per row of analysis/output/table5a_nbais_contrasts.csv with status "computed":
  5. ci_lb <= diff <= ci_ub

A case written up in docs/COMPOSITE_INTERVAL_TRIAGE.md does not fail the gate, under the same rule
the other triage gates use: a judged case is recorded, a new one blocks.

Usage
  python3 -I src/composite_interval_check.py
  python3 -I src/composite_interval_check.py --self-test
"""
import csv
import os
import sys

ROOT = os.getcwd()
NBAIS = os.path.join(ROOT, "analysis", "output", "table5_nbais.csv")
CONTRASTS = os.path.join(ROOT, "analysis", "output", "table5a_nbais_contrasts.csv")
TRIAGE = os.path.join(ROOT, "docs", "COMPOSITE_INTERVAL_TRIAGE.md")


def num(s):
    if s is None:
        return None
    s = s.strip()
    if s == "" or s.upper() in ("NA", "NAN", "NULL"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def triaged_keys():
    """Keys named in the triage document, one per line as `- key: ...`."""
    keys = set()
    if not os.path.exists(TRIAGE):
        return keys
    with open(TRIAGE) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("- key:"):
                keys.add(line.split("- key:", 1)[1].strip())
    return keys


def check_nbais(rows):
    """Return (failures, notes). Each failure is (key, message)."""
    failures, notes = [], []
    for r in rows:
        key = "nbais|%s|%s" % (r.get("receptor_class", ""), r.get("weighting", ""))
        point, lo, hi = num(r.get("nbais")), num(r.get("ci_lb")), num(r.get("ci_ub"))
        ci_type = (r.get("ci_type") or "").strip()

        # A class with fewer included markers than the composite floor is reported as a row with no
        # estimate and a stated reason, which is the honest record of a quantity that was not
        # computed. It is not checked for an interval it does not have, but it must say why: a blank
        # row would be indistinguishable from a row the pipeline forgot.
        status = (r.get("status") or "").strip()
        if status and status != "computed":
            if point is not None or lo is not None or hi is not None:
                failures.append((key, "status is %r and yet an estimate or bound is present"
                                 % status))
            elif ":" not in status:
                failures.append((key, "status %r does not state why the composite was not computed"
                                 % status))
            else:
                notes.append("%s: %s" % (key, status))
            continue

        if not ci_type:
            failures.append((key, "ci_type is blank; an interval whose method is not declared "
                                 "cannot be reported"))
        if point is None:
            failures.append((key, "nbais is missing"))
            continue
        if lo is None or hi is None:
            failures.append((key, "interval bound missing: ci_lb=%r ci_ub=%r"
                             % (r.get("ci_lb"), r.get("ci_ub"))))
            continue
        if lo > hi:
            failures.append((key, "ci_lb %.4f exceeds ci_ub %.4f" % (lo, hi)))
        elif not (lo <= point <= hi):
            failures.append((key, "estimate %.4f lies outside its own interval %.4f to %.4f"
                             % (point, lo, hi)))

        # The declared check column must agree with the arithmetic, or the column is decoration.
        declared = (r.get("point_inside_ci") or "").strip().upper()
        if declared in ("TRUE", "FALSE"):
            actual = "TRUE" if (lo is not None and hi is not None and lo <= point <= hi) else "FALSE"
            if declared != actual:
                failures.append((key, "point_inside_ci says %s, arithmetic says %s"
                                 % (declared, actual)))

        bca_lo, bca_hi = num(r.get("bca_lb")), num(r.get("bca_ub"))
        bca_status = (r.get("bca_status") or "").strip()
        if bca_lo is None or bca_hi is None:
            if not bca_status.startswith("not_computable"):
                failures.append((key, "BCa bounds are absent and bca_status is %r; an absent "
                                      "interval must say why" % bca_status))
        else:
            if bca_status != "computed":
                failures.append((key, "BCa bounds present but bca_status is %r" % bca_status))
            if not (bca_lo <= point <= bca_hi):
                notes.append("%s: the secondary BCa interval %.4f to %.4f excludes the estimate "
                             "%.4f; the primary percentile interval is the reported one"
                             % (key, bca_lo, bca_hi, point))
            elif bca_hi - bca_lo > (hi - lo):
                notes.append("%s: BCa interval is wider than the primary (%.2f against %.2f)"
                             % (key, bca_hi - bca_lo, hi - lo))
    return failures, notes


def check_contrasts(rows):
    failures = []
    for r in rows:
        if (r.get("status") or "").strip() != "computed":
            continue
        key = "contrast|%s" % r.get("comparison", "")
        d, lo, hi = num(r.get("diff")), num(r.get("ci_lb")), num(r.get("ci_ub"))
        if d is None or lo is None or hi is None:
            failures.append((key, "computed contrast with a missing estimate or bound"))
            continue
        if lo > hi:
            failures.append((key, "ci_lb %.4f exceeds ci_ub %.4f" % (lo, hi)))
        elif not (lo <= d <= hi):
            failures.append((key, "difference %.4f lies outside its own interval %.4f to %.4f"
                             % (d, lo, hi)))
    return failures


def read(path):
    if not os.path.exists(path):
        print("MISSING: %s" % os.path.relpath(path, ROOT))
        return None
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def self_test():
    """A gate that has reported nothing has not shown that it works.

    Inject the defect this gate exists for, as it was actually printed, and require the gate to
    catch it; then inject a point_inside_ci column that lies, and require that too.
    """
    bad = [{
        "receptor_class": "GLP1_GCGR", "weighting": "equal", "nbais": "15.965005752606972",
        "ci_lb": "19.508552479620302", "ci_ub": "39.72625406259983",
        "ci_type": "bca", "point_inside_ci": "TRUE",
        "bca_lb": "19.508552479620302", "bca_ub": "39.72625406259983", "bca_status": "computed",
    }]
    failures, _ = check_nbais(bad)
    msgs = " | ".join(m for _k, m in failures)
    ok_outside = any("outside its own interval" in m for _k, m in failures)
    ok_lying = any("point_inside_ci says TRUE" in m for _k, m in failures)

    liar = [{
        "receptor_class": "X", "weighting": "equal", "nbais": "1.0",
        "ci_lb": "0.0", "ci_ub": "2.0", "ci_type": "percentile_two_level",
        "point_inside_ci": "FALSE", "bca_lb": "", "bca_ub": "",
        "bca_status": "not_computable: too few markers",
    }]
    f2, _ = check_nbais(liar)
    ok_liar2 = any("point_inside_ci says FALSE" in m for _k, m in f2)

    blank = [{
        "receptor_class": "X", "weighting": "equal", "nbais": "1.0", "ci_lb": "0.0",
        "ci_ub": "2.0", "ci_type": "", "point_inside_ci": "TRUE",
        "bca_lb": "", "bca_ub": "", "bca_status": "not_computable: x",
    }]
    f3, _ = check_nbais(blank)
    ok_blank = any("ci_type is blank" in m for _k, m in f3)

    contrast_bad = [{"comparison": "A vs B", "status": "computed", "diff": "5.0",
                     "ci_lb": "6.0", "ci_ub": "9.0"}]
    ok_contrast = any("outside its own interval" in m
                      for _k, m in check_contrasts(contrast_bad))

    print("SELF TEST")
    print("  estimate outside its interval caught : %s" % ok_outside)
    print("  point_inside_ci TRUE but false caught: %s" % ok_lying)
    print("  point_inside_ci FALSE but true caught: %s" % ok_liar2)
    print("  blank ci_type caught                 : %s" % ok_blank)
    print("  contrast outside its interval caught : %s" % ok_contrast)
    print("  messages: %s" % msgs)
    passed = all([ok_outside, ok_lying, ok_liar2, ok_blank, ok_contrast])
    print("  %s" % ("PASS" if passed else "FAIL"))
    return 0 if passed else 1


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
        if rc != 0:
            return rc
        print()

    nbais = read(NBAIS)
    contrasts = read(CONTRASTS)
    if nbais is None:
        print("FAIL: run the analysis pipeline first")
        return 1

    failures, notes = check_nbais(nbais)
    if contrasts is not None:
        failures += check_contrasts(contrasts)

    triaged = triaged_keys()
    blocking = [(k, m) for k, m in failures if k not in triaged]
    accepted = [(k, m) for k, m in failures if k in triaged]

    print("composite interval check")
    print("  %d composite row(s), %d contrast row(s)"
          % (len(nbais), 0 if contrasts is None else len(contrasts)))
    for k, m in accepted:
        print("  TRIAGED  %s: %s" % (k, m))
    for n in notes:
        print("  NOTE     %s" % n)
    if not blocking:
        print("  every interval contains its own estimate")
        return 0
    print("\nFAIL: %d interval(s) do not contain their own estimate or declare their method"
          % len(blocking))
    for k, m in blocking:
        print("  %s: %s" % (k, m))
    print("\nEither correct the interval or write the case up in docs/COMPOSITE_INTERVAL_TRIAGE.md")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
