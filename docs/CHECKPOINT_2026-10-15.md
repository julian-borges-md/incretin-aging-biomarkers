# Checkpoint, 15 October 2026

State of the review at the end of the extraction session. Written so a fresh session can resume without reconstructing anything.

## Where the work stands

| Component | State |
|---|---|
| Protocol, 12 sections | Fixed and public |
| Analysis pipeline, 784 lines | Executable, validated against known truth |
| Extraction schema | Corrected for contrast-level reporting |
| Master extraction | **43 rows, 5 trials, 15 biomarkers, all 4 receptor classes** |
| Manuscript | Introduction, Methods, Discussion 4.3 to 4.10 written; Results blocked on more extraction |
| PROSPERO | Not registered. Decision taken to proceed unregistered; disclosed in Methods 2.1 |
| CI | Three jobs green: verify, selftest, validate, plus the no-fabricated-results gate |

## Corpus

| Receptor class | Rows | Biomarkers | Drugs | Weight covariate |
|---|---|---|---|---|
| GLP-1/GCGR | 15 | 7 | survodutide | Yes |
| GLP-1/GIP | 12 | 7 | tirzepatide | **No** |
| GLP-1 mono | 8 | 7 | dulaglutide, semaglutide | Partial |
| GLP-1/GIP/GCGR | 8 | 1 | retatrutide | Yes |

Variance provenance: 19 rows arm_sems, 15 log_RR_ci, 9 ci_95.

## The constraint that matters most

The weight-adjusted meta-regression currently sees 23 of 43 rows, and both contributing trials are GCGR-containing. It is blind to the entire GLP-1 mono and GLP-1/GIP evidence, which is exactly the comparison the central question needs.

This is not a technicality. Until the weight covariates are recovered for Wilson 2021 and SELECT, the primary analysis cannot answer Q3.

Recovering them requires:

| Source | Needed | Status |
|---|---|---|
| Frias 2018 Lancet, PMID 30293770 | Per-arm percentage weight change | Abstract gives kilogram range only, no mean baseline weight. Needs full text |
| Lincoff 2023 NEJM, SELECT main | Percentage weight change at 104 weeks | Not yet retrieved |

## Three claims withdrawn after extraction

Recorded because each was in a draft and each is now gone.

**Hepatic saturation, retatrutide.** The draft held that liver fat plateaus between 8 and 12 mg while weight keeps falling. Both plateau. Liver fat difference 1.00 (95% CI -16.68 to 18.68, p = 0.91); weight difference 0.30 (95% CI -3.63 to 3.03, p = 0.86). The 4 to 8 mg step does move liver fat (24.40, 95% CI 2.16 to 46.64, p = 0.032), so the analysis can detect a dose effect where one exists.

**GDF-15 receptor-class differential.** The draft held that tirzepatide reduces GDF-15 while GLP-1 mono agonists do not. Dulaglutide reduced it by 15.4%, more than any tirzepatide dose, and the between-group contrasts were not significant versus placebo or dulaglutide.

**The composite's sign convention.** Not a claim about drugs, but it inverted most of the score. Corrected and now tested in both senses.

## Strongest surviving evidence

The weight-independence premise is supported, from the inflammatory domain rather than the hepatic one where it is usually argued.

SELECT, n = 17,604: hsCRP fell 37.8% (95% CI 35.9 to 39.7, placebo-corrected). It fell before meaningful weight loss (19% by week 8 against 2.8% of body weight), in patients who lost under 2% of weight, and **in patients who gained weight** (ratio 0.85 on semaglutide against 1.06 on placebo).

Wilson 2021: weight change explained 0% of hsCRP variability with tirzepatide against 13% with dulaglutide, and 6% of YKL-40 against 21%.

Ekinci 2026, the only GCGR-class data: weight explained 12% of HOMA-IR variance, 3% of adiponectin, 5% of glucagon.

## Next actions, in order

1. Recover the weight covariates from Frias 2018 and Lincoff 2023. Highest value; unblocks the primary analysis for two receptor classes.
2. Run the pipeline on the current master for the first real pooled estimates, accepting the meta-regression's current blindness.
3. Extract Corley 2026 (PMC13381876), the only epigenetic clock data for any agent in this class.
4. Extract Jara 2025 (PMC12443624) and Maretty 2025 (PMC11750704) proteomics.
5. Add the 28 August 2026 PROSPERO registration on GLP-1/glucagon agonists in MASH to the reference corpus and Discussion.
6. Generate renv.lock.
7. M1 to M3 self-critique, untouched for weeks.

## Open items needing the Lab Director

- PROSPERO account carries fxmedbrasil@gmail.com; institutional standard is jyborges@bu.edu
- Zenodo DOI for the protocol, if the deposition route is to be settled
- Whether to contact CRD about the registration question at all, given the decision to proceed unregistered

## Repository

`julian-borges-md/incretin-aging-biomarkers`, public. Local at `~/dev/fxmedus-ai/incretin-aging-biomarkers`.

Note the path: `~/Documents/fxmedus-ai/` does not exist and earlier notes referring to it are wrong.
