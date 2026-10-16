# Biomarker lexicon scan of the full text screen inputs

One regular expression per inventory biomarker (criterion O), case insensitive, run over the exact text each reviewer received (553 records with a text). Produced by `src/biomarker_scan.py`; per record counts are in the untracked `biomarker_scan_2026-10-16.csv`. A mention shows the marker is discussed, not that a result is reported.

| Biomarker | conference_abstract | registry_summary | ctgov_entry | epmc_fulltext | direct_fulltext | proxy_fulltext | proxy_partial | Any |
|---|---|---|---|---|---|---|---|---|
| crp | 106 | 59 | 37 | 86 | 7 | 77 | 14 | 386 |
| il6 | 17 | 4 | 31 | 39 | 4 | 25 | 11 | 131 |
| tnf | 17 | 17 | 23 | 41 | 4 | 26 | 11 | 139 |
| gdf15 | 9 | 0 | 2 | 6 | 0 | 3 | 1 | 21 |
| ykl40 | 1 | 0 | 0 | 2 | 0 | 1 | 1 | 5 |
| icam1 | 4 | 0 | 0 | 8 | 0 | 2 | 1 | 15 |
| leptin | 16 | 11 | 15 | 27 | 1 | 24 | 4 | 98 |
| adiponectin | 39 | 16 | 15 | 35 | 4 | 27 | 5 | 141 |
| insulin | 24 | 15 | 9 | 42 | 2 | 30 | 3 | 125 |
| homa_ir | 11 | 1 | 9 | 24 | 5 | 21 | 2 | 73 |
| homa_beta | 4 | 0 | 0 | 5 | 2 | 4 | 2 | 17 |
| cpeptide | 6 | 1 | 16 | 13 | 2 | 14 | 1 | 53 |
| glucagon | 19 | 9 | 14 | 57 | 4 | 29 | 5 | 137 |
| glucose | 43 | 31 | 32 | 69 | 4 | 50 | 10 | 239 |
| hba1c | 93 | 59 | 45 | 103 | 6 | 73 | 18 | 397 |
| liver_fat | 10 | 6 | 11 | 27 | 3 | 18 | 3 | 78 |
| alt | 9 | 7 | 15 | 36 | 2 | 22 | 1 | 92 |
| ast | 4 | 8 | 12 | 28 | 2 | 20 | 0 | 74 |
| ggt | 1 | 2 | 8 | 7 | 2 | 8 | 0 | 28 |
| mash | 18 | 4 | 4 | 22 | 2 | 18 | 7 | 75 |
| tg | 50 | 32 | 30 | 86 | 5 | 48 | 5 | 256 |
| ldl | 33 | 31 | 18 | 76 | 5 | 45 | 5 | 213 |
| tc | 21 | 24 | 14 | 49 | 3 | 39 | 1 | 151 |
| lean_mass | 2 | 4 | 5 | 17 | 2 | 15 | 1 | 46 |
| body_fat | 5 | 8 | 9 | 35 | 3 | 37 | 2 | 99 |
| vat | 9 | 12 | 13 | 29 | 4 | 30 | 3 | 100 |
| bmd | 0 | 3 | 2 | 3 | 0 | 1 | 1 | 10 |
| egfr | 8 | 9 | 18 | 44 | 1 | 27 | 4 | 111 |
| heart_rate | 7 | 12 | 7 | 23 | 1 | 16 | 4 | 70 |
| bp | 63 | 53 | 30 | 89 | 6 | 66 | 18 | 325 |
| ntprobnp | 10 | 0 | 11 | 12 | 0 | 20 | 1 | 54 |
| mrproanp | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 |
| epigenetic_age | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 3 |

## Audit of the reviewers' biomarkers_reported field (553 records screened by both reviewers so far)

Named without a mention: a marker named by either reviewer whose pattern finds nothing in the text given to them (a naming error, a synonym outside the lexicon, or a marker the lexicon does not cover). Mentioned, not named: a marker with 3 or more mentions that neither reviewer named (a possible omission, or a marker discussed without a result).

| Biomarker | Named without a mention (records) | Mentioned, not named (records) |
|---|---|---|
| crp | 52 | 13 |
| il6 | 75 | 5 |
| tnf | 51 | 13 |
| gdf15 | 61 | 2 |
| ykl40 | 51 | 0 |
| icam1 | 56 | 0 |
| leptin | 44 | 10 |
| adiponectin | 46 | 7 |
| insulin | 51 | 17 |
| homa_ir | 93 | 10 |
| homa_beta | 68 | 2 |
| cpeptide | 56 | 5 |
| glucagon | 28 | 18 |
| glucose | 30 | 52 |
| hba1c | 7 | 109 |
| liver_fat | 79 | 10 |
| alt | 80 | 11 |
| ast | 64 | 12 |
| ggt | 64 | 3 |
| mash | 16 | 52 |
| tg | 19 | 38 |
| ldl | 26 | 42 |
| tc | 49 | 25 |
| lean_mass | 89 | 5 |
| body_fat | 79 | 15 |
| vat | 38 | 27 |
| bmd | 46 | 1 |
| egfr | 41 | 40 |
| heart_rate | 20 | 16 |
| bp | 7 | 141 |
| ntprobnp | 50 | 5 |
| mrproanp | 7 | 0 |
| epigenetic_age | 3 | 0 |
| records with at least one flag | 237 | 288 |

| Reviewer name outside the lexicon (not an inventory biomarker, or a synonym to add to the alias map) | Records |
|---|---|
| hdl | 50 |
| bmi | 47 |
| waist circumference | 34 |
| body weight | 30 |
| hdl cholesterol | 22 |
| lipids | 21 |
| hdl-c | 19 |
| mcp-1 | 19 |
| pai-1 | 18 |
| uacr | 17 |
| bnp | 17 |
| nt- | 15 |
| il-1β | 14 |
| proinsulin | 14 |
| free fatty acids | 13 |
| resistin | 13 |
| ffa | 12 |
| resting hear | 12 |
| pro-c3 | 12 |
| vldl | 9 |
| il-10 | 9 |
| creatinine | 9 |
| fgf21 | 9 |
| k-18 | 9 |
| fib-4 | 8 |
