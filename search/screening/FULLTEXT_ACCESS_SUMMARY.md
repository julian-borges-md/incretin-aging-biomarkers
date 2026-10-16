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

## Institutional route (BU EZproxy, browser capture)

Each remaining DOI was opened in the browser through `https://ezproxy.bu.edu/login?url=https://doi.org/<doi>` (publisher hosts where the DOI route fails: NEJM `www-nejm-org.ezproxy.bu.edu/doi/full/`, Springer `link-springer-com.ezproxy.bu.edu/article/`, ClinicalKey titles through the ScienceDirect PII page, Thieme `products/ejournals/html/`); the page's visible text was saved from the browser as a local file with a KEY header, then moved and classified by `src/proxy_harvest.py` (manifest beside the files, gitignored). The sign in was done by the Director; the agent never entered credentials. Classification: `fulltext` = three of the four section marks (Methods, Results, Discussion, References; English or Russian) and more than 12,000 characters; `partial` otherwise (abstract pages, but also complete short documents such as letters, comments and reviews without methods sections).

| Outcome | Records |
|---|---|
| fulltext | 90 |
| partial | 25 |

Captures of at least 2,000 characters are screened: `fulltext` as the `proxy_fulltext` source, `partial` as the `proxy_partial` source with a label that says the page may be complete or abstract only (23 records; the other 2 partial captures are resolver or error pages under 2,000 characters and count as not retrieved).

| Host of the full text captures | Records |
|---|---|
| www-sciencedirect-com.ezproxy.bu.edu | 41 |
| onlinelibrary-wiley-com.ezproxy.bu.edu | 10 |
| dom-pubs-pericles-prod-literatumonline-com.ezproxy.bu.edu | 9 |
| www-nejm-org.ezproxy.bu.edu | 8 |
| academic-oup-com.ezproxy.bu.edu | 5 |
| link-springer-com.ezproxy.bu.edu | 4 |
| journals-sagepub-com.ezproxy.bu.edu | 2 |
| jamanetwork-com.ezproxy.bu.edu | 1 |
| www-cambridge-org.ezproxy.bu.edu | 1 |
| portlandpress-com.ezproxy.bu.edu | 1 |
| www-tandfonline-com.ezproxy.bu.edu | 1 |
| journals-lww-com.ezproxy.bu.edu | 1 |
| www-thieme-connect-com.ezproxy.bu.edu | 1 |
| www.omet-endojournals.ru | 1 |
| www.oaepublish.com | 1 |
| diabetesjournals-org.ezproxy.bu.edu | 1 |
| www.wjgnet.com | 1 |
| dmu.repo.nii.ac.jp | 1 |

Three captures that the rule marked `fulltext` were reclassified as `partial` after reading (1-142 Springer abstract page, 1-532 AHA abstract page, 1-183 yiigle abstract page with its reference list); they are named in `src/proxy_harvest.py` with the reason, and the rule itself is unchanged. Two Chinese language records are abstract pages reached on a second attempt (1-183 Chinese Journal of Diabetes on yiigle; 1-48 Chinese Journal of Clinical Research on CNKI oversea, which the BU EZproxy does not cover).


One record without a DOI (1-595, Dokkyo J Med Sci 2014;41(3):211) was found as a PDF in the Dokkyo Medical University repository (dmu.repo.nii.ac.jp), rendered with pdftotext and added to the same manifest.


### Records still without a text (recorded by hand from the capture attempts)

| Record | Identifier | What was found |
|---|---|---|
| 1-90 | 10.25258/ijddt.16.44s.15 | DOI does not resolve (impactfactor.org placeholder, 105 characters) |
| 1-160 | 10.31838/ijprt/15.02.374 | DOI not found at doi.org |
| 1-443 | no DOI; Int J Clin Exp Med 2020;13(2):1219 | publisher site answered 509 Bandwidth Limit Exceeded; not in PubMed |
| 2-223 | no DOI; Drug Invention Today 2019;12(11):2549 | ResearchGate lists it with the abstract and a request full text button only; not in PubMed; publisher PDF not located |

