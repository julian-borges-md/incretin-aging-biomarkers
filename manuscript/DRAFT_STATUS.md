# M5-AGE Draft Status

Updated: 2026-10-14

## Complete

| Section | State |
|---|---|
| Title page, byline | FINAL |
| Abstract (Background, Objectives, Methods) | COMPLETE |
| 1. Introduction | COMPLETE |
| 2.1-2.8 Methods | COMPLETE |
| 2.9 Statistical Analysis (10 subsections) | COMPLETE |
| 2.10-2.11 | COMPLETE |
| 4.3 GDF-15 receptor-class discriminator | COMPLETE |
| 4.4 Hepatic aging reversal / retatrutide case | COMPLETE |
| 4.5 Lean mass as unfavorable signal | COMPLETE |
| 4.6 Disease-specific to biological age | COMPLETE |
| 4.7 Metabolic age normalization | COMPLETE |
| 4.8 Geroscience and trial design | COMPLETE |
| 4.9 Retatrutide dedicated section | COMPLETE |
| 4.10 Strengths and limitations | COMPLETE |
| Table 1 (26-marker inventory) | POPULATED |
| Table 6 (normalization thresholds) | POPULATED |
| References 1-29 | VERIFIED, DOI-confirmed |
| Analysis pipeline | COMPLETE, executable |

## Blocked on data extraction

| Section | Blocker |
|---|---|
| Abstract Results/Conclusions | Needs pooled estimates |
| 3.1-3.10 Results | Needs extraction_master.csv |
| 4.1 Summary of findings | Needs Results |
| 4.2 Favorable:unfavorable ratio | Needs Results |
| 5. Conclusions | Needs Results |
| Tables 2,3,4,5,7 | Needs Results |
| Figures 1-6 | Pipeline generates on extraction |

## Critical path

1. Extract trials into analysis/data/extraction_master.csv per extraction_schema.csv
2. Run analysis/M5_AGE_analysis_pipeline.R
3. Populate Results from output/*.csv
4. Write 4.1, 4.2, Conclusions, Abstract Results
5. Self-critique 3-pass
6. Submit

## Retatrutide data position

Available: weight (-24.2% ph2, -15.3% ph3), HbA1c (-2.02% ph2, -1.94% ph3),
liver fat (-82.4% at 12mg, 86% reaching normal), SBP (-6.8), TG (-40.9),
LDL (-13.1), DXA body composition (Coskun 2025 LDE).

Absent: GDF-15, hsCRP, IL-6, adiponectin, leptin, epigenetic clocks,
biopsy-confirmed MASH histology.

Consequence: triple-agonist node populated for metabolic/hepatic-imaging/
vascular/lipid domains, empty for inflammatory/epigenetic. NBAIS computed
over ~7 biomarkers vs ~16 for GLP-1 mono. Handled by weighted-mean
formulation and shared-biomarker restriction on pairwise contrasts.
