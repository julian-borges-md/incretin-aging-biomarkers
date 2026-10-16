# CENTRAL export: recall against the known corpus, and deduplication

Produced by `src/dedup_embase.py` from the gitignored export. Count gate: 460 TY and 460 ER records; SHA-256 `7c12c8811563…` equals the value in SEARCH_LOG.md.

## Export composition

| Quantity | Value |
|---|---|
| Records | 460 |
| With DOI | 287 |
| Duplicate DOIs within the export | 54 records in 23 DOI groups |
| Duplicate normalised titles within the export | 40 records in 19 title groups |
| Records matching something already in the corpus | 36 |
| Records new to screening | 424 |

## Recall of the CENTRAL string against trials known from other routes

| Known set | Items | Retrieved by CENTRAL | Recall |
|---|---|---|---|
| extracted | 11 | 8 | 73% |
| references | 29 | 4 | 14% |
| Alrasheed2026 | 38 | 26 | 68% |

An item counts as retrieved when a record shares its DOI, or its first author surname and year. Author plus year matches are listed with the matched title so a false match can be seen.

| Set | Item | Matched by | Matched record title |
|---|---|---|---|
| extracted | Anholm 2019 (NCT01595789) | doi | Liraglutide in combination with metformin may improve the atherogenic lipid profile and de |
| extracted | Derosa 2012 (Derosa-2012) | doi | Exenatide plus metformin compared with metformin alone on β-cell function in patients with |
| extracted | Ekinci 2026 (1404-0002) | doi | Dual Glucagon and GLP-1 Receptor Agonist Survodutide Improves Biomarkers of Beta-Cell Func |
| extracted | Meyhofer 2026 (NCT03574597-LIVER) | NOT RETRIEVED |  |
| extracted | Plutzky 2026 (NCT03574597-hsCRP) | doi | Effect of Semaglutide on the Inflammatory Biomarker High-Sensitivity CRP in Patients With  |
| extracted | Sanyal 2024 (NCT04881760-MASLD) | NOT RETRIEVED |  |
| extracted | Simo 2015 (EUREXA) | doi | Long-term changes in cardiovascular risk markers during administration of exenatide twice  |
| extracted | von Scholten 2017 (NCT02545738) | doi | Effects of liraglutide on cardiovascular risk biomarkers in patients with type 2 diabetes  |
| extracted | Wägner 2019 (LIPER2) | NOT RETRIEVED |  |
| extracted | Wilson 2021 (NCT03131687-BIO) | doi | The dual glucose-dependent insulinotropic polypeptide and glucagon-like peptide-1 receptor |
| extracted | Wu 2011 (Wu-2011) | doi | Effect of exenatide on inflammatory and oxidative stress markers in patients with type 2 d |
| references | REF1 Corley MJ, et al. Semaglutide slows epigenetic aging in a ra | NOT RETRIEVED |  |
| references | REF2 Johnson AA, Sinclair DA. Turning back time: interventions th | NOT RETRIEVED |  |
| references | REF3 Guarente L, Sinclair DA, Kroemer G. Human trials exploring a | NOT RETRIEVED |  |
| references | REF4 Wilson JM, et al. Tirzepatide biomarker analysis. Diabetes O | doi | The dual glucose-dependent insulinotropic polypeptide and glucagon-like peptide-1 receptor |
| references | REF5 Konstantinidou SK, et al. Liraglutide and GDF-15. Diabetes O | doi | Total and H-specific growth/differentiation factor 15 levels are unaffected by liraglutide |
| references | REF6 Plutzky J, et al. Effect of semaglutide on hsCRP in SELECT.  | doi | Effect of Semaglutide on the Inflammatory Biomarker High-Sensitivity CRP in Patients With  |
| references | REF7 Maretty L, et al. Proteomic changes upon treatment with sema | NOT RETRIEVED |  |
| references | REF8 Jara M, et al. Modulation of metabolic, inflammatory and fib | NOT RETRIEVED |  |
| references | REF9 Masson W, et al. Tirzepatide inflammatory markers. Rev Endoc | NOT RETRIEVED |  |
| references | REF10 Ekinci EI, et al. Survodutide improves biomarkers of beta-ce | doi | Dual Glucagon and GLP-1 Receptor Agonist Survodutide Improves Biomarkers of Beta-Cell Func |
| references | REF11 Banerjee R, et al. Weight as determinant of MASLD treatment  | NOT RETRIEVED |  |
| references | REF12 Sanyal AJ, et al. Semaglutide for MASH (ESSENCE). N Engl J M | NOT RETRIEVED |  |
| references | REF13 Loomba R, et al. Tirzepatide for MASH (SYNERGY-NASH). N Engl | NOT RETRIEVED |  |
| references | REF14 Sanyal AJ, et al. Survodutide for MASH. N Engl J Med. 2024;3 | NOT RETRIEVED |  |
| references | REF15 Sanyal AJ, Kaplan LM, Frias JP, et al. Triple hormone recept | NOT RETRIEVED |  |
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
| Alrasheed2026 | Forst 2012 | author+year+drug | Addition of liraglutide in patients with Type 2 diabetes well controlled on metformin mono |
| Alrasheed2026 | Guarnotta 2021 | NOT RETRIEVED |  |
| Alrasheed2026 | Gurkan 2014 | author+year+drug | Evaluation of exenatide versus insulin glargine for the impact on endothelial functions an |
| Alrasheed2026 | Kang 2021 | author+year+drug | Effects of exenatide on urinary albumin in overweight/obese patients with T2DM: a randomiz |
| Alrasheed2026 | Lambadiari 2018 | NOT RETRIEVED |  |
| Alrasheed2026 | Lambadiari 2021 | NOT RETRIEVED |  |
| Alrasheed2026 | le Roux 2017 | NOT RETRIEVED |  |
| Alrasheed2026 | Liang 2013 | NOT RETRIEVED |  |
| Alrasheed2026 | Liu 2017 | NOT RETRIEVED |  |
| Alrasheed2026 | Liu 2019 | NOT RETRIEVED |  |
| Alrasheed2026 | Pastel 2017 | author+year+drug | GLP-1 analogue-induced weight loss does not improve obesity-induced AT dysfunction |
| Alrasheed2026 | Quan 2017 | NOT RETRIEVED |  |
| Alrasheed2026 | Santilli 2017 | NOT RETRIEVED |  |
| Alrasheed2026 | Savvidou 2016 | author+year+drug | Circulating adiponectin levels in type 2 diabetes mellitus patients with or without non-al |
| Alrasheed2026 | Shi 2017 | author+year+drug | Comparison of exenatide and acarbose on intra-abdominal fat content in patients with obesi |
| Alrasheed2026 | Simó 2015 | author+year+drug | Long-term changes in cardiovascular risk markers during administration of exenatide twice  |
| Alrasheed2026 | Suzuki 2014 | author+year+drug | Greater efficacy and improved endothelial dysfunction in untreated type 2 diabetes with li |
| Alrasheed2026 | Takeshita 2015 | author+year+drug | Vildagliptin vs liraglutide as a second-line therapy switched from sitagliptin-based regim |
| Alrasheed2026 | Tian 2018 | author+year+drug | Efficacy of liraglutide in treating type 2 diabetes mellitus complicated with non-alcoholi |
| Alrasheed2026 | von Scholten 2017 | author+year+drug | Effects of liraglutide on cardiovascular risk biomarkers in patients with type 2 diabetes  |
| Alrasheed2026 | Wang 2019 | author+year+drug | The Effects of Once-Weekly Dulaglutide and Insulin Glargine on Glucose Fluctuation in Poor |
| Alrasheed2026 | Wang 2020 | author+year+drug | Comparison between the effects of sitagliptin and liraglutide on blood glucose and cogniti; Comparison between the effects of sitagliptin and liraglutide on blood glucose and cogniti |
| Alrasheed2026 | Wu 2011 | author+year+drug | Effect of exenatide on inflammatory and oxidative stress markers in patients with type 2 d |
| Alrasheed2026 | Wägner 2019 | NOT RETRIEVED |  |
| Alrasheed2026 | Xie 2022 | author+year+drug | Effects of dulaglutide on endothelial progenitor cells and arterial elasticity in patients |
| Alrasheed2026 | Yan 2019 | NOT RETRIEVED |  |
| Alrasheed2026 | Yao 2020 | author+year+drug | Use of flash glucose-sensing technology in patients with type 2 diabetes treated with lira |
| Alrasheed2026 | Ying 2023 | NOT RETRIEVED |  |
| Alrasheed2026 | Zhang 2018 | author+year+drug | Effect of exenatide on carotid intima-media thickness and the biomarkers of atherosclerosi; Liraglutide ameliorates beta-cell function, alleviates oxidative stress and inhibits low g |

## Overlap with the Embase export

| Quantity | Value |
|---|---|
| Embase records compared | 659 |
| CENTRAL records also in Embase, matched by DOI | 236 |
| CENTRAL records also in Embase, matched by normalised title only | 24 |
| CENTRAL records not in the Embase export | 200 |

A title match without a DOI match is a candidate duplicate, not a confirmed one; the per record flag names the route.


Per record flags (matched_known, duplicate DOI, duplicate title, in_embase_export) are in `central_460_dedup.csv`, which stays untracked beside the export.


## Manual reading of the automated matches, 2026-10-15

The author, year and drug rule is a screen, not an identity. Each of the 26 automated Alrasheed matches was read against the intervention and comparator columns of `search/known_relevant_trials.csv`. Twenty five are consistent with the trial Alrasheed included (for example Derosa 2010 exenatide versus glibenclamide, Savvidou 2016 exenatide plus glargine with adiponectin as the outcome, Takeshita 2015 liraglutide versus vildagliptin, Wang 2019 dulaglutide versus glargine, Wang 2020 sitagliptin versus liraglutide, Pastel 2017 liraglutide versus calorie restriction; Zhang 2018 matched two records of which the liraglutide versus metformin record is the right one). Yao 2020 is the same unresolved case as in the Embase reading (flash glucose monitoring under liraglutide; Alrasheed's is CSII plus liraglutide, same group, possibly the same trial) and is counted as a miss. Recall of the CENTRAL strategy against the 38 adopted mono agonist trials is therefore 25 of 38 (66 per cent), the same ceiling as Embase; against the 11 extracted papers it is 8 of 11, the misses being Meyhofer 2026, Sanyal 2024 and Wägner 2019.

Across the two databases the union reaches 27 of 38: CENTRAL adds Kang 2021 and Zhang 2018, Embase alone holds Quan 2017 and Yan 2019. Eleven trials are in neither (Guarnotta 2021, Lambadiari 2018 and 2021, le Roux 2017, Liang 2013, Liu 2017 and 2019, Santilli 2017, Wägner 2019, Ying 2023, and Yao 2020 as unresolved). The free text and abbreviation line in CENTRAL did not raise the ceiling set by the biomarker concept itself: trials that measure CRP or TNF alpha incidentally do not name them in the title, abstract or keywords either.

Within export duplicates (23 DOI groups, 54 records) are mostly conference abstracts that share the DOI of a meeting supplement (Diabetologia EASD abstract volumes, Obesity supplements), so a shared DOI there is not one study; a few groups are the same article delivered twice with different hyphenation. They are flagged per record and resolved at title and abstract screening, not collapsed by DOI.
