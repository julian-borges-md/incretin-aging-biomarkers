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
| Web of Science search | Not run; no string exists |
| Second independent screener, blinded | Implemented 15 October 2026 as two local reviewer agents with a third adjudicating (`src/screen_titles.py`); first run on the 659 Embase articles complete: 338 include, 321 exclude (`search/screening/SCREENING_SUMMARY.md`) |
| Kappa per screening stage | Title and abstract, Embase pool, criteria v1: 0.649 (SE 0.030), agreement 82.4 per cent, 116 of 116 disagreements adjudicated |
| Screening sensitivity audit | 5 of 37 known relevant records wrongly excluded by both reviewers, in two recurring criterion misreadings; criteria clarified (v2) and the 321 exclusions rescreened under v2: 24 rescued to full text (3 of the 5 known misses among them), 297 stay excluded; set to full text 362; sensitivity on known positives 35 of 37 after both stages, the two residual misses (Wang 2020, Takeshita 2015) recovered through the adopted list (`search/screening/SCREENING_AUDIT_2026-10-15.md`, `SCREENING_SUMMARY_v2.md`); pool 2 (51 registry + 200 CENTRAL only) screened under v2: kappa 0.556, 185 include / 66 exclude (`SCREENING_SUMMARY_batch2_v2.md`); 547 records of 910 go to full text; pool assembled with retrieval routes and candidate study grouping (`search/screening/FULLTEXT_POOL_SUMMARY.md`: 439 candidate studies after DOI, title and NCT grouping; 228 journal articles by DOI of which 109 open access and harvested, 106 closed access pending the institutional route, 13 outside Europe PMC; 162 conference abstracts; 140 registry records of which 56 ClinicalTrials.gov entries fetched through the public API, 84 on other registers; 12 already extracted; 5 by title) |
| Full text retrieval for the 547 record pool | 16 October 2026: a text in hand for 530 of the 533 records that need one (14 already extracted): 160 conference abstracts (the record is the document), 56 ClinicalTrials.gov entries (public API), 84 other register summaries (index record only), 108 Europe PMC open access full texts, 8 publisher open access pages or preprints, 89 full texts captured through BU EZproxy and 5 from repository or open access copies located by title or through OpenAlex, 20 publisher or index pages of at least 2,000 characters that may be complete short documents or abstracts only (6 of them trial reports behind subscriptions BU lacks, listed for interlibrary request); 3 records without any text, listed with reasons (`search/screening/FULLTEXT_ACCESS_SUMMARY.md`). The three agent full text screen runs over every record with a text (`src/fulltext_screen.py`, `FULLTEXT_SCREENING_SUMMARY.md` when complete) |
| Full-text retrieval of the five paywalled placebo-controlled trials | Done 15 October 2026 through BU EZproxy; all five extracted under amendment R1 to R4 |
| Record counts at each PRISMA step for Stream A | Partially available, needs reconstruction from search logs |
