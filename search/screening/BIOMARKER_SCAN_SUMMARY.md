# Biomarker lexicon scan of the full text screen inputs

One regular expression per inventory biomarker (criterion O), case insensitive, run over the exact text each reviewer received (530 records with a text). Produced by `src/biomarker_scan.py`; per record counts are in the untracked `biomarker_scan_2026-10-16.csv`. A mention shows the marker is discussed, not that a result is reported.

| Biomarker | conference_abstract | registry_summary | ctgov_entry | epmc_fulltext | direct_fulltext | proxy_fulltext | proxy_partial | Any |
|---|---|---|---|---|---|---|---|---|
| crp | 107 | 59 | 37 | 79 | 7 | 77 | 11 | 377 |
| il6 | 17 | 4 | 31 | 34 | 4 | 24 | 11 | 125 |
| tnf | 17 | 17 | 23 | 36 | 4 | 26 | 10 | 133 |
| gdf15 | 9 | 0 | 2 | 5 | 0 | 3 | 1 | 20 |
| ykl40 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 3 |
| icam1 | 4 | 0 | 0 | 6 | 0 | 2 | 1 | 13 |
| leptin | 16 | 11 | 15 | 21 | 1 | 24 | 3 | 91 |
| adiponectin | 40 | 16 | 15 | 28 | 4 | 28 | 3 | 134 |
| insulin | 24 | 15 | 9 | 38 | 2 | 31 | 3 | 122 |
| homa_ir | 11 | 1 | 9 | 25 | 5 | 22 | 2 | 75 |
| homa_beta | 4 | 0 | 0 | 5 | 2 | 3 | 1 | 15 |
| cpeptide | 6 | 1 | 16 | 13 | 2 | 13 | 1 | 52 |
| glucagon | 20 | 9 | 14 | 51 | 4 | 30 | 5 | 133 |
| glucose | 44 | 31 | 32 | 67 | 4 | 50 | 7 | 235 |
| hba1c | 93 | 59 | 45 | 94 | 6 | 73 | 14 | 384 |
| liver_fat | 11 | 6 | 11 | 22 | 3 | 19 | 2 | 74 |
| alt | 10 | 7 | 15 | 33 | 2 | 23 | 1 | 91 |
| ast | 5 | 8 | 12 | 26 | 2 | 21 | 0 | 74 |
| ggt | 1 | 2 | 8 | 6 | 2 | 9 | 0 | 28 |
| mash | 19 | 4 | 4 | 20 | 2 | 19 | 2 | 70 |
| tg | 50 | 32 | 30 | 78 | 5 | 48 | 5 | 248 |
| ldl | 33 | 31 | 18 | 71 | 5 | 45 | 5 | 208 |
| tc | 21 | 24 | 14 | 46 | 3 | 38 | 1 | 147 |
| lean_mass | 2 | 4 | 5 | 13 | 2 | 15 | 1 | 42 |
| body_fat | 5 | 8 | 9 | 30 | 3 | 37 | 2 | 94 |
| vat | 9 | 12 | 13 | 25 | 4 | 30 | 3 | 96 |
| bmd | 0 | 3 | 2 | 3 | 0 | 1 | 1 | 10 |
| egfr | 8 | 9 | 18 | 42 | 1 | 27 | 4 | 109 |
| heart_rate | 7 | 12 | 7 | 21 | 1 | 16 | 3 | 67 |
| bp | 64 | 53 | 30 | 81 | 6 | 66 | 15 | 315 |
| ntprobnp | 10 | 0 | 11 | 10 | 0 | 20 | 1 | 52 |
| mrproanp | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 |
| epigenetic_age | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 3 |

## Audit of the reviewers' biomarkers_reported field (311 records screened by both reviewers so far)

Named without a mention: a marker named by either reviewer whose pattern finds nothing in the text given to them (a naming error, a synonym outside the lexicon, or a marker the lexicon does not cover). Mentioned, not named: a marker with 3 or more mentions that neither reviewer named (a possible omission, or a marker discussed without a result).

| Biomarker | Named without a mention (records) | Mentioned, not named (records) |
|---|---|---|
| crp | 23 | 0 |
| il6 | 25 | 0 |
| tnf | 9 | 1 |
| gdf15 | 6 | 0 |
| ykl40 | 4 | 0 |
| icam1 | 9 | 0 |
| leptin | 3 | 2 |
| adiponectin | 5 | 1 |
| insulin | 23 | 1 |
| homa_ir | 28 | 2 |
| homa_beta | 13 | 0 |
| cpeptide | 11 | 0 |
| glucagon | 2 | 1 |
| glucose | 13 | 9 |
| hba1c | 3 | 38 |
| liver_fat | 10 | 3 |
| alt | 14 | 0 |
| ast | 7 | 1 |
| ggt | 5 | 1 |
| mash | 0 | 23 |
| tg | 2 | 7 |
| ldl | 6 | 8 |
| tc | 14 | 0 |
| lean_mass | 12 | 1 |
| body_fat | 13 | 1 |
| vat | 4 | 3 |
| bmd | 3 | 0 |
| egfr | 4 | 5 |
| heart_rate | 4 | 5 |
| bp | 2 | 50 |
| ntprobnp | 16 | 0 |
| records with at least one flag | 114 | 112 |

| Reviewer name outside the lexicon (not an inventory biomarker, or a synonym to add to the alias map) | Records |
|---|---|
| hdl | 37 |
| waist circumference | 21 |
| hdl cholesterol | 20 |
| body weight | 14 |
| bmi | 14 |
| lipids | 13 |
| bnp | 13 |
| pai-1 | 12 |
| il-1β | 11 |
| proinsulin | 10 |
| free fatty acids | 10 |
| mcp-1 | 10 |
| vldl | 9 |
| ffa | 9 |
| pro-c3 | 8 |
| creatinine | 8 |
| non-hdl cholesterol | 7 |
| resistin | 7 |
| k-18 | 6 |
| fgf21 | 6 |
| mmp-9 | 6 |
| fibrinogen | 6 |
| ghrelin | 6 |
| vcam | 6 |
| proinsulin/c-peptide | 5 |
