# Submission readiness, 16 October 2026

Written in response to the instruction to close the manuscript today and send it out. This is the
audit that instruction requires, because the answer is no, and the reason has to be checkable rather
than asserted. Head `3512ea4`, fifteen gates green, 524 rows, 76 trials.

## The one line answer

The evidence base is finished. The manuscript is not written. Of the IMRAD sections, Methods and
Results exist; the Introduction, the Discussion, the Conclusions, the Abstract's results and
conclusions, Table 1, every figure and the included studies reference list do not exist in any form.
A registered systematic review cannot be sent out in that state, and three substantive items would
fail peer review on sight even if the prose existed.

## What exists

| Artifact | State | Where |
|---|---|---|
| Analysis pipeline, prespecified | Ported and executing; reproduces the pooled table on all 28 shared biomarkers to within 0.001 | `analysis/M5_AGE_analysis_pipeline.R` |
| Gate chain | Fifteen gates, all green | `scripts/run_gates.sh` |
| Extraction master | 524 rows, 76 trials, all 340 ledger groups terminal | `analysis/data/extraction_master.csv` |
| Risk of bias | 77 RoB 2 records | `analysis/data/risk_of_bias.csv` |
| Methods | Written 16 October, with six protocol deviations disclosed in one place | `manuscript/METHODS_2026-10-16.md` |
| Results | Written, refreshed through the day | `manuscript/RESULTS_2026-10-16.md` |
| Tables 2 to 7 | Written | `manuscript/TABLES_2_to_7_2026-10-16.md` |
| Anchor references | 29, each PubMed verified with a resolvable DOI | `docs/REFERENCES.md` |
| PRISMA counts | Recorded, diagram not drawn | `docs/PRISMA_FLOW.md` |
| Protocol and amendments | Complete and version controlled | `prespecification/` |

## What does not exist

`DRAFT_STATUS.md` lists most of the following as COMPLETE. They are in no reachable location: never
committed to this repository, and absent from Drive, the Obsidian vault, Notion and Spotlight. The
Director's decision of 16 October is to treat them as lost and rewrite from the repository.

| Missing | Blocks submission | Depends on the pooled numbers |
|---|---|---|
| 1. Introduction | Yes | No. Can be written now from `docs/REFERENCES.md` and the protocol |
| 4.3 to 4.10 Discussion | Yes | Partly. Structure and mechanism do not; the figures quoted in them do |
| 4.1 Summary of findings | Yes | Yes |
| 4.2 Favourable to unfavourable ratio | Yes | Yes |
| 5. Conclusions | Yes | Yes |
| Abstract, results and conclusions | Yes | Yes |
| Title page and byline | Yes | No |
| Table 1, the 26 marker inventory | Yes | No. Generable from `analysis/data/biomarker_inventory.csv` |
| Figures 1 to 6 | Yes | Yes. Figures 1, 4 and 5 come only from the prespecified pipeline |
| Included studies reference list | Yes | No. Generable from the master's DOI and PMID fields for all 76 trials |
| PRISMA flow diagram | Yes | No |

## Three substantive items that would fail review even with the prose written

| Item | Why it cannot go out | Owner |
|---|---|---|
| The pooled fibrosis improvement estimate spans minus 807 to plus 807 per cent | A confidence interval that wide is not an estimate. It is decision D-X6, open since 15 October, and it appears in Table 2 as though it were a result | Director |
| Fan 2013 remains in the corpus with an unresolved duplication | Its post treatment ALT means are the same two values, to two decimals, that a later paper reports for a different drug in the same population. The ledger records that its rows must be reviewed before the analysis is final. Submitting a review that pools a trial under an open integrity question is the kind of thing that is found after publication | Director |
| Four biomarkers appear in the synthesis table with k equal to one | BMD, ICAM-1, YKL-40 and MR-proANP are presented with an estimate and a confidence interval that are a single trial's. A reader takes a row in a meta-analysis table for synthesis | Director, on presentation |

## Decisions still open, eleven

Several change the pooled numbers, which is why the number dependent prose cannot be written first and
then corrected. Writing it twice is how errors enter.

| Decision | Changes numbers |
|---|---|
| D-X6, the fibrosis interval | Yes |
| D-X1 and its three adjacent holds, 16 held groups | Yes |
| A6 held populations, 13 groups | Yes |
| D-X7, DPP-4 comparators | Yes |
| Fan 2013 duplication | Yes |
| Trial level backfill for the retatrutide parent publications | Yes, and the PRISMA identification count |
| BNP inventory key | Possibly |
| Dutour 2016 leptin standard error | Yes, one row |
| Master trailing zero repair | No, a tolerance only |
| Registered title against the method | No, but it is a registration consistency question and must be settled before a journal sees it |
| The six protocol deviations now disclosed in Methods 2.12 | No, but each needs approval to stand as written |

## What can honestly be done today

In descending order of value, all of it mine to do and none of it requiring a decision:

1. Finish the pipeline run: the weight adjusted meta regression now has a recorded estimator fallback
   and is executing for the first time, which yields Q3, H1 and Figures 1, 4 and 5.
2. Write the Introduction, which depends on no pooled number.
3. Generate Table 1 from the biomarker inventory and the included studies reference list from the
   master, both mechanical.
4. Draw the PRISMA diagram from the recorded counts.
5. Write the Discussion sections whose argument does not turn on a figure that may move.

That leaves the Abstract's results, Discussion 4.1 and 4.2, and the Conclusions, which are the four
pieces that must be written once, after the decisions land.

## The honest schedule

With the eleven decisions cleared, the remaining work is one to two sessions and the package is
submission ready. Without them it stops at roughly eighty per cent, with the fibrosis interval and
the Fan 2013 question still in the manuscript. The constraint is not throughput.

A complete internal draft for the Director's own revision is a different and achievable target, and
is what "close it today" can honestly mean. It would carry the gaps above as a marked register rather
than as silence.

---

## Addendum, 19 October 2026

This audit is kept as written, dated to the sixteenth. The live status document is
`manuscript/DRAFT_STATUS.md`, rewritten on the nineteenth to a rule that stops it asserting work
that is not on disk. Four rows of the tables above have changed, and three of the changes are
defects this audit did not find because it accepted a claim rather than checking it.

| Row above | State on 19 October |
| --- | --- |
| Gate chain, fifteen gates, all green | Twenty one gates, all green. Six were added: PRISMA reconciliation, biomarker inventory coverage, Table 2 reproduction, composite interval coherence, the citation record, and the figure set. The first three existed and were reachable only by being remembered |
| Every figure does not exist | Figures 1 to 6 and S1 exist and are version controlled. They had never existed because the pipeline requested a graphics device that cannot load on this machine and warns instead of failing; the three it drew went into one overwritten file in the repository root. `docs/FIGURES.md` records the failure and the three changes that prevent it |
| Anchor references, 29, each PubMed verified with a resolvable DOI | This was the claim, not the fact. The check now exists, `src/anchor_references_check.py`. Seven of the 29 recorded an issue or page range that points at the wrong article in the right journal, two of those also a wrong year and volume, one a wrong author initial. All 29 rows have been rebuilt from the registry and all 29 now verify |
| Included studies reference list does not exist | It exists, 76 trials, 73 identifiers verified and 3 with no identifier to resolve, each written up. Eight wrong first authors and one wrong year were corrected at the extraction spec level |

Two findings of the nineteenth are not in the tables above at all, because neither was visible to a
reader of the outputs.

The composite interval was built around a quantity other than the estimate it qualified. For one
receptor class under equal weighting the table printed an estimate outside its own confidence
interval. The cause was a bias corrected and accelerated interval computed for a statistic that is
not a deterministic function of its resample. Both intervals are now computed and reported, the
percentile interval as primary and the registered BCa alongside, and a gate fails the chain on an
interval that does not contain its estimate.

The per class composite was computed over every biomarker that pooled in the class, which is the set
`prespecification/nbais_inclusion_rule.md` was written on 15 October to prevent: it names eleven
markers and excludes ten, among them glucagon by name, "because most of the defective markers are
ones the drug moves strongly". Applying the rule changes what the review can say about question 4.
Of the four receptor classes, one supports a composite over nine of the eleven markers, one over
three, one over a single marker and one over none, and one of the six pairwise class contrasts
remains computable. That is a narrower claim than the figures of the sixteenth implied, and it is
the claim the prespecification licenses.

The schedule above still holds: the constraint is the Director's decisions, not throughput.
