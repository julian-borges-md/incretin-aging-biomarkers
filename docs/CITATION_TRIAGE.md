# Citation triage

Companion to `src/included_studies_references.py`, which builds the included studies reference list
from the extraction master and verifies every identifier against Europe PMC before the list is
published. This document doubles as that check's allowlist: a case written up here does not fail it,
a new case does.

Run `python3 -I src/included_studies_references.py`.

## Why this check exists

`docs/REFERENCES.md` states that its 29 anchor references were each verified against PubMed with a
resolvable DOI. The 76 included studies, which are the larger part of the reference list and the part
a reader consults to find the source of a pooled number, had never been through that check. No gate
in the provenance chain can catch it: the fifteen gates compare numbers against texts, and this is a
question of whether an identifier points at the paper the numbers came from.

## Result, 19 October 2026

| Verdict | Trials |
| --- | --- |
| Verified: PMID or DOI resolves, first author and year agree | 58 |
| Author absent in the master, supplied by the registry | 4 |
| Mismatch: the master and the registry name different people or years | 8 |
| Identifier does not resolve at Europe PMC | 6 |
| **Total** | **76** |

Separately, 46 trials record `NA` in the `pmid` field and were verified through their DOI. The PMID
the registry holds is reported for each, and is deliberately NOT written back to the master, because
changing an extracted field belongs to a spec and not to a reference formatter.

## Shared DOIs are correct and must not be "fixed"

Four DOIs are each carried by more than one `trial_id`. All four are one publication reporting
several trials, which is the expected pattern in this corpus and not a duplication.

| DOI | Trials | Publication |
| --- | --- | --- |
| 10.1016/j.eclinm.2022.101737 | STEP 2, STEP 3 | one pooled C reactive protein analysis of two trials |
| 10.1111/dom.70861 | 1404-0002, 1404-0036 | the survodutide paper reporting two trials |
| 10.1113/ep091815 | NCT01761318, NCT02660047 | the GDF-15 paper reporting two trials |
| 10.1186/s12933-022-01585-7 | PIONEER 1, PIONEER 2, PIONEER 5 | one analysis across three PIONEER trials |

## The 8 mismatches, each needing a read

In every case the recorded first author names one paper and the recorded DOI resolves to another, so
one of the two fields is wrong and the check cannot say which. Citing the wrong paper for a pooled
number is a citation integrity failure, so each must be settled before the reference list is
published. None of these affects a pooled estimate: the numbers were read from a text and verified
against it by gates nine and eleven; what is in question is which publication the reference list
should name.

| Trial | Master records | Registry returns for the recorded DOI | What to check |
| --- | --- | --- | --- |
| STEP 2 | Mosenzon | Verma S, Bhatta M, Davies M, Deanfield JE, Garvey WT, Jensen | The extraction file is named for Mosenzon 2023 while the DOI is a 2022 eClinicalMedicine paper. Which paper the CRP rows were read from decides it |
| STEP 3 | Mosenzon | Verma S, Bhatta M, Davies M, Deanfield JE, Garvey WT, Jensen | Same publication as STEP 2 above, same question |
| NCT02660047 | Hoogstad-van Evert | Hoekx CA, Straat ME, Bizino MB, van Eyk HJ, Lamb HJ, Smit JW | Both are from the same Leiden group; the DOI may name a companion paper rather than the GDF-15 one the rows came from |
| NCT01648582 dulaglutide vs glargine (Nanjing) | Shao | Wang J, Li HQ, Xu XH, Kong XC, Sun R, Jing T, Ye L, Su XF, M | Same group, several publications; which one carries the extracted table |
| NCT01644500 dulaglutide vs glimepiride (Nanjing) | Shao | Li H, Xu X, Wang J, Kong X, Chen M, Jing T, Zhang Z, Yin G, | As above |
| Jin 2020 exenatide vs insulin CIMT (Harbin) | Jin | Zhang J, Xian TZ, Wu MX, Li C, Pan Q, Guo LX. | The returned paper is a different first author entirely |
| Wang 2026 Xi'an DKD | Wang | Long W, Ningning L, Weijun H. | As above |
| NCT05442450 | year 2025 | year 2026 | Likely an online first against issue year difference, the mildest case here |

## The 6 that do not resolve

Europe PMC indexes most but not all of the literature, and a conference abstract or a journal outside
its coverage will not resolve by either identifier. That is an expected limitation rather than a
defect, but each still needs a citable form for the reference list, which for an abstract is the
meeting and the abstract number.

| Trial | Likely reason |
| --- | --- |
| EUREXA adipokine addendum | A conference abstract addendum to the main trial |
| NCT00781937 | Registry record; the publication, if any, is not linked |
| MDI-liraglutide study (Sweden) | Journal outside Europe PMC coverage, or an abstract |
| Suzuki 2014 Dokkyo | Japanese journal, likely outside coverage |
| STEP UP | Recent publication or a conference presentation |
| Yu 2015 Dalian liraglutide vs metformin | Journal of Endocrinology and Metabolism, outside Europe PMC coverage. The capture names volume, issue, pages and doi 10.14740/jem304w |

## What this does not put in doubt

No pooled estimate. Every number in the master was read from a retained text and checked against it
by the numbers and attachment gates, and the source provenance gate records which kind of text each
row rests on. The question here is bibliographic: which publication the reference list names for a
trial whose rows are themselves verified.
