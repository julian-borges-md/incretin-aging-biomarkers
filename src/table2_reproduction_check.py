#!/usr/bin/env python3
"""
table2_reproduction_check.py

The acceptance test for the pipeline port recorded in docs/PIPELINE_DIVERGENCE_2026-10-15.md.

Until 16 October this review had two analysis implementations. The prespecified pipeline,
analysis/M5_AGE_analysis_pipeline.R, implements the registered plan but could not run on the data as
extracted, because it was written around arm level means and standard deviations that this
literature does not publish. The gate scripts under src/ produced every number in the manuscript but
implement only part of the plan: no permutation meta regression, no bias corrected composite
intervals, no estimator sweep, no influence diagnostics, no output manifest.

The port points the prespecified pipeline at the harmonised master. Its correctness is not a matter
of opinion: pooling the same rows by the same estimator must give the same numbers the manuscript
already reports. This script is that comparison, biomarker by biomarker, over the estimate, both
confidence bounds, both prediction bounds, tau squared and k.

A difference in the last decimal is expected and allowed, because the two implementations format and
round independently. A difference a reader would notice is not.

Usage
  python3 -I src/table2_reproduction_check.py
  exit 1 on any biomarker where the two implementations disagree beyond tolerance, or where one
  table holds a biomarker the other does not
"""
import csv
import os
import sys

ROOT = os.getcwd()
GATE = os.path.join(ROOT, "analysis", "output", "table2_pooled_by_biomarker.csv")
PIPE = os.path.join(ROOT, "analysis", "output", "table2_pipeline.csv")

# Gate column -> pipeline column. The gate scripts and the pipeline named these independently.
FIELDS = [("est", "estimate"), ("lo", "ci_lb"), ("hi", "ci_ub"),
          ("pi_lo", "pi_lb"), ("pi_hi", "pi_ub"), ("tau2", "tau2")]
# Tolerance on a percent change scale. Estimates run to tens of per cent, so a thousandth of a
# percentage point is far below anything a reader could see and far above floating point noise.
TOL = 1e-3


def load(path, key="biomarker"):
    if not os.path.exists(path):
        sys.exit(f"missing {os.path.relpath(path, ROOT)}; run the pipeline first")
    return {r[key]: r for r in csv.DictReader(open(path, newline=""))}


def num(x):
    x = (x or "").strip()
    if x in ("", "NA", "NaN"):
        return None
    try:
        return float(x)
    except ValueError:
        return None


# Biomarkers the ported pipeline is expected not to carry in this table, stated as a rule rather
# than a list so that a new omission still fails.
#   - binary outcomes pool as log odds ratios through a separate estimator and a separate table
#   - a biomarker with fewer than two contributing trials is refused by pool_effect, which returns
#     NULL below k = 2. The gate scripts do report those rows, with an estimate and a confidence
#     interval that are one trial's, and whether a synthesis table should present them that way is
#     a reporting decision for the Director, recorded in the commit that added this check
BINARY = {"MASH_resolution", "fibrosis_improvement"}


def expected_omission(bm, gate_row):
    if bm in BINARY:
        return "binary outcome, pooled on the log odds ratio scale in its own table"
    k = num(gate_row.get("k"))
    if k is not None and k < 2:
        return f"k = {int(k)}, below the two trials pool_effect requires"
    return None


def main():
    gate, pipe = load(GATE), load(PIPE)
    missing = {bm: expected_omission(bm, gate[bm]) for bm in sorted(set(gate) - set(pipe))}
    only_gate = sorted(bm for bm, why in missing.items() if why is None)
    only_pipe = sorted(set(pipe) - set(gate))
    shared = sorted(set(gate) & set(pipe))
    bad = []
    for bm in shared:
        g, p = gate[bm], pipe[bm]
        if num(g.get("k")) != num(p.get("k")):
            bad.append((bm, "k", num(g.get("k")), num(p.get("k"))))
        for gf, pf in FIELDS:
            a, b = num(g.get(gf)), num(p.get(pf))
            if a is None and b is None:
                continue
            if a is None or b is None or abs(a - b) > TOL:
                bad.append((bm, gf, a, b))
    print(f"Table 2 reproduction: {len(shared)} biomarker(s) in both implementations")
    print(f"  agreeing within {TOL} on estimate, both confidence bounds, both prediction bounds, "
          f"tau squared and k: {len(shared) - len({b[0] for b in bad})}")
    accounted = {bm: why for bm, why in missing.items() if why}
    if accounted:
        print("  carried by the gate scripts and not by the pipeline, for stated reasons:")
        for bm, why in sorted(accounted.items()):
            print(f"    {bm:22} {why}")
    if only_gate:
        print(f"  UNEXPLAINED, in the gate scripts only: {', '.join(only_gate)}")
    if only_pipe:
        print(f"  in the ported pipeline only: {', '.join(only_pipe)}")
    if bad:
        print("\nDisagreements, gate value against pipeline value")
        for bm, f, a, b in bad:
            d = "" if (a is None or b is None) else f"  diff {abs(a - b):.6g}"
            print(f"  {bm:20} {f:8} {a!s:>22} {b!s:>22}{d}")
    sys.exit(1 if (bad or only_gate or only_pipe) else 0)


if __name__ == "__main__":
    main()
