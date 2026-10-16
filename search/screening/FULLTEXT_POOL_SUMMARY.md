# Full text screening pool, assembled 16 October 2026

Produced by `src/build_fulltext_pool.py` from the screening decision files and the gated exports. Per record rows (with titles) are in the untracked `fulltext_pool_2026-10-16.csv` beside the decision files.

| Quantity | Value |
|---|---|
| Records in the pool | 547 |
| By stage | v1 include 338; v2 rescued 24; pool 2 include 185 |
| By source | embase 362; central 159; embase_registry 26 |
| With DOI / with PMID / with an NCT identifier in the record | 381 / 29 / 142 |
| Linked to a known relevant trial at screening | 38 |
| Already extracted (DOI, PMID or NCT in the extraction master) | 14 |
| Candidate studies after grouping (shared DOI, title or NCT) | 452 |
| Groups with more than one record | 42 (records in them 137) |
| Registry records grouped with another record in the pool | 15 of 140 |

| Retrieval route | Records | What retrieval means |
|---|---|---|
| doi | 228 | journal article, fetch by DOI through the institutional route |
| pmid | 0 | journal article without DOI in the record, fetch by PMID |
| title_search | 5 | no DOI or PMID in the record, locate by title |
| abstract_only | 162 | conference abstract; the record is the full text, judged as such |
| registry_record | 140 | ClinicalTrials.gov or ICTRP entry; read the registry page and its results and publications |
| already_extracted | 12 | trial already in the extraction master; no retrieval |

| Publication type (as exported) | Records |
|---|---|
| Article | 196 |
| Conference Abstract | 150 |
| Trial registry record | 114 |
| Journal article | 32 |
| Clinical Trial | 26 |
| Journal article; Conference proceeding | 12 |
| Article in Press | 8 |
| Preprint | 3 |
| Letter | 3 |
| Note | 2 |
| Short Survey | 1 |

| Year | Records |
|---|---|
| 2026 | 70 |
| 2025 | 81 |
| 2024 | 59 |
| 2023 | 40 |
| 2022 | 38 |
| 2021 | 43 |
| 2020 | 18 |
| 2019 | 20 |
| 2018 | 28 |
| 2017 | 21 |
| 2016 | 26 |
| 2015 | 18 |

Grouping joins records, not trials: two records in one group are the same study only if full text confirms it, and a registry record grouped with an article is the natural pair to read together. Reviews and meta analyses that survived screening (the criteria say include when in doubt) are carried with their publication type so they can be excluded at the first page of full text.

