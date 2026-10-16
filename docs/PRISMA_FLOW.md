# PRISMA flow and search provenance

Written 2026-10-15. Describes the identification and selection process **as actually performed**, including the ways it departs from a conventional systematic review search.

## The honest summary first

This review's corpus was assembled in two distinct ways, and they are not equivalent:

| Arm | How trials were found | Status |
|---|---|---|
| Dual and triple agonists (GIP, GCGR, triple) | Our own anchor searching in PubMed | Independent, but not an exhaustive multi-database search |
| Mono-agonist comparator | Included-study lists of two published systematic reviews | Adopted, not independently searched |

Describing the whole as a single systematic search would be inaccurate. The structure is closer to a hybrid: an overview of reviews for the comparator arm, plus original searching for the agents those reviews did not cover.

This must appear in the Methods in these terms.

## Identification

### Stream A: our anchor searches, dual and triple agonists

PubMed searched for tirzepatide, retatrutide, survodutide, pemvidutide, mazdutide and cotadutide against the pre-specified 26-biomarker inventory. These searches were run to populate receptor classes that no existing synthesis covers.

| Search | Records |
|---|---|
| Body composition anchor | 156 PMIDs |
| Hepatic anchor | 95 PMIDs |
| GDF-15 anchor | 13 PMIDs |

Embase and CENTRAL were executed on 15 October 2026 (`search/embase_2026-10-15/SEARCH_LOG.md`, `search/central_2026-10-15/SEARCH_LOG.md`). Web of Science has not been run. The statement that stood here until 15 October, that strings for all three were drafted, was not true for CENTRAL or Web of Science: no string for either existed anywhere in the repository or the vault, and the CENTRAL strategy is a dated translation of the Embase lines, recorded as such.

### Stream B: adopted from published reviews, mono-agonists

Two systematic reviews provided the mono-agonist comparator pool:

| Source | Trials | Scope |
|---|---|---|
| Alrasheed 2026, PMID 41625236, PROSPERO CRD420251157476 | 40 RCTs, n=6029 | CRP, IL-6, TNF-alpha, MDA in T2D. Liraglutide 23, exenatide 13, dulaglutide 2, no semaglutide |
| Ren 2025, PMID 40230207 | 52 RCTs, n=4734 | CRP, TNF-alpha, IL-6, IL-1beta, leptin, adiponectin, PAI-1, MCP-1, AGEs |

Neither stratifies by receptor class, and neither includes tirzepatide, retatrutide or any glucagon receptor containing agent. Alrasheed state this explicitly as a limitation and call for exactly the comparison this review attempts.

## Screening

**Stream A** was screened against the eligibility criteria by one reviewer. The protocol specifies two independent blinded reviewers with third-party adjudication. **That has not yet been implemented.** Current screening is single-reviewer and must be described as such until the blinded second pass is run.

**Stream B** inherits the screening of the source reviews. Their eligibility criteria are narrower than ours in population (T2D only) and broader in comparator (any glucose-lowering agent). Trials adopted from them were re-screened against our criteria, which is how the comparator restriction below was applied.

## Eligibility applied at full text

| Criterion | Effect |
|---|---|
| RCT, minimum 12 weeks | Applied |
| Adults, overweight through MASH | Applied |
| Reports a biomarker from the inventory | Applied |
| Extractable variance | **Binding constraint.** Several trials report direction without values, or p-value bounds from which no standard error is recoverable |
| Placebo-controlled, for Q2 only | Amendment of 2026-10-15, see COMPARATOR_PROBLEM.md |

## Included

**6 trials, 7 trial-analyses, 43 poolable rows, 20 biomarkers.**

| Trial | Class | Rows | RoB |
|---|---|---|---|
| SELECT, Plutzky | mono | 1 | some concerns |
| SELECT, Meyhofer | mono | 4 | some concerns |
| EUREXA, Simo | mono | 1 | high |
| Wilson | GIP dual | 19 | high |
| Ekinci 1404-0002 | GCGR dual | 7 | high |
| Ekinci 1404-0036 | GCGR dual | 8 | high |
| Sanyal | triple | 8 | some concerns |

## Excluded at full text, with reasons

| Reason | Trials |
|---|---|
| Full text not accessible, abstract gives direction without values | Derosa 2012 (PMID 22540883), von Scholten 2017 (PMID 28105731), Wu 2011, Anholm 2019, Wagner 2019 |
| Not in PMC, no institutional retrieval yet attempted | NEJM MASH trials: Sanyal survodutide (38847460), Loomba tirzepatide (38856224), Sanyal ESSENCE (40305708), Noureddin pemvidutide (41237796) |
| Active comparator, excluded from Q2 only | EUREXA (retained for Q1) |

The first category is the current bottleneck for Q2 and is a retrieval problem, not an eligibility one.

**Update 2026-10-15, 21:10.** All five trials in the first category were retrieved in full through the BU EZproxy route (none is in PMC). Their status moves from "not accessible" to "retrieved, extraction pending three analysis rule decisions" (final value versus change score for parallel trials without change SDs, inventory reconciliation, crossover handling); details and the per trial extractable quantities are in `docs/MONO_TRIALS_RETRIEVAL_2026-10-15.md`. The Embase search has since been executed (710 hits, 659 article records, `search/embase_2026-10-15/SEARCH_LOG.md`; the 51 registry records followed at 22:00), and CENTRAL at 22:10 (460 trial records, `search/central_2026-10-15/SEARCH_LOG.md`); Web of Science remains unrun, and the 514 record Web of Science export once attributed to this review belongs to another workstream (`docs/LICENSED_DATABASE_ACCESS.md`). The included set is now 7 trial analyses, 48 rows, 19 biomarkers, 43 rows convertible to the common scale.

## What a PRISMA diagram cannot yet show

A conventional PRISMA diagram reports records identified, screened, excluded with reasons, and included, with numbers at each step. Stream A can supply those numbers. Stream B cannot, because the screening was done by other groups and we inherited their output.

The diagram will therefore be drawn for Stream A only, with Stream B shown as a separate inflow labelled as adopted from published reviews. A single merged diagram implying one unified search would misrepresent the process.

## Outstanding before this section is complete

| Item | Status |
|---|---|
| Embase search | Run 15 October 2026: 710 hits, 659 article records exported and screened, 51 registry records exported (22:00) |
| CENTRAL search | Run 15 October 2026: 460 trial records exported; 260 overlap the Embase articles, 200 do not (143 registry derived, 57 journal articles) |
| Web of Science search | Run 16 October 2026 through BU EZproxy as the dated translation of the Embase lines (`search/wos_2026-10-16/SEARCH_LOG.md`): 22,770 / 807,756 / 3,445,325 / 317 records exported (RIS, count and SHA gated); 196 also in Embase, 135 also in CENTRAL, 99 in neither, screened as pool batch3 under criteria v2 (queued behind the full text chains); adds no known relevant item beyond Embase and CENTRAL |
| Second independent screener, blinded | Implemented 15 October 2026 as two local reviewer agents with a third adjudicating (`src/screen_titles.py`); first run on the 659 Embase articles complete: 338 include, 321 exclude (`search/screening/SCREENING_SUMMARY.md`) |
| Kappa per screening stage | Title and abstract, Embase pool, criteria v1: 0.649 (SE 0.030), agreement 82.4 per cent, 116 of 116 disagreements adjudicated |
| Screening sensitivity audit | 5 of 37 known relevant records wrongly excluded by both reviewers, in two recurring criterion misreadings; criteria clarified (v2) and the 321 exclusions rescreened under v2: 24 rescued to full text (3 of the 5 known misses among them), 297 stay excluded; set to full text 362; sensitivity on known positives 35 of 37 after both stages, the two residual misses (Wang 2020, Takeshita 2015) recovered through the adopted list (`search/screening/SCREENING_AUDIT_2026-10-15.md`, `SCREENING_SUMMARY_v2.md`); pool 2 (51 registry + 200 CENTRAL only) screened under v2: kappa 0.556, 185 include / 66 exclude (`SCREENING_SUMMARY_batch2_v2.md`); 547 records of 910 go to full text; pool assembled with retrieval routes and candidate study grouping (`search/screening/FULLTEXT_POOL_SUMMARY.md`: 439 candidate studies after DOI, title and NCT grouping; 228 journal articles by DOI of which 109 open access and harvested, 106 closed access pending the institutional route, 13 outside Europe PMC; 162 conference abstracts; 140 registry records of which 56 ClinicalTrials.gov entries fetched through the public API, 84 on other registers; 12 already extracted; 5 by title) |
| Full text retrieval for the 547 record pool | 16 October 2026: a text in hand for 530 of the 533 records that need one (14 already extracted): 160 conference abstracts (the record is the document), 56 ClinicalTrials.gov entries (public API), 84 other register summaries (index record only), 108 Europe PMC open access full texts, 8 publisher open access pages or preprints, 89 full texts captured through BU EZproxy and 5 from repository or open access copies located by title or through OpenAlex, 20 publisher or index pages of at least 2,000 characters that may be complete short documents or abstracts only (6 of them trial reports behind subscriptions BU lacks, listed for interlibrary request); 3 records without any text, listed with reasons (`search/screening/FULLTEXT_ACCESS_SUMMARY.md`). The three agent full text screen runs over every record with a text (`src/fulltext_screen.py`, `FULLTEXT_SCREENING_SUMMARY.md` when complete) |
| Full-text retrieval of the five paywalled placebo-controlled trials | Done 15 October 2026 through BU EZproxy; all five extracted under amendment R1 to R4 |
| Record counts at each PRISMA step for Stream A | Partially available, needs reconstruction from search logs |

## Update 2026-10-16, 14:30 local: the full text screening stage is complete

The full text pool closed at 576 records (the 547 record pool of 15 October plus the 29 pool 3 records
that the Web of Science only export contributed after title screening under criteria v2). Every record
with a text was read independently by two local reviewer agents (different models, temperature 0, fixed
seed, blinded to each other) under criteria v2 plus the full text addendum, and every disagreement was
settled by the session's cloud model reading the same text, on the Director's instruction of 16 October
08:45 local. `search/screening/FULLTEXT_SCREENING_SUMMARY.md` is produced by `src/fulltext_screen.py
summarise` from the three decision files and is the auditable record.

| Quantity | Value | Note |
|---|---|---|
| Records in the full text pool | 576 | 158 conference abstracts, 84 other register summaries, 56 ClinicalTrials.gov entries, 120 Europe PMC full texts, 8 publisher open access pages, 94 full texts through the institutional route, 33 publisher or index pages (partial), 3 without any text, 20 already in the master |
| Records needing a screen (with a text) | 553 | 576 minus the 3 without a text and the 20 already extracted |
| Screened by both reviewers | 558 | the 553 plus 5 already extracted records that carried a text and were screened anyway; the apparent mismatch in the summary table is this and nothing else |
| Reviewer 1 include / exclude | 538 / 20 | one reviewer is far more inclusive than the other |
| Reviewer 2 include / exclude / model error | 389 / 167 / 2 | the two error rows sit outside the agreement statistic and were adjudicated |
| Raw agreement | 409 of 556 (73.6 per cent) | |
| Cohen's kappa | 0.160 (SE 0.059) | low because the marginals are extremely unbalanced; reported as it is, with the agreement, and discussed in the limitations |
| Disagreements adjudicated | 149 of 149 | 51 to include, 98 to exclude |
| Final include / exclude / pending | 440 / 118 / 0 | |
| Known relevant records with a text, included | 26 of 28 | the two excluded are listed by key in the summary for audit: a tirzepatide meta analysis (1-76) and a 14 day flash glucose monitoring study (1-441) |

Criterion failures recorded by the reviewers, as counts of records (reviewer 1 then reviewer 2):
design 16 then 50, population 4 then 57, intervention 5 then 63, outcome 4 then 72, timing 3 then 57.

The 440 included records group into 338 candidate studies (`src/extraction_packets.py`), of which 148
have a full text and 190 only an abstract, register entry or partial publisher page. Grouping is by DOI,
title and registry identifier, so one study with a conference abstract, a register entry and a full text
is one packet.

### Extraction status of the included studies at this update

| Ledger status | Groups | Meaning |
|---|---|---|
| extracted | 43 | rows written to `analysis/data/extraction_*.csv` |
| already_extracted | 16 | the trial is in the master under another record |
| no_usable_contrast_scan | 104 | closed by the deterministic variance mark scan (`src/abstract_scan.py`) without an agent read |
| no_usable_contrast | 60 | read, but no dispersion, interval or exact p from which a standard error is recoverable |
| excluded_at_extraction | 26 | eligibility failure visible only at extraction (reviews, single arm or same intervention in both arms, no incretin) |
| molecule_not_admitted | 3 | NNC0090-2746, lixisenatide, orforglipron class agents |
| held_pending_decision | 12 | populations held under amendment A6 (PCOS, OSA, HIV, schizophrenia, knee osteoarthritis), the amylin co formulation under D-X1, and the stratified table case D-X8 |
| ongoing_no_results | 8 | registered, no results posted |
| queued | 68 | released by this packet rebuild, extraction in progress |

The master at this update holds 388 rows over 54 trials or trial analyses and 35 biomarkers, 361 of them
convertible to the placebo corrected percent change scale; the 27 unconvertible rows are mean differences
in absolute units whose baseline denominator is not printed in any text in hand, listed by trial in
`work/gate_harmonise_units.log`. A PRISMA diagram drawn now would therefore be accurate for
identification, screening and eligibility, and provisional for the included count.

### Update 2026-10-16, 16:00 local: the extraction queue is closed

The queue is empty. Every one of the 340 ledger groups now carries a terminal status, so the included
count of the PRISMA diagram is final for this corpus and no longer provisional.

| Ledger status | Groups | Meaning |
|---|---|---|
| no_usable_contrast_scan | 104 | closed by the deterministic variance mark scan (`src/abstract_scan.py`) without an agent read |
| no_usable_contrast | 84 | read, but no dispersion, interval or exact p from which a standard error is recoverable |
| extracted | 61 | rows written to `analysis/data/extraction_*.csv` |
| excluded_at_extraction | 37 | eligibility failure visible only at extraction (design, population, molecule) or a data integrity refusal |
| already_extracted | 22 | the trial is in the master under another record |
| held_pending_decision | 16 | 13 populations held under amendment A6 (five polycystic ovary syndrome trials, two obstructive sleep apnoea, two HIV associated lipohypertrophy, schizophrenia, knee osteoarthritis and two combination designs) and three groups waiting on the fifth receptor class or on a stratified table decision |
| ongoing_no_results | 11 | registered, no results posted |
| molecule_not_admitted | 5 | NNC0090-2746, lixisenatide and orforglipron class agents |
| queued | 0 | the queue is closed |

The 340 ledger groups are the 338 indexed packets plus two conference abstract packets built after the
index (groups 158 and 429), whose trials were extracted from other records.

The master at this update holds 518 rows over 75 trials or trial analyses and 35 of the 36 inventory
biomarkers, 480 of them convertible to the placebo corrected percent change scale; the 38 unconvertible
rows are mean differences in absolute units whose baseline denominator is not printed in any text in
hand, listed by trial in `work/gate_harmonise_units.log`. Risk of bias with RoB 2 is recorded for 76
trials, the 75 that contribute a pooled row and one whose rows were closed at extraction.

Three integrity refusals are recorded in the ledger with their arithmetic rather than as eligibility
exclusions: two trials whose printed statistics are impossible for their printed means and standard
deviations, and one whose baseline MCP-1 differs between randomised arms by 8.05 standard errors while
its other ten baseline comparisons behave exactly as randomisation predicts.

What remains is not extraction but the supplement pass: named tables and appendices of trials already
in the corpus that hold further rows, including the hsCRP and adiponectin contrasts of the exenatide
against insulin detemir trial, which the publisher renders as a table graphic behind a subscriber gate
and which the registry record does not post.
