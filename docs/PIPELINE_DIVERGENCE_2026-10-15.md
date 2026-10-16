# Two implementations: the prespecified pipeline and the gate scripts have diverged

Found 2026-10-15, 21:50 local, by running `analysis/M5_AGE_analysis_pipeline.R` on the current master. Recorded because it decides where the manuscript's numbers may come from.

## What was executed

| Step | Result |
|---|---|
| `Rscript analysis/M5_AGE_analysis_pipeline.R`, first run | stopped at package loading: `netmeta` not installed |
| after installing `netmeta` | stopped: `dmetar` not installed; it is not on CRAN for R 4.5.2 and was installed from GitHub (`MathiasHarrer/dmetar`) |
| after installing `patchwork` and `sessioninfo` | reached `check_integrity()` and stopped: "pct_weight_change missing for at least one trial" |
| what would follow | `escalc(measure = "SMD", m1i = mean_tx, sd1i = sd_tx, …)` on rows with `outcome_type == "continuous"`; the current master carries `outcome_type` values `contrast` and `arm_means`, contrast level `yi`, `se`, `vi` and the harmonised `yi_pct`, `vi_pct`; zero rows would reach the estimator |

## Why this matters

| Fact | Consequence |
|---|---|
| The pipeline implements the public analysis plan (REML, HKSJ, four estimator sweep, 10,000 permutation meta regression, two level BCa composite, nine sensitivity analyses, influence diagnostics, SHA-256 manifest) against the original schema of arm level means and SDs and Hedges' g | It cannot run on the data as extracted, because this literature reports contrasts, not arm SDs (`docs/LESSONS.md`, schema correction of 2026-10-15), and because the unit harmonisation layer was built outside it |
| The eight gate scripts (`build_master`, `harmonise_units`, `pool_biomarkers`, `compute_composite`, `receptor_class_contrast`, with `verify`, `selftest`, `validate_pipeline`) are what produces every number quoted in the docs and the session records | They are the operational analysis. They implement REML plus HKSJ, Table 2, the composite under the inclusion rule, and the Q2 coverage logic, but not the permutation meta regression, the estimator sweep, the BCa intervals, the influence diagnostics or the manifest |
| `verify.R` Gate 2 checks the pipeline's declarations (seed, estimators, prediction intervals, permutations, composite normalisation, BCa) by reading its text, and `selftest.R` proves those checks can fail | Gate 2 passes on a pipeline that cannot execute. A declaration check is not an execution check. `validate_pipeline.R` does execute `pool_effect` and `compute_nbais` on simulated data, so those two functions are exercised; the data path from the master to them is not |
| `check_integrity()` still requires `pct_weight_change` on every row | The rule that was relaxed in `build_master.R` on 2026-10-15 ("require only what the analysis needs, where it needs it") was never propagated to the pipeline |

## Decision required

The manuscript must draw from one path. Two options:

| Option | Work | Risk |
|---|---|---|
| A. Port the prespecified pipeline onto the harmonised master: replace the `escalc` block with a reader of `yi_pct`, `vi_pct`, `receptor_class`, `pct_weight_change`, `rob_overall`; keep `pool_effect`, `run_weight_adjusted_metareg`, `compute_nbais`, `nbais_boot`, `sensitivity_*`, diagnostics and the manifest; drop or gate the `netmeta` block until a connected network exists; relax `check_integrity` to the build master rules; make `verify.R` Gate 2 execute the pipeline on `validate_pipeline`'s simulated master | A day of careful work; every prespecified feature survives; one path |
| B. Declare the gate scripts the analysis and retire the pipeline | Faster; loses the permutation inference, BCa intervals, estimator sweep and influence diagnostics the plan promises, each of which would then have to be rebuilt in the gate scripts anyway |

Recommendation: A, in a dedicated session, with the gate chain kept green throughout and the port verified by reproducing Table 2 and the composite to the last decimal before anything else is added.

## Environment

Installed on the workstation during this probe: `netmeta` 3.7-0 (with `meta` 8.5-0), `dmetar` from GitHub, `patchwork`, `sessioninfo`. `renv.lock` is still absent; `requirements.R` is the only dependency record. Generating the lock file belongs to the same session as the port.

## Resolution, 16 October 2026: option A executed, one blocker remains

Option A was taken. `analysis/M5_AGE_analysis_pipeline.R` now reads
`analysis/data/extraction_master_harmonised.csv`, takes `yi_pct` and `vi_pct` as the effect and its
variance rather than recomputing a standardised mean difference from arm level data this literature
does not publish, and applies the two selection rules the gate scripts had and it did not.

`check_integrity` was relaxed to the build master principle, require only what the analysis needs
where it needs it. The old rule failed on 392 of 453 continuous rows for missing arm SDs and on any
row missing `pct_weight_change`; the covariate is now required where the meta regression runs, which
excludes 161 rows from that regression alone and is reported rather than fatal.

### The acceptance test

`src/table2_reproduction_check.py` compares the ported pipeline's per biomarker pooling against the
gate scripts' `table2_pooled_by_biomarker.csv` on estimate, both confidence bounds, both prediction
bounds, tau squared and k.

**28 of 28 shared biomarkers agree to within 0.001.** Six biomarkers the gate scripts carry are
absent from the pipeline's table for reasons the test states as a rule rather than a list: four have
k = 1 and `pool_effect` refuses fewer than two trials, and two are binary outcomes pooled on the log
odds ratio scale in their own table.

Reaching that agreement took two corrections to the port, and both were found by the test rather than
by reading:

| Correction | Why it mattered |
|---|---|
| Collapse to one arm per trial per biomarker, highest dose | The first run pooled 18 liver fat rows where the analysis pools 9, 44 HbA1c rows where it pools 38, and 94 dose arms in total. Dose arms share a control, so pooling them as independent studies narrows every interval. The rule is `src/pool_biomarkers.R` decision 1 |
| Suppress prediction intervals below k = 3 | metafor returns one from two studies, where tau rests on a single degree of freedom. It disagreed with the analysis on exactly the two biomarkers that have two trials, body fat percentage and lean mass |

### What this surfaced, for the Director

| Item | Status |
|---|---|
| The pooling scale is percent change, not Hedges' g as registered | A protocol deviation already present in every reported number. The port does not introduce it; it makes the registered pipeline compute what is reported. Needs approval and a Methods disclosure |
| One arm per trial per biomarker, highest dose | A real analytic decision, absent from the registered plan, visible in the pooled k of every biomarker, and currently implicit in a script. Needs a Methods sentence |
| Four biomarkers are reported in Table 2 with k = 1 | BMD, ICAM1, YKL40 and MR-proANP appear in a synthesis table with an estimate and a confidence interval that are one trial's. A reader infers synthesis. Recommend a separate single trial section of the table rather than removal, since the evidence is real and the presentation is what misleads |
| The weight adjusted meta regression does not complete | `metafor::rma()` reports "Fisher scoring algorithm did not converge" on the second biomarker of the loop. This is the prespecified inferential core and it has never run before today, so the failure is new information rather than a regression. It is the remaining blocker on the port |

### Remaining work on the port

1. The convergence failure above. Options are an optimiser change, a fallback estimator recorded per
   biomarker, or skipping the affected biomarker with the reason carried into the table; the choice
   affects what the manuscript can claim, so it is not a silent fix.
2. The shared control collapse is now stated in two places, `src/pool_biomarkers.R` and the pipeline.
   That is the duplicated rule defect this repository has hit three times. One of them must become
   the definition and the other must call it.
3. Figures 1, 4 and 5 are generated only by this pipeline and `figures/` is still empty; they follow
   once the run completes.
4. `renv.lock` is still absent. `requirements.R` remains the only dependency record.
