# Title and abstract screening of the Embase export

Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), a third agent adjudicating disagreements. Models are named only in the untracked configuration file. Criteria version v2. Produced by `src/screen_titles.py summarise`.

## Rescreen of the records excluded under criteria v1

| Quantity | Value |
|---|---|
| Records finally excluded under v1 | 321 |
| Rescreened by both reviewers under v2 | 321 |
| Included by either reviewer under v2 (rescued, to full text) | 24 |
| Excluded by both reviewers under v2 | 297 |
| Agreement on the rescreened set | 299 of 321 (93.1%) |
| Set going to full text: v1 includes plus rescued | 338 + 24 = 362 |
| Known relevant records among the rescreened | 8: rescued 4, still excluded 4 |

| Criterion failed in the rescreen | Reviewer 1 | Reviewer 2 |
|---|---|---|
| D | 269 | 269 |
| P | 22 | 182 |
| I | 29 | 69 |
| O | 1 | 21 |
| T | 5 | 33 |

| n | Title | Reviewer 1 | Reviewer 2 |
|---|---|---|---|
| 244 | Total and H-specific growth/differentiation factor 15 levels are unaffected by liraglutide | exclude D | exclude DT |
| 330 | Liraglutide ameliorates oxidized LDL-induced endothelial dysfunction by GLP-1R-dependent d | exclude D | exclude DPT |
| 446 | Effect of vildagliptin combined with liraglutide on bmi, hbalc and fbg in diabetic patient | exclude I | exclude I |
| 568 | Vildagliptin vs liraglutide as a second-line therapy switched from sitagliptin-based regim | exclude I | exclude I |

Per record decisions stay untracked beside the export (decisions_A_v2.csv, decisions_B_v2.csv).
