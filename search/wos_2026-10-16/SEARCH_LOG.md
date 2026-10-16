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

Pending the Director's confirmation of the download (set 4, 317 records, RIS through Export, Other File Formats, Full Record). The file will be saved as `search/wos_2026-10-16/wos_317.ris` (gitignored, licensed content) with TY and ER counts and SHA-256 recorded here, and registered in `src/dedup_embase.py` SOURCES for overlap with Embase and CENTRAL and recall against the extracted corpus and the adopted list.
