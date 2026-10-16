# Protocol amendment, 15 October 2026: three analysis rules and the operational inventory

Recorded after full text retrieval of five placebo controlled mono agonist trials (Derosa 2012, Wu 2011, Anholm 2019, Wägner 2019, von Scholten 2017). Provenance of the ordering, so it can be checked in the history: the three rules were stated as open decisions with the recommended option in commit 43adbb3 (`docs/MONO_TRIALS_RETRIEVAL_2026-10-15.md`) while no row from these trials existed in the master; this file and the rows landed together in the following commit. The prompting observation was structural (what the papers report and in what form), not any pooled result; no class contrast involving these trials had been computed when the options were recorded.

## R1. Parallel group trials reporting baseline and final arm means with SDs but no SD of change

| Item | Rule |
|---|---|
| Problem | Three of the five trials tabulate mean (SD) per arm at baseline and at end of study and nothing about the within patient change. A final value contrast reproduces any chance baseline imbalance as a treatment effect (Wägner 2019: CRP 0.37 against 0.66 mg/dL at entry in a 24 patient trial, final value P = 0.017, within arm changes P = 0.99 and P = 0.57). The extraction schema defines mean_tx and sd_tx as change quantities, so final values cannot be entered there without redefining the columns |
| Rule | The contrast is the difference of mean changes. The SD of change in each arm is imputed from the reported baseline and final SDs with an assumed pre post correlation r: sd_change = sqrt(sd_base^2 + sd_final^2 − 2 r sd_base sd_final), Cochrane Handbook section 6.5.2.8. The pooled SD and SE follow the arm_sds formula |
| r | 0.5 for the primary analysis, recorded on every row in corr_assumed; the build refuses a row on this route without it. Sensitivity reruns at 0.3 and 0.7 |
| Direction of the assumption | A lower r gives a larger change SD and a wider interval. If 0.5 overstates the true correlation the primary interval is too narrow, which is why the 0.3 rerun is mandatory and reported |
| Implementation | Route arm_change_imputed_r in src/extraction_tools.R, with counterexamples asserted at source time (equal SDs with r = 0.5 give sd_change = 1; a baseline imbalance with equal within arm changes gives a zero contrast); nine new schema columns |
| Not applied to | Rows that report a contrast with an interval, a standard error, an exact p, or arm means with SEMs: those routes are unchanged |

## R2. Operational inventory against the prespecified Table 1 inventory

Q1 is phrased as "which of a pre-specified set of 26 biomarkers". The 26 are listed in the manuscript's Table 1. The markers actually extracted and pooled had drifted from that list in both directions before this amendment, and the drift was undocumented.

| Status | Markers |
|---|---|
| In Table 1 and pooled | hsCRP, IL-6, GDF-15, YKL-40, ICAM-1, leptin, fasting insulin, HOMA-IR, fasting glucose, liver fat PDFF, ALT, AST |
| Pooled but not in Table 1 (added opportunistically during extraction, before this amendment) | NT-proBNP, adiponectin, HOMA-beta, C-peptide, glucagon, GGT, fatty liver index |
| Added by this amendment | TNF-alpha (inflammaging, lower is better, provisional clinical weight 3 as for IL-6; reported by eight mono trials in the screening pool and by Derosa, Anholm and von Scholten here); MR-proANP (cardiac aging, lower is better, provisional weight 2 as for NT-proBNP; reported by von Scholten as a prespecified endpoint). Neither enters the eleven marker composite inclusion rule; both appear in Table 2 and in the S3 all markers sensitivity |
| In Table 1 and not extracted | HbA1c, SBP, DBP, triglycerides, LDL, total cholesterol, total lean mass, body fat percentage, visceral adipose tissue, BMD, eGFR, resting heart rate, MASH resolution, fibrosis improvement. These are not excluded; they have not been extracted yet, and the Methods must say so |
| Not admitted | MR-proADM, suPAR, copeptin, MCP-1, PGF2alpha: reported by the new trials but outside any aging hallmark domain named in the protocol |

Rule going forward: a marker enters the master only if it is in Table 1 or is listed in this table with its domain, direction and provisional weight, and the manuscript reports the operational inventory as it was pooled, not as Table 1 reads.

## R3. Crossover trials

| Item | Rule |
|---|---|
| Rule | The contrast is the reported within patient treatment difference (end of period versus end of period, or change versus change where that is the authors' primary contrast), with its reported interval or exact p. It is never recomputed from arm level SDs, which would ignore the pairing |
| Applied to | von Scholten 2017 (percent differences with 95 per cent CI from a paired log scale analysis: ci_95 route); Anholm 2019 (median of paired differences with a signed rank p: exact_p route, with the approximation stated on the row) |
| Scale | A paired median difference is an approximation to a mean difference on a skewed marker; such rows carry the approximation in their notes and are candidates for the leave one out analysis |
| Denominators | A percent conversion needs a baseline MEAN. Anholm reports medians only, so its rows stay in native units and do not enter the percent scale pooling; this is recorded rather than worked around |

## Related deviations now made explicit

| Deviation | Where it was made | Status |
|---|---|---|
| Composite weighting: the plan names inverse variance as primary and equal weighting as sensitivity; compute_composite.R reports equal weighting as primary because inverse variance across biomarkers weights by how precisely each marker happened to be measured (SELECT's hsCRP alone took 85 per cent) | Origin session, documented in the script header, not previously in prespecification/ | Recorded here; both schemes are reported in every run; the plan's ranking stability rule applies |
| Composite inputs: the composite was built on fixed effect inverse variance means per marker while the plan's primary estimator is REML with Hartung Knapp | Found 2026-10-15 when five hsCRP trials made the two diverge (−36.9 against −26.4) | Corrected: compute_composite.R now takes each marker's estimate and standard error from Table 2 |
| Highest dose rule drops within trial cross class arms (Wilson 2021 dulaglutide) | Origin session | Open; recorded in the SIRLP addendum; not changed by this amendment |

Baseline denominators entered under R1 for the percent scale are keyed by trial and biomarker in src/harmonise_units.R, each with the table and arithmetic that produced it.
