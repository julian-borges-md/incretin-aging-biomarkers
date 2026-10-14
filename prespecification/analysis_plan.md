# Prespecification

Fixed 2026-10-14, before any trial was extracted. The analysis pipeline was written before the extraction file existed. Timestamped by the commit history of this repository.

The purpose of fixing this in public is narrow and specific: no later choice of estimator, moderator, weighting scheme or subgroup can be made after seeing the estimates.

## Questions

| # | Question |
|---|---|
| Q1 | Which established aging biomarkers are modified by incretin and glucagon receptor containing peptide therapies, and in which direction |
| Q2 | Does the aging biomarker signature differ by receptor class |
| Q3 | Is the hepatic aging signal with GCGR containing agents independent of weight loss magnitude |
| Q4 | Can a composite score compare receptor classes on a single scale |
| Q5 | What thresholds would define metabolic age normalization sufficient to justify a structured discontinuation trial |

## Hypotheses

| # | Hypothesis | Direction fixed in advance |
|---|---|---|
| H1 | GCGR containing agents produce greater hepatic benefit per unit of weight loss than GLP-1 mono agents | Receptor class coefficient for liver fat remains non-null after adjustment for percentage weight change |
| H2 | Lean mass is the single aging domain in which the class moves unfavorably | Pooled lean mass effect is negative in direction adjusted terms across all four classes |
| H3 | Multi-receptor agonism produces a broader favorable signature than mono-agonism | Composite score higher for dual and triple than for mono, stable across all three weighting schemes |
| H4 | GDF-15 modification tracks GIP receptor engagement rather than receptor breadth | Not testable with current data; recorded so that it cannot be claimed as a post hoc prediction if data later appear |

H4 is stated as untestable deliberately. It is the prediction the corpus most invites and the one no published data can currently address.

## Receptor classes

| Class | Molecules |
|---|---|
| GLP1_mono | semaglutide, liraglutide |
| GLP1_GIP | tirzepatide |
| GLP1_GCGR | survodutide, mazdutide, pemvidutide, cotadutide |
| GLP1_GIP_GCGR | retatrutide |

Class assignment follows the molecule's receptor pharmacology, not the trial's framing or indication.

## Eligibility

| Element | Inclusion | Exclusion |
|---|---|---|
| Design | Randomized controlled trials | Observational, single arm, retrospective |
| Population | Adults 18 or over with overweight, obesity, type 2 diabetes, MASH or MASLD | Pediatric, type 1 diabetes, post bariatric |
| Intervention | The ten molecules above plus amycretin, cagrilintide, CagriSema | Exenatide and dulaglutide except as comparators |
| Outcome | At least one biomarker from the 26 marker intersection inventory | No aging relevant biomarker reported |
| Duration | 12 weeks or more | Under 12 weeks |

## Primary and secondary outcomes

Primary: weight adjusted aging biomarker change by receptor class, and the composite score per receptor class.

Secondary: the GDF-15 receptor class differential; MASH resolution and fibrosis improvement by receptor class adjusted for weight; lean mass change as the unfavorable axis by receptor class.

Tertiary: off treatment regain kinetics by domain and class, where data exist.

## Analysis plan

Fixed in full before extraction. Summarised here; implemented in `analysis/M5_AGE_analysis_pipeline.R`, which `make verify` checks has not drifted from it.

| Element | Specification |
|---|---|
| Effect size, continuous | Hedges' g; mean difference reported alongside where scales match |
| Effect size, binary | Log odds ratio, continuity correction applied only to zero cells |
| Primary estimator | REML random effects |
| Sensitivity estimators | DerSimonian-Laird, Paule-Mandel, Sidik-Jonkman |
| Small sample correction | Hartung-Knapp-Sidik-Jonkman when fewer than 10 trials contribute |
| Uncertainty | Confidence interval and prediction interval on every pooled estimate |
| Primary heterogeneity statistic | tau-squared; I-squared reported for comparability only |
| Meta-regression | `biomarker ~ receptor_class + pct_weight_change`, plus the interaction; four nested models; permutation inference at 10,000 iterations |
| Model identifiability | Fitted only where trials exceed estimated parameters by at least three |
| Composite | Weighted mean of direction adjusted standardized effects, normalised by the sum of weights |
| Composite weighting | Inverse variance primary; equal weighting sensitivity; clinical importance exploratory |
| Composite intervals | Two level BCa bootstrap, 10,000 resamples: biomarker level resampling plus perturbation of each estimate by its own standard error |
| Class contrasts | Difference bootstrapped directly, restricted to biomarkers measured in both classes |
| Network | Frequentist graph theoretical; four node class network primary, ten node drug network in parallel; node splitting and design by treatment interaction |
| Small study effects | Egger and trim and fill only where 10 or more trials contribute; otherwise reported not assessable |
| Influence | Leave one out on every estimate with at least three trials |
| Seed | 20261013 |

## Pre-specified sensitivity analyses

Nine, fixed in advance: drug level versus class level network; T2D versus non-T2D; MASH versus non-MASH; dose stratification within class; trial duration in three bands; industry versus non-industry; DXA only versus combined body composition methods; exclusion of high risk of bias trials; the four estimator sweep.

## Reporting rules, fixed in advance

**Fragility.** A pooled estimate whose direction or statistical significance reverses on removal of a single trial is reported as fragile and is not advanced as a conclusion, whatever its nominal p value.

**Ranking stability.** The composite ranking of receptor classes is reported as a finding only where it is stable across all three weighting schemes. Where the ranking changes with the weighting, that instability is itself reported as the result.

**Class level pooling.** If the drug level and class level networks disagree materially, the class level simplification is reported as invalidated rather than preferred.

**Coverage disclosure.** Any composite score or contrast is reported with the number of contributing biomarkers stated alongside it. A score computed over seven biomarkers is not presented as commensurate with one computed over sixteen.

## Threats acknowledged in advance

**Ecological fallacy.** Trial level slopes can differ in magnitude and sign from within patient relationships. Every conclusion is framed about drug classes, never about individuals.

**Overadjustment.** Weight loss plausibly lies on the causal path from receptor engagement to biomarker improvement. Conditioning on it removes part of the effect being estimated. The adjusted estimate is therefore read as a conservative lower bound, and the unadjusted coefficient is reported beside it.

**Undetectable reporting bias.** Aging biomarkers in this literature appear predominantly in industry post hoc analyses rather than pre-specified endpoints. Selective reporting in that setting is not detectable by funnel asymmetry, because unreported results never enter the literature as small imprecise studies. The `prespecified_endpoint` field is extracted so the extent of post hoc reporting is at least visible. No statistical method available here resolves it.
