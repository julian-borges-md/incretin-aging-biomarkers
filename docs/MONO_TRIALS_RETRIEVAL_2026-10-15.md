# Placebo controlled mono agonist trials: retrieval and extraction status

Written 2026-10-15, 21:10 local, after full text retrieval of the five trials named in `docs/PRISMA_FLOW.md` as "full text not accessible". All five were retrieved the same evening through the Boston University EZproxy route documented in `docs/LICENSED_DATABASE_ACCESS.md`; none is in PMC (checked by ID conversion before any proxy request). Full texts are held under `work/fulltext/` (gitignored, licensed content) with the proxied hostname and capture time recorded in each file.

## Identity resolution

| Listed as | Resolved to | PMID | DOI | Journal |
|---|---|---|---|---|
| Derosa 2012 | Derosa G et al. 2012 | 22540883 | 10.1111/j.1464-5491.2012.03699.x | Diabet Med 29(12):1515 |
| von Scholten 2017 | von Scholten BJ et al. 2017, prespecified sub-study of NCT02545738 | 28105731 | 10.1111/dom.12884 | Diabetes Obes Metab 19(6):901 |
| Wu 2011 | Wu JD et al. 2011 | 21284481 | 10.1089/dia.2010.0048 | Diabetes Technol Ther 13(2):143 |
| Anholm 2019 | Anholm C et al. 2019, AddHope2, NCT01595789 | 31326727 | 10.1016/j.atherosclerosis.2019.07.007 | Atherosclerosis 288:60 |
| Wagner 2019 | Wägner AM et al. 2019, LIPER2, EudraCT 2012-005197-63 | 30223083 | 10.1016/j.diabet.2018.08.010 | Diabetes Metab 45(3):268 |

Alrasheed 2026 (PMC12852008) confirms all five in its included studies table and its placebo stratum forest plot for CRP (Wu, Derosa, Wagner, Pastel, Anholm). Pastel 2017 compares liraglutide with calorie restriction, not placebo, and is not eligible for the Q2 contrast.

## What each trial supplies

| Trial | Design | n | Weeks | Comparator | Biomarkers in inventory scope | Contrast as reported | Variance recoverable now |
|---|---|---|---|---|---|---|---|
| Derosa 2012 | parallel, double blind | 85 vs 86 (82 vs 81 completers) | 52 | placebo, both on metformin | hsCRP, HOMA-IR, fasting glucose, fasting insulin, C-peptide, glucagon, adiponectin, HOMA-beta (plus TNF-alpha, not in inventory) | end of study arm means with SD; authors report hsCRP and TNF-alpha "no differences between the two groups" by ANCOVA | arm SDs at 12 months are implausibly small (hsCRP 0.2 and 0.4 mg/L against 0.8 at baseline); a final value MD would be P < 0.001 against the authors' ns. Not usable without a decision |
| Wu 2011 | parallel, double blind, pilot | 12 vs 11 | 16 | placebo, background metformin and/or SU | hsCRP (plus MCP-1, PGF2alpha, not in inventory) | week 16 arm means with SD: 0.2 (0.3) vs 1.4 (1.6) mg/L, P < 0.05; ANCOVA F = 5.44, P = 0.032 | yes, arm SDs: MD -1.2 mg/L, SE 0.49; baseline means 0.4 and 0.6 mg/L, so the percent scale is extreme and the row carries little weight |
| Anholm 2019 | crossover, double blind | 41 randomised, 39 ITT, 28 completers | 12 + 12 | placebo, both on metformin | CRP, HOMA-IR (plus TNF-alpha) | CRP: within liraglutide -0.5 (-1.58; 0.03) mg/L median, P = 0.01; between treatments P = 0.2, estimate in Supplementary Table A2 | no; the paired between treatment estimate and interval are in the supplementary Word file, not retrieved |
| Wägner 2019 | parallel, double blind | 12 vs 12 | 26 | placebo, all on metformin | CRP (mg/dL), NT-proBNP, weight | end of study CRP 0.31 (0.29) vs 0.64 (0.30) mg/dL, P = 0.017; baseline already 0.37 vs 0.66, P = 0.036; within arm changes -0.06 and -0.02, both ns | arm SDs exist, but the final value contrast is the baseline imbalance carried forward; change score SDs not reported |
| von Scholten 2017 | crossover, double blind, prespecified sub-study | 32 randomised, 27 completers | 12 + 12 | placebo plus standard therapy | TNF-alpha, MR-proADM, MR-proANP, suPAR, copeptin (none in the Table 1 inventory; hsCRP not measured) | percent differences with 95 per cent CI from paired log scale analysis: TNF-alpha -12 (-20; -3), MR-proANP -13 (-21; -4), MR-proADM -4 (-8; 0) | yes, ci_95 route, if the markers are admitted |

## Why no row was added to the master tonight

Three analysis rules are missing, and each would change what the rows mean. Adding rows before the rules are written would be a post hoc choice made after seeing the numbers, which the public protocol exists to prevent.

| ID | Decision needed | Why it matters here | Options |
|---|---|---|---|
| R1 | Parallel trials reporting baseline and final arm means with SDs but no change score SD: final value contrast, change score with an imputed pre post correlation, or exclusion when baseline imbalance exceeds a stated threshold | Wägner: final value MD -3.3 mg/L (P = 0.017) against change score MD about -0.4 mg/L (null); Derosa: final value SDs implausible | Cochrane Handbook 6.5.2.8 imputation with r prespecified (0.5) and a sensitivity over r in {0.3, 0.7}; or final values with the imbalance flagged in RoB D1 |
| R2 | Inventory reconciliation | The Table 1 inventory of 26 markers does not contain NT-proBNP, adiponectin, HOMA-beta, C-peptide, glucagon, GGT or the fatty liver index, all of which are already extracted and pooled, and does contain HbA1c, SBP, DBP, lipids, lean mass, body fat, VAT, BMD, eGFR and resting heart rate, none of which is extracted. TNF-alpha (eight mono trials in the screening pool, one GCGR class trial to come) and MR-proANP would be further additions | Record an inventory amendment with the rationale for each addition and each omission before any new marker enters; Q1 is phrased as "which of a pre-specified set of 26" and the Methods must say what was actually pooled |
| R3 | Crossover trials: use the reported paired contrast as published (von Scholten, Anholm) and never recompute from arm SDs | Both Danish trials analyse end of period versus end of period with pairing; a parallel group SE would be wrong in both directions | Adopt as a rule in `prespecification/analysis_plan.md`; it is consistent with the existing contrast against concurrent control rule |

Operational items that need the Lab Director: the Anholm supplementary file (Word, 130 KB) carries the only between treatment CRP estimate and has not been downloaded; the harmoniser's baseline table is keyed by biomarker only and must be keyed by trial and biomarker before any trial specific denominator is entered (Derosa hsCRP baseline 2.0 mg/L, Table 3; Wu pooled baseline about 0.5 mg/L; Wägner pooled baseline 5.2 mg/L); the within trial dulaglutide arm of Wilson 2021 is currently dropped by the highest dose rule and is the only within trial cross class comparison in the corpus (see the SIRLP addendum).

## What this changes for Q2

With R1 to R3 settled, hsCRP would hold placebo controlled mono class data from SELECT, Derosa, Wu and Wägner (Anholm pending its supplement), which is the replication the class contrast needs on the mono side; the GIP side still rests on Wilson alone. The contrast therefore moves from "not computable" to "computable on the mono side, unreplicated on the GIP side" and stays confounded by one trial per class on that side until a second GIP trial reports hsCRP.
