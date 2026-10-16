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
