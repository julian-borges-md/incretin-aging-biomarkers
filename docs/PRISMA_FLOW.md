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

Embase, CENTRAL and Web of Science searches are specified in the protocol and **have not yet been executed**. Strings are drafted and institutional access is available; this is outstanding work, not a decision to omit them.

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

**Update 2026-10-15, 21:10.** All five trials in the first category were retrieved in full through the BU EZproxy route (none is in PMC). Their status moves from "not accessible" to "retrieved, extraction pending three analysis rule decisions" (final value versus change score for parallel trials without change SDs, inventory reconciliation, crossover handling); details and the per trial extractable quantities are in `docs/MONO_TRIALS_RETRIEVAL_2026-10-15.md`. The Embase search has since been executed (710 hits, 659 article records, `search/embase_2026-10-15/SEARCH_LOG.md`); CENTRAL and Web of Science remain unrun, and the 514 record Web of Science export once attributed to this review belongs to another workstream (`docs/LICENSED_DATABASE_ACCESS.md`). The included set is now 7 trial analyses, 48 rows, 19 biomarkers, 43 rows convertible to the common scale.

## What a PRISMA diagram cannot yet show

A conventional PRISMA diagram reports records identified, screened, excluded with reasons, and included, with numbers at each step. Stream A can supply those numbers. Stream B cannot, because the screening was done by other groups and we inherited their output.

The diagram will therefore be drawn for Stream A only, with Stream B shown as a separate inflow labelled as adopted from published reviews. A single merged diagram implying one unified search would misrepresent the process.

## Outstanding before this section is complete

| Item | Status |
|---|---|
| Embase, CENTRAL, Web of Science searches | Strings drafted, access available, not run |
| Second independent screener, blinded | Not implemented |
| Kappa per screening stage | Cannot be computed until the above |
| Full-text retrieval of the five paywalled placebo-controlled trials | Blocked on institutional access |
| Record counts at each PRISMA step for Stream A | Partially available, needs reconstruction from search logs |
