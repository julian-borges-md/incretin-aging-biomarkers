[![verify](https://github.com/julian-borges-md/incretin-aging-biomarkers/actions/workflows/verify.yml/badge.svg)](https://github.com/julian-borges-md/incretin-aging-biomarkers/actions/workflows/verify.yml)
[![Code](https://img.shields.io/badge/Code-R-blue)](#)
[![Design](https://img.shields.io/badge/Design-Systematic_review_%2B_network_meta--analysis-blue)](#)
[![Statistics](https://img.shields.io/badge/Statistics-validated_against_known_truth-brightgreen)](docs/MANIFEST.md#statistical-validation)
[![Stage](https://img.shields.io/badge/Stage-protocol_and_pipeline_complete-yellow)](docs/MANIFEST.md)
[![Results](https://img.shields.io/badge/Results-not_yet_extracted-lightgrey)](docs/MANIFEST.md)
[![Prespecified](https://img.shields.io/badge/Analysis_plan-fixed_before_extraction-orange)](prespecification/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

# Beyond Disease-Specific Endpoints

### A geroscience framework for evaluating incretin and glucagon receptor agonism through aging biomarker signatures

**Author:** Julian Borges, MD, MS

---

## Project Overview

Incretin based therapies are evaluated one disease at a time. Weight loss for obesity, HbA1c for diabetes, histology for steatohepatitis, major adverse cardiac events for atherosclerosis. Each indication has its own trials and its own meta-analyses, and the fragmentation is appropriate for regulatory purposes.

It also obscures something. The biomarkers these drugs move are, to a striking extent, the same biomarkers the geroscience literature uses to index biological aging. Of 26 markers that function simultaneously as metabolic endpoints and as established aging markers, incretin based therapies modify at least 16, and 14 of those move in the direction associated with slower biological aging. Two, lean mass and resting heart rate, move the other way.

This project asks whether that pattern differs by **receptor class** rather than by molecule, and whether the hepatic component of it survives adjustment for the weight loss that accompanies it.

The question is now answerable because the evidence base changed. Semaglutide has been shown in a randomized trial to decelerate validated epigenetic aging clocks. No equivalent data exist for any dual or triple agonist.

---

## Pre-specified questions

| # | Question |
|---|---|
| Q1 | Which established aging biomarkers are modified by incretin and glucagon receptor containing peptide therapies, and in which direction |
| Q2 | Does the aging biomarker signature differ by receptor class: GLP-1 mono, GLP-1/GIP dual, GLP-1/GCGR dual, GLP-1/GIP/GCGR triple |
| Q3 | Is the hepatic aging signal with GCGR containing agents independent of weight loss magnitude |
| Q4 | Can a composite Net Biological Age Impact Score compare receptor classes on a single scale |
| Q5 | What thresholds would define metabolic age normalization sufficient to justify a structured discontinuation trial |

Hypotheses and the full analysis plan were fixed in `prespecification/` before any trial was extracted. The analysis pipeline was written before the extraction file existed.

---

## Status

This repository is published at the protocol and pipeline stage. **No pooled estimate has been computed, and none is reported.**

| Component | State |
|---|---|
| Pre-specified protocol, 12 sections | Complete |
| Analysis pipeline, executable | Complete |
| Extraction schema, 51 columns | Complete |
| Anchor reference corpus, 29 papers, DOI verified | Complete |
| Manuscript: Introduction, Methods, Discussion | Complete |
| Trial extraction | **Not started** |
| Results, Tables 2 to 5 and 7, Figures 1 to 6 | **Blocked on extraction** |

The badge above is green when the pipeline's integrity gates and self test pass, not when results exist. Publishing the protocol and the code before the data is deliberate: it fixes the analysis plan in a public, timestamped form, so that no later choice of estimator, moderator or weighting scheme can be made after seeing the estimates.

---

## Methods and tools

| Layer | Choice |
|---|---|
| Language | R 4.4+ (metafor, netmeta, meta, dmetar, boot, tidyverse) |
| Environment | Reference package set in `requirements.R`; the exact versions a run used recorded by `make pin` in `analysis/output/environment_pinned.csv` |
| Determinism | `set.seed(20261013)` on every stochastic operation |
| Effect size, continuous | Hedges' g; mean difference reported alongside where scales match |
| Effect size, binary | Log odds ratio, continuity correction applied only to zero cells |
| Pooling | Random effects, REML primary; DerSimonian-Laird, Paule-Mandel and Sidik-Jonkman as sensitivity |
| Small sample | Hartung-Knapp-Sidik-Jonkman when fewer than 10 trials contribute |
| Uncertainty | Confidence interval **and** prediction interval on every pooled estimate |
| Heterogeneity | tau-squared primary, I-squared reported for comparability |
| Meta-regression | Permutation inference, 10,000 iterations |
| Composite metric | Weighted mean, not weighted sum; two level BCa bootstrap, 10,000 resamples |
| Class contrasts | Difference bootstrapped directly, restricted to shared biomarkers |
| Network | Frequentist graph theoretical, node splitting and design by treatment interaction |
| Reporting | PRISMA 2020 and PRISMA-NMA |

---

## Three statistical decisions worth stating

**The prediction interval is reported everywhere, not the confidence interval alone.** A confidence interval describes uncertainty about the mean effect across past trials. A prediction interval describes where the true effect of the next trial is expected to fall. Under non-negligible heterogeneity these can point in opposite directions, and the second is the one a clinician needs.

**The composite is a weighted mean, not a weighted sum.** A sum grows with the number of biomarkers measured, so a drug studied with a broader panel would score higher as an artifact of measurement coverage. Dividing by the total weight keeps the score on the effect size scale and makes classes with unequal coverage comparable. This matters concretely: the triple agonist node will carry roughly seven biomarkers against sixteen for GLP-1 mono.

**Class differences are bootstrapped directly rather than read off overlapping intervals.** Inferring a difference from whether two confidence intervals overlap is an invalid test. Pairwise contrasts resample both classes simultaneously and are restricted to biomarkers measured in both, so a difference cannot be manufactured by unequal panels.

---

## Three threats stated in the Methods, not deferred to the Limitations

| Threat | Why it is in the Methods |
|---|---|
| Ecological fallacy | Trial level slopes can differ in sign from within patient relationships. Every conclusion is framed about drug classes, never about individuals |
| Overadjustment | Weight loss plausibly lies on the causal path from receptor engagement to biomarker improvement. Conditioning on it biases the receptor coefficient toward the null, so the adjusted estimate is reported as a conservative lower bound, with the unadjusted estimate beside it |
| Undetectable reporting bias | Aging biomarkers appear mostly in industry post hoc analyses. Unreported unfavorable panels never enter the literature as small imprecise studies, so funnel asymmetry cannot find them. No method available here resolves this |

---

## Repository layout

```
analysis/
  M5_AGE_analysis_pipeline.R   sole source of every number in the paper
  data/extraction_schema.csv   51 column extraction contract
  output/                      generated; includes MANIFEST.csv with SHA-256
docs/
  MANIFEST.md                  claim to command map
  RUNBOOK.md                   full reproduction path
  REFERENCES.md                29 anchor papers, DOI verified
manuscript/
prespecification/              analysis plan, fixed before extraction
src/
  verify.R                     gate checks
  selftest.R                   proves the gates can fail
```

---

## Reproduction

```
make install     # the reference package set (requirements.R)
make pin         # record the exact package versions the run used
make verify      # integrity gates on the extraction contract
make selftest    # proves verify fails on perturbed input
make validate    # proves the statistics recover known truth
make analysis    # runs the pipeline (requires analysis/data/extraction_master.csv)
```

`verify` and `selftest` need no data and no network. Both run in CI.

---

## Citation

See `CITATION.cff`. Correspondence: jyborges@bu.edu | ORCID [0009-0001-9929-3135](https://orcid.org/0009-0001-9929-3135)
