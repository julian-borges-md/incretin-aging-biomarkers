# CENTRAL search log, 15 October 2026

Cochrane Central Register of Controlled Trials, Issue 10 of 12, October 2026. Executed in the Cochrane Library Search manager through the BU EZproxy route (`www-cochranelibrary-com.ezproxy.bu.edu`), which is what makes the citation export available: as a guest the same search returns the same 460 count but the results page shows no selection or export controls ("Authenticate to get access to full CENTRAL content"). The strategy was first run unauthenticated at `www.cochranelibrary.com`, then rerun line by line through the proxy; every line count was identical in both runs.

## Provenance of the strategy

No CENTRAL string exists in the protocol, the repository or the vault; the PROSPERO record names CENTRAL as a source and states that full strategies will be published as a supplement. The strategy below is a translation of the Embase lines in `search/embase_2026-10-15/SEARCH_LOG.md`, written on the day of the run. Every difference from the Embase string is deliberate and listed in the translation table, so the Director can accept or reverse each one.

## Line by line

| # | Query | Hits (all Cochrane Library content) |
|---|---|---|
| 1 | `[mh Exenatide]` | 695 |
| 2 | `[mh Liraglutide]` | 1,071 |
| 3 | `(exenatide OR liraglutide OR dulaglutide OR semaglutide OR tirzepatide OR retatrutide OR survodutide OR mazdutide OR pemvidutide OR cotadutide OR efinopegdutide):ti,ab,kw` | 7,368 |
| 4 | `#1 OR #2 OR #3` | 7,368 |
| 5 | `[mh "C-Reactive Protein"]` | 6,600 |
| 6 | `[mh Interleukin-6]` | 4,610 |
| 7 | `[mh "Tumor Necrosis Factor-alpha"]` | 4,483 |
| 8 | `[mh Adiponectin]` | 1,157 |
| 9 | `[mh Leptin]` | 1,390 |
| 10 | `[mh "Growth Differentiation Factor 15"]` | 132 |
| 11 | `("c reactive protein" OR "c-reactive protein" OR CRP OR hsCRP OR "hs-CRP" OR "interleukin 6" OR "interleukin-6" OR IL6 OR "IL-6" OR "tumor necrosis factor" OR "tumour necrosis factor" OR TNF OR "TNF-alpha" OR adiponectin OR leptin OR "growth differentiation factor 15" OR GDF15 OR "GDF-15"):ti,ab,kw` | 72,087 |
| 12 | `#5 OR #6 OR #7 OR #8 OR #9 OR #10 OR #11` | 72,087 |
| 13 | `#4 AND #12` | **460** (Trials 460; Cochrane Reviews, Protocols, Editorials, Special Collections, Clinical Answers all 0) |
| 14 | `(#1 OR #2) AND (#5 OR #6 OR #7 OR #8 OR #9 OR #10)` | 38 (diagnostic only, not exported) |

`[mh X]` explodes the MeSH tree below X. Lines 4 and 12 equal lines 3 and 11: in CENTRAL the free text block contains every record the MeSH block finds, so the MeSH lines add nothing and are kept only to show that.

## Translation table: what differs from the Embase string, and why

| Embase element | CENTRAL element | Reason |
|---|---|---|
| Line 1: six Emtree drug terms with `/exp`, five free text names, mapping options cleared (indexing only for the Emtree terms) | Lines 1 to 3: MeSH explode where a descriptor exists (Exenatide, Liraglutide) plus all eleven names as free text in title, abstract and keywords | Dulaglutide, semaglutide and tirzepatide are MeSH supplementary concepts, not descriptors, and cannot be searched as `[mh]`; 143 of the 460 records are registry entries that carry no MeSH at all. Indexing only would miss them by construction |
| Line 2: six Emtree biomarker terms with `/exp`, indexing only | Lines 5 to 11: six MeSH explosions plus free text for the preferred term and its common abbreviation (CRP, hsCRP, IL-6, TNF, GDF-15) | Same reason. The abbreviation list is the only vocabulary added beyond the Emtree preferred terms; it is declared here and is the first thing to remove if the Director wants strict equivalence |
| Line 3: randomised design filter | None | CENTRAL holds only reports of controlled trials; a design filter inside it is not standard practice and would exclude registry records that lack a structured abstract |
| Articles and registry records exported separately | One export | CENTRAL mixes journal records (317) and registry derived records (143: 98 ICTRP, 45 ClinicalTrials.gov) in one list; the per record `journal` field distinguishes them |

Line 14 is the closest thing to the Embase construction (indexing only on both sides, no design filter): 38 records against 460. That gap is the size of the free text contribution in CENTRAL and is why the strict translation was not used.

## Export and count gate

All 460 Trials selected, RIS (EndNote) format, "Include abstract" on.

| Check | Value |
|---|---|
| Search reported | 460 |
| TY record starts in file | 460 |
| ER record ends in file | 460 |
| Distinct CENTRAL accession numbers (AN, CN-prefixed) | 460 |
| **Gate** | **PASS, counts reconcile exactly** |
| File | `search/central_2026-10-15/central_460.ris` (gitignored, licensed content) |
| Bytes | 1,905,402 |
| SHA-256 | `7c12c88115631e45195e82641d2b0a6f9c5bd0835d48f7972c5b08372c0547f3` |

Download mechanics, same as the Embase registry export earlier tonight: Chrome wrote the file under its temporary download name and did not finalise the rename. The file above is a copy of that complete temporary file; completeness is established by the counts, not by the browser.

## Record composition

| Field | Coverage |
|---|---|
| Journal records | 317 |
| Registry derived records | 143 (98 WHO ICTRP, 45 ClinicalTrials.gov) |
| DOI present | 287 of 460 (registry records never carry one) |
| Abstract present | 458 of 460 |
| Year first published (facet) | 2026: 43, 2025: 54, 2024: 49, 2023: 32, 2022: 38, 2021: 37, 2020: 19, 2019: 19; earlier years smaller |
| Date added to CENTRAL (facet) | last 3 months 21, last 6 months 43, last 9 months 72, last year 83, last 2 years 127 |
| Source facet as displayed | Embase 237, PubMed 143, ICTRP 98, CT.gov 45 (a record can carry more than one source; the facet list was truncated at four entries on screen) |

## Linkage to the Embase export and to the known corpus

Produced by `python3 -I src/dedup_embase.py central` (`RECALL_AND_DEDUP.md` beside this file, per record flags in the untracked `central_460_dedup.csv`).

| Quantity | Value |
|---|---|
| CENTRAL records also in the 659 Embase articles, by DOI | 236 |
| Also in Embase, by normalised title only (candidate duplicates) | 24 |
| CENTRAL records not in the Embase article export | 200: 143 registry derived, 57 journal articles (50 with DOI) |
| ClinicalTrials.gov derived CENTRAL records also among the 51 Embase registry records | 35 of 45 |
| Recall against the 11 extracted papers | 8 of 11 (misses: Meyhofer 2026, Sanyal 2024, Wägner 2019) |
| Recall against the 38 Alrasheed 2026 mono trials, automated | 26 of 38 |
| Same, after manual reading (Yao 2020 unresolved, counted as a miss) | 25 of 38, the same ceiling as Embase |
| Union of Embase and CENTRAL against the 38 | 27 of 38 (CENTRAL adds Kang 2021 and Zhang 2018; Embase alone has Quan 2017 and Yan 2019) |

The reading is the same as for Embase: the trials neither database retrieves report the biomarker incidentally, and the biomarker line is the ceiling. CENTRAL contributes 57 journal articles and 108 registry records that Embase did not deliver, at the cost of 260 duplicates to collapse at screening.

## Not yet done

| Item | Status |
|---|---|
| Screening of the 200 records not in Embase | Not started; the 260 overlapping records are screened once, under their Embase copy |
| Web of Science | Not run; no string exists, the same translation question applies |
| Director decision on the translation (free text and abbreviations) | Open; the strict variant (line 14, 38 records) is the alternative |
