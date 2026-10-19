# Citation triage

Companion to `src/included_studies_references.py`, which builds the included studies reference list
from the extraction master and verifies every identifier against Europe PMC and Crossref before the
list is published. This document doubles as that check's allowlist, and as the allowlist of
`src/citation_record_check.py`, the offline gate that asks whether the committed reference record
still describes the committed corpus: a case written up here does not fail either, a new case does.

Run `python3 -I src/included_studies_references.py` (network) and `python3 -I
src/citation_record_check.py` (offline, in the gate chain).

## Why this check exists

`docs/REFERENCES.md` states that its 29 anchor references were each verified against PubMed with a
resolvable DOI. The 76 included studies, which are the larger part of the reference list and the part
a reader consults to find the source of a pooled number, had never been through that check. No gate
in the provenance chain could catch it: the first fifteen gates compare numbers against texts, and
this is a question of whether an identifier points at the paper the numbers came from.

## Result

| Verdict | First pass, 19 October | After the corrections below |
| --- | --- | --- |
| Verified: identifier resolves, first author and year agree | 58 | 73 |
| Author absent in the master, supplied by the registry | 4 | 0 |
| Mismatch: the master and the registry name different people or years | 8 | 0 |
| Identifier does not resolve at either registry | 6 | 0 |
| No identifier exists to resolve | 0 | 3 |
| **Total** | **76** | **76** |

Two things moved the first pass to the second. Crossref was added as a second registry, which
resolved three of the six non resolving identifiers that Europe PMC does not index; and the verdict
`identifier_not_found` was split from `no_identifier_exists`, because a recorded identifier that
fails to resolve is a defect while a trial that has no identifier at all is a terminal state and a
different problem. The remaining three are the second kind.

Separately, 46 trials record `NA` in the `pmid` field and were verified through their DOI. The PMID
the registry holds is reported for each and is deliberately NOT written back to the master: filling a
field from the registry that performs the verification would make the verification partly self
confirming without adding independent information. The exception is a trial that had no identifier at
all, where supplying one adds information rather than circularity; that happened twice, in specs 50
and 185.

## Shared DOIs are correct and must not be "fixed"

Four DOIs are each carried by more than one `trial_id`. All four are one publication reporting
several trials, which is the expected pattern in this corpus and not a duplication.

| DOI | Trials | Publication |
| --- | --- | --- |
| 10.1016/j.eclinm.2022.101737 | STEP 2, STEP 3 | one pooled C reactive protein analysis of two trials |
| 10.1111/dom.70861 | 1404-0002, 1404-0036 | the survodutide paper reporting two trials |
| 10.1113/ep091815 | NCT01761318, NCT02660047 | the GDF-15 paper reporting two trials |
| 10.1186/s12933-022-01585-7 | PIONEER 1, PIONEER 2, PIONEER 5 | one analysis across three PIONEER trials |

## The eight mismatches, resolved 19 October 2026

Each mismatch meant that the recorded first author named one paper and the recorded DOI resolved to
another, and the check could not say which field was wrong. The full Europe PMC record was fetched
for all eight. In every case the DOI resolves to a record whose title, drug, comparator, duration and
population match the trial the extraction spec describes, so the identifier is right and the name is
wrong. The correction was applied in the extraction spec, with the registry evidence written into the
spec's notes, and the tracked extraction file was regenerated from the spec; the regeneration was
required to differ from the committed file in the corrected columns and in nothing else before it was
promoted, which is the check that the spec and its artefact still describe each other.

| Trial | Spec | Field | From | To | Registry record behind the recorded DOI |
| --- | --- | --- | --- | --- | --- |
| STEP 2 | 137 | first_author | Mosenzon | Verma | Verma S, Bhatta M, Davies M, Deanfield JE, Garvey WT, Jensen C, Kandler K, Kushner RF, Rubino DM, Kosiborod MN, EClinicalMedicine 2023, pmid 36467859 |
| STEP 3 | 137 | first_author | Mosenzon | Verma | the same publication, which reports STEP 1, 2 and 3 |
| NCT02660047 | 305 | first_author | Hoogstad-van Evert | Hoekx | Hoekx CA, Straat ME, Bizino MB, van Eyk HJ, Lamb HJ, Smit JWA, Jazet IM, de Jager SCA, Boon MR, Martinez-Tellez B, Exp Physiol 2024, pmid 38965822 |
| NCT01648582 dulaglutide vs glargine (Nanjing) | 187 | first_author, journal | Shao, J Diabetes Res | Wang, Biomed Res Int | Wang J, Li HQ, Xu XH, Kong XC, Sun R, Jing T, Ye L, Su XF, Ma JH, Biomed Res Int 2019, pmid 31950036 |
| NCT01644500 dulaglutide vs glimepiride (Nanjing) | 188 | first_author | Shao | Li | Li H, Xu X, Wang J, Kong X, Chen M, Jing T, Zhang Z, Yin G, Liu X, Hu Y, Ye L, Su X, Ma J, J Diabetes Res 2019, pmid 31183384 |
| Jin 2020 exenatide vs insulin CIMT (Harbin) | 172 | first_author | Jin | Zhang | Zhang J, Xian TZ, Wu MX, Li C, Pan Q, Guo LX, Cardiovasc Diabetol 2020, pmid 32334592 |
| Wang 2026 Xi'an DKD | 16 | first_author | Wang | Long | Long W, Ningning L, Weijun H, Pak J Pharm Sci 2026, pmid 42170981 |
| NCT05442450 | 2 | year | 2025 | 2026 | Katrevula A, Kalapala R, Agrawal S, Jagtap N, Chhabra P, Kulkarni AV, Merugu C, Katukuri GR, Duvvur NR, Indian J Gastroenterol, publication year 2026, pmid 41066034 |

Two of these carry a further observation worth keeping on the record.

The Nanjing pair came from one group at one hospital, and the name `Shao` appears in the author list
of neither paper. The two trials were recorded under the same journal as well, and only one of them
is in that journal. A single wrong field is a typing error; two trials sharing a wrong surname and a
wrong journal is a record copied from somewhere else, and the extraction notes do not say where. The
numbers themselves were read from the texts behind these DOIs, and the design each spec describes
matches the paper the DOI resolves to, so nothing in the synthesis depends on the resolution; but the
provenance of those two bibliographic rows is weaker than the rest and is recorded as such.

`Mosenzon` is the first author of the PIONEER cardiovascular report, spec 142, doi
10.1186/s12933-022-01585-7, which verifies and is untouched. The STEP 2 and STEP 3 rows appear to
have inherited that name.

## The four author absent cases, supplied 19 October 2026

Four rows carried the literal placeholder `not named in the capture`, an honest record of the capture
and a useless one in a reference list. The name was taken from the Europe PMC record behind the DOI
already on the row, and each spec's notes now say that the author is registry evidence rather than
something read from the page.

| Trial | Spec | first_author | Registry record |
| --- | --- | --- | --- |
| SURMOUNT-1 | 9 | Sattar | Sattar N et al, Comprehensive Long-Term Changes in Cardiovascular Risk Biomarkers With Tirzepatide: A SURMOUNT-1 Post Hoc Analysis, J Am Coll Cardiol 2026, pmid 42233927 |
| semaglutide psoriasis T2D open label | 87 | Petkovic-Dabic | Petkovic-Dabic J et al, Biomolecules 2025, pmid 39858442. The registry prints an acute accent on both c characters; the master is ASCII throughout and the check folds diacritics before comparing surnames |
| NCT04904913 mazdutide phase 2 | 120 | Ji | Ji L et al, A phase 2 randomised controlled trial of mazdutide in Chinese overweight adults or adults with obesity, Nat Commun 2023, pmid 38092790 |
| SURPASS-1 | 135 | Lee | Lee CJ, Mao H, Thieu VT, Lando LF, Thomas MK, Tirzepatide as Monotherapy Improved Markers of Beta-cell Function and Insulin Sensitivity in Type 2 Diabetes (SURPASS-1), J Endocr Soc 2023, pmid 37153701. This is the beta cell function report, not the parent trial report, and the row's numbers come from it |

## The two identifiers supplied where none existed

| Trial | Spec | Supplied | Evidence |
| --- | --- | --- | --- |
| STEP UP | 50 | doi 10.1016/s2213-8587(25)00226-8, pmid 40961952 | Wharton S et al, Once-weekly semaglutide 7.2 mg in adults with obesity (STEP UP), Lancet Diabetes Endocrinol 2025. A companion paper reports STEP UP T2D under doi 10.1016/s2213-8587(25)00225-6, pmid 40961953; this row is the obesity trial, 72 weeks, and the two must not be conflated |
| MDI-liraglutide study (Sweden) | 185 | doi 10.1002/osp4.324, pmid 31019730 | Ahmadi S et al, MDI-liraglutide study 5, Obes Sci Pract 2019. The abstract names 124 randomised, 24 weeks, placebo comparator and adiponectin, which matches this row. The journal recorded as Diabetes Obes Metab is corrected to Obes Sci Pract |

## The three with no identifier to resolve

Europe PMC and Crossref between them index most but not all of the literature, and a conference
abstract or a trial with no publication will not resolve by any identifier because there is none to
resolve. Each still needs a citable form, which for an abstract is the meeting and the abstract
number, and for a journal outside both registries is volume, issue and pages.

| Trial | Status | Citable form |
| --- | --- | --- |
| EUREXA adipokine addendum | Conference abstract addendum to the main trial | meeting and abstract number, to be taken from the capture |
| NCT00781937 | Registry record; no linked publication found | the registry entry, with the access date |
| Suzuki 2014 Dokkyo | Dokkyo Journal of Medical Sciences, indexed by neither registry | volume, issue and pages from the capture |

`Yu 2015 Dalian liraglutide vs metformin` was in this group on the first pass and now verifies: its
doi 10.14740/jem304w resolves at Crossref, which Europe PMC does not index.

## Known representational defect, not corrected here

The three trials above carry the literal string `NA` in the `doi` and `pmid` fields of the master,
because that is what the captures printed. The reference list writes an empty string. Both mean
absent, and `src/citation_record_check.py` normalises the two spellings before comparing, with the
reason in its own docstring. Correcting the master would mean rewriting three extractions for a field
that is empty under either spelling, so it is recorded as an amendment candidate rather than done:
the string `NA` should not appear in an identifier column. It belongs with the master's other
representational amendment candidate, the dropped printed trailing zeros recorded in
`docs/ARM_ORIENTATION_TRIAGE.md`.

## Five tracked extraction files are named for a superseded author

`extraction_mosenzon2023_step2_step3_semaglutide_crp_fulltext_text.csv`,
`extraction_shao2019_dulaglutide_vs_glargine_nanjing_fulltext_tables1_2.csv`,
`extraction_shao2019_dulaglutide_vs_glimepiride_nanjing_fulltext_table3.csv`,
`extraction_wang2026_semaglutide_vs_placebo_early_dkd_fulltext_table3.csv` and
`extraction_hoogstad2024_liraglutide_gdf15_two_trials_fulltext_text.csv` encode the surnames
corrected above. They are not renamed. A file name in this repository is an opaque identifier fixed
at creation and referenced by the master's `source_file` column, by the packet manifests, by the
attachment and source provenance gates and by every provenance record written since; renaming five of
them to correct a surname that the data columns now carry correctly would invalidate those references
for a cosmetic gain. The rule is stated here so that a reader who notices the discrepancy finds it
already judged rather than undiscovered.

## What this does not put in doubt

No pooled estimate. Every number in the master was read from a retained text and checked against it
by the numbers and attachment gates, and the source provenance gate records which kind of text each
row rests on. The question settled here is bibliographic: which publication the reference list names
for a trial whose rows are themselves verified.
