# Full text screening of the pool

Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), disagreements adjudicated by the session's cloud model (Claude, model id claude-fable-5-1, Anthropic), reading the same text the two local reviewers received, on the Lab Director's instruction of 16 October 2026 08:45 local ("take over and help the models"); decisions written through src/session_adjudicate.py; the local adjudicator (gpt-oss:20b) remains the adjudicator of record for the title and abstract stage, criteria v2 plus the full text addendum. Produced by `src/fulltext_screen.py summarise`.

| Text source | Records | Screened by both | Final include | Final exclude | Pending |
|---|---|---|---|---|---|
| conference_abstract | 160 | 160 | 141 | 19 | 0 |
| registry_summary | 84 | 84 | 72 | 12 | 0 |
| ctgov_entry | 56 | 56 | 45 | 11 | 0 |
| epmc_fulltext | 108 | 3 | 2 | 1 | 0 |
| direct_fulltext | 8 | 8 | 6 | 2 | 0 |
| proxy_fulltext | 94 | 94 | 74 | 20 | 0 |
| proxy_partial | 20 | 20 | 7 | 4 | 9 |
| awaiting_fulltext | 3 | 0 | 0 | 0 | 0 |
| already_extracted | 14 | 0 | 0 | 0 | 0 |

| Quantity | Value |
|---|---|
| Screened by both reviewers | 425 of 530 with a text |
| Reviewer 1 include / exclude | 414 / 10 |
| Reviewer 2 include / exclude | 299 / 125 |
| Agreement | 309 of 424 (72.9%) |
| Records with a reviewer row recorded as model error (outside the agreement statistic, adjudicated) | 1 |
| Cohen's kappa | 0.109 (SE 0.071) |
| Disagreements adjudicated | 107 of 116 |
| Final include / exclude / pending | 347 / 69 / 9 |
| Known relevant records with a text, included | 19 of 20 |

| Criterion failed | Reviewer 1 | Reviewer 2 |
|---|---|---|
| D | 7 | 29 |
| P | 4 | 48 |
| I | 3 | 47 |
| O | 3 | 56 |
| T | 3 | 44 |

| Biomarker named as reported (either reviewer), included records | Records |
|---|---|
| hscrp | 207 |
| hba1c | 146 |
| adiponectin | 109 |
| triglycerides | 108 |
| il-6 | 83 |
| homa-ir | 82 |
| alt | 76 |
| crp | 66 |
| ldl | 64 |
| tnf-alpha | 61 |
| total cholesterol | 60 |
| ast | 58 |
| nt-probnp | 58 |
| body fat | 57 |
| blood pressure | 56 |
| leptin | 55 |
| liver fat | 54 |
| lean mass | 52 |
| c-peptide | 50 |
| fasting glucose | 48 |
| fasting insulin | 42 |
| ggt | 42 |
| egfr | 38 |
| homa-beta | 36 |
| hdl | 36 |

Per record decisions, durations, comparators and biomarker maps stay untracked beside the exports (fulltext_decisions_A.csv, fulltext_decisions_B.csv, fulltext_adjudication_002.csv). A known relevant record excluded at full text is listed below for audit.

| key | Title | Reviewer 1 | Reviewer 2 | Adjudicator |
|---|---|---|---|---|
| 1-76 | Anti-inflammatory effects of tirzepatide: a systematic review and meta-analysis | include  | exclude D | exclude D |
