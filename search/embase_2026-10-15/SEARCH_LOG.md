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

## Clinical trial registry records, exported 15 October 2026, 22:00 EDT

The four lines were rerun in the same institutional session before the export, with the mapping options cleared as above. Every count reproduced exactly: 42,445 / 1,126,492 / 2,948,113 / 710, splitting into 659 Articles and 51 Clinical trials. The reproduction is the evidence that the registry export belongs to the same search as the article export, not a near neighbour of it.

Clinical trials tab, all 51 selected, RIS format, full record content (study overview, collaborators and investigators, all additional options).

| Check | Value |
|---|---|
| Search reported | 51 |
| TY record starts in file | 51 |
| ER record ends in file | 51 |
| Distinct registry identifiers (AN) | 51 |
| **Gate** | **PASS, counts reconcile exactly** |
| File | `search/embase_2026-10-15/embase_registry_51.ris` (gitignored, licensed content) |
| Bytes | 624,926 |
| SHA-256 | `d740d349bf45d00d5311d6cb72cf4c7fc92e64d21ee6bb9744940be6c407665a` |

Download mechanics, corrected 16 October 02:10 from Chrome's own download history: the first click completed normally (`~/Downloads/ctrecords.ris`, 624,926 bytes, state complete at 22:00:07), the second click was recorded as cancelled, and the earlier note that the rename never happened was written before the first download had finalised. `~/Downloads/ctrecords.ris` and the repository copy have the same SHA-256. Completeness is still established by the TY, ER and identifier counts, not by the browser.

### Registry export composition

| Field | Coverage |
|---|---|
| Source | 51 of 51 ClinicalTrials.gov (NCT); no other registry contributes |
| Study type (C5) | 46 interventional, 5 observational |
| Recruitment status (C2) | 20 completed, 9 recruiting, 10 not yet recruiting, 3 active not recruiting, 9 unknown status |
| Results posted on the registry (C6) | 8 yes, 43 no |
| Phase (SN) | 21 phase 4, 9 phase 2, 2 phase 3, 2 phase 1/2, 1 phase 1, 11 not applicable, 5 blank |
| Registry record year (Y1) | 2006 to 2026; 17 of 51 from 2025 and 2026 |
| Overlap with NCT identifiers already in the repository (5) | none |

Five observational records sit in a set retrieved by a randomised design filter; the filter matched on free text (`random*:ti,ab`) within the registry record, not on design. They are screened out at title and abstract level, where the exclusion is counted, rather than removed here.

Reading of the eight with results posted, from the registry title and brief summary only: five fall outside the review population or intervention (NCT02664441 hypothalamic obesity; NCT02417142 schizophrenia; NCT01991197 sitagliptin, a DPP-4 inhibitor, in psoriasis with diabetes; NCT01832532 liraglutide in adults without diabetes with sleep apnoea; NCT01269047 type 1 diabetes). Three are candidates for the mono class with a vascular or inflammatory outcome (NCT03260881 liraglutide, epicardial fat inflammatory genes, type 2 diabetes with coronary disease; NCT03010683 GLP-1 receptor agonists, arterial stiffness and endothelial glycocalyx; NCT00353834 exenatide versus insulin glargine, endothelial function). All 51 go through the same blinded screening as the article records; nothing is decided from this reading.

## Not yet done

| Item | Status |
|---|---|
| 51 clinical trial registry records | Exported 22:00 EDT, count gate passed (section above); not yet screened |
| CENTRAL | Not run |
| Web of Science | Not run |
| Deduplication against the existing corpus | Done for the 659 articles (`RECALL_AND_DEDUP.md`); not yet run for the 51 registry records |
| Screening of the 659 | Running: two blinded local reviewer agents plus adjudicator (`search/screening/`) |

Screening cannot begin as a two-reviewer process until the blinded second screener is configured. Single-reviewer screening of this set would have to be described as such.
