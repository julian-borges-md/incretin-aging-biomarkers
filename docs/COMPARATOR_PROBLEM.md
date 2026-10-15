# The comparator problem in Q2

Surfaced 2026-10-15 on extracting the first mono-agonist trial for the class contrast. It is a design issue, not a data issue, and it constrains how Q2 can be answered.

## What happened

Simó 2015 (EUREXA, PMID 26338040) is the largest mono-agonist hsCRP trial available: n=1029, 36 months, exenatide versus **glimepiride** added to metformin. hsCRP fell 1.7 mg/L on exenatide against 0.2 mg/L on glimepiride, p=0.004.

Our existing hsCRP rows are placebo-controlled: SELECT (semaglutide vs placebo) and Wilson (tirzepatide vs placebo).

These contrasts are not interchangeable.

## Why it matters

Glimepiride is a sulfonylurea and causes weight **gain**. In EUREXA, body weight fell in the exenatide arm and rose in the glimepiride arm, a between-group difference of roughly 5 kg. Any biomarker that tracks adiposity will therefore show a larger contrast against glimepiride than against placebo, purely because the comparator moved in the opposite direction.

Pooling an active-controlled contrast with a placebo-controlled one, and then attributing the difference to receptor class, would confound receptor pharmacology with comparator choice. If the mono-agonist trials are predominantly active-controlled and the dual and triple agonist trials predominantly placebo-controlled, that confounding runs systematically in one direction.

This is not hypothetical. Of Alrasheed's 40 mono trials: placebo 6, insulin 10, metformin 9, other oral agents 12. **Only 6 of 40 are placebo-controlled.** Our GIP, GCGR and triple agonist data are placebo-controlled throughout.

So the naive class contrast would compare mostly active-controlled mono trials against entirely placebo-controlled dual and triple trials. Whatever that produced would not be a receptor class effect.

## Alrasheed handled this and we must too

They stratified every analysis by comparator type and reported separately against placebo, insulin and other oral agents. Their CRP results differ substantially by stratum: SMD −0.59 against placebo, −1.06 against other oral agents, and non-significant against insulin.

A single pooled "mono-agonist effect" collapsing those strata does not exist as a meaningful quantity.

## Consequences for Q2

The class contrast must be restricted to **placebo-controlled trials only**. That is the only comparison in which the counterfactual is the same across classes.

This shrinks the usable mono-agonist pool for hsCRP from 14 trials to roughly 6, of which some will lack extractable variance. It is a substantial loss and it is not negotiable: the alternative is a contrast that measures comparator choice.

| Biomarker | Placebo-controlled mono trials available |
|---|---|
| hsCRP | Derosa 2012, Wu 2011, Wagner 2019, Anholm 2019, plus SELECT |
| TNF-alpha | Derosa 2012, von Scholten 2017, Anholm 2019 |
| IL-6 | fewer; most IL-6 trials are active-controlled |
| adiponectin | very few placebo-controlled |

## Second constraint: the comparator is not inert even when it is placebo

In several of these trials both arms receive background metformin, and metformin has its own modest anti-inflammatory effect. A placebo-controlled add-on trial therefore measures the incremental effect over metformin, not over nothing. This is consistent across the corpus and is a smaller problem than the active-comparator issue, but it belongs in the Methods.

## What this changes in the protocol

The eligibility criteria registered in the PROSPERO draft permit any comparator. That remains correct for Q1, where the question is whether the biomarker moves at all.

For Q2 specifically, a comparator restriction is added: **class contrasts are computed within placebo-controlled trials only**, with active-controlled trials reported separately and never pooled across comparator types.

This is a protocol amendment made after seeing the data, and is recorded as one. The justification is structural rather than empirical: it was prompted by noticing the design asymmetry, not by seeing which way the results came out. No class contrast had been computed at the time this restriction was adopted.
