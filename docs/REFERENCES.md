# Anchor Reference Corpus

29 papers, each recorded here with a DOI. These are the references the protocol and the Introduction
and Discussion rest on. The 76 included studies are a separate list, generated and identifier checked
by `src/included_studies_references.py` and reported in `analysis/output/included_studies.md`.

Status note, 19 October 2026. This file previously stated that all 29 were verified against PubMed
with a resolvable DOI. The check that states that has now been written, `src/anchor_references_
check.py`, and run. Every DOI did resolve. The rest of the claim did not hold:

| Finding | Count |
| --- | --- |
| References whose recorded issue or pages disagreed with the registry | 7 |
| Of those, also a wrong year and volume | 2 |
| Of those, also a wrong author initial | 1 |
| References carrying a paraphrased short title rather than the published one | 22 |
| DOIs that failed to resolve | 0 |

Two examples of the first row, which a DOI check cannot see: reference 12, the ESSENCE trial, was
recorded at 392(22):2226-2238 and is published at 392(21):2089-2099; reference 16 was recorded at
47(4):698-704 and is published at 47(10):1718-1730. A reader following either citation reaches the
right journal and the wrong article. Reference 11 was recorded as Banerjee R and is by Banerjee M.

Every row has therefore been rebuilt from the registry record behind its DOI, so the document and
the check now draw on one source, and all 29 verify on author, year, journal, volume, issue and
pages. The prose annotations between the tables are this project's reading of the references and
were not touched. Rerun with `python3 -I src/anchor_references_check.py`; the committed result is
`analysis/output/anchor_references_check.csv`, which the offline gate `src/citation_record_check.py`
requires to be complete and clean.

One dependency is worth naming here rather than leaving for a reader to find. Reference 1, the
epigenetic aging anchor, is the semaglutide trial in HIV associated lipohypertrophy, which is
extraction group 386 and is held under amendment A6 pending the Director's decision on that
population. Under the eligibility criteria as they stand, the trial that makes this review's central
question answerable sits in a population the review has not yet decided to include. The decision
therefore reaches further than the sixteen held groups: it reaches the framing of the Introduction.

Grouped by the role each plays in the argument.

## Epigenetic aging, the evidence that makes the question answerable

| # | Reference | DOI |
|---|---|---|
| 1 | Corley MJ, Dwaraka VB, Pang AP, et al. Semaglutide slows epigenetic aging in a randomized trial of HIV-associated lipohypertrophy. Nat Commun. 2026;17(1):6606 | 10.1038/s41467-026-72861-3 |
| 2 | Johnson AA, Sinclair DA. Turning back time: a comprehensive list of interventions that decrease next-generation epigenetic aging clocks in humans. Front Genet. 2026;17:1836446 | 10.3389/fgene.2026.1836446 |
| 3 | Guarente L, Sinclair DA, Kroemer G. Human trials exploring anti-aging medicines. Cell Metab. 2024;36(2):354-376 | 10.1016/j.cmet.2023.12.007 |

Reference 1 is the single most important paper in the corpus. It is the first randomized evidence that any incretin based therapy modulates validated epigenetic aging clocks, and no equivalent data exist for any dual or triple agonist.

## The GDF-15 receptor class differential

| # | Reference | DOI |
|---|---|---|
| 4 | Wilson JM, Lin Y, Luo MJ, et al. The dual glucose-dependent insulinotropic polypeptide and glucagon-like peptide-1 receptor agonist tirzepatide improves cardiovascular risk biomarkers in patients with type 2 diabetes: A post hoc analysis. Diabetes Obes Metab. 2022;24(1):148-153 | 10.1111/dom.14553 |
| 5 | Konstantinidou SK, Argyrakopoulou G, Simati S, et al. Total and H-specific growth/differentiation factor 15 levels are unaffected by liraglutide or naltrexone/bupropion administration. Diabetes Obes Metab. 2024;26(8):3147-3154 | 10.1111/dom.15642 |

Reference 4 reports a reduction in GDF-15 with tirzepatide and reference 5 reports no change with
liraglutide. **This review does not carry that contrast as a finding.** The class differential it
suggests was withdrawn on the evidence of the synthesis itself and may not be reinstated without new
data: the pooled GDF-15 estimate rests on three trial arms, all of them GLP-1 mono, so no receptor
class comparison is estimable for this marker, and no GDF-15 data exist for any GCGR containing
agent. What the two references establish is that the marker has been measured in two molecules and
reported differently; the inference from that to a property of the receptor classes is exactly the
step the data do not support. The section is retained under this heading because the heading records
what the protocol set out to test, and the answer is that it could not be tested.

## Inflammatory and proteomic signatures

| # | Reference | DOI |
|---|---|---|
| 6 | Plutzky J, Bogdański P, Colhoun HM, et al. Effect of Semaglutide on the Inflammatory Biomarker High-Sensitivity CRP in Patients With Established Cardiovascular Disease and Overweight or Obesity in SELECT: A Prespecified Secondary Analysis. Circulation. 2026;154(11):976-991 | 10.1161/CIRCULATIONAHA.125.074482 |
| 7 | Maretty L, Gill D, Simonsen L, et al. Proteomic changes upon treatment with semaglutide in individuals with obesity. Nat Med. 2025;31(1):267-277 | 10.1038/s41591-024-03355-2 |
| 8 | Jara M, Norlin J, Kjær MS, et al. Modulation of metabolic, inflammatory and fibrotic pathways by semaglutide in metabolic dysfunction-associated steatohepatitis. Nat Med. 2025;31(9):3128-3140 | 10.1038/s41591-025-03799-0 |
| 9 | Masson W, Lobo M, Nogueira JP, et al. Anti-inflammatory effects of tirzepatide: a systematic review and meta-analysis. Rev Endocr Metab Disord. 2026;27(1):5-15 | 10.1007/s11154-025-09991-4 |

Reference 6 carries the strongest weight independent signal in the corpus: hsCRP fell 37.8%, the reduction preceded weight loss, and it occurred in participants who did not lose weight.

## Weight independent metabolic effects of GCGR agonism

| # | Reference | DOI |
|---|---|---|
| 10 | Ekinci EI, Maldonado SG, Unseld A, et al. Dual Glucagon and GLP-1 Receptor Agonist Survodutide Improves Biomarkers of Beta-Cell Function and Insulin Sensitivity in People With Type 2 Diabetes or Living With Overweight/Obesity. Diabetes Obes Metab. 2026;28(9):8242-8253 | 10.1111/dom.70861 |
| 11 | Banerjee M, Pal R, Pal S. Histological efficacy of anti-diabetic agents in MASH and the mediating role of weight loss: A network meta-analysis. Diabetes Obes Metab. 2026;28(1):287-295 | 10.1111/dom.70187 |

Reference 10 reports improvements in HOMA-IR and adiponectin described as largely independent of bodyweight change. Reference 11 finds weight loss explains 54% of fibrosis improvement, leaving 46% unattributed to any receptor mechanism. That residual is the quantity this project's hepatic meta-regression is built to interrogate.

## Hepatic outcomes by receptor class

| # | Reference | DOI |
|---|---|---|
| 12 | Sanyal AJ, Newsome PN, Kliers I, et al. Phase 3 Trial of Semaglutide in Metabolic Dysfunction-Associated Steatohepatitis. N Engl J Med. 2025;392(21):2089-2099 | 10.1056/NEJMoa2413258 |
| 13 | Loomba R, Hartman ML, Lawitz EJ, et al. Tirzepatide for Metabolic Dysfunction-Associated Steatohepatitis with Liver Fibrosis. N Engl J Med. 2024;391(4):299-310 | 10.1056/NEJMoa2401943 |
| 14 | Sanyal AJ, Bedossa P, Fraessdorf M, et al. A Phase 2 Randomized Trial of Survodutide in MASH and Fibrosis. N Engl J Med. 2024;391(4):311-319 | 10.1056/NEJMoa2401755 |
| 15 | Sanyal AJ, Kaplan LM, Frias JP, et al. Triple hormone receptor agonist retatrutide for metabolic dysfunction-associated steatotic liver disease: a randomized phase 2a trial. Nat Med. 2024;30(7):2037-2048 | 10.1038/s41591-024-03018-2 |

Reference 15 is the retatrutide hepatic anchor: liver fat fell 81.4% at 8 mg and 82.4% at 12 mg, with
86% reaching a normal liver fat fraction at 12 mg against 0% on placebo. Retatrutide has no biopsy
confirmed MASH trial, so its hepatic effect is established at imaging but not histology.

**The plateau argument that stood here is withdrawn and may not be reinstated without new data.** It
read that the near identical effect at 8 and 12 mg, while weight loss continues to increase across
that interval, is a dose response feature arguing against pure weight mediation. Two trial arms at
the top of a dose range cannot carry that inference: the difference between 81.4 and 82.4 per cent
is within the reporting precision, both arms sit near the floor of the measurement, and a ceiling in
the outcome is indistinguishable from a plateau in the mechanism when the outcome cannot fall much
further. The weight mediation question is answered in this review by the hepatic meta-regression
across all trials with the covariate, not by one trial's top two doses.

## Body composition and the unfavorable aging axis

| # | Reference | DOI |
|---|---|---|
| 16 | Locatelli JC, Costa JG, Haynes A, et al. Incretin-Based Weight Loss Pharmacotherapy: Can Resistance Exercise Optimize Changes in Body Composition?. Diabetes Care. 2024;47(10):1718-1730 | 10.2337/dci23-0100 |
| 17 | Linge J, Birkenfeld AL, Neeland IJ. Muscle Mass and Glucagon-Like Peptide-1 Receptor Agonists: Adaptive or Maladaptive Response to Weight Loss?. Circulation. 2024;150(16):1288-1298 | 10.1161/CIRCULATIONAHA.124.067676 |
| 18 | Nong K, Shi Q, Xie X, et al. Comparative effects of drugs for adults with overweight or obesity: systematic review and network meta-analysis. BMJ. 2026;394:e372161 | 10.1136/bmj-2026-372161 |

Reference 16 frames lean mass loss as comparable to a decade or more of aging. Reference 17 distinguishes adaptive from maladaptive muscle change, which is the ambiguity the available data cannot resolve. Reference 18 spans 262 trials and 99,791 participants and reports tirzepatide producing both the largest fat mass reduction and the largest lean mass reduction in the class.

## Off treatment trajectory

| # | Reference | DOI |
|---|---|---|
| 19 | Wilding JPH, Batterham RL, Davies M, et al. Weight regain and cardiometabolic effects after withdrawal of semaglutide: The STEP 1 trial extension. Diabetes Obes Metab. 2022;24(8):1553-1564 | 10.1111/dom.14725 |
| 20 | Aronne LJ, Sattar N, Horn DB, et al. Continued Treatment With Tirzepatide for Maintenance of Weight Reduction in Adults With Obesity: The SURMOUNT-4 Randomized Clinical Trial. JAMA. 2024;331(1):38-48 | 10.1001/jama.2023.24945 |

Off treatment data exist for body weight only. Nothing comparable exists for hepatic fat, inflammatory markers or epigenetic age, for any agent. This is the gap that bounds the metabolic age normalization framework.

## Retatrutide clinical programme

| # | Reference | DOI |
|---|---|---|
| 21 | Coskun T, Urva S, Roell WC, et al. LY3437943, a novel triple glucagon, GIP, and GLP-1 receptor agonist for glycemic control and weight loss: From discovery to clinical proof of concept. Cell Metab. 2022;34(9):1234-1247.e9 | 10.1016/j.cmet.2022.07.013 |
| 22 | Jastreboff AM, Kaplan LM, Frías JP, et al. Triple-Hormone-Receptor Agonist Retatrutide for Obesity - A Phase 2 Trial. N Engl J Med. 2023;389(6):514-526 | 10.1056/NEJMoa2301972 |
| 23 | Rosenstock J, Frias J, Jastreboff AM, et al. Retatrutide, a GIP, GLP-1 and glucagon receptor agonist, for people with type 2 diabetes: a randomised, double-blind, placebo and active-controlled, parallel-group, phase 2 trial conducted in the USA. Lancet. 2023;402(10401):529-544 | 10.1016/S0140-6736(23)01053-X |
| 24 | Bajaj HS, Welch M, Shah P, et al. Efficacy and safety of retatrutide, a GIP, GLP-1, and glucagon receptor agonist, in people with type 2 diabetes and inadequate glycaemic control with diet and exercise (TRANSCEND-T2D-1): a double-blind, randomised, phase 3 trial. Lancet. 2026;407(10546):2402-2413 | 10.1016/S0140-6736(26)00967-0 |
| 25 | Simental-Mendía LE, Barragán-Zúñiga LJ, Reyes-Avitia V. Effect of Retatrutide, a Novel Triple Receptor Agonist, on Blood Pressure and Lipid Levels: A Systematic Review and Meta-analysis of Randomized Controlled Trials. High Blood Press Cardiovasc Prev. 2026;33(5):503-516 | 10.1007/s40292-026-00812-6 |

## Cardiovascular, framing and precedent

| # | Reference | DOI |
|---|---|---|
| 26 | Nicholls SJ, Pavo I, Bhatt DL, et al. Cardiovascular Outcomes with Tirzepatide versus Dulaglutide in Type 2 Diabetes. N Engl J Med. 2025;393(24):2409-2420 | 10.1056/NEJMoa2505928 |
| 27 | Savas M, Kuckuck S, Boon MR, et al. Beyond weight loss: multisystem benefits of obesity medications. Lancet Diabetes Endocrinol. 2026;14(8):678-692 | 10.1016/S2213-8587(26)00100-2 |
| 28 | Paschou IA, Sali E, Paschou SA, et al. GLP-1RA and the possible skin aging. Endocrine. 2025;89(3):680-685 | 10.1007/s12020-025-04293-w |
| 29 | Riddle MC, Cefalu WT, Evans PH, et al. Consensus Report: Definition and Interpretation of Remission in Type 2 Diabetes. Diabetes Care. 2021:dci210034 | 10.2337/dci21-0034 |

Reference 29 is the methodological precedent for the normalization thresholds. It defined remission before prospective trials had tested whether patients meeting the definition experienced different long term outcomes, and the definition was valuable because it converted an unstructured clinical question into a measurable one. The thresholds proposed here are offered in the same spirit and carry the same provisional status.
