# NBAIS inclusion rule

Written 2026-10-15 after the surrogacy appraisal graded all 20 biomarkers. The rule is stated before the composite is computed.

## Why a rule is needed

The original specification pooled every biomarker in the inventory. The appraisal showed that ten of twenty carry a problem that is not about evidence strength but about whether including them is coherent at all: markers that double-count each other, markers whose assumed favourable direction is contradicted by outcome data, markers that restate adiposity, and one marker that is not an aging marker.

A composite built from that set would have produced a number, and the number would have been uninterpretable. Worse, it would have been uninterpretable in ways that favour the review's hypothesis, because most of the defective markers are ones the drug moves strongly.

## Exclusion criteria, applied in order

### E1. Not an aging biomarker on face validity

A marker whose movement reflects pharmacological target engagement rather than a hallmark process.

| Excluded | Reason |
|---|---|
| glucagon | Target engagement for glucagon receptor agonism. Falls because the receptor is being agonised, not because an aging process changed. Carried 8.4 per cent of composite weight under the old specification |

### E2. Derived index sharing inputs with another included marker

Including an index and its components counts the same information more than once and silently inflates whichever domain the index belongs to.

| Decision | Detail |
|---|---|
| Retain HOMA-IR | It is the interpretable quantity and the one the literature discusses |
| Exclude fasting glucose, fasting insulin | Both are inputs to HOMA-IR. Retaining all three counts the same information up to three times and would have made nutrient sensing the dominant domain by construction |
| Exclude HOMA-beta | Shares the same two inputs |
| Exclude C-peptide | Measures endogenous insulin secretion, overlaps fasting insulin, and has no claim to being an aging marker |
| Exclude fatty liver index | Computed from BMI and waist circumference. Including an adiposity index in a composite that is then tested for weight independence is close to circular |

Fasting glucose is excluded here on the double-counting rule. It would in any case have carried the ACCORD problem: three large trials lowered glucose without the outcome benefit its epidemiology predicted, and one increased mortality. Scoring a glucose reduction as slowed biological aging makes precisely the inference those trials refuted.

### E3. Assumed direction contradicted by outcome evidence in a comparable population

| Excluded | Reason |
|---|---|
| adiponectin | The composite scores a rise as favourable. In 14,063 patients with established cardiovascular disease, higher adiponectin predicted higher all-cause mortality (HR 1.45) and cardiovascular mortality (HR 1.69). SELECT is a cardiovascular disease population. Until the direction is resolved, scoring a rise as anti-aging may be scoring a harm as a benefit |

Adiponectin is excluded from the composite and reported separately with the discordance stated. It is not dropped from the review.

### E4. Measured within the normal range where the direction of benefit is not established

| Excluded | Reason |
|---|---|
| ALT, AST | Both have U-shaped mortality associations, with low values marking frailty in older adults. SELECT lowered them from baselines already within normal limits. A reduction of a normal value cannot be scored as an aging benefit without evidence that it is one |

GGT is retained. Its association with mortality is monotonic rather than U-shaped, it is the best validated of the three liver enzymes for this purpose, and it showed the largest relative change.

## What remains

| Biomarker | Domain | Axis B | Note |
|---|---|---|---|
| hsCRP | inflammaging | B1 | The only marker with mediation evidence in the treated population |
| IL-6 | inflammaging | B0 | Causal genetic evidence, though the drug barely moves it |
| YKL-40 | inflammaging | B3 | |
| GDF-15 | mitochondrial stress | B3 | Direction caution: rises with metformin and cachexia |
| ICAM-1 | endothelial aging | B3 | Weakly validated after adjustment |
| GGT | hepatocellular senescence | B3 | |
| liver fat PDFF | hepatocellular senescence | B4 | Retained with a stated caveat: fibrosis, not steatosis, carries the prognostic weight |
| leptin | adipose senescence | B4 | Retained with a stated caveat: closest of any marker to a restatement of fat mass |
| HOMA-IR | nutrient sensing | B4 | Retained as the nutrient sensing representative |
| NT-proBNP | cardiac aging | B2 | Retained specifically because the drug does NOT move it |
| lean mass | musculoskeletal aging | B3 | The unfavourable axis. Retained as essential |

Eleven markers across seven hallmark domains, down from twenty.

## Two retentions that need defending

**NT-proBNP is retained because the effect is null.** It has the second strongest outcome prediction in the inventory and the point estimate is unfavourable. Dropping it would leave a composite assembled only from markers that moved in the desired direction, which is the selective reporting this review's own Methods identify as undetectable by funnel plot. A validated null belongs in the score.

**Lean mass is retained although its prognostic meaning in this population is unknown.** It is the only axis moving unfavourably. A composite that excludes the one domain where the drug class may cause harm is not a net score. The uncertainty is handled by reporting the composite with and without it, not by omitting it.

## Sensitivity analyses this rule requires

| Analysis | Purpose |
|---|---|
| Composite with and without lean mass | Shows how much the unfavourable axis changes the conclusion |
| Composite restricted to B0 to B2 markers only | The defensible core: hsCRP, IL-6, NT-proBNP |
| Composite with all 20 markers, as originally specified | Shows what the inclusion rule changed, so the effect of the rule is visible rather than hidden |
| Composite with adiponectin re-included at reversed direction | Tests whether the discordance matters to the result |

The third is important. A reader must be able to see what the exclusion rule did, or the rule becomes an undocumented researcher degree of freedom.

## Honest statement of what this costs

The composite now rests on eleven markers, of which one has mediation evidence, one has causal genetic evidence, and most have neither. It is a weighted summary of markers that the drug moves and that are plausibly aging related, not a measure of biological age.

The name Net Biological Age Impact Score overstates that. The score should be renamed to describe what it measures, and biological age language reserved for epigenetic clock evidence, which exists for one drug in one trial.
