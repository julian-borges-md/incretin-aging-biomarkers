# Full text screening of the pool

Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), disagreements adjudicated by the session's cloud model (Claude, model id claude-fable-5-1, Anthropic), reading the same text the two local reviewers received, on the Lab Director's instruction of 16 October 2026 08:45 local ("take over and help the models"); decisions written through src/session_adjudicate.py; the local adjudicator (gpt-oss:20b) remains the adjudicator of record for the title and abstract stage, criteria v2 plus the full text addendum. Produced by `src/fulltext_screen.py summarise`.

| Text source | Records | Screened by both | Final include | Final exclude | Pending |
|---|---|---|---|---|---|
| conference_abstract | 158 | 158 | 139 | 19 | 0 |
| registry_summary | 84 | 84 | 72 | 12 | 0 |
| ctgov_entry | 56 | 56 | 45 | 11 | 0 |
| epmc_fulltext | 120 | 120 | 92 | 28 | 0 |
| direct_fulltext | 8 | 8 | 6 | 2 | 0 |
| proxy_fulltext | 94 | 94 | 73 | 21 | 0 |
| proxy_partial | 33 | 33 | 8 | 25 | 0 |
| awaiting_fulltext | 3 | 0 | 0 | 0 | 0 |
| already_extracted | 20 | 5 | 5 | 0 | 0 |

| Quantity | Value |
|---|---|
| Screened by both reviewers | 558 of 553 with a text |
| Reviewer 1 include / exclude | 536 / 20 |
| Reviewer 2 include / exclude | 389 / 167 |
| Agreement | 409 of 556 (73.6%) |
| Records with a reviewer row recorded as model error (outside the agreement statistic, adjudicated) | 2 |
| Cohen's kappa | 0.160 (SE 0.059) |
| Disagreements adjudicated | 149 of 149 |
| Final include / exclude / pending | 440 / 118 / 0 |
| Known relevant records with a text, included | 26 of 28 |

| Criterion failed | Reviewer 1 | Reviewer 2 |
|---|---|---|
| D | 16 | 50 |
| P | 4 | 57 |
| I | 5 | 63 |
| O | 4 | 72 |
| T | 3 | 57 |

| Biomarker named as reported (either reviewer), included records | Records |
|---|---|
| hscrp | 273 |
| hba1c | 197 |
| adiponectin | 149 |
| triglycerides | 148 |
| il-6 | 131 |
| homa-ir | 130 |
| alt | 128 |
| ldl | 109 |
| body fat | 106 |
| ast | 103 |
| liver fat | 97 |
| lean mass | 92 |
| total cholesterol | 91 |
| tnf-alpha | 91 |
| leptin | 89 |
| crp | 81 |
| c-peptide | 81 |
| fasting glucose | 80 |
| nt-probnp | 80 |
| ggt | 78 |
| fasting insulin | 75 |
| blood pressure | 74 |
| gdf-15 | 67 |
| egfr | 67 |
| homa-beta | 67 |

Per record decisions, durations, comparators and biomarker maps stay untracked beside the exports (fulltext_decisions_A.csv, fulltext_decisions_B.csv, fulltext_adjudication_002.csv). A known relevant record excluded at full text is listed below for audit.

| key | Title | Reviewer 1 | Reviewer 2 | Adjudicator |
|---|---|---|---|---|
| 1-76 | Anti-inflammatory effects of tirzepatide: a systematic review and meta-analysis | include  | exclude D | exclude D |
| 1-441 | Use of flash glucose-sensing technology in patients with type 2 diabetes treated with lira | include  | exclude T | exclude T |
