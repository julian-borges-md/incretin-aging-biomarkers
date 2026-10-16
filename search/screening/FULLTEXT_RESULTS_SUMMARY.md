# Full text screen, study level view

Record outcomes from `fulltext_decisions_A.csv`, `fulltext_decisions_B.csv` and `fulltext_adjudication_002.csv` rolled up to the candidate study groups of `FULLTEXT_POOL_SUMMARY.md`. Produced by `src/fulltext_results.py`; the per group table is the untracked `fulltext_results_2026-10-16.csv`. A group is included when any of its records is included at full text; an exclusion settles a group only when none of its records is still without a text.

Snapshot taken 2026-10-16 14:23 EDT; screening complete.

| Record outcome | Records |
|---|---|
| include | 435 |
| exclude | 118 |
| pending | 0 |
| no_text | 3 |
| already_extracted | 20 |
| total | 576 |

| Study group status | Groups |
|---|---|
| included | 338 |
| pending | 0 |
| excluded | 113 |
| excluded_but_untexted_record | 0 |
| no_text | 3 |
| already_extracted | 13 |
| total | 467 |

| Included groups by best text | Groups |
|---|---|
| with a full text (Europe PMC, publisher page, institutional route) | 148 |
| abstract, registry entry or partial page only | 190 |
| known relevant (adopted list) among included groups | 27 |

| Biomarker | Named by a reviewer in an included group | Named and mentioned in the text (lexicon scan) |
|---|---|---|
| crp | 266 | 204 |
| hba1c | 176 | 126 |
| tg | 137 | 92 |
| adiponectin | 130 | 76 |
| ldl | 121 | 69 |
| glucose | 115 | 65 |
| il6 | 119 | 54 |
| tnf | 106 | 51 |
| tc | 99 | 47 |
| bp | 91 | 45 |
| alt | 112 | 41 |
| insulin | 95 | 39 |
| leptin | 81 | 35 |
| homa_ir | 119 | 34 |
| ast | 89 | 26 |
| glucagon | 55 | 25 |
| liver_fat | 91 | 23 |
| cpeptide | 71 | 19 |
| body_fat | 96 | 18 |
| egfr | 62 | 18 |
| ntprobnp | 65 | 18 |
| vat | 56 | 13 |
| gdf15 | 61 | 12 |
| ggt | 66 | 12 |
| lean_mass | 80 | 8 |
| homa_beta | 68 | 7 |
| icam1 | 55 | 6 |
| heart_rate | 29 | 5 |
| mash | 18 | 3 |
| bmd | 41 | 3 |

The second column is the one to use: the reviewers echo the example list of the prompt, so a name without a mention in the text is not evidence (audit in `BIOMARKER_SCAN_SUMMARY.md`). Included groups whose included records mention no inventory biomarker at all: 1 (flagged `no_inventory_mention` in the CSV; these rest on the rule that an unjudgeable criterion includes).

## Included study groups

| Group | Records | Years | Text | Duration (weeks, as read) | Comparator (as read) | Identifiers | Known | Title |
|---|---|---|---|---|---|---|---|---|
| 10 | 1 (1 inc) | 2026 | full text | 60 | placebo | 10.1001/jama.2026.8142 | no | Treatment With 9-mg Mazdutide for Weight Reduction in Chinese Adults With Obesity |
| 101 | 1 (1 inc) | 2024 | full text | 52 | placebo, exercise, liraglutide, combined exercise and liragl | 10.1016/j.xcrm.2024.101629 | no | Weight-loss maintenance is accompanied by interconnected alterations in circulating FGF21- |
| 102 | 1 (1 inc) | 2024 | full text | 52 | placebo | 10.1016/j.jacc.2024.04.022 | no | Semaglutide and NT-proBNP in Obesity-Related HFpEF: Insights From the STEP-HFpEF Program |
| 103 | 1 (1 inc) | 2024 | full text | 52 | placebo | 10.1111/apt.18042 | no | Randomised clinical trial: Design of the SYNERGY-NASH phase 2b trial to evaluate tirzepati |
| 107 | 1 (1 inc) | 2024 | full text | 52 | empagliflozin, placebo;semaglutide, empagliflozin and semagl | 10.1371/journal.pone.0302155 | no | Semaglutide combined with empagliflozin vs. monotherapy for non-alcoholic fatty liver dise |
| 112 | 1 (1 inc) | 2024 | full text | 24;26 | conventional treatment;conventional treatment of cardiovascu | 10.1001/jamanetworkopen.2024.1545;NCT04881110 | no | Liraglutide for Lower Limb Perfusion in People With Type 2 Diabetes and Peripheral Artery  |
| 113 | 1 (1 inc) | 2024 | full text | 104;68 | placebo | 10.1111/dom.15386 | no | Efficacy and safety of semaglutide 2.4 mg for weight loss in overweight or obese adults wi |
| 114 | 1 (1 inc) | 2024 | full text | 24 |  cpap plus liraglutide;cpap;cpap, placebo;liraglutide, combi | 10.1513/annalsats.202309-821oc | no | Continuous Positive Airway Pressure but Not GLP1-mediated Weight Loss Improves Early Cardi |
| 116 | 1 (1 inc) | 2024 | full text | 52 | placebo | 10.1161/circulationaha.123.067505 | no | Effects of Semaglutide on Symptoms, Function, and Quality of Life in Patients With Heart F |
| 117 | 1 (1 inc) | 2024 | full text |  |  | 10.1007/s12020-023-03487-4;NCT03151005 | no | Effects and plasma proteomic analysis of GLP-1RA versus CPA/EE, in combination with metfor |
| 12 | 1 (1 inc) | 2026 | full text | 16 | metformin | 10.1111/dom.70966 | no | Short-Term Combined Treatment With Tirzepatide and Metformin for Overweight/Obese Chinese  |
| 120 | 1 (1 inc) | 2023 | full text |  |  | 10.1038/s41467-023-44067-4;NCT04904913 | no | A phase 2 randomised controlled trial of mazdutide in Chinese overweight adults or adults  |
| 126 | 2 (2 inc) | 2023 | full text | 68 | placebo | 10.1002/oby.23939;10.1016/s0140-6736(23)01185-6;NCT05035095 | no | Oral semaglutide 50 mg taken once per day in adults with overweight or obesity (OASIS 1):  |
| 127 | 1 (1 inc) | 2023 | full text | 32 | semaglutide and placebo, cagrilintide and placebo;semaglutid | 10.1016/s0140-6736(23)01291-6 | no | CagriSema and the link between obesity and type 2 diabetes |
| 13 | 1 (1 inc) | 2026 | full text |  |  | 10.1113/ep093787 | no | Effects of tumour necrosis factor and interleukin-6 inhibitor therapy on exercise-related  |
| 130 | 1 (1 inc) | 2023 | full text | 48 | placebo | 10.1016/s2468-1253(23)00068-7;NCT03987451 | no | Semaglutide 2·4 mg once weekly in patients with non-alcoholic steatohepatitis-related cirr |
| 131 | 1 (1 inc) | 2023 | full text | 24;26 | lifestyle interventions | 10.3892/etm.2023.11948 | no | Effect of liraglutide on atherosclerosis in patients with impaired glucose tolerance: A do |
| 132 | 1 (1 inc) | 2023 | full text | 24 |  cpap plus liraglutide;cpap;cpap or placebo;liraglutide, cpa | 10.1101/2023.05.23.23290424;NCT04186494 | no | Continuous positive airway pressure but not Liraglutide-mediated weight loss improves earl |
| 133 | 1 (1 inc) | 2023 | full text | 104;208 | placebo | 10.2337/dc22-2397 | no | Biomarker changes associated with both dulaglutide and cardiovascular events in the rewind |
| 135 | 1 (1 inc) | 2023 | full text | 40 | placebo | 10.1210/jendso/bvad056 | no | Tirzepatide as Monotherapy Improved Markers of Beta-cell Function and Insulin Sensitivity  |
| 137 | 1 (1 inc) | 2023 | full text | 68 | placebo;placebo, semaglutide 1.0 mg | 10.1016/j.eclinm.2022.101737 | no | Effects of once-weekly semaglutide 2.4 mg on C-reactive protein in adults with overweight  |
| 138 | 1 (1 inc) | 2023 | full text | 16 | placebo | 10.1177/20420188231207348;NCT04979130 | no | Design and rationale for the SIB trial: a randomized parallel comparison of semaglutide ve |
| 14 | 3 (3 inc) | 2024 to 2026 | full text | 240;72 | placebo | 10.1007/s12072-026-11095-3;10.1111/apt.18331;10.20517/mtod.2 | no | Semaglutide demonstrates efficacy in improving liver fibrosis across diverse subpopulation |
| 142 | 1 (1 inc) | 2022 | full text | 26 | placebo, exenatide extended-release, empagliflozin;placebo,  | 10.1186/s12933-022-01585-7;NCT01885208;NCT02827708;NCT028633 | no | Impact of semaglutide on high-sensitivity C-reactive protein: exploratory patient-level an |
| 143 | 1 (1 inc) | 2022 | full text |  |  | 10.1186/s12933-022-01634-1 | yes | Effects of dulaglutide on endothelial progenitor cells and arterial elasticity in patients |
| 147 | 1 (1 inc) | 2022 | full text |  |  | 10.1016/j.metabol.2022.155237 | no | Circulating total and intact GDF-15 levels are not altered in response to weight loss indu |
| 149 | 1 (1 inc) | 2022 | full text | 52 | insulin aspartate 70/30 | 10.1136/jim-2021-002237 | no | Comparing the effects of twice-daily exenatide and insulin on renal function in patients w |
| 15 | 5 (5 inc) | 2025 to 2026 | full text | 104;52 | placebo | 10.1016/j.jacc.2025.03.009;10.1016/j.jacc.2025.04.059;10.101 | no | Influence of Type 2 Diabetes on the Effects of Tirzepatide in Patients With Heart Failure  |
| 150 | 1 (1 inc) | 2022 | full text | 16 | placebo | 10.1017/s1092852920002217 | no | Proinflammatory biomarkers are associated with prediabetes in patients with schizophrenia |
| 151 | 1 (1 inc) | 2022 | full text | 12 | conventional dn medications | 10.12669/pjms.38.5.4719 | no | Effects of glucagon-like peptide-1 receptor agonists (GLP-1RAs) on podocytes, inflammation |
| 154 | 1 (1 inc) | 2022 | full text | 40 | placebo | 10.2147/copd.s350133 | no | Respiratory Effects of Treatment with a Glucagon-Like Peptide-1 Receptor Agonist in Patien |
| 155 | 1 (1 inc) | 2022 | full text | 52 | insulin;metformin | 10.1155/2022/7128859 | no | Efficacy of Exenatide Administered Twice Daily in Body Mass Index Reduction in Patients wi |
| 156 | 1 (1 inc) | 2022 | full text | 12 | liraglutide;liraglutide and dapagliflozin | 10.36468/pharmaceutical-sciences.976 | no | Clinical Efficacy Evaluation and Long-Term Prognosis of Glucagon-Like Peptide-1 Combined w |
| 157 | 1 (1 inc) | 2021 | full text | 12 | metformin | 10.1097/cm9.0000000000001712;NCT04029272 | no | Short-term combined treatment with exenatide and metformin for overweight/obese women with |
| 159 | 1 (1 inc) | 2021 | full text | 26 | placebo | 10.3389/fendo.2021.790405 | no | Effect of 26 Weeks of Liraglutide Treatment on Coronary Artery Inflammation in Type 2 Diab |
| 16 | 1 (1 inc) | 2026 | full text | 24 | canagliflozin, placebo;placebo, canagliflozin, semaglutide | 10.36721/pjps.2026.39.7.204.1 | no | Short-term comparative effects of semaglutide, either alone or in conjunction with canagli |
| 160 | 3 (3 inc) | 2020 to 2021 | full text | 24;72 | placebo;placebo, cilofexor, firsocostat;sema alone, sema+cil | 10.1002/hep.32188;10.1016/j.cct.2020.106174;NCT02970942 | no | Combination treatments including cilofexor and/or firsocostat in addition to semaglutide l |
| 163 | 1 (1 inc) | 2021 | full text | 180;26 | placebo | 10.1002/ehf2.13348 | no | Growth differentiation factor-15, treatment with liraglutide, and clinical outcomes among  |
| 164 | 1 (1 inc) | 2021 | full text | 26 | placebo | 10.3390/diagnostics11081431 | no | Effect of liraglutide on vascular inflammation evaluated by [64 cu]dotatate |
| 165 | 1 (1 inc) | 2021 | full text | 26 | sitagliptin | 10.1111/dom.14343 | yes | Effects of liraglutide versus sitagliptin on circulating cardiovascular biomarkers, includ |
| 168 | 1 (1 inc) | 2021 | full text | 68 | placebo | 10.1056/nejmoa2032183 | no | Once-weekly semaglutide in adults with overweight or obesity |
| 169 | 1 (1 inc) | 2021 | full text | 16 | placebo | 10.1002/jgh3.12464 | no | Liraglutide reduces attenuation coefficient as a measure of hepatic steatosis during 16 we |
| 17 | 1 (1 inc) | 2026 | full text | 12 | standard therapy | 10.1161/strokeaha.125.056010;NCT03948347 | no | Liraglutide and Recurrent Stroke by Baseline Insulin Resistance: A Post Hoc Analysis of th |
| 172 | 1 (1 inc) | 2020 | full text | 52 | insulin aspart 70/30 | 10.1186/s12933-020-01014-7 | no | Comparison of the effects of twice-daily exenatide and insulin on carotid intima-media thi |
| 174 | 1 (1 inc) | 2020 | full text | 26 | placebo | 10.1007/s00125-019-05021-6;NCT01761318 | no | Placebo-controlled randomised trial with liraglutide on magnetic resonance endpoints in in |
| 176 | 1 (1 inc) | 2020 | full text |  |  | 10.14341/omet12274 | no | Prediction of Early Response to Liraglutide Therapy in Patients with Obesity |
| 177 | 1 (1 inc) | 2020 | full text | 16 | placebo | 10.1093/schizbullopen/sgaa044 | no | Leptin Serum Levels are Associated With GLP-1 Receptor Agonist-Mediated Effects on Glucose |
| 18 | 5 (4 inc) | 2018 to 2026 | full text | 52 | placebo (with or without exercise);placebo, exercise;placebo | 10.1038/s42255-026-01554-4;10.1093/humrep/deac096;10.1186/s1 | no | Combination of exercise and GLP-1 receptor agonist treatment reduces severity of metabolic |
| 183 | 1 (1 inc) | 2019 | full text | 26 | liraglutide, sitagliptin, insulin glargine;sitagliptin, insu | 10.1002/hep.30320 | yes | Liraglutide, Sitagliptin, and Insulin Glargine Added to Metformin: The Effect on Body Weig |
| 185 | 1 (1 inc) | 2019 | full text | 24 | placebo | 10.1002/osp4.324 | no | Effect of liraglutide on anthropometric measurements, sagittal abdominal diameter and adip |
| 187 | 1 (1 inc) | 2019 | full text | 52 | glargine | 10.1155/2019/2682657;NCT01648582 | yes | The Effects of Once-Weekly Dulaglutide and Insulin Glargine on Glucose Fluctuation in Poor |
| 188 | 1 (1 inc) | 2019 | full text | 26 | glimepiride | 10.1155/2019/6423987 | no | A randomized study to compare the effects of once-weekly dulaglutide injection and once-da |
| 189 | 1 (1 inc) | 2018 | full text | 12 | metformin | 10.1042/bsr20181304 | yes | Efficacy of liraglutide in treating type 2 diabetes mellitus complicated with non-alcoholi |
| 19 | 1 (1 inc) | 2026 | full text | 104 | placebo | 10.1002/dad2.70432 | no | Semaglutide attenuates a proteomics-based dementia risk signature in older adults with ove |
| 190 | 1 (1 inc) | 2018 | full text | 16;168 | lifestyle changes;lifestyle counseling | 10.3390/nu10121872 | no | Thromboxane-dependent platelet activation in obese subjects with prediabetes or early type |
| 199 | 1 (1 inc) | 2018 | full text | 48 | low dose exenatide/metformin/biphasic insulin aspart;low-dos | 10.1097/mjt.0000000000000431 | no | Phase III Study on Efficacy and Safety of Triple Combination (Exenatide/Metformin/Biphasic |
| 2 | 2 (2 inc) | 2024 to 2026 | full text | 28 | diet and lifestyle;dietary and lifestyle modifications alone | 10.1002/ueg2.12613;10.1007/s12664-025-01856-7;NCT05442450 | no | EFFICACY and SAFETY of ORAL SEMAGLUTIDE in COMBINATION with DIETARY and LIFESTYLE MODIFICA |
| 200 | 1 (1 inc) | 2018 | full text | 26 | placebo | 10.1111/dom.13053 | no | Effect of liraglutide on ectopic fat in polycystic ovary syndrome: A randomized clinical t |
| 202 | 1 (1 inc) | 2017 | full text | 12;24 | metformin | 10.1111/cen.13454 | yes | Efficacy of exenatide on weight loss, metabolic parameters and pregnancy in overweight/obe |
| 203 | 1 (1 inc) | 2017 | full text | 36 | metformin and biphasic insulin aspart 30 or metformin and ex | 10.3892/etm.2017.4863 | yes | A crossover study of the combination therapy of metformin and exenatide or biphasic insuli |
| 204 | 1 (1 inc) | 2017 | full text | 12 | acarbose | 10.1016/j.orcp.2017.01.003 | yes | Comparison of exenatide and acarbose on intra-abdominal fat content in patients with obesi |
| 205 | 1 (1 inc) | 2017 | full text | 12 | metformin | 10.1016/j.obmed.2017.06.003 | no | Short term monotherapy with exenatide is superior to metformin in weight loss, improving i |
| 206 | 3 (3 inc) | 2016 to 2017 | full text | 24;26 |  insulin glargine u100;insulin degludec;insulin degludec and | 10.1007/s00125-017-4350-z;10.1016/j.conctc.2016.06.007 | no | IDegLira improves cardiovascular risk markers in patients with type 2 diabetes uncontrolle |
| 212 | 1 (1 inc) | 2017 | full text | 30 | insulin glargine | 10.1016/s2213-8587(17)30085-2;NCT02128932 | no | Efficacy and safety of once-weekly semaglutide versus once-daily insulin glargine as add-o |
| 213 | 1 (1 inc) | 2017 | full text | 16 | diet;dietetic counselling | 10.1042/cs20160803 | yes | GLP-1 analogue-induced weight loss does not improve obesity-induced AT dysfunction |
| 214 | 1 (1 inc) | 2017 | full text | 24 | insulin | 10.1507/endocrj.ej16-0449 | yes | Reduction of visceral fat by liraglutide is associated with ameliorations of hepatic steat |
| 224 | 1 (1 inc) | 2016 | full text | 26 | intense insulin therapy;intense insulin therapy (active) | 10.1016/j.diabres.2015.12.003 | yes | Circulating adiponectin levels in type 2 diabetes mellitus patients with or without non-al |
| 225 | 3 (3 inc) | 2013 to 2016 | full text | 12 | placebo | 10.1002/hep.26849;10.1016/j.jhep.2015.08.038;NCT01237119 | no | Glucagon like peptide 1 analogue, liraglutide, reduces adipose insulin resistance and hepa |
| 23 | 3 (3 inc) | 2025 to 2026 | full text | 32 | placebo | 10.1093/cid/ciaf577;10.1093/ofid/ofaf152;10.1097/qad.0000000 | no | The Effects of Semaglutide on Inflammation and Immune Activation in HIV-associated Lipohyp |
| 237 | 1 (1 inc) | 2015 | full text | 52 | control group (no glp-1ra);placebo | 10.1038/ijo.2014.177 | no | Treatment with a GLP-1 receptor agonist diminishes the decrease in free plasma leptin duri |
| 239 | 1 (1 inc) | 2014 | full text | 26 | insulin glargine | 10.1016/j.diabres.2014.09.046 | yes | Evaluation of exenatide versus insulin glargine for the impact on endothelial functions an |
| 24 | 1 (1 inc) | 2026 | full text | 156 | placebo | 10.1001/jamacardio.2026.0245 | no | Oral Semaglutide and Change in Cardiovascular Risk Factors in High-Risk Type 2 Diabetes: A |
| 243 | 1 (1 inc) | 2015 | full text | 16 | glimepiride;glimepiride and metformin | 10.1016/j.diabres.2015.05.051 | no | Liraglutide treatment causes upregulation of adiponectin and downregulation of resistin in |
| 249 | 1 (1 inc) | 2014 | full text | 24 | insulin, pioglitazone | 10.1007/s00592-014-0638-3 | yes | Effects of exenatide, insulin, and pioglitazone on liver fat content and body fat distribu |
| 25 | 1 (1 inc) | 2026 | full text | 72 | placebo | 10.1093/eurheartjsupp/suag029 | no | Pharmacological therapy in the obese patient: is it only a matter of fat loss? |
| 250 | 1 (1 inc) | 2014 | full text | 24 | sitagliptin |  | yes | Greater efficacy and improved endothelial dysfunction in untreated type 2 diabetes with li |
| 252 | 1 (1 inc) | 2013 | full text | 26 | insulin detemir | 10.2337/dc12-1333 | no | Once-weekly exenatide versus once- or twice-daily insulin detemir |
| 253 | 1 (1 inc) | 2013 | full text | 12 | metformin |  | yes | Exenatide improves type 2 diabetes concomitant with non-alcoholic fatty liver disease |
| 254 | 1 (1 inc) | 2013 | full text | 26 | exenatide twice daily | 10.1111/j.2040-1124.2012.00238.x;NCT00917267 | no | Efficacy and safety of exenatide once-weekly vs exenatide twice-daily in Asian patients wi |
| 256 | 1 (1 inc) | 2013 | full text | 48;52 |  the surgical arm is not used);usual care (exenatide arm vs  | 10.1016/j.diabres.2013.04.005 | no | Effect of laparoscopic Roux-en-Y gastric bypass surgery on type 2 diabetes mellitus with h |
| 259 | 1 (1 inc) | 2012 | full text | 12 | metformin;metformin monotherapy | 10.1111/j.1464-5491.2012.03589.x | yes | Addition of liraglutide in patients with Type2 diabetes well controlled on metformin monot |
| 262 | 1 (1 inc) | 2012 | full text | 12 | placebo | 10.1210/jc.2011-1508 | no | Exenatide exerts a potent antiinflammatory effect |
| 264 | 1 (1 inc) | 2011 | full text | 52 | pioglitazone;pioglitazone or pioglitazone and exenatide | 10.1038/oby.2011.152 | no | Effects of combined exenatide and pioglitazone therapy on hepatic fat content in type 2 di |
| 269 | 1 (1 inc) | 2011 | full text | 52 | sitagliptin or pioglitazone;sitagliptin, pioglitazone | 10.1111/j.1464-5491.2011.03301.x | no | DURATION-2: Efficacy and safety of switching from maximum daily sitagliptin or pioglitazon |
| 274 | 1 (1 inc) | 2010 | full text | 52 | insulin glargine | 10.2337/dc09-2361 | yes | Exenatide affects circulating cardiovascular risk biomarkers independently of changes in b |
| 275 | 1 (1 inc) | 2010 | full text | 52 | glibenclamide | 10.1089/dia.2009.0141 | yes | Exenatide versus glibenclamide in patients with diabetes |
| 28 | 10 (10 inc) | 2025 to 2026 | full text | 36;48;68;72;76 | placebo;placebo and lifestyle modification;placebo, dulaglut | 10.1002/oby.24184;10.1002/oby.70103;10.1055/s-0046-1819895;1 | no | Survodutide for treatment of obesity: Baseline characteristics of participants in a random |
| 3 | 1 (1 inc) | 2026 | full text | 68 | placebo, semaglutide, cagrilintide;semaglutide, cagrilintide | 10.1111/dom.71134 | no | Efficacy of CagriSema for Reaching Anthropometric Treatment Targets and Cardiometabolic Ou |
| 30 | 1 (1 inc) | 2026 | full text | 12 | empagliflozin, gliclazide;metformin plus liraglutide, empagl | 10.1016/j.jdiacomp.2026.109273 | no | Modulation of circulating extracellular vesicles by antihyperglycemic therapies: A pilot r |
| 305 | 1 (1 inc) | 2024 | full text | 26 | placebo | 10.1113/ep091815 | no | Growth differentiation factor 15 is not modified after weight loss induced by liraglutide  |
| 31 | 1 (1 inc) | 2026 | full text |  |  | 10.1038/s41591-026-04204-0;NCT05616013 | no | Bimagrumab plus semaglutide alone or in combination for the treatment of obesity: a random |
| 312 | 1 (1 inc) | 2017 | full text | 12 | placebo, liraglutide | 10.1016/j.cmet.2017.07.011 | no | The Sustained Effects of a Dual GIP/GLP-1 Receptor Agonist, NNC0090-2746, in Patients with |
| 313 | 1 (1 inc) | 2016 | full text | 28 | metformin | 10.1016/j.jdiacomp.2016.01.013 | no | Gender-related different effects of a combined therapy of Exenatide and Metformin on overw |
| 317 | 1 (1 inc) | 2012 | full text | 30 | exenatide once weekly or twice daily;placebo | 10.2147/vhrm.s37969 | no | Treatment with exenatide once weekly or twice daily for 30 weeks is associated with change |
| 319 | 1 (1 inc) | 2021 | full text | 24 | insulin glargine | 10.1038/s41598-021-99527-y | yes | Effects of exenatide on urinary albumin in overweight/obese patients with T2DM: a randomiz |
| 326 | 1 (1 inc) | 2021 | full text | 26 | placebo | 10.1038/s41598-021-97967-0 | no | Effect of liraglutide on expression of inflammatory genes in type 2 diabetes |
| 329 | 1 (1 inc) | 2018 | full text | 144;192 | sitagliptin and linagliptin;sitagliptin, linagliptin | 10.1111/eci.13007 | no | Liraglutide relieves cardiac dilated function than DPP-4 inhibitors |
| 331 | 1 (1 inc) | 2013 | full text | 12 | placebo | 10.2337/dc12-0940 | no | Zinc-α2-glycoprotein is associated with insulin resistance in humans and is regulated by h |
| 334 | 1 (1 inc) | 2023 | full text | 12 | metformin | 10.1097/md.0000000000035046 | no | Effects of liraglutide on extraglycemic inflammatory markers and renal hemodynamic paramet |
| 338 | 1 (1 inc) | 2015 | full text | 24;26 | controls;placebo | 10.1186/s12902-015-0005-6 | no | The effects of treatment with liraglutide on atherothrombotic risk in obese young women wi |
| 339 | 1 (1 inc) | 2016 | full text | 26 | placebo | 10.4158/ep151181.or | no | EFFECTS OF LIRAGLUTIDE 3.0 MG ON WEIGHT AND RISK FACTORS IN HISPANIC VERSUS NON-HIPANIC PO |
| 34 | 1 (1 inc) | 2026 | full text | 12 | placebo | 10.3389/fendo.2025.1629157 | no | Effect of liraglutide on depressive symptoms in overweight or obese patients with type 2 d |
| 340 | 1 (1 inc) | 2026 | full text | 26 | insulin glargine | 10.1016/j.ekir.2026.103789 | no | Dulaglutide Effect on Proteins Associated With CKD Progression |
| 345 | 1 (1 inc) | 2020 | full text | 26 | dulaglutide, placebo | 10.2337/dc19-1892 | no | Effects of Novel Dual GIP and GLP-1 Receptor Agonist Tirzepatide on Biomarkers of Nonalcoh |
| 348 | 1 (1 inc) | 2021 | full text | 26 | dulaglutide, placebo;placebo, dulaglutide | 10.1210/clinem/dgaa863 | no | Dual GIP and GLP-1 Receptor Agonist Tirzepatide Improves Beta-cell Function and Insulin Se |
| 351 | 1 (1 inc) | 2026 | full text | 24 | usual care | 10.1093/eurheartj/ehaf690 | no | Semaglutide promotes bone marrow-derived progenitor cell flux towards an anti-inflammatory |
| 353 | 1 (1 inc) | 2024 | full text |  |  | 10.1016/j.heliyon.2023.e23309 | no | Comparison of changes in adipokine and inflammatory cytokine levels in patients with newly |
| 376 | 1 (1 inc) | 2019 | full text | 104;52 | placebo;placebo, liraglutide | 10.1111/apt.15316 | no | Effect of semaglutide on liver enzymes and markers of inflammation in subjects with type 2 |
| 386 | 1 (1 inc) | 2025 | full text | 32 | placebo | 10.1101/2025.07.09.25331038 | no | Semaglutide Slows Epigenetic Aging in People with HIV-associated lipohypertrophy: evidence |
| 391 | 1 (1 inc) | 2025 | full text | 26;36 | placebo, dulaglutide | 10.1186/s12933-025-02781-x;NCT05048719;NCT05051579 | no | Treatment with orforglipron, an oral glucagon like peptide-1 receptor agonist, is associat |
| 392 | 1 (1 inc) | 2024 | full text | 20 | lifestyle counseling | 10.2196/62667;NCT05786521 | no | Effect of Semaglutide on Physical Function, Body Composition, and Biomarkers of Aging in O |
| 4 | 4 (4 inc) | 2024 to 2026 | full text | 52 | placebo | 10.1016/j.eclinm.2026.104203;10.1038/s41591-025-04071-1;10.1 | no | Association between early body weight reduction and treatment outcomes in participants wit |
| 40 | 1 (1 inc) | 2026 | full text | 20;32 | semaglutide, cagrilintide, placebo | 10.2147/dmso.s616418 | no | Efficacy and Safety of CagriSema for Metabolic Outcomes: Systematic Review and Pairwise Me |
| 42 | 1 (1 inc) | 2026 | full text | 72 | placebo;placebo plus lifestyle modification | 10.1016/j.eprac.2026.09.006 | no | Changes in Abdominal Adiposity and Associations with Metabolic Health Markers Following Ti |
| 43 | 1 (1 inc) | 2025 | full text |  |  | 10.1186/s12933-025-02706-8 | no | Interleukin-1β in circulating mononuclear cells predicts steatotic liver disease improveme |
| 44 | 1 (1 inc) | 2025 | full text |  |  | 10.1186/s12958-025-01447-3 | no | Effects of combined metformin and semaglutide therapy on body weight, metabolic parameters |
| 443 | 1 (1 inc) | 2025 | full text | 52 | placebo;placebo or dulaglutide | 10.3390/ijms262412028 | no | Beyond Diabetes: The Vasculoprotective Effects and Anti-Atherosclerotic Potential of Tirze |
| 444 | 1 (1 inc) | 2015 | full text | 24 | metformin, sitagliptin | 10.14740/jem304w | no | Beneficial Effects of Incretin-Based Therapy on Glycemic Control, Adipokines, Insulin Sens |
| 445 | 1 (1 inc) | 2026 | full text | 68;80 | placebo | 10.1111/dom.70209 | no | Retatrutide for the treatment of obesity, obstructive sleep apnea and knee osteoarthritis: |
| 447 | 1 (1 inc) | 2023 | full text |  |  | 10.1016/j.molmet.2023.101801 | no | Results from three phase 1 trials of NNC9204-1177, a glucagon/GLP-1 receptor co-agonist: E |
| 45 | 1 (1 inc) | 2025 | full text | 52 | placebo | 10.2337/dc25-1306;NCT04166773 | no | Relationship Between Metabolic and Histological Responses in People With Metabolic Dysfunc |
| 451 | 1 (1 inc) | 2022 | full text | 26 | placebo | 10.3389/fcdhc.2022.856485;NCT03449654 | no | Liraglutide Lowers Palmitoleate Levels in Type 2 Diabetes. A Post Hoc Analysis of the LIRA |
| 464 | 1 (1 inc) | 2012 | full text | 26 | metformin and sulphonylureas/dpp-iv inhibitors;metformin, su | 10.1371/journal.pone.0050117 | no | Improved Glycaemia Correlates with Liver Fat Reduction in Obese, Type 2 Diabetes, Patients |
| 48 | 1 (1 inc) | 2025 | full text | 26 | dulaglutide, placebo;placebo, dulaglutide | 10.1111/dom.70022 | no | Orforglipron, an oral non-peptide glucagon-like peptide-1 receptor agonist, improves marke |
| 49 | 1 (1 inc) | 2025 | full text | 52 | placebo | 10.1002/ejhf.70049 | no | Effects of semaglutide in obesity-related heart failure with preserved ejection fraction a |
| 5 | 1 (1 inc) | 2026 | full text | 104;156 | placebo | 10.1093/eurheartj/ehag524 | no | Semaglutide and cardiovascular risk reduction: a mediation analysis of the SELECT trial |
| 50 | 1 (1 inc) | 2025 | full text |  |  | 10.1016/s2213-8587(25)00226-8;NCT05646706 | no | Once-weekly semaglutide 7·2 mg in adults with obesity (STEP UP): a randomised, controlled, |
| 56 | 1 (1 inc) | 2025 | full text | 64;71 | placebo | 10.1056/nejmoa2500969 | no | Oral Semaglutide at a Dose of 25 mg in Adults with Overweight or Obesity |
| 59 | 1 (1 inc) | 2025 | full text | 52;78 | placebo | 10.1016/j.numecd.2025.104036 | no | The impact of semaglutide on liver fat assessed by serial cardiac CT scans in patients wit |
| 60 | 1 (1 inc) | 2025 | full text | 68 | placebo, semaglutide alone, cagrilintide alone;placebo, sema | 10.1056/nejmoa2502081 | no | Coadministered Cagrilintide and Semaglutide in Adults with Overweight or Obesity |
| 61 | 1 (1 inc) | 2025 | full text |  |  | 10.1002/oby.24329 | no | Long-acting PYY3−36 analogue with semaglutide for obesity: from preclinical assessment thr |
| 65 | 1 (1 inc) | 2025 | full text |  |  | 10.1111/dom.16366 | no | The effect of GLP-1 receptor agonists on circulating inflammatory markers in type 2 diabet |
| 66 | 1 (1 inc) | 2025 | full text | 252;96 | tailored therapeutic prescriptions;tailored therapeutic pres | 10.1111/dom.16419 | no | Liraglutide improves peripheral perfusion and markers of angiogenesis and inflammation in  |
| 68 | 1 (1 inc) | 2025 | full text | 72 | placebo | 10.1056/nejmoa2413258 | yes | Phase 3 Trial of Semaglutide in Metabolic Dysfunction-Associated Steatohepatitis. |
| 69 | 1 (1 inc) | 2025 | full text |  |  | 10.1111/jebm.70021 | no | Efficacy of Hypoglycemic Agents in Metabolic Dysfunction Associated Steatotic Liver Diseas |
| 77 | 1 (1 inc) | 2025 | full text | 104 | placebo | 10.1161/circulationaha.124.072679 | no | Effects of Tirzepatide on the Clinical Trajectory of Patients With Heart Failure, Preserve |
| 78 | 1 (1 inc) | 2025 | full text |  |  | 10.1161/jaha.124.039129;NCT03878706 | no | Effects of Glucagon-Like Peptide-1 Receptor Agonists, Sodium-Glucose Cotransporter-2 Inhib |
| 79 | 1 (1 inc) | 2025 | full text | 28 | placebo, metformin;semaglutide, placebo | 10.1111/dom.16159 | no | Greater improvement in insulin sensitivity per unit weight loss associated with tirzepatid |
| 8 | 18 (13 inc) | 2023 to 2026 | full text | 156;52 | placebo | 10.1016/j.jacc.2023.09.811;10.1016/j.jacc.2024.04.038;10.101 | yes | Proportion of patients with systemic inflammation and their characteristics for groups at  |
| 80 | 1 (1 inc) | 2025 | full text | 52 | placebo | 10.1016/j.ocarto.2024.100562;NCT02905864 | no | Effect of weight loss and liraglutide on neutrophil gelatinase-associated lipocalin levels |
| 81 | 1 (1 inc) | 2025 | full text | 68 | placebo | 10.1016/j.orcp.2025.03.003;NCT03811574 | no | Effect of once-weekly subcutaneous semaglutide on abdominal visceral fat area in Japanese  |
| 85 | 1 (1 inc) | 2025 | full text | 104 | placebo | 10.1056/nejmoa2410027 | no | Tirzepatide for Heart Failure with Preserved Ejection Fraction and Obesity. |
| 86 | 1 (1 inc) | 2025 | full text | 68 | placebo | 10.1038/s41591-024-03355-2 | yes | Proteomic changes upon treatment with semaglutide in individuals with obesity |
| 87 | 1 (1 inc) | 2025 | full text | 12 | metformin;standard metformin therapy | 10.3390/biom15010046 | no | Effects of Semaglutide Treatment on Psoriatic Lesions in Obese Patients with Type 2 Diabet |
| 9 | 2 (2 inc) | 2026 | full text | 72 | placebo | 10.1016/j.jacc.2026.04.044;10.1111/dom.71009;NCT04184622;NCT | no | Tirzepatide Efficacy and Tolerability According to Early Weight Response: a Post Hoc Analy |
| 90 | 1 (1 inc) | 2024 | full text | 52 | placebo | 10.1186/s13195-024-01573-x;NCT01144338 | no | Inflammatory proteins associated with Alzheimer’s disease reduced by a GLP1 receptor agoni |
| 94 | 1 (1 inc) | 2024 | full text | 156 | placebo | 10.1016/j.jacc.2024.08.022 | no | Semaglutide Effects on Cardiovascular Outcomes in People With Overweight or Obesity (SELEC |
| 95 | 1 (1 inc) | 2024 | full text | 32 | empagliflozin, placebo;placebo, empagliflozin, combination t | 10.1007/s00125-024-06228-y | no | Effects of semaglutide, empagliflozin and their combination on renal diffusion-weighted MR |
| 100 | 1 (1 inc) | 2024 | conference_abstract | 104 | placebo | 10.1016/j.atherosclerosis.2024.118518 | no | Semaglutide, inflammatory markers and cardiovascular outcomes in patients with overweight  |
| 104 | 1 (1 inc) | 2024 | proxy_partial | 12 | metformin;routine treatment (metformin, diet, exercise) |  | no | Effects of GLP-1 Receptor Agonist on Glycolipid Metabolism and Micro Inflammatory Status i |
| 108 | 1 (1 inc) | 2024 | conference_abstract | 52 | placebo, exercise, liraglutide, combination of exercise and  | 10.1159/000538577 | no | Exercise Reduces Chronic Low-grade Inflammation in Adults with Obesity After Weight Loss:  |
| 111 | 1 (1 inc) | 2024 | proxy_partial | 52 | placebo | 10.1093/eurheartjsupp/suae011 | no | Role of glucagon-like peptide-1 agonists in obesity and heart failure with preserved eject |
| 118 | 1 (1 inc) | 2024 | conference_abstract | 52 | placebo | 10.1016/j.cardfail.2023.10.465 | no | Effects Of Semaglutide Across The Range Of Left Ventricular Ejection Fraction In Obesity P |
| 121 | 9 (9 inc) | 2021 to 2023 | conference_abstract | 68 | placebo;placebo plus lifestyle intervention;placebo, semaglu | 10.1016/j.cjca.2023.06.377;10.1016/j.jcjd.2023.10.380;10.101 | no | Efficacy and safety of semaglutide 2.4 mg once- weekly in adults with overweight or obesit |
| 122 | 1 (1 inc) | 2023 | conference_abstract | 24;26 | insulin, empagliflozin, liraglutide, combination | 10.1093/eurheartj/ehad655.2571 | no | Effect of glucagon-like peptide-1 receptor agonists, sodium-glucose cotransporter-2 inhibi |
| 123 | 1 (1 inc) | 2023 | conference_abstract | 24;26 |  empagliflozin; liraglutide plus empagliflozin;insulin;insul | 10.1093/eurheartj/ehad655.2558 | no | Association of GDF15, NTpoBNP and PLGF with subclinical cardiac dysfunction in type 2 diab |
| 128 | 1 (1 inc) | 2023 | proxy_partial |  | placebo, insulin glargine, semaglutide;placebo, insulin glar | 10.1016/j.ejim.2023.04.005 | no | Tirzepatide decreases systolic and diastolic blood pressure |
| 139 | 4 (4 inc) | 2021 to 2023 | conference_abstract | 104;68 | liraglutide 3.0 mg;liraglutide 3.0 mg od plus lifestyle inte | 10.1002/oby.23328;10.1038/s41366-023-01306-4;NCT03693430;NCT | no | Semaglutide 2.4 mg vs liraglutide 3.0 mg for weight management in overweight or obesity (S |
| 146 | 2 (2 inc) | 2022 | conference_abstract | 40;52 | insulin degludec;placebo | 10.1007/s00125-022-05755-w | no | Changes in abdominal fat and clinical/analytical parameters in tirzepatide- or insulin deg |
| 148 | 3 (3 inc) | 2021 to 2022 | conference_abstract | 68;72 | placebo;placebo or semaglutide 1.0 mg | 10.1007/s00125-021-05519-y;10.1007/s12072-022-10337-4 | no | Treatment with once-weekly semaglutide 2.4 mg improves cardiometabolic risk factors in adu |
| 152 | 1 (1 inc) | 2022 | conference_abstract | 12 | hypocaloric diet plus placebo;hypocaloric diet plus placebo  | 10.1016/j.eprac.2022.03.159 | no | Abstract #1183459: Effect of Exenatide versus Hypocaloric Diet on High-sensitivity C-react |
| 153 | 1 (1 inc) | 2022 | conference_abstract | 12 | no comparator specified | 10.1016/j.eprac.2022.03.167 | no | Abstract #1184608: Exenatide Improves Cardiovascular Risk Factors in Absence of Clinically |
| 161 | 1 (1 inc) | 2021 | conference_abstract | 12 | lifestyle counseling | 10.1002/rth2.12589 | no | Effects of liraglutide vs. lifestyle changes on SST2 and Galectin-3 in obese subjects with |
| 166 | 2 (2 inc) | 2021 | conference_abstract | 68 | placebo;placebo or semaglutide 1.0 mg | 10.2337/db21-80-or | no | Treatment with once-weekly semaglutide 2.4 mg improves cardiometabolic risk factors in adu |
| 170 | 2 (2 inc) | 2020 to 2021 | conference_abstract | 26 | dulaglutide, placebo;placebo, dulaglutide | 10.1089/dia.2021.2525.abstracts;10.1161/circ.142.suppl_3.134 | yes | The dual gip and GLP-1 receptor agonist tirzepatide improves biomarkers associated with ca |
| 171 | 1 (1 inc) | 2020 | conference_abstract | 36;48 | exenatide, insulin, pioglitazone;insulin, pioglitazone | 10.2337/db20-962-p | no | Impacts of different hypoglycemic agents on adipokines and inflammatory markers in newly d |
| 178 | 1 (1 inc) | 2020 | conference_abstract |  | placebo or other treatments;placebo or standard of care | 10.1111/obr.13117 | no | Drug development for obesity management |
| 179 | 1 (1 inc) | 2019 | conference_abstract | 12 | glimepiride combined with glucophage, glucophage alone;glime | 10.1002/dmrr.3222 | no | Influence of liraglutide on insulin resistance in patients with type 2 diabetes mellitus |
| 180 | 1 (1 inc) | 2019 | conference_abstract | 26 | dulaglutide, placebo |  | no | Effects of tirzepatide, a novel dual gip and glp-1 receptor agonist, on biomarkers of non- |
| 182 | 2 (2 inc) | 2019 | conference_abstract | 26 | dulaglutide, placebo;placebo and dulaglutide;placebo, dulagl | 10.1007/s00125-019-4946-6 | no | Effects of tirzepatide (TZP), a novel dual GIP and GLP-1 receptor agonist, on biomarkers o |
| 184 | 1 (1 inc) | 2019 | conference_abstract | 26 | dulaglutide, placebo | 10.2337/db19-134-or | no | Effects of tirzepatide (TZP), a novel dual gip and GLP-1 receptor agonist, on biomarkers o |
| 191 | 1 (1 inc) | 2018 | conference_abstract | 8 | csii;csii (insulin pump) alone;csii alone | 10.1111/jdi.12937 | no | The genetic markers for the effect of GLP-1 analogue in patients with poorly controlled ty |
| 193 | 2 (2 inc) | 2018 | conference_abstract | 12 | placebo/metformin | 10.1007/s00125-018-4693-0 | no | Liraglutide and metformin may rock and roll the most atherogenic LDL fraction in patients  |
| 194 | 1 (1 inc) | 2018 | conference_abstract | 52 | placebo;placebo, liraglutide 3.0 mg/day | 10.1002/hep.30257;NCT02453711 | no | High-sensitivity C-reactive protein reductions in subjects with elevated alanine aminotran |
| 197 | 1 (1 inc) | 2018 | conference_abstract | 26 |  insulin glargine u100;ideg, iglar u100;insulin degludec | 10.4081/itjm.2018.s2 | no | IDegLira improves cardiovascular risk markers in patients with type 2 diabetes uncontrolle |
| 20 | 1 (1 inc) | 2026 | proxy_partial | 12;13 | metformin | 10.13429/j.cnki.cjcr.2026.06.008 | no | Effect of Semaglutide Combined with Metformin on Type 2 Diabetes Mellitus and its Regulati |
| 201 | 1 (1 inc) | 2018 | conference_abstract | 12 | placebo | 10.1080/13625187.2018.1442911 | no | PCOS: Intervention possibilities |
| 209 | 1 (1 inc) | 2017 | conference_abstract | 24 | insulin;insulin treatment |  | yes | Reduction of visceral fat by liraglutide is associated with ameliorations of hepatic steat |
| 21 | 1 (1 inc) | 2026 | conference_abstract | 24 | placebo | 10.2337/db26-2869-lb;NCT05822544 | no | Increasing Energy Expenditure with the Liver-Targeted Mitochondrial Protonophore TLC-6740  |
| 210 | 1 (1 inc) | 2017 | conference_abstract | 12 | placebo, liraglutide | NCT02205528 | no | The effect of NNC0090-2746, a dual GIP/GLP-1 receptor agonist (RA), on glycemic control, p |
| 211 | 1 (1 inc) | 2017 | conference_abstract | 12 | linagliptin, gliclazid mr |  | no | Exenatide ameliorates proinflammatory expression profile in peripheral monocytes of subjec |
| 216 | 1 (1 inc) | 2016 | conference_abstract | 48 | insulin, pioglitazone | 10.1002/dmrr.2855 | no | Changes in adipokines in newly diagnosed type 2 diabetes patients treated with exenatide,  |
| 219 | 2 (2 inc) | 2016 | conference_abstract | 156;24;26 | metformin plus glibenclamide;placebo | 10.1007/s00125-016-4046-9 | no | Exenatide plus metformin and glibenclamide compared with metformin plus glibenclamide on b |
| 22 | 1 (1 inc) | 2026 | conference_abstract | 104 | placebo | 10.2337/db26-1723-p | no | Semaglutide Reduces Asthma-Related Adverse Outcomes in Patients with Comorbid Asthma and O |
| 222 | 4 (4 inc) | 2014 to 2016 | conference_abstract | 156;160;56 | placebo | 10.1111/obr.12401;10.1159/000446744;10.1210/endo-meetings.20 | no | Liraglutide 3.0 mg reduces body weight and improves cardiometabolic risk factors in adults |
| 226 | 1 (1 inc) | 2016 | conference_abstract | 26 | reference treatment;reference treatment according to french  | 10.2337/db16-1771-2041 | yes | Exenatide led to a significant decrease in liver fat content and epi cardial adipose tissu |
| 229 | 2 (2 inc) | 2015 | conference_abstract | 16;26 | dietetic counselling;lifestyle counseling | 10.1007/s00125-015-3687-4 | no | Effects of liraglutide vs lifestyle changes on subcutaneous and visceral fat, liver steato |
| 230 | 1 (1 inc) | 2015 | conference_abstract | 26 | basal insulin and metformin vs. rapid-acting insulin analogs | 10.2337/db151385 | no | Glucose variability in type 2 diabetes: The initial results of the flat-sugar trial |
| 231 | 1 (1 inc) | 2015 | conference_abstract | 12 | glimepiride | 10.2337/db159321471 | no | Effect of liraglutide on cardiovascular markers in type 2 diabetes mellitus |
| 233 | 1 (1 inc) | 2015 | conference_abstract | 26;29 | glargine insulin alone;intense, self-regulated, insulin ther |  | no | The effects of short-term exenatide on circulating adiponectin levels in patients with typ |
| 234 | 1 (1 inc) | 2015 | conference_abstract | 56 | placebo;placebo plus diet and exercise |  | no | Liraglutide 3.0 mg reduces body weight and improves cardiometabolic risk factors in adults |
| 236 | 1 (1 inc) | 2015 | conference_abstract | 56 | liraglutide 1.8mg and placebo;liraglutide 1.8mg, placebo | 10.1111/dme.12668 | no | Liraglutide 3.0mg results in significant weight loss and improvements in cardiometabolic r |
| 240 | 1 (1 inc) | 2014 | conference_abstract | 56 | placebo | org/10.1016/j.orcp.2014.10.211 | no | Liraglutide 3.0mg improves body weight and cardiometabolic risk factors in overweight or o |
| 242 | 1 (1 inc) | 2014 | conference_abstract | 12 | insulin | 10.1002/dmrr.2604 | no | Effect of exenatide versus insulin on inflammation in newly diagnosed and drug-naïve Chine |
| 244 | 2 (2 inc) | 2014 | conference_abstract | 56 | placebo;placebo, diet and exercise | 10.1007/s00125-014-3355-0 | no | Effect of liraglutide 3.0/1.8 mg on body weight and cardiometabolic risk factors in overwe |
| 245 | 1 (1 inc) | 2014 | conference_abstract | 56 | placebo;placebo, diet and exercise | NCT01272232 | no | Effects of liraglutide 3.0 mg and 1.8 mg on body weight and cardiometabolic risk factors i |
| 246 | 1 (1 inc) | 2014 | conference_abstract | 26 | insulin humalog mix25, pioglitazone;insulin, pioglitazone | 10.2337/db14-1741-2092 | yes | Effects of exenatide, insulin, and pioglitazone on liver fat content and body fat distribu |
| 251 | 1 (1 inc) | 2013 | conference_abstract | 30 | insulin lispro on glargine;insulin lispro tid | 10.1007/s00125-013-3012-z | no | Impact on cardiovascular risk factors of exenatide BID vs insulin lispro TID added to titr |
| 258 | 2 (2 inc) | 2012 | conference_abstract | 156;52 | glimepiride;glimepiride plus metformin;metformin;placebo | 10.1007/s00125-012-2688-9 | no | Long-term administration of exenatide and changes in body weight and markers of cardiovasc |
| 26 | 1 (1 inc) | 2026 | conference_abstract | 16 | placebo | 10.1097/01.hjh.0001195672.80545.cb | no | REDUCTION OF PULSE PRESSURE BY TREATMENT WITH GLP-1 RECEPTOR AGONIST SEMAGLUTIDE IS ASSOCI |
| 261 | 1 (1 inc) | 2012 | conference_abstract | 12 | metformin | 10.2337/db12-378-655 | no | Effects of exenatide vs. Metformin on endothelial function in obese patients with pre-diab |
| 263 | 1 (1 inc) | 2012 | conference_abstract | 30 | exbid vs exqw;placebo | 10.1016/j.jacl.2012.04.015 | no | Reduction in estimated 10-year coronary heart disease risk using reynolds risk Score: A po |
| 267 | 1 (1 inc) | 2011 | conference_abstract | 26 | lifestyle modification and oral antihyperglycemic medication | 10.1007/s00125-011-2276-4 | no | Efficacy and safety of exenatide once weekly versus liraglutide in subjects with type 2 di |
| 268 | 3 (3 inc) | 2011 | conference_abstract | 12;52 | glimepiride;placebo | 10.2337/db11-868-1281 | no | Exenatide or glimepiride on insulin resistance in type 2 diabetic patients |
| 27 | 1 (1 inc) | 2026 | conference_abstract | 72 | placebo | 10.1055/s-0046-1819977 | no | Changes in Physical Function by Degree of Improvement in Inflammatory Biomarkers: A Post‑  |
| 270 | 1 (1 inc) | 2011 | conference_abstract | 26 | insulin glargine | 10.1111/j.1464-5491.2011.03233_1.x | no | Impact of exenatide once weekly and insulin glargine on glucose control and cardiovascular |
| 272 | 2 (2 inc) | 2010 | conference_abstract | 26;52 | glimepiride;insulin glargine | 10.1007/s00125-010-1872-z | no | Comparison between exenatide and glimepiride on metabolic control and on insulin resistanc |
| 273 | 1 (1 inc) | 2010 | conference_abstract | 16 | placebo;placebo, metformin and/or sulfonylurea |  | no | The effect of exenatide on inflammation and oxidative stress in type 2 diabetes mellitus |
| 276 | 1 (1 inc) | 2010 | conference_abstract | 26 |  pioglitazone;sitagliptin;sitagliptin or pioglitazone;sitagl | 10.1111/j.1464-5491.2009.02935.x | no | Duration-2: Exenatide once weekly demonstrated significant glycaemic control and weight re |
| 277 | 1 (1 inc) | 2009 | conference_abstract | 26 | glimepiride, rosiglitazone, insulin glargine, exenatide, pla |  | no | Reductions in lipids and CV risk markers in patients with type 2 diabetes treated with lir |
| 278 | 2 (2 inc) | 2009 | conference_abstract | 26 | sitagliptin and pioglitazone;sitagliptin, pioglitazone |  | no | DurAtion-2: Exenatide once weekly demonstrated superior glycemic control and weight reduct |
| 279 | 3 (3 inc) | 2009 | conference_abstract | 26;36;39 | glimepiride on metformin;glimepiride on metformin background | 10.1007/s00125-009-1445-1 | no | Changes in adipokines in type 2 diabetic patients treated with exenatide versus glimipirid |
| 280 | 2 (2 inc) | 2026 | ctgov_entry | 52 | no_intervention;standard care, no intervention;standard clin | NCT07747805 | no | GLIMR COPD: GLP-1 Agonists for Lung Function Improvement and Muscle Restoration in COPD |
| 282 | 2 (2 inc) | 2026 | ctgov_entry | 72 | placebo;placebo, glp-1 receptor agonists, basal insulin | NCT07706088 | no | Effect of Tirzepatide on Diabetic Peripheral Sensorimotor Neuropathy: A Randomized, Open L |
| 285 | 2 (2 inc) | 2025 | ctgov_entry | 12 | placebo | NCT07046819 | no | A Randomized, Double-Blind, Placebo-Controlled, Flexible Dose Phase 2 Study of Efficacy an |
| 286 | 2 (2 inc) | 2024 | ctgov_entry | 180;78 | placebo | NCT06557811 | no | Effect of Oral Semaglutide on Epicardial and Pericoronary Adipose Tissues in Type 2 Diabet |
| 287 | 1 (1 inc) | 2024 | ctgov_entry | 48 | placebo;placebo, mibavademab-placebo;tirzepatide plus mibava | NCT06373146 | no | A Phase 2, Randomized, Double-Blind, Placebo-Controlled, Proof-of-Concept Study of Once-We |
| 288 | 2 (2 inc) | 2024 | ctgov_entry | 12 | standard of care | NCT06243536 | no | The Effect of Semaglutide on Disordered Eating Behaviour in Type 2 Diabetic Patients |
| 290 | 2 (2 inc) | 2023 | ctgov_entry | 260 | standard treatment | NCT05700877 | no | Screening and Intervention for Subclinical Coronary Artery Disease in Patients With Type 2 |
| 291 | 2 (2 inc) | 2022 | ctgov_entry | 14 | placebo | NCT05702931 | no | Safety and Efficacy of Oral Semaglutide in Hyperglycaemic Patients After Renal Transplanta |
| 292 | 2 (2 inc) | 2020 | ctgov_entry | 16 | pioglitazone | NCT04657939 | no | Targeting Beta-cell Failure in Lean Patients With Type 2 Diabetes |
| 293 | 2 (2 inc) | 2019 | ctgov_entry | 24;26 |  dulaglutide (all arms eligible);liraglutide;placebo or stan | NCT04135287 | no | Relationship Between Improvement in Insulin Secretion and Decrease in HbA1c in GLP-1 RA Th |
| 294 | 2 (2 inc) | 2018 | ctgov_entry | 24 | standard treatment;standard treatment for type 2 diabetes | NCT03590626 | no | Effect of Dulaglutide on Liver Fat in Patients With Type 2 Diabetes and Nonalcoholic Fatty |
| 295 | 1 (1 inc) | 2018 | ctgov_entry | 44 | placebo | NCT03466021 | no | Effects of GLP-1 Receptor Agonist Treatment on Pulmonary Function and Quality of Life in O |
| 296 | 1 (1 inc) | 2018 | ctgov_entry | 52 | placebo | NCT03426085 | no | The Effects of Liraglutide on Sudomotor Function and Inflammation in Type 2 Diabetes |
| 297 | 2 (2 inc) | 2017 | ctgov_entry | 12 | placebo;placebo and low calorie diet | NCT03260881 | no | Effects of Liraglutide on Epicardial Fat Pro-Inflammatory Genes in Type 2 Diabetes and Cor |
| 298 | 2 (2 inc) | 2016 | ctgov_entry | 52 | metformin | NCT03010683 | no | Effects of Agonists of Glucagon Like Peptide - 1 Receptors (GLP-1R) on Arterial Stiffness, |
| 300 | 2 (2 inc) | 2014 | ctgov_entry | 24 | placebo | NCT02113332 | no | Addition of Liraglutide to Overweight Patients With Type 2 Diabetes Treated With Multiple  |
| 302 | 1 (1 inc) | 2011 | ctgov_entry | 52 |  gastric bypass;basal treatment;basal treatment, gastric byp | NCT01435980 | no | Study of Comparison the Treatment Effect Between Gastric Bypass and Exenatide in Type 2 Di |
| 303 | 2 (2 inc) | 2010 | ctgov_entry | 12 | metformin;metformin monotherapy | NCT01208012 | no | Impact of Liraglutide on Endothelial Function and Microvascular Blood Flow in Type 2 Diabe |
| 304 | 2 (2 inc) | 2006 | ctgov_entry | 12 | lantus insulin | NCT00353834 | no | The Effect of Exenatide Compared to Lantus Insulin on Vascular Function Before and After a |
| 308 | 1 (1 inc) | 2024 | registry_summary | 52 | no comparator;no comparator specified |  | no | The effect of substantial weight loss with tirzepatide on heart failure with preserved eje |
| 309 | 1 (1 inc) | 2018 | ctgov_entry | 104;96 |  within arm drugs include dpp-4 inhibitors, sglt2 inhibitors | NCT03804411 | no | Prognostic Predictors of Response to Hypoglycemic Therapy |
| 310 | 1 (1 inc) | 2024 | registry_summary | 36 | optimised guideline based conventional asthma care;placebo |  | no | Effect of tirzepatide on asthma control in obese asthmatics |
| 311 | 1 (1 inc) | 2026 | registry_summary | 24;26 | structured exercise;supervised physical activity program |  | no | A randomised controlled trial in adults with obesity to evaluate the effects of tirzepatid |
| 315 | 1 (1 inc) | 2013 | ctgov_entry | 24;26 | glipizide | NCT01951651 | no | Effect of Exenatide on Liver and Heart Fat and Inflammation |
| 316 | 1 (1 inc) | 2026 | conference_abstract | 104 | placebo | 10.2337/db26-1685-p | no | Exploring Semaglutide's Effect on the ASCVD-Related Proteomic Signature and Their Predicti |
| 318 | 1 (1 inc) | 2011 | ctgov_entry | 52 | pioglitazone | NCT01432405 | no | Effect Of Exenatide Treatment on Liver Fat Content in Patients With Diabetes |
| 320 | 1 (1 inc) | 2026 | conference_abstract | 48 | placebo | 10.2337/db26-1693-p;NCT06124807 | no | Mazdutide Improves Markers of Insulin Sensitivity in Adults with Obesity without Type 2 Di |
| 321 | 1 (1 inc) | 2026 | ctgov_entry | 52 | placebo | NCT07657676 | no | Effect of Mazdutide on Coronary Plaque in Patients With Coronary Atherosclerosis and Overw |
| 323 | 1 (1 inc) | 2015 | registry_summary |  | exenatide;humalog mi x25;humalog mi x25, oah;oah |  | no | Intensive Lifestyle Interference for Targeted Body Weight Couple with Different Pharmacal  |
| 324 | 1 (1 inc) | 2020 | registry_summary | 12 | empagliflozin;empagliflozin (sglt2 inhibitor) |  | no | Effects of GLP-1 Receptor Agonists on Bile Acid Metabolism and Intestinal Microorganisms:  |
| 327 | 1 (1 inc) | 2012 | registry_summary | 52 | placebo |  | no | The impact of liraglutide on glucose tolerance and the risk of type 2 diabetes in women wi |
| 328 | 1 (1 inc) | 2012 | ctgov_entry | 12 | lifestyle counselling | NCT01739049 | no | Influence of Appetite Related Hormones in Binge Eating Behaviour Among the Overweight and  |
| 332 | 1 (1 inc) | 2025 | registry_summary | 24 | placebo;placebo, probiotics |  | no | A single-center, randomized, placebo-controlled, double-blind study: the efficacy and safe |
| 333 | 1 (1 inc) | 2019 | ctgov_entry | 12;13 | insulin | NCT04137328 | no | Clinical Study on the Improvement of Diabetic Neuropathic Pain by Liraglutide |
| 336 | 1 (1 inc) | 2011 | ctgov_entry | 26 | insulin;insulin titration only | NCT01654120 | no | Study of Effectiveness of Liraglutide Added to High Dose Insulin in Type II Diabetics |
| 337 | 1 (1 inc) | 2022 | ctgov_entry | 26 | basal bolus insulin (glargine plus aspart);insulin basal bol | NCT05360537 | no | Effects of Degludec/Liraglutide on Time in Range, Inflammation and Endothelial Function vs |
| 341 | 1 (1 inc) | 2022 | registry_summary | 26 | oral hypoglycaemic agents other than semaglutide;oral hypogl |  | no | The Influence of Oral Semaglutide for Vascular Inflammation in Japanese Patients with Type |
| 342 | 1 (1 inc) | 2025 | registry_summary | 12 | metformin;routine body weight management and metformin;routi |  | no | A study of the effects of a new GLP-1RA weekly preparation on ovarian function and pregnan |
| 343 | 1 (1 inc) | 2026 | registry_summary |  | metformin |  | no | The Effect of GLP-1 Receptor Agonist on GLP-1/cAMP/VEGF, SDF-1/CRCX4 Pathways and the Mech |
| 344 | 1 (1 inc) | 2026 | registry_summary | 12 | matching placebo;placebo |  | no | The effects of encapsulated oral formulation of semaglutide, which is a diabetes medicatio |
| 346 | 1 (1 inc) | 2013 | registry_summary | 26 | sitagliptin |  | no | Comparing the effects of two new therapies for diabetes on the heart, measures of fat and  |
| 347 | 1 (1 inc) | 2026 | registry_summary | 16;4 | semaglutide;semaglutide (both arms eligible) |  | no | Effects of Tirzepatide on Endothelium-Dependent Vasodilation in Patients with Type 2 Diabe |
| 349 | 1 (1 inc) | 2017 | registry_summary | 12 | exenatide vs sitagliptin;sitagliptin |  | no | Prospective, randomized, open-label, clinical trial comparing the effects of exenatide and |
| 352 | 1 (1 inc) | 2022 | conference_abstract | 40 | placebo;placebo, dulaglutide | 10.2337/db22-715-p | no | Tirzepatide as Monotherapy Improved Markers of Beta-Cell Function and Insulin Sensitivity  |
| 354 | 1 (1 inc) | 2023 | registry_summary | 24 | dpp-4i |  | no | Oral semaglutide vs DPP-4i on body weight in Japanese people with type 2 diabetes |
| 356 | 1 (1 inc) | 2021 | registry_summary |  | glargine |  | no | Evaluation of the efficacy of liraglutide or glargine in type 2 diabetes patients combined |
| 358 | 1 (1 inc) | 2009 | registry_summary | 2 | nacl 0.9% iv |  | no | Central nervous effects of exendin-4 on hunger and satiety in obesity and diabetes mellitu |
| 359 | 1 (1 inc) | 2009 | registry_summary | 26 | insulin detemir |  | no | Efficacy of Once-Weekly Exenatide versus Once or Twice Daily Insulin Detemir in Patients w |
| 360 | 1 (1 inc) | 2017 | registry_summary | 16 |  dapagliflozin; exenatide plus dapagliflozin;dapagliflozin + |  | no | De effects of the bloodglucose lowering drugs exenatide (GLP-1 receptor agonist) and dapag |
| 361 | 1 (1 inc) | 2019 | registry_summary | 16 |  dapagliflozin; exenatide plus dapagliflozin;dapagliflozin,  |  | no | Combined effects of SGLT2 inhibition and GLP-1 receptor agonism on food intake, body weigh |
| 362 | 1 (1 inc) | 2026 | registry_summary |  | nutritional and dietary guidance combined with liraglutide |  | no | Efficacy of Individualized Medical Nutrition Therapy Combined with Liraglutide in Patients |
| 363 | 1 (1 inc) | 2022 | registry_summary | 52 | placebo;placebo and lifestyle intervention |  | no | Tirzepatide Study of Renal Function in People with Overweight or Obesity and Chronic Kidne |
| 364 | 1 (1 inc) | 2009 | registry_summary | 24 | dietary guidance;placebo |  | no | Effects of Exenatide (Byetta®) on biochemical and histological parameters of liver functio |
| 366 | 1 (1 inc) | 2019 | registry_summary | 52 | empagliflozin + placebo;placebo |  | no | Effect of treatment with Empagliflozin alone or in combination with Semaglutide on protein |
| 367 | 1 (1 inc) | 2025 | registry_summary |  | standard treatment |  | no | Semaglutide for Coronary Plaque Stabilization in Acute Coronary Syndromes with Type 2 Diab |
| 369 | 1 (1 inc) | 2025 | registry_summary | 48;52 | placebo;placebo multivitamin (both arms on tirzepatide) |  | no | Multivitamin Benefits for People Using GLP-1 Medications |
| 370 | 1 (1 inc) | 2025 | conference_abstract | 16 | placebo | 10.2337/db25-762-p | no | Semaglutide Improves Intestinal Barrier Function in T2D—A Double-Blind Randomized Controll |
| 371 | 1 (1 inc) | 2020 | registry_summary | 240 | placebo |  | no | Research study on whether semaglutide works in people with non-alcoholic steatohepatitis ( |
| 372 | 1 (1 inc) | 2020 | registry_summary | 52 | placebo |  | no | Research study to investigate how well semaglutide works in people living with obesity and |
| 375 | 1 (1 inc) | 2021 | registry_summary | 24 | placebo |  | no | SeMaglutide and Albuminuria Reduction Trial in obese individuals without diabetes |
| 378 | 1 (1 inc) | 2021 | registry_summary | 52 | conventional care |  | no | EFFECTS OF THE GLP-1 RECEPTOR AGONIST LIRAGLUTIDE ON LOWER LIMB PERFUSION IN PEOPLE WITH T |
| 379 | 1 (1 inc) | 2018 | registry_summary | 208 | placebo |  | no | A randomised, double-blind, parallel group, placebo-controlled trial comparing semaglutide |
| 381 | 1 (1 inc) | 2026 | conference_abstract | 16.5;72 | placebo | 10.2337/db26-2700-lb | no | High-Dose Semaglutide Is Associated with Preservation of Kidney Function in People Living  |
| 382 | 1 (1 inc) | 2022 | registry_summary | 72 | placebo |  | no | A research study to see how semaglutide helps losing weight in people with excess weight a |
| 383 | 1 (1 inc) | 2022 | registry_summary | 72 | placebo;placebo, semaglutide 2.4 mg |  | no | A research study to see how semaglutide helps losing weight in people with excess weight ( |
| 384 | 2 (2 inc) | 2018 | registry_summary | 68 | placebo, semaglutide 1.0 mg;semaglutide placebo |  | no | Research study investigating how well semaglutide works in people with type 2 diabetes suf |
| 385 | 1 (1 inc) | 2023 | conference_abstract | 52 | insulin glargine |  | no | AWARD-7 Post Hoc Analysis: circulating Proteins Measured by Joslin Kidney Panel Identify D |
| 387 | 1 (1 inc) | 2024 | registry_summary | 12 | other hypoglycemic drugs |  | no | Observation and mechanism of liraglutide in the treatment of obese/overweight patients wit |
| 388 | 1 (1 inc) | 2023 | registry_summary | 52 | empagliflozin;sglt2 inhibitor |  | no | Can Semaglutide or empagliflozin stabilise coronary atherosclerosis in people with type 2  |
| 389 | 1 (1 inc) | 2021 | registry_summary | 52 | placebo |  | no | Research study to look at how well semaglutide works in people living with heart failure,  |
| 390 | 1 (1 inc) | 2021 | registry_summary | 24 | placebo |  | no | Trial to study the effect of semaglutide on reducing urinary albumin excretion in people w |
| 393 | 1 (1 inc) | 2021 | registry_summary | 34 | placebo, nnc0480-0389, semaglutide |  | no | A research study looking at how well a combination of the medicines semaglutide and NNC048 |
| 394 | 1 (1 inc) | 2022 | conference_abstract | 6 | placebo (vitamin b12);vitamin b12 (placebo) | 10.1016/j.eprac.2022.10.165 | no | #1322037: GLP-1 and IL6 in Human Adipose Tissue Beiging: preliminary Results From a Crosso |
| 395 | 1 (1 inc) | 2020 | registry_summary | 52 | placebo |  | no | Effect of semaglutide 2.4 mg once weekly on function and symptoms in subjects with obesity |
| 396 | 1 (1 inc) | 2021 | registry_summary | 52 | placebo |  | no | Research study on whether a combination of 2 medicines (NNC0194-0499 and semaglutide) work |
| 397 | 1 (1 inc) | 2012 | registry_summary | 12 | sitagliptin |  | no | Differences in endothelial function amongst Sitagliptin and Liraglutide Users. A randomize |
| 400 | 1 (1 inc) | 2022 | registry_summary | 64 | placebo |  | no | Research study looking at how well semaglutide tablets taken once daily work in people who |
| 401 | 1 (1 inc) | 2021 | registry_summary | 68 | placebo |  | no | Research study to investigate how well semaglutide tablets taken once daily work in people |
| 402 | 1 (1 inc) | 2023 | registry_summary | 242 | placebo |  | no | A research study to see the effects of CagriSema in people living with diseases in the hea |
| 403 | 1 (1 inc) | 2026 | registry_summary | 72 | placebo;placebo, cagrisema 2.4 mg, cagrisema 7.2 mg, semaglu |  | no | NN9838-7910: a research study to look at how two different doses of CagriSema and one dose |
| 405 | 1 (1 inc) | 2021 | registry_summary | 52 | placebo |  | no | Effect of Semaglutide 2.4 mg once-weekly on function and symptoms in subjects with obesity |
| 406 | 1 (1 inc) | 2025 | ctgov_entry | 24 | dapagliflozin;placebo or standard care (not specified) | NCT07295223 | no | Effect of Glp-1 and Antidiabetic sgLT2 Agents for myoCardial infarcTion and Ultrasensitive |
| 407 | 1 (1 inc) | 2025 | registry_summary |  | ai-assisted multi-domain lifestyle intervention vs. continue |  | no | Effect of AI-assisted multi-domain lifestyle intervention versus continued semaglutide tre |
| 408 | 2 (2 inc) | 2022 | registry_summary | 52 | placebo |  | no | A Study in Patients with Obesity and Obstructive Sleep Apnea |
| 411 | 1 (1 inc) | 2023 | registry_summary |  | forxiga, rybelsus, formetic, phlorizin;placebo/control group |  | no | A multiarm, randomized, open label Clinical study comparing AntiatheroSClerotic efficacy o |
| 412 | 1 (1 inc) | 2012 | registry_summary | 26 | metformin;metformin monotherapy |  | no | The effect of liraglutide on the treatment of coronary artery disease and type 2 diabetes |
| 413 | 1 (1 inc) | 2016 | registry_summary | 52 | placebo |  | no | Liraglutide for obese patients with knee osteoarthritis |
| 414 | 1 (1 inc) | 2022 | registry_summary | 68 | placebo |  | no | REDEFINE 1: a research study to see how well CagriSema helps people losing weight in peopl |
| 416 | 1 (1 inc) | 2024 | registry_summary | 8 | conventional hypoglycemic therapy;oral hypoglycemic agents a |  | no | An exploratory randomized controlled study of GDP-1 receptor agonists improving cardiac fu |
| 417 | 1 (1 inc) | 2015 | registry_summary | 24 | sitagliptin |  | no | Effects of exenatide extended-release in patients with type 2 diabetes mellitus |
| 420 | 1 (1 inc) | 2011 | registry_summary | 26 | not specified |  | no | Liraglutide Effect and Action in Diabetes: evaluation of Cardiovascular Outcome Results Tr |
| 421 | 1 (1 inc) | 2016 | registry_summary | 52 | metformin;metformin, high dose liraglutide, low dose liraglu |  | no | Analysis of curative effect of Liraglutide monotherapy, Metformin monotherapy and Liraglut |
| 422 | 1 (1 inc) | 2014 | registry_summary | 52 | liraglutide-placebo |  | no | Effects of weight reducing surgery and liraglutide on blood glucose in diabetes |
| 423 | 1 (1 inc) | 2014 | registry_summary | 26 | placebo |  | no | The effect of liraglutide in patients with prediabetes and kidney failure |
| 425 | 1 (1 inc) | 2012 | registry_summary | 26 | oral agents, insulin;placebo |  | no | Effect of liraglutide (antidiabetic drug) on physical performance in patiens with type 2 d |
| 426 | 1 (1 inc) | 2020 | registry_summary | 52 |  empagliflozin;sleeve gastrectomy;sleeve gastrectomy, empagl |  | no | Sleeve Procedure vs Liraglutide vs Empagliflozin in NASH Disease and Obesity RCT (SPLENDOR |
| 427 | 1 (1 inc) | 2018 | registry_summary |  | insulin;insulin aspart |  | no | Effect of Exenatide on Carotid Intima-media Thickness and the Biomarkers of Atherosclerosi |
| 428 | 1 (1 inc) | 2012 | registry_summary | 52 | glimepiride;glimepiride and metformin |  | no | Clinical trial to compare the effect of liraglutide and glimepiride, both in combination w |
| 430 | 1 (1 inc) | 2018 | registry_summary |  | metformin |  | no | The effects of liraglutide on beta-cell function and its mechanisms in young patients with |
| 431 | 1 (1 inc) | 2023 | registry_summary | 52 | calorie restricted diet |  | no | FIT-HF - Effect of weight loss on physical and cardiac performance in patients with heart  |
| 432 | 1 (1 inc) | 2016 | registry_summary | 26 | usual care;usual care versus intensive lifestyle with liragl |  | no | A pre-pregnancy study examining the effects of an intensive lifestyle package supported wi |
| 433 | 1 (1 inc) | 2019 | proxy_partial | 160 | placebo | 10.1016/j.orcp.2016.10.079 | no | Liraglutide 3.0 mg reduces body weight and improves cardiometabolic risk factors in adults |
| 434 | 1 (1 inc) | 2011 | registry_summary |  | placebo |  | no | Safety and effect of treatment with the antidiabetic drug liraglutide in patients with typ |
| 435 | 1 (1 inc) | 2017 | registry_summary | 40 | placebo |  | no | Effects of Saxenda (R) on respiratory function in obese patients with chronic obstructive  |
| 436 | 1 (1 inc) | 2015 | registry_summary | 12;13 | insulin + metformin;nph insulin plus metformin |  | no | Effects on re-endothelialisation in type 2 diabetic subjects on Bydureon treatment add on  |
| 438 | 1 (1 inc) | 2013 | registry_summary | 26 | placebo |  | no | Prevention of early cardiovascular disease in Polycystic Ovary syndrome |
| 457 | 1 (1 inc) | 2023 | proxy_partial | 32 | semaglutide, cagrilintide | 10.1016/s0140-6736(23)01163-7 | no | Efficacy and safety of co-administered once-weekly cagrilintide 2.4 mg with once-weekly se |
| 51 | 1 (1 inc) | 2025 | conference_abstract | 104;208 | placebo | 10.1093/eurheartj/ehaf784.4313 | no | Impact of oral semaglutide on cardiovascular risk factors in patients with type 2 diabetes |
| 52 | 1 (1 inc) | 2025 | conference_abstract | 228;237 | placebo | 10.1093/eurheartj/ehaf784.4317 | no | Effects of oral semaglutide on heart failure outcomes in people with type 2 diabetes and a |
| 53 | 1 (1 inc) | 2025 | conference_abstract | 156;179.4 | placebo | 10.1093/eurheartj/ehaf784.4244 | no | Relationship between baseline LDL cholesterol levels and cardiovascular outcomes in adults |
| 54 | 2 (2 inc) | 2025 | conference_abstract | 64;68 | placebo;semaglutide;semaglutide 2.4 mg | 10.1002/oby.70102;NCT05564117;NCT05813925 | no | Improvements in Glycemic Parameters and Cardiovascular Risk Factors with Oral Semaglutide  |
| 57 | 1 (1 inc) | 2025 | proxy_partial | 12 | dulaglutide + placebo;placebo | 10.1007/s42000-025-00649-z | no | Comparative evaluation of dulaglutide alone vs. dulaglutide combined with probiotics on ca |
| 6 | 4 (2 inc) | 2025 to 2026 | already_extracted;conference_abstract | 46 | placebo | 10.1080/00325481.2025.2604924;10.1111/dom.70861;10.1159/0005 | yes | Dual Glucagon and GLP-1 Receptor Agonist Survodutide Improves Biomarkers of Beta-Cell Func |
| 70 | 1 (1 inc) | 2025 | conference_abstract |  | placebo | 10.1093/eurjpc/zwaf236.265 | no | Efficacy and safety of semaglutide in patients with obesity-related heart failure: A meta- |
| 72 | 1 (1 inc) | 2025 | conference_abstract | 36;48 | placebo | 10.1055/s00451807451 | no | Retatrutide, an Agonist of GIP, GLP-1, and Glucagon Receptors, Improved Markers of Pancrea |
| 74 | 1 (1 inc) | 2025 | conference_abstract | 52 | placebo | 10.1016/s0735-1097(25)00865-4 | no | CARDIOMETABOLIC EFFECTS OF SEMAGLUTIDE IN OBESE AND OVERWEIGHT PATIENTS WITH PREEXISTING C |
| 75 | 1 (1 inc) | 2025 | conference_abstract | 52 | placebo | 10.1016/j.joca.2025.02.024 | no | Effect of weight loss and liraglutide on neutrophil gelatinase-associated lipocalin levels |
| 76 | 1 (1 inc) | 2025 | conference_abstract | 32 | placebo |  | no | Semaglutide Improves Cognitive Function in HIV, Effect Mediated by Decrease in Inflammatio |
| 82 | 1 (1 inc) | 2025 | proxy_partial | 18;26 | basal insulin | 10.3760/cma.j.cn115791-20240318-00120 | no | Effect of liraglutide on anxiety and depression in patients with type 2 diabetes mellitus |
| 84 | 1 (1 inc) | 2025 | conference_abstract | 39.8 | placebo;placebo with standard of care | 10.1089/dia.2024.78502.abstracts | no | LESSONS FROM THE SELECT TRIAL: RETHINKING THE CLINICAL APPLICATIONS FOR THE GLP-1RA SEMAGL |
| 91 | 1 (1 inc) | 2024 | conference_abstract | 64 | placebo;placebo, non-prescribers | 10.1016/j.ihj.2024.11.290 | no | The Correlation of oral Semaglutide and NT-proBNP in Obesity-Related HFpEF in India |
| 92 | 1 (1 inc) | 2024 | conference_abstract | 72 | placebo | 10.1161/circ.150.suppl_1.4139912 | no | Inflammatory biomarkers in people treated with tirzepatide living with overweight or obesi |
| 93 | 1 (1 inc) | 2024 | conference_abstract | 104 | placebo | 10.1002/oby.24194 | no | Inflammatory Markers in Cardiovascular Risk and Outcomes in SELECT |
| 96 | 1 (1 inc) | 2024 | conference_abstract | 52 | insulin, empagliflozin;insulin, empagliflozin, liraglutide,  | 10.1093/eurheartj/ehae666.2915 | no | Effects of glucagon-like peptide-1 receptor agonists, sodium-glucose cotransporter-2 inhib |
| 98 | 1 (1 inc) | 2024 | conference_abstract | 156;159.2 | placebo | 10.1093/eurheartj/ehae666.2792 | no | Exploratory mediation analysis of the effect of semaglutide on cardiovascular outcomes in  |
| 99 | 4 (4 inc) | 2024 | conference_abstract | 36;48;52 | insulin, empagliflozin;insulin, empagliflozin, liraglutide,  | 10.1007/s00125-024-06226-0;10.2337/db24-266-or | no | The effect of 12-month treatment with glucagon-like peptide-1 receptor agonists, sodium-gl |
