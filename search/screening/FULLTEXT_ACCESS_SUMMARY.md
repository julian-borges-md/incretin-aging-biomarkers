# Full text access for the screening pool, 16 October 2026

Lookup: Europe PMC REST search by DOI (batches of 20) and by PMID for records without a DOI; no key, no email, no personal data sent. Harvest: Europe PMC full text XML for every record with a PMCID and `isOpenAccess` = Y, saved as XML and a plain text rendering under `work/fulltext/pool/` (gitignored). Per record rows are in the untracked `fulltext_access_2026-10-16.csv`; the harvest manifest is beside the files.

| Route | Records looked up | Found in Europe PMC | With PMCID | Open access |
|---|---|---|---|---|
| doi (journal articles) | 228 | 215 | 117 | 109 |
| already_extracted | 12 | 12 | 7 | 7 |
| abstract_only with a DOI | 141 | 45 | 11 | 11 |
| title_search | 5 | 0 | 0 | 0 |

Of the 228 journal articles to retrieve by DOI: 109 are open access, 106 are closed access and need the institutional route (BU EZproxy), 13 are not in Europe PMC at all (articles in press, preprints and journals outside its coverage; locate by DOI resolver).

| Harvest | Value |
|---|---|
| Open access records with PMCID attempted | 127 |
| Fetched | 126 |
| Substantive full text (2,000 characters or more) | 120 |
| Stub (front matter, news or calendar items that share a supplement DOI with a conference abstract) | 6 |
| Errors | 1 |

A stub is not a failure of the review record: the conference abstract itself is the full text for that record, and the DOI it carries belongs to the supplement issue.

## Direct fetch of the records still needing a text (no proxy, no credentials)

Produced by `src/direct_fetch.py`: DOI resolved and the publisher page saved as text, classified by section headings, length and paywall marks; preprints fetched as JATS XML from the bioRxiv or medRxiv API; records without a DOI looked up in PubMed by title.

| Outcome | Records |
|---|---|
| blocked_or_empty | 49 |
| http 403 | 48 |
| abstract_or_partial | 8 |
| paywalled_page | 6 |
| fulltext | 5 |
| no_doi | 4 |
| fulltext_preprint | 3 |
| http 404 | 1 |

Full texts obtained this way: 8 (publisher open access pages and preprints), screened as the `direct_fulltext` source. Everything else on this list needs the institutional route (BU EZproxy), which requires a live sign in.

