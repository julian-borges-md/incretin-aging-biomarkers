# Title and abstract screening of the Embase clinical trial registry records and the CENTRAL records not in the Embase export

Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), a third agent adjudicating disagreements. Models are named only in the untracked configuration file. Criteria version v2. Produced by `src/screen_titles.py summarise`.

| Quantity | Value |
|---|---|
| Records in pool | 251 |
| Pool composition | embase_registry 51; central 200 |
| Screened by both reviewers | 251 |
| Reviewer 1 include / exclude | 182 / 69 |
| Reviewer 2 include / exclude | 144 / 107 |
| Agreement | 199 of 251 (79.3%) |
| Cohen's kappa | 0.556 (SE 0.055) |
| Disagreements adjudicated | 52 of 52 |
| Final include / exclude / pending | 185 / 66 / 0 |
| Records already known relevant, included by screening | 2 of 3 |

| Criterion failed | Reviewer 1 | Reviewer 2 |
|---|---|---|
| D | 46 | 31 |
| P | 22 | 57 |
| I | 19 | 38 |
| O | 0 | 23 |
| T | 6 | 33 |

Per record decisions and reasons stay untracked beside the export (decisions_A_batch2_v2.csv, decisions_B_batch2_v2.csv, adjudication_002_batch2_v2.csv). A known relevant record excluded by screening is listed below for audit.

| n | Title | Reviewer 1 | Reviewer 2 | Adjudicator |
|---|---|---|---|---|
| 232 | Liraglutide ameliorates beta-cell function, alleviates oxidative stress and inhibits low g | include | exclude | exclude |
