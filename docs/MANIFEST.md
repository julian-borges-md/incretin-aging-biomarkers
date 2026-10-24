# Reproducibility Manifest

This repository is published at the protocol and pipeline stage. **No pooled estimate has been computed and none is reported.** That is the central fact a reader needs, and it governs everything below.

Repositories in this line normally carry a claim to evidence map, where every asserted number maps to a command that re-derives it. There are no asserted numbers yet. What `make verify` checks instead is the contract: that the code still implements the protocol the prespecification commits to, and that the pipeline cannot silently pool malformed data.

## What the green badge means

| It means | It does not mean |
|---|---|
| The analysis pipeline still declares the seed, estimators, interval types and inference method fixed in `prespecification/` | That results exist |
| The extraction schema still covers every column the pipeline reads by name | That any trial has been extracted |
| The pipeline's integrity function still rejects each malformed input the protocol names | That any estimate has been computed |
| Each of those gates has been proven able to fail | That the manuscript is complete |

## Gate to command map

| Gate | Checks | Command |
|---|---|---|
| 1 | Schema header is well formed, no duplicate columns, every column the pipeline reads by name is declared | `make verify` |
| 2a | Pipeline sets the pre-specified seed `20261013` | `make verify` |
| 2b | All four between-study variance estimators (REML, DL, PM, SJ) are referenced | `make verify` |
| 2c | Pipeline emits prediction interval bounds, not confidence intervals alone | `make verify` |
| 2d | Meta-regression uses permutation inference at the pre-specified 10,000 iterations | `make verify` |
| 2e | The composite is normalised by the sum of weights, so it is a weighted mean and not a weighted sum | `make verify` |
| 2f | Bootstrap requests BCa intervals | `make verify` |
| 3 | The pipeline's `check_integrity` accepts well formed input and rejects: unknown receptor class, harmonised columns absent, no usable continuous row, non-positive variance, undeclared aging direction, weight covariate absent throughout | `make verify` |
| 4 | Every table under `analysis/data`, `analysis/output` and `search` has a header and as many fields on each line as its header; an empty file is refused | `make verify` |
| 5 | The reference run raised no warning: `analysis/output/run_warnings.csv`, written by the pipeline before its manifest, has its header and no row, and it exists whenever the manifest does | `make verify` |
| 6 | Every gate above can fail. The unperturbed copy must pass, then ten perturbations are applied in temporary copies and `verify.R` must exit non-zero for each | `make selftest` |

Gate 2e exists because the error it guards against is specific and consequential. A weighted sum grows with the number of biomarkers measured, so a receptor class studied with a broader panel would score higher as an artifact of measurement coverage. The triple agonist node is expected to carry roughly seven biomarkers against sixteen for GLP-1 mono, which is precisely the circumstance that would turn a coverage difference into a false biological finding.

## The CI gate against fabrication

A second CI job, `no-fabricated-results`, fails if the manuscript's results sections stop being marked `[PENDING` while `analysis/data/extraction_master.csv` is absent from the repository. Publishing a protocol before its data creates one specific failure mode, which is that a placeholder is later replaced by a plausible number with nothing behind it. This job makes that failure visible rather than silent.

## When results exist

On completion of extraction this file is replaced by a claim to evidence map in the usual form: one row per asserted finding, the command that re-derives it, and the expected value. The pipeline writes `analysis/output/MANIFEST.csv` listing every output file with its SHA-256 hash, so a reviewer can confirm the files accompanying a submission are exactly those the script produced.

## Reproduction

```
make install     # reference package set (requirements.R)
make pin         # record the exact package versions the run used
make verify      # gates 1 to 5, no data and no network needed
make selftest    # gate 6, proves the gates can fail
make analysis    # full pipeline; requires analysis/data/extraction_master.csv
```

## Statistical validation

`make validate` is the third gate, and it answers a different question from the other two. `verify` checks that the code still declares what the protocol commits to. `selftest` checks that `verify` can fail. Neither checks whether the statistics are **correct**.

`src/validate_pipeline.R` simulates data under known true parameters, passes it through the same `pool_effect` and `compute_nbais` functions the real analysis uses (lifted from the pipeline at runtime, not reimplemented), and asserts recovery. Values below are produced by that script under seed 20261013 and reproduce on rerun.

| Test | What it establishes | Result |
|---|---|---|
| 1 | A known pooled effect of 0.450 is recovered | 0.425, 95% CI 0.307 to 0.543; true tau 0.200 recovered as 0.230 |
| 1 | The prediction interval is genuinely wider than the confidence interval | CI width 0.236, PI width 0.932; PI spans -0.041 to 0.891 while the CI excludes zero |
| 2 | Interval coverage is nominal, over 500 replications at k = 8 | 0.952 with HKSJ, against an acceptance band of 0.95 ± 0.029 derived from the binomial standard error |
| 2 | The HKSJ rule below k = 10 is empirically motivated, not decorative | Uncorrected coverage 0.924, an undercoverage of 0.028 |
| 3 | The composite is invariant to how many biomarkers a class happens to have measured | Identical to 0 decimal places across a 16 marker and a 7 marker panel with identical per marker effects |
| 3 | The weighted sum this protocol rejects would have inflated instead | 750.00 against 328.12, a 2.29 fold artifact driven purely by panel size |
| 4 | The direction indicator handles the unfavorable axis correctly | 15 favorable markers at +0.30 with lean mass at 0.60 unfavorable gives 0.24375, matching the hand calculation exactly |
| 4 | A dominant unfavorable axis can drive the composite negative | -0.03125, so the metric can express the clinical concern that motivates it |
| 5 | A receptor effect is not invented where none exists | Class coefficient -0.041, p = 0.563 against a truth of zero |
| 5 | A real receptor effect survives adjustment for weight loss | 0.375 recovered against a truth of 0.350, p < 0.0001, with the weight slope recovered as 0.0426 against a truth of 0.0400 |

Test 1 is the clearest illustration of why this protocol reports prediction intervals everywhere. The confidence interval excludes zero; the prediction interval does not. A reader given only the first would conclude the next trial will show an effect. The second says it may not.

Test 3 is the load bearing one. The triple agonist node is expected to carry roughly seven measured biomarkers against sixteen for GLP-1 mono. Had the composite been built as a weighted sum, that coverage difference alone would have produced a 2.29 fold apparent advantage for the better studied class, with no biology behind it.

### A real bug this caught

Test 5 initially failed. The class effect came back as -0.375 against a truth of +0.350: correct magnitude, inverted sign. The cause was that the simulation left `receptor_class` as a character vector, so R ordered the levels alphabetically, placing `GLP1_GCGR` before `GLP1_mono` and making the GCGR class the reference. Every class contrast then pointed the wrong way.

The pipeline sets factor levels explicitly and was never affected. But the failure mode is worth naming, because it is the most dangerous kind available here: the magnitude is right, every diagnostic looks healthy, and only the sign is wrong. Nothing about the output announces the error. The validation now pins the reference level and fails loudly if it ever moves.
