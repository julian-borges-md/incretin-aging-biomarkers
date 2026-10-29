# Science resolution memorandum, 28 October 2026

M5-AGE, incretin and glucagon receptor therapies and aging relevant biomarkers.
Companion to `docs/DIRECTOR_DECISIONS_2026-10-19.md`, which it answers in part and
replaces in no part. Repository head `c3fd45a`. Twenty six gates green, log
`work/gates_59452f5.log` and again after the D-X10 guard. 524 master rows, 76 trials,
392 pooled contrasts after the shared control collapse.

## Purpose

The instruction was to resolve the science before any submission engineering. This
memorandum states, against the register of 19 October, which questions the evidence
settles, which of them were defects rather than decisions, which remain yours and why,
and two findings that are new.

Nothing here is a decision I have taken. Where a register item has a determinate answer
in the data, it is reported as resolved with the measurement that resolved it. Where an
item requires an authority judgement, naming the paper, approving a deviation, writing to
another trial's authors, or enlarging the corpus, it is reported as reserved, and the
preparatory work that makes the decision cheap is named instead.

The separation is deliberate and it is the same one the laboratory applies elsewhere:
learning authority is wide, decision authority is not. A measurement that forces an answer
is not a decision. A choice between two defensible reportings is.

## Section 1. Disposition of the register

| ID | Question | Status now | Basis |
| --- | --- | --- | --- |
| A1 | Registered title against the method used | Reserved | The paper's name and the PROSPERO amendment are yours; the evidence that no network exists is unchanged and in the register |
| A2 | How H1 is reported | Resolved, answer unchanged, evidence strengthened | Sections 6 and 7 |
| A3 | Which composite interval is primary | Resolved in substance | Both intervals are computed and reported; which one carries the word primary remains a reporting choice |
| A4 | How question 4 is reported | Resolved for the coverage reporting, renaming deferred | Two classes computable with k on every bar and one contrast; renaming the metric touches registered terminology |
| A5 | The six protocol deviations in Methods 2.12 | Reserved | A sign off, not a finding |
| B1 | The thirteen A6 populations | Reframed, then reserved | Section 4. The thirteen were never extracted, so the item commissions work rather than ruling on rows |
| B2 | D-X1, a fifth receptor class | No action required | The register recommends holding the class and the corpus already holds it; approval is nominal |
| B3 | D-X7, DPP-4 comparators | Resolved, and the sensitivity the recommendation presumed now exists | Section 3.3 |
| B4 | Fan 2013 | Reframed, rows retained, exclusion reported as a sensitivity | Section 3.2 |
| B5 | Trial level backfill by registry number | Deferred, with finding F7 added to its scope | Sections 8 and 11 |
| B6, D-X3 | How two timepoints of one trial enter the pool | Resolved as a defect and fixed | Section 3.1 |
| B6, D-X8 | Tables reported only within weight strata | Deferred, needs an extraction before it can be ruled on | Section 11 |
| B6, D-X9 | Weight adjusted contrasts published by the trial | Deferred, needs the Bunck 2010 extraction | Section 11 |
| B6, D-X10 | IFCC conversion for HbA1c | Closed as a guard rather than a conversion | Section 5 |
| B7 | BNP as an inventory key | Deferred, needs one DUAL II extraction | Section 11 |
| C1 | D-X6, binary outcomes in Table 2 | Resolved and implemented in the generator | Section 6 |
| C2 | Dutour 2016 leptin standard error | Reserved | Author correspondence is yours to send; the row stays as extracted meanwhile, which is the register's own recommendation |
| C3 | Funnel panel | Deferred with a reason | Section 11 |
| D1 | Splitting `prespecified_endpoint` | Reserved, schema decision unchanged | The gate's triage document records both readings; no column was split |
| D2 | Registry identifiers for 32 trials | Closed 22 October | Recorded in the register |

Of the twenty items, seven are resolved on evidence, three were defects and are fixed, one
is closed by construction, five are deferred because each needs data the corpus does not
yet hold, and four remain reserved to you. None of the four reserved items is blocked on
analysis.

## Section 2. What changed in the repository

| Change | File | Consequence |
| --- | --- | --- |
| The shared control collapse declared once, with a deterministic tie break and an error on an undecidable group | `src/collapse_rule.R`, sourced by four callers | One pooled value changed; the rule is now order invariant and gate twenty six proves it |
| DPP-4 comparator trials declared as data rather than matched by pattern | `analysis/data/comparator_dpp4_trials.csv` | B3 testable; a pattern on comparator text misclassified a third trial |
| Four comparator sensitivities added | `analysis/M5_AGE_analysis_pipeline.R` | B3 and B4 both reportable as sensitivities rather than as exclusions |
| Binary hepatic outcomes reported as counts by the generator, not by hand | `src/make_tables.py` | C1 implemented where the table is built, so it survives the next rebuild |
| HbA1c scale guard with a counterexample self test | `src/harmonise_units.R` | D-X10 closed; an IFCC row can no longer enter the percent scale silently |
| Tables regenerated under the new rules | `manuscript/TABLES_2_to_7_2026-10-28.md` | Table 2 is 32 pooled rows, 29 favourable and three unfavourable; the plus or minus 807 interval is gone |

## Section 3. Three items were defects, not decisions

### 3.1 D-X3, the collapse was decided by file order

The register treats D-X3 as a choice about which timepoint of one trial enters the pool.
It was not a choice. The unit of analysis rule, one arm per trial per biomarker at the
highest dose, was written out separately in four scripts, each using
`dplyr::slice_max(order_by = dose_mg, n = 1, with_ties = FALSE)`. That argument does not
break a tie on the evidence. It breaks it by the order the rows happen to sit in the CSV.

Measurement before acting: 392 groups, 64 of them with more than one row, exactly one with
a tie at the highest dose, and duration separates that one. The tied group is the
retatrutide hepatic trial, whose eight liver fat arms carry no assessment timepoint and
differ only in `duration_weeks`, 24 against 48. The single triple agonist liver fat value
in the whole review was therefore selected by CSV position.

The rule is now one declaration, `src/collapse_rule.R`, sourced by the pipeline and by the
three other callers. It ranks by highest stated dose, then by whether the series reaches
the twelve week on treatment floor the extraction brief already required, then by the
longest duration, and it stops the run rather than picking a row when a group is still
undecided. Gate twenty six runs its fixtures, shuffles the harmonised corpus four ways and
asserts the same rows survive, then asserts that exactly one group moves against the
superseded file order pick and names it.

| Quantity | Under the file order pick | Under the declared rule |
| --- | --- | --- |
| Kept arm, retatrutide liver fat | 12 mg at 24 weeks | 12 mg at 48 weeks |
| Its percent change | minus 82.7 | minus 81.4 |
| Its weight change covariate | minus 17.6 | minus 25.9 |
| Groups affected | 1 of 392 | 1 of 392 |

### 3.2 B4, the recommended rationale does not survive inspection

The register recommends excluding the Fan 2013 rows and states the reason: "A corpus that
keeps both counts the same patients twice and narrows the interval as though the evidence
had doubled." The corpus does not keep both. `docs/DUPLICATE_TRIAGE.md` records that the
duplicated record is a 2018 report that "never entered the master" and "was excluded at
extraction, so its numbers are in the ledger's reason field and not in any row". Only one
of the two is in the analysis, and it is the earlier and original report.

So the question B4 actually asks is narrower: does a trial whose numbers were later
reproduced elsewhere under another drug's name stay in a review that never ingested the
later report. The duplication is evidence against the 2018 report, which is excluded, and
not against Fan 2013, which is the source the duplicate copied.

Measured effect of excluding it, within receptor class, which is the scale on which the
laboratory's sensitivity machinery reports:

| Cell | With Fan 2013 | Without | Reading |
| --- | --- | --- | --- |
| ALT, GLP-1 mono | k 8, minus 16.59, minus 37.66 to plus 4.47 | k 7, minus 15.71, minus 41.36 to plus 9.93 | Not significant either way; the interval widens |
| GGT, GLP-1 mono | k 5, minus 17.62, minus 34.82 to minus 0.41 | k 4, minus 12.82, minus 39.24 to plus 13.60 | Exclusion costs the only significant GGT estimate in the review |
| hsCRP, GLP-1 mono | k 32, minus 29.36, minus 35.34 to minus 23.38 | k 31, minus 30.44, minus 36.35 to minus 24.53 | Unchanged in substance |

Three of 46 class cells move. The rows are retained, the duplication is reported in the
integrity paragraph as what it is, a finding about the 2018 report, and the exclusion is
available as `analysis/output/sensitivity_without_fan2013.csv` so that a reviewer who
prefers the stricter corpus can read the consequence rather than ask for it. If you want
the exclusion as primary, it is one line and one pipeline run.

### 3.3 B3, the sensitivity the recommendation presumed did not exist

The register recommends admitting the DPP-4 comparator trials and reporting them "within
the existing comparator sensitivity analysis". There was no such analysis. The pipeline
carried nine sensitivities, by population, duration, risk of bias, funding and estimator,
and none of them by comparator type. The recommendation could not be executed as written.

Three things were therefore built. First, the declaration
`analysis/data/comparator_dpp4_trials.csv`, which names the trials and carries the evidence
string for each, because a pattern over comparator text misclassifies Light-On, whose
comparator is insulin glargine and whose text mentions sitagliptin only to record that the
arm was not entered. The register says three trials; the master holds two, LYDIA and
Suzuki 2014 Dokkyo. Second, `placebo_only` and `active_only`, which are the comparator
sensitivity the register assumed. Third, `without_dpp4`, which is the exclusion the
register declined, kept available for the same reason as B4's.

What the comparator sensitivity shows, on the thirteen cells where both strata pool:

| Reading | Value |
| --- | --- |
| Cells where placebo and active strata disagree in sign | 0 of 13 |
| Cells whose intervals do not overlap | 2 of 13, hsCRP and fasting glucose |
| hsCRP, GLP-1 mono | placebo k 12, minus 38.71; active k 16, minus 18.20 |
| Fasting glucose, GLP-1 mono | placebo k 3, minus 7.44; active k 20, minus 2.69 |

This is the attenuation the register predicted, and it is now measured rather than
asserted: an active comparator halves the apparent hsCRP effect and cuts the glucose effect
to about a third, while no marker changes direction. Excluding the two DPP-4 trials, by
contrast, moves ten of 46 class cells and all but three of those by less than half a
percentage point, so the specific worry that prompted D-X7 is the smallest part of the
comparator question. The honest statement for the manuscript is about comparator type in
general, not about DPP-4 inhibitors in particular.

## Section 4. B1 commissions thirteen extractions rather than admitting rows

The register presents B1 as an inclusion decision over thirteen populations held under
amendment A6, which instructed the extractor to extract in full and hold rather than
exclude. The ledger says the first half of that instruction was not carried out.

| Check | Result |
| --- | --- |
| Groups at `held_pending_decision` in `analysis/data/EXTRACTION_LEDGER.csv` | 16 |
| Of those, groups with a reconciled extraction file | 0 |
| Of those, groups that wrote a row | 0, every `rows_written` is 0 |
| Populations present in `analysis/data/extraction_master.csv` | T2D 327 rows, obesity 146, MASH 38, MASLD 8, obesity_ASCVD 5 |
| Polycystic ovary syndrome, sleep apnoea, HIV lipohypertrophy, schizophrenia, knee osteoarthritis rows | None |

The consequence for the decision is not cosmetic. Admitting the thirteen does not promote
rows that exist; it commissions thirteen extractions, each with full text retrieval,
reconciliation and a second extractor pass under the laboratory's own extraction standard.
The register's estimate that any Part B approval costs "one further pipeline run, about
twenty minutes" holds for B2 to B7 and does not hold for B1.

The dependency the register names is also sharper than it reads. The epigenetic age data
sits in group 386, the semaglutide trial in HIV associated lipohypertrophy, which is also
anchor reference 1 of the Introduction. That data is not in the pool and has never been
extracted, so the Introduction currently rests on a trial whose numbers the review does not
hold in any form. Either B1 is approved and the extraction is commissioned, or the
Introduction is reframed to say that its framing evidence lies outside the review's scope.
Both are defensible. Neither is available without a decision, and the second costs nothing
to execute.

I have not started any of the thirteen extractions. Commissioning work of that size on an
inference about your intent is the kind of thing the governance separation exists to
prevent.

## Section 5. D-X10 closed as a guard rather than as a conversion

The register recommends converting IFCC values for HbA1c, "since the pooling scale is
percent change and the conversion is deterministic". The measurement says there is nothing
to convert: all 44 HbA1c rows in the corpus are on the NGSP percent scale. Forty three
state a percent unit and the forty fourth, the EUREXA adipokine addendum, stated percentage
points in its own notes with baseline means of 7.5 and 7.6 percent, and its unit cell is
now filled to say so.

The hazard is real but it runs the other way, and it is silent. Percent change is invariant
under a proportional change of unit and not under an affine one. Every other unit pair in
this inventory is proportional, mg/L against mg/dL for hsCRP, mg/dL against mmol/L for
glucose, pmol/L against micro international units per mL for insulin, so the factor cancels
in `100 * yi / baseline_mean` and those rows need no unit string at all. The two HbA1c
scales are the exception in routine clinical use, IFCC equals NGSP minus 2.15 all times
10.929, an affine map with a non zero intercept. A fall from 7.5 to 7.0 is minus 6.67 per
cent on the NGSP scale and minus 9.35 per cent on the IFCC scale.

The conversion path keys on `measure` and `baseline_mean` and never reads the unit string,
so an IFCC row arriving later would be rescaled by its own IFCC baseline and enter the
percent scale about 1.4 times too large with no gate objecting. `src/harmonise_units.R`
therefore now refuses an HbA1c row whose unit is not an NGSP percent, and its self test
reports two of five fixture rows, the IFCC row and the row with an empty unit cell, before
it reports none on the corpus. A conversion has to be remembered. A guard does not.

The fix changed no computed value, which is itself the verification: 524 rows before and
after, every `yi` and `se` identical, one unit cell and one notes cell different, and no
file under `analysis/output/` touched.

## Section 6. What the numbers did

The collapse fix is the only change that moved a result, and it moved one row of Table 2
and the hepatic model that row feeds.

| Quantity | Before | After |
| --- | --- | --- |
| Liver fat PDFF, pooled, k 9 | minus 31.46, minus 48.99 to minus 13.94, tau2 466.38 | minus 30.55, minus 47.17 to minus 13.93, tau2 366.53 |
| Hepatic model tau2, null | 588.04 | 482.38 |
| Hepatic model tau2, weight only | 287.33 | 95.52 |
| R2, weight only | 51.14 per cent | 80.20 per cent |
| Weight slope, unadjusted | plus 3.21, SE 1.32, permutation p 0.070 | plus 2.43, SE 0.68, permutation p 0.063 |
| Weight slope, adjusted | minus 3.19, SE 6.39, permutation p 0.648 | minus 3.19, SE 6.39, permutation p 0.646 |
| R2, adjusted | 96.97 per cent | 96.30 per cent |
| Adjusted omnibus permutation p | 0.320 | 0.324 |
| ALT, every quantity | unchanged | unchanged |
| Composite, `table5_nbais` | unchanged | unchanged |

Table 2 as the manuscript carries it is now 32 pooled rows, 29 favourable and three
unfavourable, those being body fat percentage, resting heart rate and lean mass. The two
binary rows are out of it under C1 and reported as counts: MASH resolution in NCT04822181,
336 of 534 against 91 of 266, and fibrosis improvement in NCT03987451, 5 of 47 against 7 of
24, and in NCT04822181, 197 of 534 against 60 of 266. The prose figure for liver fat is
corrected in Results and in the draft Abstract, and gate nine, which recomputes every
pooled figure cited in prose against the table it comes from, passes.

A2's answer is unchanged. H1 is not supported on its prespecified criterion, the omnibus
permutation p having moved from 0.320 to 0.324 at k of 7. What changed is the quality of the
alternative reading: weight alone now accounts for 80.2 per cent of between study variance
rather than 51.1, on a slope of plus 2.43 with a standard error half the size of the
previous one. The unadjusted association the register recommends reporting alongside is
therefore a stronger finding than it was, while the hypothesis it does not answer is still
unanswered.

## Section 7. Finding F6, the adjusted hepatic model cannot see the arm whose value changed

The register argues the unidentifiability of the weight adjusted hepatic model from two
readings, an R2 of 99.99999982 per cent on the class only model and a sign reversal of the
weight coefficient on adjustment. The collapse fix supplied a third reading that is
stronger than either, because it is an experiment rather than an interpretation.

The adjusted model fits an intercept, three receptor class dummies and a weight slope on
seven arms. Their composition is this.

| Receptor class | Arms in the hepatic model |
| --- | --- |
| GLP-1 mono | 4 |
| GLP-1 and GIP and glucagon, triple agonist | 1 |
| GLP-1 and glucagon | 1 |
| GLP-1 and GIP | 1 |

Three of the seven arms are the only arm of their class, so each is fitted exactly by its
own dummy and contributes no residual information to the weight slope. The slope can only
be identified by variation within a class, and the only class with variation is GLP-1 mono.
The adjusted weight coefficient is therefore an estimate from four arms with three exactly
fitted points attached, not a class adjusted estimate from seven.

The collapse fix tested that claim without being designed to. It changed the triple
agonist arm's liver fat value from minus 82.7 to minus 81.4 and its weight covariate from
minus 17.6 to minus 25.9 per cent. The result:

| Quantity | Before | After |
| --- | --- | --- |
| Weight slope, adjusted | minus 3.1940507827347 | minus 3.1940507827346 |
| Its standard error, adjusted | 6.394428034745 | 6.394428034745 |
| tau2, adjusted | 17.8370550393 | 17.8370550393 |
| Weight slope, unadjusted | plus 3.2128 | plus 2.4259 |
| Omnibus Wald statistic | 49.62 | 26.83 |

The adjusted slope, its standard error and the residual heterogeneity are identical to
twelve significant figures, the difference being optimiser noise in the last bits. The
unadjusted slope, which uses all seven arms, moved by 0.79. The entire change was absorbed
by that class's own dummy, which is why the omnibus statistic nearly halved while its
permutation p moved by 0.004.

A model whose adjusted coefficient is numerically unaffected by an eight point change in
the covariate of one of its seven observations is not adjusting for that observation. This
belongs in Discussion 4.4 as the demonstration of the collinearity, in place of or beside
the R2, because it cannot be read as an artefact of a variance ratio. It also means B5 is
not a refinement but the precondition for the hepatic model: until the triple agonist class
has more than one arm, no amount of better inference will identify the slope.

## Section 8. Finding F7, the review holds no participant characteristics

This is new, unrecorded anywhere in the repository, and it blocks submission on reporting
grounds rather than analytical ones.

`analysis/data/extraction_schema.csv` is the declaration of record for the extraction. It
declares 59 columns. The master also carries 59, and they are not the same 59.

| Direction | Count | Content |
| --- | --- | --- |
| Declared in the schema, absent from the master | 21, of which 13 are marked required | Participant and study descriptors, and the five risk of bias domains |
| Present in the master, not declared in the schema | 21 | Five are computed downstream, `yi`, `se`, `vi`, `se_route`, `source_file`; the other sixteen are extraction fields, including `measure` and `unit` |

The five risk of bias domains are satisfied elsewhere: `analysis/data/risk_of_bias.csv`
carries `d1_randomisation` through `d5_selection`, an overall rating and a justification for
77 trials. That leaves eight fields marked required in the schema that no extraction file
carries at all, checked across all 75 files.

| Field | Status |
| --- | --- |
| `age_mean` | Absent from every extraction file |
| `pct_female` | Absent from every extraction file |
| `bmi_mean` | Absent from every extraction file |
| `weight_mean` | Absent from every extraction file |
| `n_randomized` | Absent from every extraction file |
| `country_region` | Absent from every extraction file |
| `sponsor` | Absent from every extraction file |
| `dose_frequency` | Absent from every extraction file |

Also absent, and not marked required: `age_sd`, `race_white_pct`, `bmi_sd`, `weight_sd`,
`hba1c_mean`, `hba1c_sd`, `assessment_method`, `coi_declared`. No file under `manuscript/`,
`docs/` or `prespecification/` mentions a study or participant characteristics table, and
the review's Table 1 is the biomarker inventory.

What the corpus does hold at trial level is design, drug, dose, comparator, comparator
type, duration, population label, arm sizes, industry funding, risk of bias and percent
weight change. What it does not hold is who the participants were.

| Consequence | Severity |
| --- | --- |
| No participant characteristics table, which PRISMA 2020 item 17 requires and which every journal in this space expects as Table 1 | Submission blocking at most venues |
| Applicability cannot be stated: the review cannot say the pooled estimates come from populations with a mean age of x and y per cent women | Reviewer certain to raise |
| Age and sex cannot be examined as effect modifiers, even descriptively, in a review whose subject is aging biology | Scientific, and awkward given the title |
| The schema's own required fields are unmet, so the extraction cannot be said to conform to its declaration | Governance |

The remediation is a trial level characteristics backfill, 76 trials by eight fields, most
of which are in the first table of each already retrieved full text or in the registry
records that D2 resolved. It is the same retrieval pass as B5 and should be scoped with it
rather than separately. It does not change a single pooled estimate, which is why it can
proceed in parallel with any decision in Part A or B.

I have not started it. Eight fields across 76 trials is a corpus wide extraction pass, and
the governance rule that held for B1 holds here.

## Section 9. Corrections to the record

| Where | What it says | What is the case |
| --- | --- | --- |
| Register A2 evidence table | Liver fat tau2 under the class only model is 1.04 | The output value is 1.0395e-6. The R2 of 99.99999982 per cent beside it is consistent only with the smaller number. The saturation reading is unaffected and is strengthened |
| Register B4 rationale | "A corpus that keeps both counts the same patients twice" | The corpus never held both; the 2018 report was excluded at extraction. Section 3.2 |
| Register B3 recommendation | Report within "the existing comparator sensitivity analysis" | No comparator sensitivity existed. Section 3.3 |
| Register B3 scope | Three trials whose only comparator is a DPP-4 inhibitor | The master holds two, LYDIA and Suzuki 2014 Dokkyo |
| Register Part B preamble | Any Part B approval costs one pipeline run of about twenty minutes | True for B2 to B7. B1 commissions thirteen extractions. Section 4 |
| Commit `59452f5` subject line | "the four binary hepatic histology outcomes" | Three binary rows reporting two outcomes across two trials. The generated table and the Results prose are correct; the commit subject is not. Corrected here rather than by rewriting a pushed commit |

## Section 10. Risks of the state as it stands

| Risk | Mechanism | Standing |
| --- | --- | --- |
| The adjusted R2 reaching print | A reviewer who sees 96.3 per cent beside k of 7 discounts everything near it. Gate nine checks that a cited figure matches its table, not that a meaningless figure is omitted | Open. The register says do not print it; nothing enforces that |
| The manuscript's numbers written twice | If B1 is approved after the numbers are final, every pooled estimate that gains an arm changes | Open, and it is the reason the register grouped Part B |
| Desk rejection on characteristics | F7. Most venues in this space return a review with no participant table before review | Open, remediation scoped in section 11 |
| GGT resting on one trial | The only significant GGT estimate loses significance when Fan 2013 is excluded, k 5 to 4 | Mitigated by reporting the sensitivity; the limitations paragraph should name it |
| The triple agonist class as a single arm | F6. No inference method identifies the hepatic slope while the class has one arm | Open, and it is what B5 is for |
| Reversibility of the two retentions | Fan 2013 and the DPP-4 trials are retained as primary with the exclusions available as sensitivities | Each flips in one line and one pipeline run, so neither forecloses the register's recommendation |

## Section 11. Next actions

### Reserved to you

| ID | What is needed | Cost of answering |
| --- | --- | --- |
| A1 | Retitle or do not, and amend PROSPERO accordingly | One line from you; the deviation text is drafted and the comparator counts that justify it are in the register |
| A5 | Approve the six deviations, and the seventh if A1 is approved | One line |
| B1 | Admit, admit in part, or exclude the thirteen populations | One line, then thirteen extractions if admitted. The Introduction's framing follows either way |
| C2 | Send the Dutour 2016 request for change standard deviations | One email; the draft is in `docs/CRD_email_draft.md` style and can be prepared on request |
| D1 | Split `prespecified_endpoint` into registration and report, or leave it | One line; the triage document holds both readings |
| New | Whether the Fan 2013 and DPP-4 retentions stand as primary, with the exclusions as sensitivities, or the register's exclusions become primary | One line each |
| New | Whether F7 is remediated before submission or the review states the absence as a limitation | One line. The first is the defensible answer at most venues |

### Executable without a decision

| Action | Why it is unblocked |
| --- | --- |
| Add an identifiability diagnostic to the hepatic table, arms per class and a flag for singleton classes, so F6 is a gate checked quantity rather than a sentence | A measured property of the fitted model |
| Write the F6 demonstration into Discussion 4.4 beside the existing collinearity paragraph | Strengthens the reporting A2 already settles; changes no answer |
| Refresh `manuscript/DRAFT_STATUS.md`, which is dated 19 October, still says twenty one gates and still references the retired `TABLES_2_to_7_2026-10-16.md` | Stale record of a current state |
| Prepare the F7 retrieval plan, naming for each of the 76 trials where the eight fields will come from, without extracting | Planning, not corpus change |
| Draw the funnel panel for the four biomarkers at k of ten or more, under figure style 2 and its content gate | C3, deferred only on sequencing; it changes no estimate |

### Blocked on data the corpus does not hold

| ID | What it needs |
| --- | --- |
| B6, D-X8 | One extraction of the stratified tables, to see whether the strata recombine with the printed n |
| B6, D-X9 | The Bunck 2010 weight adjusted contrasts, as a column and never as rows |
| B7 | One DUAL II extraction for the BNP contrast, under a new inventory key that never pools with NT-proBNP |
| B5 | Targeted retrieval for the triple agonist arm, which F6 shows is the precondition for the hepatic model rather than a refinement |
| B1 | Thirteen extractions, if admitted |

## Verification

| Check | Result |
| --- | --- |
| Gate chain | Twenty six gates, 33 steps, all exit 0, `work/gates_59452f5.log`, rerun green after the D-X10 guard |
| Collapse rule gate | 486 rows in, 392 kept, four permutations identical, exactly one group moved against the superseded pick and it is the one the measurement predicted |
| HbA1c guard | Reports two of five fixture rows before reporting none on the corpus; 44 HbA1c rows, every one NGSP |
| Prose figures | Gate nine recomputes 22 pooled figures cited in Results against `table2_pooled_by_biomarker.csv`, zero mismatches |
| D-X10 fix is inert | 524 rows before and after, every `yi` and `se` identical, nothing under `analysis/output/` changed |
| Commits | `59452f5` the science package, `c3fd45a` the D-X10 guard, both pushed to `main` |
| Why this memorandum is not in gate nine's file list | It quotes superseded values by design, in sections 6 and 7, which the checker must treat as mismatches. Every current value it quotes also appears in Results or in a table, where gate nine does check it |
