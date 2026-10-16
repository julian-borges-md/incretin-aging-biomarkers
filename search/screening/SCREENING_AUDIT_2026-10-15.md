# Screening audit, 15 October 2026: the first run on the Embase pool and what it forced

## The first run (criteria v1)

Two blinded local reviewer agents screened all 659 Embase article records (`SCREENING_SUMMARY.md`): agreement 543 of 659 (82.4 per cent), Cohen's kappa 0.649 (SE 0.030), 116 disagreements adjudicated by the third agent (112 include, 4 exclude), final 338 include and 321 exclude. The disagreement structure is one sided: reviewer 1 included and reviewer 2 excluded 107 records, the reverse 9. Reviewer 2 failed records on population, intervention, outcome and duration far more often than reviewer 1 (P 192 vs 38, I 106 vs 31, O 94 vs 7, T 97 vs 15), so the two models do not read the same criteria the same way, which is the point of using two.

## Known relevant records excluded by both reviewers

Forty records in the pool are linked to trials the review already knows to be relevant (`RECALL_AND_DEDUP.md`). Thirty two were included; eight were excluded by both reviewers and therefore never reached the adjudicator. Each was read against the record and the reviewers' stated reasons.

| n | Record | Both reviewers' reason | Reading |
|---|---|---|---|
| 76 | Masson 2026, tirzepatide anti inflammatory effects, systematic review | D: review | Correct exclusion; the link to the known set is an author and year coincidence |
| 244 | Konstantinidou 2024, GDF-15 under liraglutide or naltrexone/bupropion | D: non randomised | Correct exclusion: the abstract states a non randomised design |
| 330 | Ying 2023, liraglutide and oxidised LDL induced endothelial dysfunction | D: mice | Correct exclusion; already identified as a false link in the Embase reading |
| 446 | Wang 2020, vildagliptin combined with liraglutide | I: vildagliptin is a DPP-4 inhibitor | Wrong. One arm receives liraglutide; the comparator never excludes a trial |
| 548 | Savvidou 2016, adiponectin, exenatide plus glargine versus intensive insulin, 6 months | T: 6 months read as shorter than 12 weeks | Wrong. 6 months is 26 weeks |
| 568 | Takeshita 2015, vildagliptin versus liraglutide | I: as for 446 | Wrong, same misapplication |
| 595 | Suzuki 2014, liraglutide versus sitagliptin in untreated type 2 diabetes | R1 I: as above; R2 P and O: type 2 diabetes without stated obesity | Wrong. Type 2 diabetes is an eligible population and the comparator is irrelevant |
| 616 | Forst 2012, liraglutide added to metformin, 12 weeks | T: 12 weeks read as too short | Wrong. The criterion is 12 weeks or longer |

Three exclusions are correct and five are misapplications of criteria that were already explicit, in two recurring patterns: a DPP-4 inhibitor comparator read as an intervention exclusion (three records), and a duration at or above the 12 week threshold read as below it (two records). Sensitivity against the known relevant set is therefore 32 of the 37 linked records that are plausibly genuine positives (86 per cent), not the 32 of 40 printed in the summary, and the five misses are systematic, not random. A systematic miss is a prompt defect, and a prompt defect is fixable without touching the criteria.

## What was done about it

Criteria version 2 appends clarifications that restate the four criteria involved (`CRITERIA_V2_ADDENDUM` in `src/screen_titles.py`): the comparator never excludes a trial; 12 weeks exactly is eligible and durations are converted before comparison; type 2 diabetes is eligible without a stated weight status; a secondary analysis of a randomised trial is eligible. Nothing is widened: every clarification is already implied by the v1 wording.

The v1 decisions are kept as the record of the first run. Both reviewers rescreen, under v2, only the 321 records the first run finally excluded (`rescreen-excluded`), and any record either reviewer includes under v2 goes to full text alongside the 338 v1 includes. Includes are not revisited, because an inclusion error is caught at full text and an exclusion error is not. The rescreen summary (`SCREENING_SUMMARY_v2.md`) reports the rescue counts and the fate of the five known relevant misses; it does not report a second kappa, because a set selected for having been excluded is not a sample on which agreement means anything.

The second pool (51 Embase registry records plus the 200 CENTRAL records not in the Embase export) is screened under v2 from the start (`SCREENING_SUMMARY_batch2_v2.md`).

## Two engineering defects found by the same run

The first attempt at the second pool crashed on a registry record: the model answered with its own JSON schema, truncated at the output token limit, and the fallback parser raised instead of returning the unparseable default. The parser now treats any malformed answer as unparseable, which the design maps to include, never to a silent exclusion. The cause was the record text: registry records carry a detailed description of up to 31,000 characters, far beyond the context window, so the reviewer saw a truncated prompt. The record text now takes the brief summary (AB) before the detailed description (N2) and caps the abstract at 10,000 characters, above the longest Embase abstract (9,551), so the first run's inputs are unchanged and the pool 2 inputs fit.

## Reading for the Methods

Two model reviewers with adjudication reached 86 per cent sensitivity on known positives at the first pass, with the misses concentrated in two interpretable criterion misreadings. The protocol statement should be that title and abstract screening was performed by two independent automated reviewers with a third adjudicating, that the criteria prompt was clarified once after an audit against known relevant records, that records excluded under the first prompt were rescreened under the clarified one, and that the audit list and both prompts are in the repository. What cannot be claimed is 95 per cent sensitivity, which was not measured against an independent reference set.

## Rescreen result (criteria v2, run 23:26 to 00:08 on 16 October)

Both reviewers rescreened the 321 records finally excluded under v1 (`SCREENING_SUMMARY_v2.md`). Twenty four were included by at least one reviewer and go to full text (21 by reviewer 1 alone, 1 by reviewer 2 alone, 2 by both), 297 stay excluded; agreement on this set 299 of 321. The set going to full text is 338 plus 24, 362 records. The rescue is deliberately permissive: among the 24 are three meta analyses and several records outside the population (psoriasis, Parkinson disease, brain dead donors), all of which fall at full text at no cost to sensitivity.

Of the five known relevant records wrongly excluded under v1, three were rescued (Savvidou 2016 and Forst 2012, the two duration misreadings, now included by both reviewers; Suzuki 2014 by reviewer 2). Two were excluded again by both reviewers under the same wrong reading: Wang 2020 (n 446) and Takeshita 2015 (n 568), both liraglutide against vildagliptin, both read by both models as "no eligible agent in any arm" despite liraglutide in the title and the v2 sentence that the comparator never excludes a trial. That is a reading failure of two different models on two records with the same shape, not a wording problem; a third prompt revision would be fitting the prompt to two records. Both trials are in the adopted mono agonist list and enter the review through that stream regardless, which is the purpose of carrying the known relevant list through screening: the miss is visible and recoverable, not silent. The two correct exclusions among the known linked records (Konstantinidou 2024, non randomised; Ying 2023, mice) were excluded again, as they should be.

Sensitivity of the two stage screen against the 37 plausibly genuine known positives is therefore 35 of 37 (95 per cent), with both residual misses named and recovered by the adopted list. The first stage alone was 32 of 37.
