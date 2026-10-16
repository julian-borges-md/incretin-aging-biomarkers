# Web of Science Core Collection: strategy draft, 16 October 2026 (NOT RUN)

No Web of Science string exists in the protocol, the repository or the vault (`docs/PRISMA_FLOW.md`, corrected 15 October). This draft translates the Embase lines (`search/embase_2026-10-15/SEARCH_LOG.md`) into Web of Science advanced search syntax the same way the CENTRAL strategy was translated (`search/central_2026-10-15/SEARCH_LOG.md`), with every difference listed. It is a proposal for the Director; nothing has been executed, and the counts column stays empty until a run through the BU EZproxy route (`https://ezproxy.bu.edu/login?url=https://www.webofscience.com/wos/woscc/advanced-search`, hostname `www-webofscience-com.ezproxy.bu.edu`; never the InCommon path).

## Lines

| # | Query (Core Collection, all editions, no date limit) | Hits |
|---|---|---|
| 1 | `TS=(exenatide OR liraglutide OR dulaglutide OR semaglutide OR tirzepatide OR retatrutide OR survodutide OR mazdutide OR pemvidutide OR cotadutide OR efinopegdutide)` | |
| 2 | `TS=("c reactive protein" OR "c-reactive protein" OR CRP OR hsCRP OR "hs-CRP" OR "interleukin 6" OR "interleukin-6" OR IL6 OR "IL-6" OR "tumor necrosis factor" OR "tumour necrosis factor" OR TNF OR "TNF-alpha" OR adiponectin OR leptin OR "growth differentiation factor 15" OR GDF15 OR "GDF-15")` | |
| 3 | `TS=(random* OR "randomised controlled trial" OR "randomized controlled trial" OR placebo OR "double blind" OR "double-blind" OR "controlled trial")` | |
| 4 | `#1 AND #2 AND #3` | |

## Translation table

| Embase element | Web of Science element | Reason |
|---|---|---|
| Emtree `/exp` drug terms, indexing only | `TS=` (title, abstract, author keywords, Keywords Plus) free text for all eleven names | Web of Science has no controlled vocabulary; TS is the only route |
| Emtree `/exp` biomarker terms | `TS=` free text with the same abbreviation list used for CENTRAL line 11 | Same reason; the abbreviation list is the only vocabulary beyond the Emtree preferred terms, declared here as for CENTRAL |
| Line 3 `'randomized controlled trial'/exp OR 'randomization'/exp OR random*:ti,ab` | Line 3 `TS=(random* OR ... OR placebo OR "double blind" OR "controlled trial")` | Web of Science is not a trials register, so a design filter is needed; `random*` alone reproduces the Embase free text part, the added terms stand in for the two Emtree explosions and widen the filter slightly (a Cochrane style Web of Science RCT filter has no validated short form) |
| No date, language or document type limits | Same | Restriction happens at screening |

Expected overlap with Embase and CENTRAL is high for journal articles; the marginal yield is conference proceedings indexed in CPCI and journals outside Embase. The recall ceiling found in Embase and CENTRAL (trials that report the biomarker incidentally) applies here too, since the biomarker line is unchanged in substance.

## To run

1. Open the advanced search through the EZproxy route and confirm the proxied hostname.
2. Enter lines 1 to 4; record each count here.
3. Export line 4 as "Full Record" plain text or RIS (Other File Formats, 1,000 records per export; split if larger) to `search/wos_<date>/wos_<n>.ris` (gitignored), with TY/ER counts and SHA-256 in a SEARCH_LOG.md beside it.
4. Run `src/dedup_embase.py` with a `wos` entry added to its SOURCES registry for recall and overlap, then add the records not in Embase or CENTRAL to a third screening pool.
