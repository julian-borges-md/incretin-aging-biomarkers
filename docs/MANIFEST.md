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
| 3 | The pipeline's `check_integrity` accepts well formed input and rejects: unknown receptor class, missing standard deviation, non-positive variance, undeclared aging direction, missing weight covariate | `make verify` |
| 4 | Every gate above can fail. Seven perturbations are applied in a temporary copy and `verify.R` must exit non-zero for each | `make selftest` |

Gate 2e exists because the error it guards against is specific and consequential. A weighted sum grows with the number of biomarkers measured, so a receptor class studied with a broader panel would score higher as an artifact of measurement coverage. The triple agonist node is expected to carry roughly seven biomarkers against sixteen for GLP-1 mono, which is precisely the circumstance that would turn a coverage difference into a false biological finding.

## The CI gate against fabrication

A second CI job, `no-fabricated-results`, fails if the manuscript's results sections stop being marked `[PENDING` while `analysis/data/extraction_master.csv` is absent from the repository. Publishing a protocol before its data creates one specific failure mode, which is that a placeholder is later replaced by a plausible number with nothing behind it. This job makes that failure visible rather than silent.

## When results exist

On completion of extraction this file is replaced by a claim to evidence map in the usual form: one row per asserted finding, the command that re-derives it, and the expected value. The pipeline writes `analysis/output/MANIFEST.csv` listing every output file with its SHA-256 hash, so a reviewer can confirm the files accompanying a submission are exactly those the script produced.

## Reproduction

```
make install     # reference package set; renv.lock pins exact versions
make verify      # gates 1 to 3, no data and no network needed
make selftest    # gate 4, proves the gates can fail
make analysis    # full pipeline; requires analysis/data/extraction_master.csv
```
