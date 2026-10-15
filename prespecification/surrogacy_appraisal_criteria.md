# Surrogacy appraisal criteria

Component 5 of the review architecture. Written 2026-10-15, before any biomarker was graded, so that grades cannot be fitted to beliefs already held about which markers matter.

## Purpose

The review's first four components establish which aging biomarkers this drug class moves, by how much, and whether that differs by receptor class. None of that establishes that moving a biomarker matters. Those are separate claims, and conflating them is the central weakness of biomarker literature in geroscience.

This component asks a narrower and answerable question for each biomarker in the inventory:

> Is there evidence that this marker predicts an outcome people already act on, in a population comparable to the one where the drug moves it?

The output is a graded table, not a verdict. A marker graded low here is not dismissed; it is identified as responsive but unvalidated, which is a useful thing to know and is currently nowhere stated for this drug class.

## Why this is worth doing

Aging biomarkers are not accepted surrogates for anything. The usual response is to assert that they should be. The more useful response is to separate the markers for which validation evidence already exists from those for which it does not, because the first group is where validation effort should go and the second is where claims are currently outrunning data.

No one has done this for incretin and glucagon receptor agonists.

## The grading scheme

Each biomarker receives a grade on two axes, assessed independently.

### Axis A: drug responsiveness

Established by components 1 to 3 of this review. Recorded here only so the two axes can be crossed.

| Grade | Criterion |
|---|---|
| A1 | Moved in at least three independent trials, consistent direction |
| A2 | Moved in one or two trials |
| A3 | Measured but no significant change |
| A0 | Not measured in any trial of this class |

### Axis B: outcome prediction

This is the axis this component adds. Graded against a fixed hierarchy.

| Grade | Criterion | What it takes |
|---|---|---|
| **B1** | Treatment-induced CHANGE in the marker predicts change in a hard outcome, within the same trial population | Mediation or time-varying covariate analysis showing attenuation of the treatment effect |
| **B2** | BASELINE level predicts a hard outcome in the same or a closely comparable trial population | Prospective association with events, adjusted for standard confounders |
| **B3** | Baseline level predicts a hard outcome in general population cohorts only | Epidemiological association outside the treated population |
| **B4** | Associated with aging phenotypes but no hard outcome prediction | Cross-sectional or phenotype-level association |
| **B5** | No outcome prediction evidence located | |

Hard outcome means death, a major adverse cardiovascular event, incident disease, or a validated functional decline measure. It does not mean another biomarker.

### Confounding qualifier

Applied to B1 and B2 only, because an unadjusted prediction is weak evidence of surrogacy.

| Qualifier | Meaning |
|---|---|
| adj+ | Association survives adjustment for body weight or adiposity AND at least one of lipids, glycaemia or treatment intensity |
| adj- | Association reported without adjustment for weight or the obvious confounders |

The weight adjustment matters specifically. A marker that predicts outcomes only because it tracks adiposity is a proxy for weight, not an independent aging signal.

## What the crossed grades mean

| Cell | Interpretation |
|---|---|
| A1 or A2 with B1 | Validation candidate. The drug moves it and its movement tracks outcomes |
| A1 or A2 with B2 or B3 | Responsive, prediction established but mediation untested. The gap is a specific, fundable study |
| A1 or A2 with B4 or B5 | Responsive but unvalidated. Movement here supports no clinical claim |
| A0 with any B | Unmeasured. Identifies what the next trial should include |

The A0 cells are where this component feeds back into trial design, which is the realistic near-term impact of the review.

## Rules of assessment

**Evidence for Axis B is sought independently of this review's own extraction.** Outcome-prediction evidence comes from different papers than biomarker-response evidence, and will often come from cohorts rather than trials.

**The same population standard is applied to every marker.** A marker is not promoted to B2 because its evidence comes from a trial we happen to have extracted. The question is whether the population is comparable, judged on age, adiposity and disease status.

**Grades are assigned by two independent assessors with a third adjudicating**, as for screening and extraction, and disagreements are logged.

**A located absence is recorded as B5, not left blank.** The distinction between "searched and found nothing" and "not searched" is maintained, and only the first is reportable.

**No marker is graded before the criteria above are fixed.** This file predates the first grade.

## Known risk

The most likely failure of this component is grade inflation on markers the review has already invested in. hsCRP will almost certainly reach B1, and there is a temptation to read the remaining markers generously so the signature looks validated as a whole. The crossed table is designed to resist that by making the B4 and B5 cells visible rather than averaged away.

If most of the inventory lands in B4 or B5, that is the finding, and it is a more useful one than a composite implying the whole signature is meaningful.
