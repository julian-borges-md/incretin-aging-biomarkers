# Web of Science Core Collection search, 16 October 2026

Run at 08:20 to 08:35 local (12:20 to 12:35 UTC) through the Boston University EZproxy route, `https://ezproxy.bu.edu/login?url=https://www.webofscience.com/wos/woscc/advanced-search`, hostname on arrival and throughout `www-webofscience-com.ezproxy.bu.edu` (the session was already authenticated; no sign in step was shown and no personal Clarivate account was used). Database: Web of Science Core Collection, editions: All, no date, language or document type limits. The strategy is the translation of the Embase lines drafted in `search/wos_DRAFT/WOS_STRATEGY_DRAFT.md` (b589543); the translation table there is the record of every difference from the Embase string. Each line was typed into the Query Preview box of the Advanced Search page and run; line 4 was produced with the Combine Sets control (sets 1 to 3 ticked, AND), because the typed form `#1 AND #2 AND #3` was cleared by the page without running. Web of Science displays the combination as `#3 AND #2 AND #1`.

## Lines and counts

| # | Query | Hits |
|---|---|---|
| 1 | `TS=(exenatide OR liraglutide OR dulaglutide OR semaglutide OR tirzepatide OR retatrutide OR survodutide OR mazdutide OR pemvidutide OR cotadutide OR efinopegdutide)` | 22,770 |
| 2 | `TS=("c reactive protein" OR "c-reactive protein" OR CRP OR hsCRP OR "hs-CRP" OR "interleukin 6" OR "interleukin-6" OR IL6 OR "IL-6" OR "tumor necrosis factor" OR "tumour necrosis factor" OR TNF OR "TNF-alpha" OR adiponectin OR leptin OR "growth differentiation factor 15" OR GDF15 OR "GDF-15")` | 807,756 |
| 3 | `TS=(random* OR "randomised controlled trial" OR "randomized controlled trial" OR placebo OR "double blind" OR "double-blind" OR "controlled trial")` | 3,445,325 |
| 4 | `#1 AND #2 AND #3` (Combine Sets, AND; displayed as `#3 AND #2 AND #1`) | 317 |

## Export

Set 4 exported at 08:29 local as RIS, Full Record, records 1 to 317 (Export, RIS (other reference software)); Chrome saved it as `savedrecs.ris`, copied unchanged to `search/wos_2026-10-16/wos_317.ris` (gitignored, licensed content).

| Gate | Value |
|---|---|
| TY records | 317 (the first TY follows a UTF-8 byte order mark; the parsers strip it) |
| ER records | 317 (Web of Science writes `ER  -` without a trailing space) |
| SHA-256 | `844f31118a3495a63892f8562f49ec8d52ab1f93cbade3b9a9051da3b12fa259` |
| Size | 1,292,966 bytes |
| With DOI | 312 |
| Record type | JOUR 317; no accession numbers in the RIS export (Web of Science puts UT in its tab delimited format only) |
| Publication years | 2022: 28, 2023: 26, 2024: 42, 2025: 47, 2026: 51 (earlier years in the file) |

## Overlap and recall (`python3 -I src/dedup_embase.py wos`, output `RECALL_AND_DEDUP.md` beside this log)

| Quantity | Value |
|---|---|
| Also in the Embase export | 196 (189 by DOI, 7 by normalised title) |
| Also in the CENTRAL export | 135 (132 by DOI, 3 by title) |
| In neither | 99, screened as pool `batch3` (`src/screen_titles.py --pool batch3 --criteria v2`, queued as work/screen_chain4.sh behind the full text chains) |
| Recall, extracted corpus | 8 of 11 |
| Recall, adopted reference list | 5 of 29 |
| Recall, Alrasheed 2026 list | 26 of 38 |

Union across the three databases, from the three recall tables as the script writes them (item counts are the script's, which include the Meyhofer liver substudy as a twelfth extracted item and 39 Alrasheed rows):

| Known set | Items | Embase | CENTRAL | Web of Science | Any of the three | None |
|---|---|---|---|---|---|---|
| extracted | 12 | 10 | 9 | 9 | 10 | 2 |
| references | 30 | 9 | 5 | 6 | 10 | 20 |
| Alrasheed 2026 | 39 | 29 | 27 | 27 | 31 | 8 |

Web of Science retrieves no known item that Embase or CENTRAL missed; its contribution is the 99 unscreened records. The items retrieved by none of the three (Meyhofer 2026 liver substudy, Wägner 2019, Guarnotta 2021, Lambadiari 2018 and 2021, le Roux 2017, Liang 2013, Liu 2019, Santilli 2017, and the reference list items that are reviews, consensus reports or trials reporting the biomarker incidentally) mark the recall ceiling of a biomarker term strategy; they enter through the adopted list as a documented second source.
