# Director decision memorandum, 19 October 2026

M5-AGE, incretin and glucagon receptor therapies and aging relevant biomarkers.
Repository head at issue: `3f73143`. Twenty two gates green, 524 rows, 76 trials, 49 outputs, all
manifest digests verified.

## Purpose

Every remaining piece of the manuscript is blocked on one of the fifteen decisions below. They were
recorded in three places, the Results decision table, the 16 October readiness audit and the draft
status file, and answering them piecemeal has meant answering them in three contexts. This document
states each one once, with the evidence, the options, the consequence of each option and a
recommendation, so that the register can be cleared in a single sitting.

How to answer: reply with the decision identifier and your answer. "A2 as recommended" is enough
where you agree. Where you do not, a one line direction is enough; I will implement and report.

Nothing here is a decision I have taken. Where the analysis settles a question, that is reported as
closed in the last section rather than presented as a choice.

## Decision summary

| ID | Decision | Blocks | Recommendation |
| --- | --- | --- | --- |
| A1 | Registered title against the method actually used | Title page, Methods framing, venue choice | Retitle to match the method and disclose the change |
| A2 | How H1, hepatic independence from weight loss, is reported | Discussion 4.4, 4.1, Abstract results | Report as not supported on its prespecified criterion |
| A3 | Which composite interval is primary | Results 3.7, 4.2, Abstract | Percentile of the two level bootstrap; BCa as the registered sensitivity |
| A4 | How question 4 is reported under the inclusion rule | 4.2, Abstract conclusions, Figure 5 caption | Report two classes only, with k on every bar, and rename the metric |
| A5 | Approval of the six protocol deviations in Methods 2.12 | Methods sign off, submission | Approve all six as recorded |
| B1 | A6 held populations, thirteen groups | Introduction framing, PRISMA counts, every pooled estimate | Admit the four conditions that meet the stated criterion, with a subgroup sensitivity |
| B2 | D-X1, a fifth receptor class for the amylin co agonists | Two CagriSema groups and one adjacent hold | Hold the class; admit the trials descriptively only |
| B3 | D-X7, trials whose only comparator is a DPP-4 inhibitor | Three trials and one second contrast | Admit, with comparator type recorded, and report in the comparator sensitivity |
| B4 | Fan 2013 status | Whether a duplicated trial stays in the analysis | Exclude the Fan 2013 rows and report the exclusion with its arithmetic |
| B5 | Trial level backfill by registry number | PRISMA identification count, the single marker triple agonist class | Approve for the triple agonist arm only |
| B6 | D-X3 timepoints, D-X8 stratified tables, D-X9 weight adjusted contrasts, D-X10 IFCC conversion | Between fifteen and forty rows, and the Bunck 2010 contrasts bearing on question 3 | Four separate answers requested; my reading is in C of this memo |
| B7 | BNP as an inventory key alongside NT-proBNP | The DUAL II contrast and any other BNP row | Add the key, with BNP and NT-proBNP never pooled together |
| C1 | D-X6, whether the binary outcomes appear in Table 2 | Table 2 presentation and one Results sentence | Remove both from Table 2; report them in the hepatic section as counts |
| C2 | Dutour 2016 leptin standard error | The stability of the leptin pooled estimate | Request the change SDs from the authors; do not raise the imputed correlation |
| C3 | Funnel panel for the four biomarkers at k of ten or more | One supplementary figure | Include as supplementary, since the diagnostics already exist |

## Part A. Reporting decisions

### A1. The registered title says network meta-analysis and nothing in the analysis is one

**Evidence.** The network block is gated off in the pipeline and writes its reason to
`table7_network_not_run.csv`. The corpus carries 36 distinct comparators and 240 of the 389 pooled
rows are active controlled. A network requires that those comparators collapse into a small number of
nodes; collapsing them into one placebo node would assert an exchangeability the data contradict, and
the alternative, a node per comparator, leaves a disconnected graph. This is not a matter of effort:
there is no network in this evidence base.

**Options.**

| Option | Consequence |
| --- | --- |
| Retitle to match the method, for example a systematic review and pairwise random effects meta-analysis with meta-regression | A registration deviation to disclose, which is routine and already one of six. The title then describes the paper |
| Keep the registered title and run a network | Not available. The analysis would have to assume what the comparator distribution refutes |
| Keep the registered title and explain in the Methods that no network was run | A reader who selected the paper from its title finds a different paper. Editors treat this as a registration integrity problem rather than a wording preference |

**Recommendation.** Retitle, and record it as a seventh deviation with the comparator counts as its
justification. The PROSPERO record should carry the same amendment.

### A2. How hypothesis H1 is reported

H1 asked whether the hepatic effect is independent of weight loss. The prespecified criterion was the
adjusted omnibus test in the weight adjusted meta-regression.

**Evidence, from `table4a_hepatic_metaregression.csv` and `table4_metaregression.csv`.**

| Quantity | Liver fat PDFF | ALT |
| --- | --- | --- |
| Contributing arms after dose collapse, k | 7 | 7 |
| Arms dropped for lacking the weight covariate | 2 | 3 |
| Adjusted omnibus permutation p | 0.320 | 0.056 |
| tau2, null model | 588.04 | 413.19 |
| tau2, receptor class only | 1.04 | 405.32 |
| R2, receptor class only | 99.99999982 per cent | 1.91 per cent |
| tau2, adjusted | 17.84 | 25.61 |
| R2, adjusted | 96.97 per cent | 93.80 per cent |
| Weight coefficient in the WEIGHT ONLY model | plus 3.21, SE 1.32, permutation p 0.070 | plus 9.16, SE 4.63, permutation p 0.122 |
| Weight coefficient in the ADJUSTED model | minus 3.19, SE 6.39, permutation p 0.648 | plus 16.09, SE 3.79, permutation p 0.031 |
| Interaction terms | Dropped as redundant | Dropped as redundant |

**Amended 2026-10-22, and the amendment changes one number in this register.** The weight only
coefficient was not in the output when this register was written. Table 4 carried three columns named
`beta_weight`, `se_weight` and `p_weight_perm`, which hold the ADJUSTED model's coefficient and sit
beside `R2_weight_only`, so the two could be read as belonging to the same model. The queued change
renamed them and added the weight only model's coefficient with its own permutation test. The first
version of this section reported the unadjusted slope as "plus 3.21, 95 per cent CI 0.63 to 5.80,
permutation p 0.015". The slope and the interval are right and the p value was not a permutation p at
all: no permutation test had been run on the weight only model, and 0.015 is its Wald p. The
permutation p the protocol requires is **0.070**, and the interval quoted is the Wald interval, which
is the only interval this model reports. The same correction applies to ALT, whose weight only
coefficient is plus 9.16 at permutation p 0.122 against the Wald p of 0.048.

This weakens the premise of the sign reversal rather than the reversal itself. Under the protocol's
own inference the unadjusted weight slope for liver fat does not reach significance either, so the
reading below should not be stated as a significant positive slope becoming a null one; it is a
positive slope of borderline significance becoming a negative one of none, in a model whose
parameters outnumber its usable points.

Three readings of that table matter and none of them is the R2.

First, the omnibus test does not reach its criterion for liver fat, p 0.320 at k of 7.

Second, the liver fat class only model drives the between study variance from 588.04 to 1.04, an R2
of 99.99999982 per cent. That is saturation, not explanation: four parameters on seven points. The
96.97 per cent adjusted R2 inherits the same defect and should not appear in the manuscript as a
quantity. A reviewer who sees an R2 of 97 per cent beside k of 7 will reach the same conclusion
faster than a reader of the text.

Third, and this is the part worth your attention, the weight coefficient reverses sign on adjustment.
Weight alone gives a slope of plus 3.21 per cent liver fat per per cent body weight, Wald 95 per cent
CI 0.63 to 5.80, permutation p 0.070, which is Figure 4. Adjusted for receptor class the same
covariate gives minus 3.19 with permutation p 0.648. A sign reversal on adjustment with four
parameters on seven points is a collinearity signature: in this corpus the triple agonist arms are
also the largest weight losses,
so class and weight are nearly the same variable and the model cannot separate them. That is the
honest answer to H1, and it is more informative than either a null or a positive result.

Where weight is a significant moderator, it is so without this problem: hsCRP, R2 69.8 per cent,
p 2e-4; HOMA-IR, R2 70.0 per cent, p 0.029 on the REML stepadj fallback; ALT, R2 93.8 per cent,
p 0.031. Nineteen of 32 biomarkers fitted, thirteen insufficient.

**Options.**

| Option | Consequence |
| --- | --- |
| Report H1 as not supported on its prespecified criterion, with the saturation and the sign reversal stated | Defensible, and consistent with the standing instruction that Q3 is reported as association. Costs the paper its strongest headline |
| Report the adjusted R2 as evidence of class explanation | Not defensible. The quantity is an artefact of four parameters on seven points |
| Report weight alone as the finding, from Figure 4 | True and publishable, but it answers a different question: it says weight loss tracks liver fat reduction, not that the hepatic effect is independent of it |
| Withhold H1 pending the trial level backfill, B5 | Defers rather than answers; backfill would add arms to the triple agonist class and might make the model identifiable |

**Recommendation.** The first option, with the third reported alongside as the unadjusted
association. If you approve B5, the hepatic model is worth refitting afterwards, because the single
marker triple agonist class is the direct cause of the identifiability problem.

### A3. Which composite interval is primary

The registered plan names a bias corrected and accelerated interval. BCa is defined for a statistic
that is a deterministic function of its resample, and the composite statistic draws from each pooled
estimate's sampling distribution inside the resample, which is the two level design the plan's own
text justifies. The two requirements are not jointly satisfiable, which is why the first
implementation printed, for the glucagon receptor class under equal weighting, an estimate of 15.97
with an interval of 19.51 to 39.73. Both are now computed and reported.

| Class, weighting | Estimate | Percentile interval | Bootstrap bias | Registered BCa |
| --- | --- | --- | --- | --- |
| GLP-1 mono, inverse variance | 5.39 | 2.90 to 20.39 | plus 2.50 | 0.43 to 19.31 |
| GLP-1 mono, equal | 13.00 | 5.47 to 20.44 | minus 0.05 | 5.83 to 19.20 |
| GLP-1 mono, clinical | 11.58 | 4.01 to 20.15 | plus 0.17 | 4.10 to 18.94 |
| GLP-1 and GIP, inverse variance | 35.34 | 9.31 to 55.10 | minus 0.05 | 8.13 to 50.54 |
| GLP-1 and GIP, equal | 35.58 | 8.73 to 55.19 | plus 0.01 | 8.13 to 50.93 |
| GLP-1 and GIP, clinical | 36.84 | 9.46 to 54.76 | minus 0.55 | 8.13 to 50.00 |

The first row is the one to read. Under inverse variance weighting the GLP-1 mono composite carries a
bootstrap bias of plus 2.50 on an estimate of 5.39, and its lower bound sits at 2.90 against a BCa
lower bound of 0.43. The estimate depends materially on which of the nine admitted markers happen to
be in the resample. The equal weighted row, bias minus 0.05, does not have that property, which is
consistent with the deviation already recorded in Methods 2.12 making equal weighting primary.

**Recommendation.** Percentile interval of the two level bootstrap as primary, because it refers to
the same quantity as the point estimate; BCa reported alongside as the registered method with its
limitation named. Report the equal weighted composite as primary per the existing deviation, and
report the inverse variance instability as a finding rather than a footnote.

### A4. How question 4 is reported under the composite inclusion rule

`prespecification/nbais_inclusion_rule.md` admits eleven markers and excludes ten. Applying it to the
per class composite, which the pipeline had not been doing, gives this coverage.

| Receptor class | Admitted markers that pool | Composite, equal weighting |
| --- | --- | --- |
| GLP-1 mono | 9 of 11 | 13.00 |
| GLP-1 and GIP | 3 of 11 | 35.58 |
| GLP-1 and glucagon | 1 of 11 | Not computed, below the three marker floor |
| Triple agonist | 0 of 11 | No marker pools in the class at all |

One of six pairwise class contrasts is computable: GLP-1 mono against GLP-1 and GIP over three shared
markers, difference minus 15.72, 95 per cent CI minus 22.35 to minus 9.32.

The prespecification's closing paragraph makes a recommendation of its own that has not been acted
on: "The name Net Biological Age Impact Score overstates that. The score should be renamed to
describe what it measures, and biological age language reserved for epigenetic clock evidence."

**Options.**

| Option | Consequence |
| --- | --- |
| Report the two computable classes with k on every bar, state the other two as not supported, and report the single contrast as a three marker comparison | What the evidence licenses. Question 4 becomes a coverage finding with one quantitative comparison |
| Report all four classes over every marker that pools | The quantity the inclusion rule exists to prevent, and the rule says why: most excluded markers are the ones the drug moves strongly |
| Drop question 4 from the paper | Loses the methodological contribution, which is the composite framework itself rather than its current values |

**Recommendation.** The first, and adopt the prespecification's renaming. A defensible name is
Aging Relevant Biomarker Composite, with the biological age language reserved for the epigenetic
clock evidence, which exists for one drug in one trial and is itself subject to B1.

### A5. The six protocol deviations recorded in Methods 2.12

| Deviation | Status |
| --- | --- |
| Pooling scale, percent change rather than Hedges' g | Implemented and reproduced to within 0.001 on all 28 shared biomarkers |
| Unit of analysis, one arm per trial per biomarker at the highest dose | Implemented; 389 rows kept of 483, 94 dose arms dropped |
| Eligibility, exenatide and dulaglutide admitted as interventions | Implemented, with a sensitivity analysis under the original criterion |
| Composite weighting, equal primary and inverse variance as sensitivity | Implemented; A3 above supports it with the bias figures |
| Biomarker inventory, amendment R2 | Implemented; Table 1 carries 36 entries over 14 domains |
| Prediction intervals suppressed below three trials | Implemented |

Each is documented with its reason and the date it was recorded, and each is already in the pipeline.
A1, if approved, becomes a seventh.

**Recommendation.** Approve all six, and the seventh if A1 is approved.

## Part B. Corpus scope decisions

Each of these changes the numbers. They are grouped because they share one operational consequence:
any approval here requires one further pipeline run, which costs about twenty minutes, and the
manuscript's numbers should be written once, after the last of them lands.

### B1. The thirteen populations held under amendment A6

Sixteen groups stand at `held_pending_decision`. Thirteen are populations held under A6, which
instructed the extractor to extract in full and hold rather than exclude: polycystic ovary syndrome
in five trials, obstructive sleep apnoea in two, HIV associated lipohypertrophy in two,
schizophrenia, knee osteoarthritis and two combination designs. The other three wait on B2 and on a
stratified table question.

The question is whether the review's eligibility criterion is the condition or the indication. As
written, participants must have overweight, obesity or type 2 diabetes as a stated condition. All
thirteen satisfy that. What differs is the population's defining label.

**What admission changes.** The PRISMA identification and inclusion counts, Table 1 coverage, and
every pooled estimate that gains an arm. It also admits the only epigenetic age data in the pool,
group 386, which is the semaglutide trial in HIV associated lipohypertrophy.

**A dependency worth naming.** Anchor reference 1, the paper the Introduction rests on for the claim
that an incretin therapy modulates validated epigenetic clocks, is that same trial. Under the
criteria as they stand, the trial that makes this review's central question answerable sits in a
population the review has not decided to include. That is not an argument for admitting it, but the
Introduction cannot be written until the question is settled either way, because if the population is
excluded the Introduction must say that its framing evidence lies outside the review's own scope.

**Options.**

| Option | Consequence |
| --- | --- |
| Admit all thirteen, with population as a prespecified subgroup sensitivity | Consistent with the stated criterion. Adds heterogeneity that the subgroup analysis exposes rather than hides |
| Admit the four conditions whose participants meet the condition criterion unambiguously and exclude the rest | Requires a stated boundary; the honest one is whether the condition is a metabolic one |
| Exclude all thirteen | Defensible as written, and costs the review its epigenetic evidence. The Introduction must then be reframed |

**Recommendation.** Admit, with population as a declared subgroup. The criterion is the condition and
all thirteen meet it; excluding them is a narrowing the protocol does not state. Report the pooled
table with and without them, which the eligibility sensitivity machinery already supports.

### B2. D-X1, a fifth receptor class for the amylin co agonists

Two CagriSema groups and one adjacent hold wait on whether cagrilintide and CagriSema constitute a
fifth class, GLP1_AMY. Amylin is not an incretin receptor; the class vocabulary is built on incretin
and glucagon receptor pharmacology.

**Recommendation.** Hold the class. Admit the trials descriptively in the Discussion as an adjacent
pharmacology, and state in the Methods that amylin co agonism was outside the receptor vocabulary
registered. Adding a fifth node to a signature that already fails to support four is not a gain.

### B3. D-X7, three trials whose only comparator is a DPP-4 inhibitor

A DPP-4 inhibitor raises endogenous GLP-1, so the contrast is not drug against no incretin signal but
drug against a weaker one, which attenuates toward the null.

**Recommendation.** Admit, with comparator type recorded as active, and report them within the
existing comparator sensitivity analysis rather than as a separate exclusion. Attenuation that is
recorded and testable is better evidence than exclusion that is not.

### B4. Fan 2013

The post treatment ALT means of 39.82 and 51.48 U/L in a 2018 report are, to two decimals, the values
Fan 2013 reports for a different drug in the same population. `docs/DUPLICATE_TRIAGE.md` records the
reading. The duplicate numbers gate now carries a self test built from this exact case.

**Recommendation.** Exclude the Fan 2013 rows and report the exclusion in the integrity paragraph
with the two values printed, as the other two integrity exclusions already are. A corpus that keeps
both counts the same patients twice and narrows the interval as though the evidence had doubled.

### B5. Trial level backfill by registry number

Several included records are conference abstracts or substudies whose main publication was never
retrieved. Backfilling by registry number would change the PRISMA identification count and is the
direct mechanism behind the single marker triple agonist class, which is what makes the hepatic model
in A2 unidentifiable.

**Recommendation.** Approve for the triple agonist arm only, as a targeted retrieval with its own
PRISMA note, rather than a corpus wide backfill. A corpus wide pass reopens screening; a targeted one
addresses the specific defect that A2 turns on, and its effect on the hepatic model is testable
immediately.

### B6. D-X3, D-X8, D-X9 and D-X10

Four separate questions, between fifteen and forty rows in total.

| ID | Question | My reading |
| --- | --- | --- |
| D-X3 | How two timepoints of one trial enter the pool | Keep the longest on treatment timepoint of twelve weeks or more, as the brief already instructs, and report the earlier timepoint in a sensitivity analysis rather than as a second row |
| D-X8 | Whether tables reported only within weight strata are usable | Admit where the strata can be recombined with the printed n per stratum; otherwise hold, since a stratum specific contrast is not the trial's contrast |
| D-X9 | Whether weight adjusted contrasts published by the trial enter | Admit as a separate column rather than as rows, because they answer question 3 directly and must not be pooled with unadjusted contrasts. The Bunck 2010 contrasts are the case that matters |
| D-X10 | IFCC conversion for HbA1c | Convert, since the pooling scale is percent change and the conversion is deterministic |

**Recommendation.** Four answers requested. D-X9 is the one that bears on a research question.

### B7. BNP as an inventory key

The DUAL II abstract reports brain natriuretic peptide falling with an estimated treatment ratio of
0.66, 0.55 to 0.79. The NT-proBNP key cannot take it. BNP and NT-proBNP are different analytes with
different reference ranges and are not interchangeable.

**Recommendation.** Add BNP as its own inventory key with the same hallmark domain and direction, and
never pool the two together. The composite admits NT-proBNP specifically because the drug does not
move it, so a BNP row must not enter that slot.

## Part C. Presentation and data quality

### C1. D-X6, the binary outcomes in Table 2

| Outcome | k | Pooled estimate | Interval | tau2 | I2 | p |
| --- | --- | --- | --- | --- | --- | --- |
| MASH resolution | 1 | 83.92 | 51.02 to 116.83 | not estimable | not estimable | not estimable |
| Fibrosis improvement | 2 | minus 0.22 | minus 807.55 to plus 807.11 | 7672.70 | 95.0 per cent | 0.998 |

The fibrosis row is not a result. An interval of plus or minus 807 per cent on an estimate of minus
0.22 with two trials carries no information and invites a reviewer to question everything near it.
The MASH row is a single trial reported as a pooled estimate.

**Recommendation.** Remove both from Table 2. Report them in the hepatic results paragraph as what
they are: one trial reporting MASH resolution and two reporting fibrosis improvement, with their own
numbers and no pooling. Table 2 is the pooled table and should contain only pooled quantities.

### C2. Dutour 2016 leptin standard error

The row's printed interaction p implies a standard error about one third of the one the row carries,
and leptin is the marker whose pooled estimate is least stable. Raising the imputed pre post
correlation would narrow the interval by assumption rather than by evidence.

**Recommendation.** Write to the authors for the change standard deviations. Until they arrive, keep
the row as extracted and name leptin's instability in the limitations, which Discussion 4.10 already
does. Do not raise the correlation.

### C3. Funnel panel

`table_diagnostics.csv` carries the Egger test and trim and fill for every biomarker. Four reach k of
ten or more, which is the threshold at which a funnel plot is informative.

**Recommendation.** Include as a supplementary figure. The diagnostics exist; drawing them costs one
pipeline section and removes a predictable reviewer request.

## Closed since the previous register, no decision required

| Item | Resolution |
| --- | --- |
| SURPASS-3 MRI appendix | Checked. Adiponectin and leptin appear only in the statistical plan's biomarker list and the schedule of assessments, so they are unreported rather than missing. Table S6 supplied the body weight row, which brought six rows into the weight adjusted regression. The Results decision table listed this as open and has been corrected |
| The composite interval defect | Fixed. Both intervals computed, a gate added, the figure redrawn |
| The figure set | Produced, versioned, hashed and mapped |
| Both reference lists | Verified against Europe PMC and Crossref, with the corrections recorded |

## What happens after the answers

One pipeline run, carrying every pending change at once rather than one run per decision.

**Done 2026-10-22, before the answers, because none of these four moves a pooled number.** The run
they required has been made, so the run that carries your answers will carry only decision driven
changes. Table 2, Table 3, Table 5, Table 5a, Table 6 and every sensitivity table are byte identical
to the previous commit's; only Table 4, Table 4a, the manifest, the figure files and the session
record changed, which is what these four changes should have changed and nothing else.

| Change | Reason | Outcome |
| --- | --- | --- |
| Rename `beta_weight`, `se_weight` and `p_weight_perm` in Table 4a to name the adjusted model | They are extracted from the adjusted model and sit beside `R2_weight_only`, which invites a reader to take them as the unadjusted coefficient. This is the discrepancy behind the sign reversal in A2, and it is a naming defect rather than a numerical one | Done, and it was not only a naming defect. The columns are now `beta_weight_adjusted`, `se_weight_adjusted` and `p_weight_perm_adjusted`, and the weight only model's coefficient is reported beside `R2_weight_only` with a permutation test of its own. That test had never been run, and it changes the unadjusted liver fat p from the Wald 0.015 to 0.070. The amendment under A2 records it |
| Move the composite inclusion rule into one data file both scripts read | It is currently read out of `src/compute_composite.R` by the pipeline, which is one declaration read in two places rather than two declarations, but a shared file is the correct end state | Done. `analysis/data/nbais_inclusion_set.csv` holds the eleven markers with each one's hallmark domain, surrogacy grade and the reason it is retained; both scripts read it and neither restates it. Table 5 and Table 5b are byte identical across the change |
| Hoist the inventory join out of `compute_nbais` | About 180,000 joins per run; the bootstrap phase costs eight of the twenty minutes | Done. The join is now one call per frame in `attach_nbais_weights`, which also asserts that it is a lookup by failing when it changes a frame's row count, and `compute_nbais` stops rather than joining when the columns are absent. Table 5 and Table 5a are byte identical |
| Set the inventory display name for BMD to Bone mineral density | `table1_name` is the abbreviation, so Table 1 and every manuscript table that uses the inventory's own names print BMD. Changing it regenerates Table 1, which the manifest gate ties to a pipeline run | Done. Both spellings resolve to the same marker in the Results number gate, which reads the key and the display name, so neither the Discussion's existing BMD row nor a future spelled out row goes unchecked |

Still queued, and dependent on your answers:

| Change | Reason |
| --- | --- |
| Funnel panel, if C3 is approved | |

Then the writing sequence, in order: Abstract results and conclusions, Discussion 4.1 and 4.2,
Discussion 4.3 and 4.4 under the A2 answer, Section 5, title page under the A1 answer. Discussion 4.5
to 4.9 do not depend on any answer here and can be drafted in parallel.

## Risk of leaving the register open

| Risk | Consequence |
| --- | --- |
| The manuscript is written against assumed answers | Every number dependent sentence is rewritten when an answer differs from the assumption, and the rewrite is where stale numbers enter |
| A1 is deferred to submission | Venue selection cannot proceed, since the title determines which journals will consider the paper at all |
| B1 is deferred | The Introduction cannot be written either way, and it is the one major section that is otherwise unblocked |
| A2 is deferred | Discussion 4.4 and the Abstract carry the paper's central claim and cannot be drafted around it |
