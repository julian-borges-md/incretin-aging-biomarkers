# Packet grouping triage, 16 October 2026

## Why this document exists

`src/extraction_packets.py` groups the included records into one packet per study, by title and
registry identifier, so that a trial represented by a conference abstract, a register entry and a
full text is extracted once. When that grouping is wrong and two unrelated studies land in one
packet, the extractor reads one of them, the ledger closes the group on that reading, and the other
study leaves the review without ever being assessed. The loss is silent: the ledger shows a closed
group, the PRISMA count shows an included study, and nothing anywhere says that a second study was
inside it.

That happened. `src/extraction_attachment_check.py`, written to ask whether each extracted number
is attached to the right biomarker, flagged a SCALE blood pressure row whose numbers it could only
find in an abstract about exenatide and glibenclamide. The cause was not the extraction: group 219
holds two unrelated 2016 Diabetologia abstracts, the SCALE obesity and prediabetes 3 year abstract
and an exenatide, metformin and glibenclamide adipocytokine abstract. The SCALE record was extracted
and closed the group; the exenatide record was never read.

`src/packet_grouping_check.py` now audits every multi record packet for this defect by comparing the
molecules named in each record's title, and it is gate ten of `work/run_gates.sh`. Six of the 50
multi record packets are flagged. This document records what each flagged record is and what was
decided about it, and it is the gate's allowlist: a flagged group listed in the table below is
triaged, and the gate fails only on a flagged group that is not.

## Triaged groups

| Group | Ledger status | What the group actually holds, and the verdict per record |
|---|---|---|
| 219 | extracted | TWO studies. (1) The SCALE obesity and prediabetes 3 year abstract, extracted and pooled through the le Roux 2017 companion capture, 10 rows, correct and unaffected. (2) An unrelated abstract, exenatide plus metformin and glibenclamide against metformin plus glibenclamide on beta and alpha cell function and adipocytokines (Diabetologia 2016, doi 10.1007/s00125-016-4046-9), never read until this triage. Verdict on record 2, now read: no usable contrast. Every figure in it is a WITHIN arm change reported separately for the exenatide and the control group, as a median with its interquartile range (HOMA-beta 34.8 [23.7; 48.3] at baseline against 53.8 [38.0; 88.1] at six months, P < 0.001; HOMA-IR 7.0 [5.0; 8.9] against 5.6 [4.8; 8.8], P 0.07) or as a percentage area under the curve change with a within arm p (glucose 27 per cent, glucagon 13.1 per cent, proinsulin 17.5 per cent), with no between arm difference and no dispersion for one; adiponectin is reported as not changed and resistin as 29 per cent lower, both without numbers for a contrast. It is recorded here rather than in the ledger because the group's single status belongs to the study that was pooled. |
| 279 | extracted | THREE studies. (1) The EUREXA adipokine addendum, extracted and in the master. (2) A DURATION-2 abstract (exenatide once weekly against sitagliptin and pioglitazone), now read: verdict no usable contrast, because the record prints no number for any inventory marker at all, only the sentence that significant improvements from baseline in systolic pressure, albumin to creatinine ratio, hsCRP, BNP and adiponectin were observed with exenatide once weekly, with hsCRP and adiponectin also improving under both comparators. The parent publication of DURATION-2 is therefore added to the supplement queue: it would carry exenatide hsCRP, adiponectin and systolic pressure contrasts against two active comparators. (3) A liraglutide meta analysis abstract, now read: not eligible under section 2 of the brief, a meta analysis is not a trial, and its figures are pooled within arm percentage changes by drug (hsCRP minus 23.1 per cent under liraglutide, minus 42.6 under rosiglitazone, minus 15.6 under exenatide) rather than trial level contrasts. |
| 6 | already_extracted | The survodutide cardiovascular risk biomarker abstract appears twice and is pooled elsewhere; the third record is a phase 2 trial of BIO101 (20E), a drug outside the admitted list whose title mentions semaglutide only as context. Verdict: not eligible, intervention. No loss. |
| 54 | no_usable_contrast | TWO studies. (1) REDEFINE 5, CagriSema in East Asian adults, which is held in substance by decision D-X1. (2) An oral semaglutide 25 mg abstract on glycaemic parameters and cardiovascular risk factors (205 against 102 randomised, week 64), now read: verdict no usable contrast, because the comparisons it prints are WITHIN the semaglutide arm between weight loss response subgroups (fasting serum insulin ratio to baseline 0.63 against 0.88, fasting glucose minus 0.6 against minus 0.3 mmol/L, HbA1c minus 0.4 against minus 0.2 percentage points for those reaching 15 per cent weight loss against those not) rather than randomised contrasts against placebo, and the placebo comparisons it does give are proportions reaching glycaemic categories. Its parent trial is the oral semaglutide 25 mg obesity programme, whose appendix is already in the supplement queue. |
| 146 | no_usable_contrast | TWO studies, and the most costly of the six. (1) SURPASS-3 MRI (tirzepatide against insulin degludec, 296 participants with evaluable MRI), whose abstract states that all tirzepatide doses reduced visceral and abdominal subcutaneous fat, increased adiponectin and decreased leptin against insulin degludec, with every number held in a table the abstract record does not carry. The closure was correct for the record, and the substudy's full publication was read through the institutional route on the same afternoon: its Table 2 gave six dose specific relative change contrasts against insulin degludec, three for liver fat and three for visceral fat, which are now in the master as the first contrasts of either marker in the GLP-1 and GIP class, the class the question 2 contrast most depends on; SURPASS-3 was not otherwise in the corpus. Pooled visceral adipose tissue moved from minus 13.1 per cent over six trials to minus 17.6 over seven. Adiponectin and leptin, which this substudy's conference abstract says improved against the comparator, appear nowhere in the article and remain in the supplement queue. (2) A liraglutide muscle fat infiltration trial: muscle fat infiltration is not an inventory marker and the between arm contrast (minus 2.81 against plus 0.29 per cent, p 0.001) carries no dispersion. |
| 28 | ongoing_no_results | TEN records spanning five trials. The status is correct for the six survodutide records (SYNCHRONIZE-1 and SYNCHRONIZE-2 baseline abstracts and the two design papers, no results posted). Four records were never read until this triage. (1) REDEFINE 1 hsCRP (CagriSema): a complete contrast exists, CagriSema against placebo minus 62.9 per cent (95 per cent CI minus 65.6 to minus 60.0) at week 68 on a geometric mean baseline of 3.2 mg/L, with semaglutide 2.4 mg against placebo printed only as arm percentages (minus 55.4 against minus 16.0) and therefore without a variance; the CagriSema row is staged and held with group 60 under decision D-X1. (2) REDEFINE 1 BMI and waist to height targets: not inventory markers. (3) Retatrutide circulating proteomic markers: relative proteomic changes, not inventory markers; it names the parent trials' triglyceride and LDL reductions as background without variance. (4) SURMOUNT-2 physical function by quartile of inflammatory biomarker improvement: a post hoc quartile analysis with no between arm biomarker contrast, so no row, but it establishes that SURMOUNT-2 measured hsCRP in 292 and IL-6 in 270 participants alongside a self reported physical function instrument, which corrects the draft's statement that no trial in the corpus pairs a functional measure with the biomarker panel. |

## What the defect cost, and what it did not

No pooled row is wrong because of this. Every row that reached the master was read from the record it
cites and passes both provenance checks. What the defect cost is assessment: nine records across six
groups were never read, and of those nine, one carries a held class contrast (REDEFINE 1 hsCRP), one
pointed at a full publication that has since been read and has improved the question 2 contrast
(SURPASS-3 MRI, six rows extracted the same afternoon),
one corrects a statement in the draft (SURMOUNT-2 physical function), and six carry nothing poolable.

## The adjacent finding, recorded here because it was found by the same thread

The triple agonist class is represented in the corpus by one trial and one marker, which the Results
report as a property of the evidence. The retatrutide marker evidence does exist: a 2025 abstract
(group 72) reports HOMA2-IR falling 39 per cent in type 2 diabetes and 52 per cent in obesity,
adiponectin rising up to 52 and 70 per cent, and HOMA2-B rising up to 88 per cent, across two phase 2
trials of 281 and 338 participants. Every one of those figures is a within arm change from baseline
with no concurrent control contrast and no dispersion, so the deterministic scan closed the group
correctly and the brief refuses the numbers.

The two parent phase 2 publications, which would carry the tables, were never retrieved by any of the
three searches: no file under `search/` contains their DOIs, and the author name hits belong to the
abstracts. The strategy requires an aging relevant biomarker term, and a parent paper whose abstract
reports only weight and HbA1c therefore does not match it. That is a retrieval blind spot rather than
a screening error, and it falls hardest on the newest classes, whose marker data live in supplements
and abstracts. The correctable version is a trial level backfill step: for every included record that
is a conference abstract or a substudy, retrieve the trial's main publication by registry number and
screen it whether or not its own abstract names a marker. It is recorded as an amendment candidate,
not applied, because adding a retrieval step changes the PRISMA identification count and is a
Director decision.
