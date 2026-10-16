# Title and abstract screening of the Embase export

Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), a third agent adjudicating disagreements. Models are named only in the untracked configuration file. Criteria version v1. Produced by `src/screen_titles.py summarise`.

| Quantity | Value |
|---|---|
| Records in pool | 659 |
| Screened by both reviewers | 659 |
| Reviewer 1 include / exclude | 333 / 326 |
| Reviewer 2 include / exclude | 235 / 424 |
| Agreement | 543 of 659 (82.4%) |
| Cohen's kappa | 0.649 (SE 0.030) |
| Disagreements adjudicated | 116 of 116 |
| Final include / exclude / pending | 338 / 321 / 0 |
| Records already known relevant, included by screening | 32 of 40 |

| Criterion failed | Reviewer 1 | Reviewer 2 |
|---|---|---|
| D | 292 | 289 |
| P | 38 | 192 |
| I | 31 | 106 |
| O | 7 | 94 |
| T | 15 | 97 |

Per record decisions and reasons stay untracked beside the export (decisions_A.csv, decisions_B.csv, adjudication_002.csv). A known relevant record excluded by screening is listed below for audit.

| n | Title | Reviewer 1 | Reviewer 2 | Adjudicator |
|---|---|---|---|---|
| 76 | Anti-inflammatory effects of tirzepatide: a systematic review and meta-analysis | exclude | exclude |  |
| 244 | Total and H-specific growth/differentiation factor 15 levels are unaffected by liraglutide | exclude | exclude |  |
| 330 | Liraglutide ameliorates oxidized LDL-induced endothelial dysfunction by GLP-1R-dependent d | exclude | exclude |  |
| 446 | Effect of vildagliptin combined with liraglutide on bmi, hbalc and fbg in diabetic patient | exclude | exclude |  |
| 548 | Circulating adiponectin levels in type 2 diabetes mellitus patients with or without non-al | exclude | exclude |  |
| 568 | Vildagliptin vs liraglutide as a second-line therapy switched from sitagliptin-based regim | exclude | exclude |  |
| 595 | Greater efficacy and improved endothelial dysfunction in untreated type 2 diabetes with li | exclude | exclude |  |
| 616 | Addition of liraglutide in patients with Type2 diabetes well controlled on metformin monot | exclude | exclude |  |
