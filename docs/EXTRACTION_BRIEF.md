# Extraction brief, systematic corpus, version 1.0 (16 October 2026)

Instructions followed by every extractor (a session agent reading one study packet) and by the
reconciler. The brief is versioned; a change is a new version with its date, never an edit in place.

## 1. Unit of extraction and the one rule that outranks the rest

One row per trial, intervention arm (each dose), comparator, biomarker and timepoint. Every row is a
contrast against the concurrent control arm of the same trial: a treatment effect (difference or
ratio) or the per arm values from which the pipeline computes one. A within arm change with no
concurrent control is never a row (the GDF-15 error of 15 October came from joining within arm
changes across trials). A trial with no control arm yields no rows and is recorded in the ledger.

## 2. Eligibility re check at the first page

| Element | Rule | If it fails |
|---|---|---|
| Design | randomised, parallel or crossover; single arm, observational, pooled post hoc across trials without a concurrent control: not eligible | ledger status excluded_at_extraction, reason design |
| Population | adults 18 or over with overweight, obesity, type 2 diabetes, MASH or MASLD; not type 1, not paediatric, not post bariatric, not a disease outside this list as the defining population | excluded_at_extraction, reason population |
| Intervention | semaglutide, liraglutide, tirzepatide, survodutide, mazdutide, pemvidutide, cotadutide, retatrutide, amycretin, cagrilintide, CagriSema; exenatide and dulaglutide admitted by amendment R4; any other molecule (lixisenatide, albiglutide, efpeglenatide, orforglipron, danuglipron, beinaglutide, PEG loxenatide, others) is NOT admitted | ledger status molecule_not_admitted with the molecule named; no rows; the Director decides whether an amendment admits it |
| Comparator | placebo, lifestyle or usual care, or an active drug (record comparator_type placebo, lifestyle, active) | a trial comparing two admitted molecules yields rows for each against the other only when one is a mono agonist comparator; record it and flag cross_class in notes |
| Duration | 12 weeks or more on treatment at the extracted timepoint | excluded_at_extraction, reason duration |
| Outcome | at least one inventory biomarker (analysis/data/biomarker_inventory.csv) reported with a usable contrast | no rows; ledger lists the biomarkers reported without usable variance |

Receptor class follows the molecule's pharmacology, not the trial's framing: GLP1_mono (semaglutide,
liraglutide, exenatide, dulaglutide), GLP1_GIP (tirzepatide), GLP1_GCGR (survodutide, mazdutide,
pemvidutide, cotadutide), GLP1_GIP_GCGR (retatrutide). Amycretin, cagrilintide and CagriSema are
eligible interventions that the pipeline's four level class factor does not hold: record
receptor_class GLP1_AMY and the molecule; such rows stay in staging until the Director confirms the
fifth level (decision D-X1), because build_master asserts the factor levels.

## 3. Which numbers

| Preference order | Columns to fill | se_source | When |
|---|---|---|---|
| 1 | yi_reported, ci_lb_reported, ci_ub_reported | ci_95 | a treatment difference or ratio with a 95% interval |
| 2 | yi_reported, se_reported | se_reported | a difference with its standard error |
| 3 | yi_reported, p_reported, p_is_bound | exact_p | a difference with an exact two sided p; a bound ("p < 0.001") is recorded with p_is_bound TRUE and is unusable for pooling (do not invent a value) |
| 4 | mean_tx, sem_tx, mean_ctrl, sem_ctrl, n_tx, n_ctrl | arm_sems | least squares mean change per arm with SEM |
| 5 | mean_tx, sd_tx, mean_ctrl, sd_ctrl, n_tx, n_ctrl | arm_sds | mean change per arm with SD of the change |
| 6 | base_mean_tx, base_sd_tx, final_mean_tx, final_sd_tx, base_mean_ctrl, base_sd_ctrl, final_mean_ctrl, final_sd_ctrl, n_tx, n_ctrl, corr_assumed = 0.5 | arm_change_imputed_r | baseline and final per arm with SDs and no SD of change (amendment R1) |

Rules on the numbers:

1. Prefer the contrast the authors report over per arm values; prefer the prespecified analysis over a post hoc one; prefer the primary timepoint (end of treatment) and record assessment_timepoint_weeks. If several timepoints are reported, take the longest on treatment timepoint of 12 weeks or more; an earlier timepoint may be added as a second row only when the trial's primary endpoint is at that earlier time.
2. Scale: record measure as reported: pct_change (percent change from baseline), abs_change (absolute units, name the unit in notes), ratio (geometric mean ratio or ratio of change: the pipeline logs it; put the ratio and its interval on the natural scale and write measure RR), log_ratio (already logged). For abs_change rows record base_mean_tx and base_mean_ctrl whenever the paper gives them, because the percent scale needs a baseline denominator.
3. Medians with IQR: record them in notes with the biomarker named, not as a row, unless the authors give a contrast with an interval or exact p (amendment R3 for crossover trials).
4. Standard deviation versus standard error: write which one the paper gives; SEM goes in sem_*, SD in sd_*. A table that says "mean (SD)" at baseline and "mean (SE)" for change is common; do not mix them up. If the paper gives a 95% CI per arm, convert nothing: record the arm mean with the CI in notes and use the contrast route if a contrast is reported.
5. Crossover trials: the reported within patient treatment difference with its interval or exact p (amendment R3); never recomputed from period means.
6. Multiple doses: one row per dose arm against the same control. Multiple active comparators: one row per comparator with comparator_type.
7. Binary markers (MASH resolution, fibrosis improvement): events_tx, events_ctrl, n_tx, n_ctrl, outcome_type binary; if only an odds ratio with CI is given, yi_reported with the interval, measure OR, se_source log_OR_ci.
8. Nothing is computed by the extractor beyond copying: no subtraction of arm means, no SE from a CI, no percent from absolute values. The pipeline does the arithmetic and records the route.
9. pct_weight_change: the intervention arm's mean percent body weight change at the extracted timepoint, placebo corrected when the paper gives the contrast (say which in notes), otherwise the arm's own change; absolute kg with the baseline weight in notes when percent is not given; NA when nothing is reported.

## 4. Study level fields

trial_id (NCT number when the paper gives one; otherwise a stable label, author year), pmid, doi,
first_author, year, journal, phase, drug, receptor_class, dose_mg (the maintenance dose; for weekly
and daily agents the dose as given, with the frequency in notes), comparator, comparator_type,
duration_weeks, population (T2D, obesity, MASH, MASLD, mixed), n_tx and n_ctrl (participants with
outcome data for that row; randomised numbers in notes if the analysed numbers are not given),
industry_funded (TRUE when the sponsor is a manufacturer or the trial is sponsor run),
prespecified_endpoint (TRUE only when the paper or its registration names the biomarker as a
primary or secondary endpoint; post hoc and exploratory analyses are FALSE), rob_overall (RoB-2:
low, some_concerns, high) with a one line justification per domain in notes
(randomisation, deviations, missing data, measurement, selective reporting), coi in notes.

## 5. Biomarker naming

Use the biomarker key of analysis/data/biomarker_inventory.csv exactly (hsCRP, IL6, GDF15, YKL40,
ICAM1, leptin, fasting_insulin, HOMA_IR, HbA1c, fasting_glucose, SBP, DBP, liver_fat_pdff, ALT, AST,
MASH_resolution, fibrosis_improvement, TG, LDL, TC, lean_mass, body_fat_pct, VAT, BMD, eGFR,
resting_heart_rate, NTproBNP, adiponectin, HOMA_beta, C_peptide, glucagon, GGT, fatty_liver_index,
TNF_alpha, MR_proANP) with the inventory's hallmark_domain, aging_direction and clinical_weight
copied onto the row. A marker outside the inventory (MCP-1, suPAR, copeptin, cystatin C, epigenetic
clocks, others) is written in the ledger's other_markers field, never as a row. CRP that is not
high sensitivity is recorded as hsCRP with "standard CRP assay" in notes.

## 6. Output

Two independent extractors (A and B) each write one CSV for the study group, columns in the order
of analysis/data/extraction_wilson2021_tirzepatide.csv or extraction_ekinci2026_survodutide.csv
(route columns as needed), to work/extraction/staging/<group>/<extractor>.csv, plus a short
ledger note (JSON: status, molecule, design, reasons, biomarkers_reported_no_variance,
other_markers, pages or tables used). The reconciler compares A and B row by row; agreement on
every numeric field within rounding becomes analysis/data/extraction_<author><year>_<drug>.csv
(tracked); every disagreement is settled by a third read of the cited table, and the resolution
is written in the row's notes. An extractor never sees the other extractor's file.

## 7. What the extractor does not do

Does not decide eligibility beyond Section 2 (doubt is recorded, not resolved). Does not search for
other papers of the same trial (the ledger notes "companion paper needed" instead). Does not fill
a number that is not on the page. Does not round beyond the paper's precision. Does not change a
biomarker's direction or weight. Does not write to analysis/data directly.

## Version 1.1 amendments, 16 October 2026, after the pilot (group 253, Fan 2013)

| Amendment | Rule | Why |
|---|---|---|
| A1 rounded p values | A p value printed as "P = 0.00" or "P = 0.000" is a rounded bound, not an exact p: record p_is_bound TRUE; prefer an arm route when per arm changes with SD or SEM are given | the pilot paper prints P = 0.00 for its main contrasts |
| A2 weight covariate | pct_weight_change holds percent only. When the paper gives kilograms, leave the field empty and write the kg change and the baseline weight (per arm when given) in notes; the reconciler computes the percent and writes the arithmetic into the row notes | both pilot reads put 4.16 kg in a percent field, which would have corrupted the meta regression covariate |
| A3 risk of bias | The extractor JSON carries a rob object: d1_randomisation, d2_deviations, d3_missing, d4_measurement, d5_selection, overall (low, some_concerns, high) and a justification naming the evidence per domain; at reconciliation the row is appended to analysis/data/risk_of_bias.csv, which build_master requires for every trial | build_master refused the pilot master until the RoB-2 row existed |
| A4 reading | Read a text in at most two read_file calls (length 1000) rather than pages of 400 lines | the cost of an agent read grows with the number of calls, not with the text |
| A5 single extraction with independent verification | For budget reasons the default is one extractor (A) plus one verifier (V) who re reads the whole text and checks every number, sign, n, timepoint, comparator and eligibility call, writing V.csv (the corrected copy) and V.json (a verdict per row). Two independent extractions (A and B) are kept for the known relevant trials and for any study in which verification changes a pooled number; every A versus V disagreement is settled by the session's third read of the cited passage and recorded in reconciled.json. The Methods report this as single extraction with independent verification | 90 or more full texts at two full reads each exceed the session's remaining budget; the Director's decision D-X2 can restore dual extraction for all |
| A6 held populations | A trial whose defining population is outside the criterion but whose participants have overweight, obesity or type 2 diabetes as a stated condition (HIV associated lipohypertrophy, obstructive sleep apnoea, polycystic ovary syndrome, psoriasis) is extracted in full and closed as held_pending_decision with the population named, never excluded by the extractor | the Director decides the boundary once, on a list, rather than case by case inside the extraction |
