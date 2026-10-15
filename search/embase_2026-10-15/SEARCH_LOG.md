# Embase search log, 15 October 2026

Executed in Dr Borges' authenticated Embase session via browser automation. Strings run as written in the protocol; mapping options cleared before execution.

## Mapping configuration

All four Embase automatic mapping options were cleared before any line was run:

| Option | State |
|---|---|
| Map to preferred term in Emtree | cleared |
| Search also as free text in all fields | cleared |
| Explode using narrower Emtree terms | cleared |
| Search as broadly as possible | cleared |
| Limit to terms indexed as 'major focus' | cleared |

Explosion is specified explicitly by `/exp` within the strings rather than inherited from a default, so the search is reproducible from the strings alone.

No date limits, no language limits, no publication type limits were applied at the search stage. Restriction happens at screening, so that exclusions are countable in the PRISMA flow rather than invisible in the search.

## Line by line

| # | Query | Hits |
|---|---|---|
| 1 | `'exenatide'/exp OR 'liraglutide'/exp OR 'dulaglutide'/exp OR 'semaglutide'/exp OR 'tirzepatide'/exp OR 'retatrutide'/exp OR 'survodutide' OR 'mazdutide' OR 'pemvidutide' OR 'cotadutide' OR 'efinopegdutide'` | 42,445 |
| 2 | `'c reactive protein'/exp OR 'interleukin 6'/exp OR 'tumor necrosis factor alpha'/exp OR 'adiponectin'/exp OR 'leptin'/exp OR 'growth differentiation factor 15'/exp` | 1,126,492 |
| 3 | `'randomized controlled trial'/exp OR 'randomization'/exp OR random*:ti,ab` | 2,948,113 |
| 4 | `#1 AND #2 AND #3` | **710** |

Line 4 splits into 659 Articles and 51 Clinical trial registry records.

## Export and count gate

Articles tab, all 659 selected, RIS format, full record content including abstract, index terms, DOI, Medline PMID field, author addresses.

| Check | Value |
|---|---|
| Search reported | 659 |
| TY record starts in file | 659 |
| ER record ends in file | 659 |
| **Gate** | **PASS, counts reconcile exactly** |
| File | `search/embase_2026-10-15/embase_659.ris` |
| Bytes | 3,036,519 |
| SHA-256 | `e8d3a9d4e195375f1d1aaaead76ae0ad0d937206194e152984d71d42405fefb2` |

## Record composition

| Field | Coverage |
|---|---|
| Publication type JOUR | 650 |
| Publication type GEN | 9 |
| DOI present | 611 of 659 |
| Abstract present | 650 of 659 |
| Embase accession (U2) | 659 |

**Note on PMIDs.** Although the export dialog lists "Medline PMID" as an included field, no PMID tag appears in the delivered records; linkage to PubMed will have to go through DOI, which is present for 611 of 659. The remaining 48 will need title matching. This is a real limitation for deduplication against our existing PubMed-derived corpus and is recorded rather than worked around silently.

## Not yet done

| Item | Status |
|---|---|
| 51 clinical trial registry records | Not exported; separate tab, separate export |
| CENTRAL | Not run |
| Web of Science | Not run |
| Deduplication against the existing corpus | Not started |
| Screening of the 659 | Not started |

Screening cannot begin as a two-reviewer process until the blinded second screener is configured. Single-reviewer screening of this set would have to be described as such.
