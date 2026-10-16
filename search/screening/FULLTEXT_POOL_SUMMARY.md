# Full text screening pool, assembled 16 October 2026

Produced by `src/build_fulltext_pool.py` from the screening decision files and the gated exports. Per record rows (with titles) are in the untracked `fulltext_pool_2026-10-16.csv` beside the decision files.

| Quantity | Value |
|---|---|
| Records in the pool | 576 |
| By stage | v1 include 338; v2 rescued 24; pool 2 include 185; pool 3 include 29 |
| By source | embase 362; central 159; wos 29; embase_registry 26 |
| With DOI / with PMID / with an NCT identifier in the record | 410 / 29 / 175 |
| Linked to a known relevant trial at screening | 38 |
| Already extracted (DOI, PMID or NCT in the extraction master) | 20 |
| Candidate studies after grouping (shared DOI, title or NCT) | 467 |
| Groups with more than one record | 54 (records in them 163) |
| Registry records grouped with another record in the pool | 40 of 140 |
| Registry records by register | ClinicalTrials.gov 56; other registers via ICTRP 84; no identifier 0 |

| Retrieval route | Records | What retrieval means |
|---|---|---|
| doi | 253 | journal article, fetch by DOI through the institutional route |
| pmid | 0 | journal article without DOI in the record, fetch by PMID |
| title_search | 5 | no DOI or PMID in the record, locate by title |
| abstract_only | 162 | conference abstract; the record is the full text, judged as such |
| registry_record | 140 | ClinicalTrials.gov or ICTRP entry; read the registry page and its results and publications |
| already_extracted | 16 | trial already in the extraction master; no retrieval |

| Publication type (as exported) | Records |
|---|---|
| Article | 196 |
| Conference Abstract | 150 |
| Trial registry record | 114 |
| Journal article | 32 |
| JOUR | 29 |
| Clinical Trial | 26 |
| Journal article; Conference proceeding | 12 |
| Article in Press | 8 |
| Preprint | 3 |
| Letter | 3 |
| Note | 2 |
| Short Survey | 1 |

| Year | Records |
|---|---|
| 2026 | 75 |
| 2025 | 86 |
| 2024 | 60 |
| 2023 | 43 |
| 2022 | 42 |
| 2021 | 44 |
| 2020 | 18 |
| 2019 | 21 |
| 2018 | 29 |
| 2017 | 24 |
| 2016 | 26 |
| 2015 | 20 |

Grouping joins records, not trials: two records in one group are the same study only if full text confirms it, and a registry record grouped with an article is the natural pair to read together. Reviews and meta analyses that survived screening (the criteria say include when in doubt) are carried with their publication type so they can be excluded at the first page of full text.

