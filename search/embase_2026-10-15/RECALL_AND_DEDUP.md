# Embase export: recall against the known corpus, and deduplication

Produced by `src/dedup_embase.py` from the gitignored export. Count gate: 659 TY and 659 ER records; SHA-256 `e8d3a9d4e195…` equals the value in SEARCH_LOG.md.

## Export composition

| Quantity | Value |
|---|---|
| Records | 659 |
| With DOI | 611 |
| Duplicate DOIs within the export | 69 records in 26 DOI groups |
| Duplicate normalised titles within the export | 45 records in 21 title groups |
| Records matching something already in the corpus | 40 |
| Records new to screening | 619 |

## Recall of the Embase string against trials known from other routes

| Known set | Items | Retrieved by Embase | Recall |
|---|---|---|---|
| extracted | 11 | 9 | 82% |
| references | 29 | 8 | 28% |
| Alrasheed2026 | 38 | 28 | 74% |

An item counts as retrieved when a record shares its DOI, or its first author surname and year. Author plus year matches are listed with the matched title so a false match can be seen.

| Set | Item | Matched by | Matched record title |
|---|---|---|---|
| extracted | Anholm 2019 (NCT01595789) | doi | Liraglutide in combination with metformin may improve the atherogenic lipid profile and de |
| extracted | Derosa 2012 (Derosa-2012) | doi | Exenatide plus metformin compared with metformin alone on β-cell function in patients with |
| extracted | Ekinci 2026 (1404-0002) | doi | Dual Glucagon and GLP-1 Receptor Agonist Survodutide Improves Biomarkers of Beta-Cell Func |
| extracted | Meyhofer 2026 (NCT03574597-LIVER) | NOT RETRIEVED |  |
| extracted | Plutzky 2026 (NCT03574597-hsCRP) | doi | Effect of Semaglutide on the Inflammatory Biomarker High-Sensitivity CRP in Patients With  |
| extracted | Sanyal 2024 (NCT04881760-MASLD) | doi | Triple hormone receptor agonist retatrutide for metabolic dysfunction-associated steatotic |
| extracted | Simo 2015 (EUREXA) | doi | Long-term changes in cardiovascular risk markers during administration of exenatide twice  |
| extracted | von Scholten 2017 (NCT02545738) | doi | Effects of liraglutide on cardiovascular risk biomarkers in patients with type 2 diabetes  |
| extracted | Wägner 2019 (LIPER2) | NOT RETRIEVED |  |
| extracted | Wilson 2021 (NCT03131687-BIO) | author+year | The dual gip and GLP-1 receptor agonist tirzepatide improves biomarkers associated with ca |
| extracted | Wu 2011 (Wu-2011) | doi | Effect of exenatide on inflammatory and oxidative stress markers in patients with type 2 d |
| references | REF1 Corley MJ, et al. Semaglutide slows epigenetic aging in a ra | NOT RETRIEVED |  |
| references | REF2 Johnson AA, Sinclair DA. Turning back time: interventions th | NOT RETRIEVED |  |
| references | REF3 Guarente L, Sinclair DA, Kroemer G. Human trials exploring a | NOT RETRIEVED |  |
| references | REF4 Wilson JM, et al. Tirzepatide biomarker analysis. Diabetes O | NOT RETRIEVED |  |
| references | REF5 Konstantinidou SK, et al. Liraglutide and GDF-15. Diabetes O | doi | Total and H-specific growth/differentiation factor 15 levels are unaffected by liraglutide |
| references | REF6 Plutzky J, et al. Effect of semaglutide on hsCRP in SELECT.  | doi | Effect of Semaglutide on the Inflammatory Biomarker High-Sensitivity CRP in Patients With  |
| references | REF7 Maretty L, et al. Proteomic changes upon treatment with sema | doi | Proteomic changes upon treatment with semaglutide in individuals with obesity |
| references | REF8 Jara M, et al. Modulation of metabolic, inflammatory and fib | NOT RETRIEVED |  |
| references | REF9 Masson W, et al. Tirzepatide inflammatory markers. Rev Endoc | doi | Anti-inflammatory effects of tirzepatide: a systematic review and meta-analysis |
| references | REF10 Ekinci EI, et al. Survodutide improves biomarkers of beta-ce | doi | Dual Glucagon and GLP-1 Receptor Agonist Survodutide Improves Biomarkers of Beta-Cell Func |
| references | REF11 Banerjee R, et al. Weight as determinant of MASLD treatment  | NOT RETRIEVED |  |
| references | REF12 Sanyal AJ, et al. Semaglutide for MASH (ESSENCE). N Engl J M | doi | Phase 3 Trial of Semaglutide in Metabolic Dysfunction-Associated Steatohepatitis. |
| references | REF13 Loomba R, et al. Tirzepatide for MASH (SYNERGY-NASH). N Engl | NOT RETRIEVED |  |
| references | REF14 Sanyal AJ, et al. Survodutide for MASH. N Engl J Med. 2024;3 | author+year | Triple hormone receptor agonist retatrutide for metabolic dysfunction-associated steatotic |
| references | REF15 Sanyal AJ, Kaplan LM, Frias JP, et al. Triple hormone recept | doi | Triple hormone receptor agonist retatrutide for metabolic dysfunction-associated steatotic |
| references | REF16 Locatelli JC, et al. Lean mass considerations with GLP-1RAs. | NOT RETRIEVED |  |
| references | REF17 Linge J, et al. Body composition changes with semaglutide. C | NOT RETRIEVED |  |
| references | REF18 Nong K, et al. Comparative effects of drugs for adults with  | NOT RETRIEVED |  |
| references | REF19 Wilding JPH, et al. STEP 1 extension. Diabetes Obes Metab. 2 | NOT RETRIEVED |  |
| references | REF20 Aronne LJ, et al. SURMOUNT-4. JAMA. 2024;331(1):38-48 | NOT RETRIEVED |  |
| references | REF21 Coskun T, Urva S, Roell WC, et al. LY3437943, a novel triple | NOT RETRIEVED |  |
| references | REF22 Jastreboff AM, et al. Triple-hormone-receptor agonist retatr | NOT RETRIEVED |  |
| references | REF23 Rosenstock J, et al. Retatrutide in people with type 2 diabe | NOT RETRIEVED |  |
| references | REF24 Bajaj HS, et al. Retatrutide TRANSCEND-T2D-1 phase 3. Lancet | NOT RETRIEVED |  |
| references | REF25 Simental-Mendia LE, et al. Retatrutide cardiovascular biomar | NOT RETRIEVED |  |
| references | REF26 Nicholls SJ, et al. SURPASS-CVOT tirzepatide vs dulaglutide. | NOT RETRIEVED |  |
| references | REF27 Savas M, et al. Beyond weight loss: multisystem benefits of  | NOT RETRIEVED |  |
| references | REF28 Paschou SA, et al. GLP-1RA and skin aging. Endocrine. 2025 | NOT RETRIEVED |  |
| references | REF29 Riddle MC, et al. Consensus report: definition and interpret | NOT RETRIEVED |  |
| Alrasheed2026 | Ahmad 2021 | author+year+drug | Effects of liraglutide versus sitagliptin on circulating cardiovascular biomarkers, includ |
| Alrasheed2026 | Anholm 2019 | author+year+drug | Liraglutide in combination with metformin may improve the atherogenic lipid profile and de |
| Alrasheed2026 | Bi 2014 | author+year+drug | Effects of exenatide, insulin, and pioglitazone on liver fat content and body fat distribu; Effects of exenatide, insulin, and pioglitazone on liver fat content and body fat distribu |
| Alrasheed2026 | Bouchi 2017 | author+year+drug | Reduction of visceral fat by liraglutide is associated with ameliorations of hepatic steat; Reduction of visceral fat by liraglutide is associated with ameliorations of hepatic steat |
| Alrasheed2026 | Bunck 2010 | author+year+drug | Exenatide affects circulating cardiovascular risk biomarkers independently of changes in b |
| Alrasheed2026 | Derosa 2010 | author+year+drug | Exenatide versus glibenclamide in patients with diabetes |
| Alrasheed2026 | Derosa 2012 | author+year+drug | Exenatide plus metformin compared with metformin alone on β-cell function in patients with |
| Alrasheed2026 | Dutour 2016 | author+year+drug | Exenatide decreases liver fat content and epicardial adipose tissue in patients with obesi; Exenatide led to a significant decrease in liver fat content and epi cardial adipose tissu |
| Alrasheed2026 | Fan 2013 | author+year+drug | Exenatide improves type 2 diabetes concomitant with non-alcoholic fatty liver disease |
| Alrasheed2026 | Forst 2012 | author+year+drug | Addition of liraglutide in patients with Type2 diabetes well controlled on metformin monot |
| Alrasheed2026 | Guarnotta 2021 | NOT RETRIEVED |  |
| Alrasheed2026 | Gurkan 2014 | author+year+drug | Evaluation of exenatide versus insulin glargine for the impact on endothelial functions an |
| Alrasheed2026 | Kang 2021 | NOT RETRIEVED |  |
| Alrasheed2026 | Lambadiari 2018 | NOT RETRIEVED |  |
| Alrasheed2026 | Lambadiari 2021 | NOT RETRIEVED |  |
| Alrasheed2026 | le Roux 2017 | NOT RETRIEVED |  |
| Alrasheed2026 | Liang 2013 | NOT RETRIEVED |  |
| Alrasheed2026 | Liu 2017 | author+year+drug | Efficacy of exenatide on weight loss, metabolic parameters and pregnancy in overweight/obe |
| Alrasheed2026 | Liu 2019 | NOT RETRIEVED |  |
| Alrasheed2026 | Pastel 2017 | author+year+drug | GLP-1 analogue-induced weight loss does not improve obesity-induced AT dysfunction |
| Alrasheed2026 | Quan 2017 | author+year+drug | A crossover study of the combination therapy of metformin and exenatide or biphasic insuli |
| Alrasheed2026 | Santilli 2017 | NOT RETRIEVED |  |
| Alrasheed2026 | Savvidou 2016 | author+year+drug | Circulating adiponectin levels in type 2 diabetes mellitus patients with or without non-al |
| Alrasheed2026 | Shi 2017 | author+year+drug | Comparison of exenatide and acarbose on intra-abdominal fat content in patients with obesi |
| Alrasheed2026 | Simó 2015 | author+year+drug | Long-term changes in cardiovascular risk markers during administration of exenatide twice  |
| Alrasheed2026 | Suzuki 2014 | author+year+drug | Greater efficacy and improved endothelial dysfunction in untreated type 2 diabetes with li |
| Alrasheed2026 | Takeshita 2015 | author+year+drug | Vildagliptin vs liraglutide as a second-line therapy switched from sitagliptin-based regim |
| Alrasheed2026 | Tian 2018 | author+year+drug | Efficacy of liraglutide in treating type 2 diabetes mellitus complicated with non-alcoholi |
| Alrasheed2026 | von Scholten 2017 | author+year+drug | Effects of liraglutide on cardiovascular risk biomarkers in patients with type 2 diabetes  |
| Alrasheed2026 | Wang 2019 | author+year+drug | The Effects of Once-Weekly Dulaglutide and Insulin Glargine on Glucose Fluctuation in Poor |
| Alrasheed2026 | Wang 2020 | author+year+drug | Comparison between the effects of sitagliptin and liraglutide on blood glucose and cogniti; Effect of vildagliptin combined with liraglutide on bmi, hbalc and fbg in diabetic patient |
| Alrasheed2026 | Wu 2011 | author+year+drug | Effect of exenatide on inflammatory and oxidative stress markers in patients with type 2 d |
| Alrasheed2026 | Wägner 2019 | NOT RETRIEVED |  |
| Alrasheed2026 | Xie 2022 | author+year+drug | Effects of dulaglutide on endothelial progenitor cells and arterial elasticity in patients |
| Alrasheed2026 | Yan 2019 | author+year+drug | Liraglutide, Sitagliptin, and Insulin Glargine Added to Metformin: The Effect on Body Weig |
| Alrasheed2026 | Yao 2020 | author+year+drug | Use of flash glucose-sensing technology in patients with type 2 diabetes treated with lira |
| Alrasheed2026 | Ying 2023 | author+year+drug | Liraglutide ameliorates oxidized LDL-induced endothelial dysfunction by GLP-1R-dependent d |
| Alrasheed2026 | Zhang 2018 | NOT RETRIEVED |  |

Per record flags (matched_known, duplicate DOI, duplicate title) are in `embase_659_dedup.csv`, which stays untracked beside the export.


## Manual reading of the automated matches, 2026-10-15

The author, year and drug rule is a screen, not an identity. Read against the titles above, three of the 28 Alrasheed matches are not the trial Alrasheed included: Liu 2017 (the retrieved record is exenatide in overweight women with PCOS; Alrasheed's Liu 2017 is liraglutide 1.2 mg against metformin), Ying 2023 (the retrieved record is a mechanistic endothelial study; Alrasheed's is a gut microbiota trial), and Yao 2020 (flash glucose monitoring; Alrasheed's is CSII plus liraglutide, same group, possibly the same trial, unresolved). Counting those as misses, the recall of the Embase string against the 38 adopted mono agonist trials is 25 of 38 (66 per cent); against the 11 extracted papers it is 9 of 11, the two misses being Meyhofer 2026 (liver enzymes, no inflammatory index term) and Wägner 2019 (physical performance trial, CRP incidental).

Reading of the misses: every trial the string failed to retrieve reports the biomarker as an incidental or secondary measurement that Embase did not index under the Emtree terms in line 2 (C reactive protein, interleukin 6, TNF alpha, adiponectin, leptin, GDF-15). The drug and RCT lines are not the problem. The string therefore has high precision for trials that are about inflammation and limited recall for trials that merely report it, which is exactly the population that Stream B (the adopted lists) supplies. Two consequences for the Methods: the Embase search cannot be described as exhaustive for incidental biomarker reporting, and any CENTRAL or Web of Science run with the same biomarker line will have the same ceiling. A broader line (drug AND RCT without the biomarker terms) would return of the order of ten thousand records and is a screening capacity decision for the Lab Director, not a correction to make silently.

Within export duplicates (26 DOI groups, 69 records) are mostly conference abstracts carrying the DOI of the later article; they are flagged per record and collapse at title and abstract screening.
