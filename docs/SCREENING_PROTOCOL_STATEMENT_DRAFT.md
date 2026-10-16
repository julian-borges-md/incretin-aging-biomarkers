# Screening protocol statement, draft for the Lab Director's adoption

Status: DRAFT, 16 October 2026. Nothing in this document is in force until the Director adopts it; the items that need a decision are listed in Section 9. Every count below was produced by execution and names the file it was read from. Once adopted, this statement becomes the screening section of the methods and the record of deviations from the registered protocol.

## 1. Purpose

To state, in one place and before the full text decisions are used for anything, how records were screened for this review: who screened, against which criteria, in which order, how disagreements were settled, what was changed after the first run and why, and what the screening cannot claim. The statement exists so that the methods section, the PRISMA flow and the disclosure of AI use are written from a record rather than from memory.

## 2. Scope of the screened set

| Source | Records | Export and gate |
|---|---|---|
| Embase, journal articles | 659 | `search/embase_2026-10-15/embase_659.ris` (gitignored), SHA-256 recorded in `SEARCH_LOG.md`; count and checksum are asserted by every script that reads the file |
| Embase, clinical trial registry records | 51 | `search/embase_2026-10-15/embase_registry_51.ris`, same gate |
| CENTRAL | 460 trial records, of which 200 not in the Embase export by DOI or title | `search/central_2026-10-15/central_460.ris`, same gate; strategy is a dated translation of the Embase lines with every difference tabled in `SEARCH_LOG.md` |
| Web of Science Core Collection | 317 records, of which 99 in neither the Embase nor the CENTRAL export | `search/wos_2026-10-16/wos_317.ris`, same gate; strategy is the dated translation drafted in `search/wos_DRAFT/WOS_STRATEGY_DRAFT.md`, run 16 October (`search/wos_2026-10-16/SEARCH_LOG.md`) |
| Screened in total | 910 unique records in two pools, plus pool 3 | pool 1: the 659 Embase articles; pool 2: the 51 registry records plus the 200 CENTRAL only records; pool 3: the 99 Web of Science only records (title and abstract screen under version 2 queued behind the full text chains; its includes then join the full text stage) |

## 3. Eligibility criteria

The criteria are coded D (design), P (population), I (intervention), O (outcome), T (duration) and are the text in `src/screen_titles.py` (`criteria_text()`), shown verbatim to every reviewer agent. Version 1 is the registered wording. Version 2, dated 15 October 2026, adds four clarifications and changes no criterion:

| Code | Clarification in version 2 | Reason it was needed |
|---|---|---|
| I | The comparator never excludes a trial; a trial is eligible when at least one arm receives an eligible agent, whatever the other arms receive. The DPP-4 inhibitor exclusion applies only when no arm receives an eligible agent | Both reviewer agents excluded trials with a sitagliptin or vildagliptin comparator arm as if the comparator were the intervention |
| T | 12 weeks exactly is eligible; 3 months, 84 days, 6 months, 1 year are converted before comparison; exclude on T only when the treatment period is clearly shorter than 12 weeks | 12 week trials were excluded as "shorter than 12 weeks" and 6 month trials as not stating weeks |
| P | Adults with type 2 diabetes are eligible whether or not overweight or obesity is mentioned | Trials in type 2 diabetes without a weight descriptor were excluded on P |
| D | A secondary or post hoc analysis of a randomised trial is eligible; exclude on D only when the text states a non randomised design, a single arm, animals, cells or a review | Post hoc analyses of randomised trials were excluded as "not an RCT" |

The clarifications were written after an audit of the first run against 37 records known to be relevant (the extracted corpus and the adopted reference list), 5 of which both reviewers had excluded; the five misapplications fell into the two patterns above (comparator and duration). The audit is `search/screening/SCREENING_AUDIT_2026-10-15.md`.

## 4. Screening design

Two reviewer agents screen every record independently and blind to each other; a third agent adjudicates every disagreement; the Lab Director holds decision authority over the resulting set and over every change to criteria or procedure. The agents are local language models run with temperature 0 and a fixed seed, so a rerun on the same inputs returns the same decisions; model names and settings are in the untracked configuration file `search/screening/screener_config.json` and are reported in the AI use disclosure, not in the manuscript body. The agents never see each other's decisions at the screening step; the adjudicator sees the document and both decisions with their reasons and is instructed to decide against the criteria rather than to side with either reviewer.

| Element | Title and abstract stage | Full text stage |
|---|---|---|
| Script | `src/screen_titles.py` | `src/fulltext_screen.py` |
| Input per record | title and abstract (abstract capped at 10,000 characters, registry descriptions included) | the best text available for the record, labelled by type (Section 6) |
| Criteria shown | version 1 (first run), version 2 (rescreen and pool 2) | version 2 plus a full text addendum: judge every criterion from the whole document, exclude only when the document shows a criterion fails, include and say so when a criterion still cannot be judged; report duration in weeks, comparator, and the inventory biomarkers with numerical results |
| Decision record | decision, failed criteria, one sentence reason | the same plus duration_weeks, comparator, biomarkers_reported |
| Disagreement | adjudicated by the third agent, every disagreement | from 08:45 on 16 October, on the Director's instruction, adjudicated by the session's cloud model (Claude, claude-fable-5-1) reading the same text the two local reviewers received, through `src/session_adjudicate.py`; the local adjudicator is not called (`search/screening/ADJUDICATOR.txt`); each adjudication row carries the reason and the criteria failed |
| Agreement statistic | Cohen's kappa with standard error, reported per pool | the same, reported per text source and overall |
| Files | `decisions_A*.csv`, `decisions_B*.csv`, `adjudication_002*.csv` (untracked, beside the licensed exports); `SCREENING_SUMMARY*.md` (tracked) | `fulltext_decisions_A.csv`, `fulltext_decisions_B.csv`, `fulltext_adjudication_002.csv` (untracked); `FULLTEXT_SCREENING_SUMMARY.md`, `FULLTEXT_RESULTS_SUMMARY.md` (tracked) |
| Supervision | built in, no separate supervising process (Director's instruction, 16 October): `python3 -I src/fulltext_screen.py check` reports every chain's state from its log and the process table, with progress measured on the decision files (a row per screened record), and exits 1 when a chain is stale (no new row for 12 minutes), stopped or dead; chains started from 09:22 retry a failed step three times, 90 s apart, before stopping; a chain that stopped is relaunched by hand and resumes where it stopped, the relaunch visible in its log; a chain whose remaining work moved to another chain carries a "retired" line with the reason; a relaunch changes no model, prompt, setting or record already decided | the same |

## 5. Title and abstract stage: what was done, in order

| Step | Date | Records | Agreement | Kappa (SE) | Adjudicated | Outcome | Record |
|---|---|---|---|---|---|---|---|
| Pool 1 under version 1 | 15 Oct | 659 | 543 (82.4%) | 0.649 (0.030) | 116 | 338 include, 321 exclude | `SCREENING_SUMMARY.md` |
| Audit against 37 known relevant records | 15 Oct | 37 | | | | 5 wrongly excluded by both reviewers, two recurring misreadings; version 2 written | `SCREENING_AUDIT_2026-10-15.md` |
| Rescreen of the 321 version 1 exclusions under version 2, both reviewers | 15 Oct | 321 | 299 (93.1%) | not reported | none: a record included by either reviewer is rescued to full text | 24 rescued, 297 stay excluded | `SCREENING_SUMMARY_v2.md` |
| Pool 2 under version 2 | 16 Oct | 251 | 199 (79.3%) | 0.556 (0.055) | 52 | 185 include, 66 exclude | `SCREENING_SUMMARY_batch2_v2.md` |
| Set to full text | | 547 of 910 | | | | 338 + 24 + 185 | `FULLTEXT_POOL_SUMMARY.md` |

Sensitivity on the known relevant set after both steps: 35 of 37. The two residual misses (Wang 2020, Takeshita 2015) are excluded by both reviewers under both versions and enter the review through the adopted reference list, which is a separate, documented source of records; they are not reinstated by hand into the screening decisions.

The rescreen rule ("included by either reviewer is rescued") is deliberately asymmetric: at this stage the cost of a false exclusion is a lost trial and the cost of a false inclusion is one more full text to read. The rule applies to the rescreen only; pools screened under version 2 from the start use adjudication as in Section 4.

## 6. Full text stage: the text that each record is judged on

A record is judged on the best text available for it, in this order of preference, and the label at the top of the text tells the reviewers what kind of document they have. The inventory is produced by `python3 -I src/fulltext_screen.py inventory`; counts at 08:15 on 16 October:

| Text source | Records | What it is | How it was obtained |
|---|---|---|---|
| conference_abstract | 160 | the record is the complete document | the export itself |
| ctgov_entry | 56 | ClinicalTrials.gov registry entry (10 with posted results) | public API v2, `src/ctgov_harvest.py` |
| registry_summary | 84 | index record of a trial on another register | the export itself |
| epmc_fulltext | 108 | open access full text | Europe PMC XML rendered to text, `src/epmc_harvest.py` |
| direct_fulltext | 8 | publisher open access page or preprint | `src/direct_fetch.py`, no authentication |
| proxy_fulltext | 94 | full text as published on the publisher site, captured through the institutional route (89), or an open access or repository copy located by title or through OpenAlex (5) | browser capture with the Director signed in, `src/proxy_harvest.py` |
| proxy_partial | 20 | a captured page of at least 2,000 characters that is either the abstract of a longer article (no subscription) or a complete short document (letter, comment, review without methods sections); the label says so and the reviewers judge from what is present | the same |
| awaiting_fulltext | 3 | no text beyond the index record | listed with reasons in `FULLTEXT_ACCESS_SUMMARY.md` |
| already_extracted | 14 | in `extraction_master` before this screen; not rescreened | |

Texts are capped at 48,000 characters (30,000 for registry entries) and captured pages are trimmed by three fixed patterns before the cap (navigation before the abstract heading, the reference list, publisher boilerplate lines); the characters given to each reviewer are logged per record. Fifteen captured texts still exceed the cap and are truncated at the end; in the one case read (1-120, STEP UP) the cut fell inside the safety tables after the efficacy results, the other fourteen have not been read, and the reason field records when a criterion could not be judged.

## 7. Retrieval record and reports not retrieved

Retrieval followed the order: Europe PMC open access (`src/epmc_lookup.py`, `src/epmc_harvest.py`), ClinicalTrials.gov entries for registry records with an NCT number (`src/ctgov_harvest.py`), publisher pages and preprint servers without authentication (`src/direct_fetch.py`), the institutional route through the Boston University EZproxy with the Director signed in and no credentials handled by any agent (`src/proxy_harvest.py`), then open access locations from OpenAlex and repositories found by title (`src/oa_locations.py`). The per record outcome is `search/screening/FULLTEXT_ACCESS_SUMMARY.md`.

For the PRISMA flow, the categories are:

| PRISMA item | Count at 08:15 on 16 October | Composition |
|---|---|---|
| Reports sought for retrieval | 533 | the 547 record pool minus the 14 already extracted |
| Reports not retrieved | 3 | 1-160 (DOI not found), 1-443 (Int J Clin Exp Med 2020, site unavailable, not in PubMed), 2-223 (Drug Invention Today 2019, no copy located) |
| Reports assessed for eligibility | 530 | of which 20 on an abstract page or a complete short document, 84 on a register index record, and 160 on a conference abstract that is the whole document |

A report assessed on an abstract page because the library holds no subscription (for example 1-142 in Hormones, 1-532 in Circulation: Cardiovascular Imaging) is assessed, not unretrieved; the limitation is stated in the record's reason field and the title is a candidate for an interlibrary request (Section 9).

## 8. What the screening can and cannot claim

| Claim | Supported | Basis |
|---|---|---|
| Two independent screeners with adjudication of every disagreement at both stages | yes | Section 4; the agents are blind to each other by construction and the adjudicator is a third model |
| Prespecified criteria | yes for version 1; version 2 is a clarification made after the first run and is disclosed as such | Section 3 |
| Sensitivity against a known relevant set | 35 of 37 after both title stage steps; the full text stage reports the same audit on completion | Section 5, `FULLTEXT_SCREENING_SUMMARY.md` |
| Human screening | no; the Director reviews the stage outputs and holds decision authority but did not screen records; at the full text stage the disagreements between the two local reviewers are settled by a cloud model reading the full document, which is disclosed as such (licensed full texts were read by that model on the Director's instruction) | Section 4 |
| Reproducibility | yes, for the same models and settings: temperature 0, fixed seed, inputs gated by count and checksum | Section 4 |
| The biomarkers_reported field | auxiliary and contaminated by prompt echo: on the first 300 records the reviewers named markers absent from the text (22 records for hsCRP alone) and twice returned the addendum's example list verbatim; a deterministic lexicon scan over the same texts (`src/biomarker_scan.py`, `BIOMARKER_SCAN_SUMMARY.md`) is the check, and only a name that the text also mentions is used in the study level biomarker map | Section 6 |
| Long document judgement | limited; a feasibility test on one 50,000 character text found one reviewer misreading the trial drug; the full text stage mitigates with the adjudicator, the text labels, the cap and trimming rules, and the model independent biomarker lexicon scan planned as a check on the reviewers' biomarker field | Section 6 |
| Equivalence to human dual screening | not claimed | the AI use disclosure describes the agents as the screeners and the Director as the decision authority |

## 9. Items requiring the Director's decision

| Item | Options | Proposed |
|---|---|---|
| D-S1 Adopt this statement as the screening section of record | adopt; adopt with edits; reject | adopt with edits |
| D-S2 Treat version 2 as a clarification (methods text: "criteria clarified after a sensitivity audit of the first run; the 321 exclusions were rescreened under the clarified wording") rather than as a protocol change | clarification; amendment logged with the registry | clarification, with the audit file cited |
| D-S3 Rescue rule for the rescreen ("either reviewer includes") stated as such in the methods | state it; silently fold into the adjudicated counts | state it |
| D-S4 Records assessed on an abstract page for lack of a subscription | interlibrary request for the eligible ones after the full text decisions; author contact; record as assessed with limitation | interlibrary request for the ones the screen includes, limitation stated for the rest |
| D-S5 The 3 reports not retrieved | record as not retrieved; further search by hand | record as not retrieved, retry 1-443 once more when the site answers |
| D-S6 Web of Science | run on 16 October on the Director's instruction (317 records, 99 new); the 99 are screened as pool 3 and the includes go through the full text stage before the stage closes | done; remaining decision is whether the full text stage waits for pool 3 (proposed: yes) |
| D-S7 The two residual known misses entering through the adopted list | state in methods as a documented second source; treat as a screening failure to be reported | state as a documented second source, with the sensitivity figure reported |

## 10. Reproduction

From the repository root with the gated exports in place and the untracked configuration file present: `python3 -I src/screen_titles.py summarise`, `python3 -I src/screen_titles.py summarise --criteria v2`, `python3 -I src/screen_titles.py summarise --pool batch2 --criteria v2`, `python3 -I src/fulltext_screen.py inventory`, `python3 -I src/fulltext_screen.py summarise`, `python3 -I src/fulltext_results.py`. Each command rewrites its summary from the decision files and prints it; a figure in this statement that a rerun does not reproduce is wrong and the rerun is right.
