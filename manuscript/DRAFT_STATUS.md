# M5-AGE Draft Status

Updated: 2026-10-19

## How to read this file

The version of this file dated 14 October recorded a title page, an abstract, seven discussion
sections and a verified reference list as COMPLETE. None of those files exists in the repository and
the git history shows that only `DRAFT_STATUS.md`, `RESULTS_*.md` and `TABLES_*.md` were ever
committed from the manuscript directory. The prose was written in a session and never written to
disk, and a status document asserted it for five days.

The rule that follows from that, and that this file now obeys: a section is recorded here as present
only when a file in `manuscript/` contains it, and every row names that file. A row with no file is
ABSENT however complete the text once was.

## Present in the repository

| Section | File | State |
| --- | --- | --- |
| 1. Introduction | `INTRODUCTION_2026-10-19.md` | Rewritten from the repository, 1393 words |
| 2.1 to 2.12 Methods, including the deviation register | `METHODS_2026-10-16.md` | Complete, 2.11 extended on 19 October to the twenty one gate chain |
| 3. Results narrative | `RESULTS_2026-10-16.md` | Written against the 16 October pooling; numbers need the 19 October rerun reconciled through `src/results_numbers_check.py` |
| 4.10 Strengths and limitations | `DISCUSSION_4.10_limitations_2026-10-19.md` | Rewritten from the provenance record, 1675 words |
| Tables 2 to 7 | `TABLES_2_to_7_2026-10-16.md` | Populated; Table 7 records that the network analysis was not run and why |
| Table 1, the biomarker inventory | `analysis/output/table1_biomarker_inventory.md` | Generated, 36 entries over 14 hallmark domains |
| Figures 1 to 6 and S1 | `analysis/output/figure*.pdf` and `.png` | First produced 19 October; mapping and captions in `docs/FIGURES.md` |
| Included studies reference list | `analysis/output/included_studies.md` | 76 trials, 73 identifiers verified against Europe PMC or Crossref, 3 with no identifier to resolve, each written up in `docs/CITATION_TRIAGE.md` |

## Absent

| Section | What it needs |
| --- | --- |
| Title page and byline | The registered title against the method actually used is a Director decision, not a writing task |
| Abstract: Background, Objectives, Methods | Rewriting; the earlier text is not in the repository |
| Abstract: Results and Conclusions | The pooled numbers, which now exist, and the Director's H1 reporting decision |
| 4.1 Summary of findings | The Results reconciliation and the H1 decision |
| 4.2 Favourable to unfavourable ratio | Same |
| 4.3 to 4.9 | Rewriting from the repository. The earlier text is not on disk. Three of these sections rested on claims that have since been withdrawn and may not be reinstated without new data: the retatrutide hepatic plateau, the GDF-15 class differential, and the answerability of Q2 |
| 5. Conclusions | The Results and the Director's decisions |
| Anchor reference list, 29 items | `docs/REFERENCES.md` exists and two of its annotations assert withdrawn claims; the list needs the same identifier check the 76 included studies have had |

## Critical path

| Step | State |
| --- | --- |
| 1. Extraction into `analysis/data/extraction_master.csv` | Done, 524 rows, 76 trials |
| 2. Run `analysis/M5_AGE_analysis_pipeline.R` | Done, 19 October, 48 outputs including the figures |
| 3. Reconcile the Results narrative against the rerun | Done, 19 October: 22 pooled figures cited, none mismatching, and figure callouts added |
| 4. Director decisions D-S1 to D-S7, D-X1, D-X6, D-X7, A6 and the 2.12 deviations | Outstanding, reserved to the Director |
| 5. Write 4.1 to 4.9, Conclusions, Abstract, title page | Blocked on 3 and 4 |
| 6. Self critique, three passes | Not started |
| 7. Submit | Not started |

## What changed on 19 October

| Change | Consequence for the draft |
| --- | --- |
| Eight bibliographic corrections and four author names supplied, all at the spec level | The reference list now names the right paper for every trial that has one |
| The composite interval method was corrected | `table5_nbais.csv` previously printed an estimate outside its own interval for one class; any Results sentence quoting a composite interval must be rewritten from the new table |
| Three figure axis labels said Hedges' g on a percent change scale | Any figure callout or Discussion sentence describing composite or pooled effects in standard deviation units is wrong by roughly a factor of twenty and must be rewritten |
| The figures exist for the first time | The Results narrative now carries callouts to Figures 1 to 6 and S1, added 19 October; the Discussion sections that are still to be written need them too |
| The receptor class signature has no triple agonist node | Within that class every biomarker is carried by a single trial after the dose collapse, so nothing pools. The 14 October note claiming the triple agonist node is populated for four domains is true of the extraction and false of the pooled analysis, and the Discussion must say which |

## Retatrutide data position

Available: weight (-24.2% ph2, -15.3% ph3), HbA1c (-2.02% ph2, -1.94% ph3), liver fat (-82.4% at
12 mg, 86% reaching normal), SBP (-6.8), TG (-40.9), LDL (-13.1), DXA body composition (Coskun 2025
LDE).

Absent: GDF-15, hsCRP, IL-6, adiponectin, leptin, epigenetic clocks, biopsy confirmed MASH histology.

Consequence: the triple agonist arm contributes rows in the metabolic, hepatic imaging, vascular and
lipid domains and no pooled estimate in any of them, because each biomarker within that class rests
on one trial after the shared control collapse. The composite is therefore not computed for the
class at all, which the figures now show as an empty column rather than as an absent one.
