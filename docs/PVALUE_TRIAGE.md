# P value reconciliation triage, 16 October 2026

## What this gate asks

`src/extraction_numbers_check.py` asks whether each number occurs in the source.
`src/extraction_attachment_check.py` asks whether it is attached to the right biomarker. Neither asks
whether a row's numbers are consistent with each other. `src/pvalue_reconcile.py` (gate twelve) does:
for every row that carries a printed exact p value and a computable effect with a standard error, it
compares the printed p with the p implied by the effect and its standard error. A row whose interval
and p value disagree is either a transcription error or a paper whose statistics do not hold
together, and both integrity exclusions of this corpus were found by that comparison, by hand.

Verdicts over the 524 rows of the 16 October corpus: 117 reconcile, one soft, three hard, 403 skipped
because they carry no exact p (a bound such as p < 0.001, or none at all). The skipped count is the
honest ceiling of this instrument: it can only check a row whose paper printed a usable p.

## The hard and soft rows, read one by one

| Trial | Marker | Verdict |
|---|---|---|
| Dutour 2016 | leptin | **EXPLAINED, no change, and the one worth the Director's attention.** Printed p 0.0004 against an implied 0.24, a factor of 600. The cause is that the printed p is a TIME BY GROUP INTERACTION p from a repeated measures model over the whole trajectory, as the row's own notes record, and not a between arm p for the week 26 change the row encodes. The two are not interchangeable, so the printed p must not be used to derive a standard error: the route `arm_means_exact_p` exists for rows whose paper prints a difference p, and using it here would transfer an interaction p to a contrast it does not describe. The row therefore keeps the standard error built from the arm SDs with an imputed within person correlation of 0.5, which is conservative for a paired marker as autocorrelated as leptin. Consequence to state plainly: this row's weight in the leptin pool is almost certainly understated, and leptin is the marker whose pooled estimate has already moved most this week (minus 47.8 to minus 35.5 per cent when its eighth trial arrived). The imputed correlation sensitivity analysis varies r across 0.3, 0.5 and 0.7 and no pooled estimate changes sign, but that analysis cannot reach the correlation this paper's own model implies. A Director decision to request the trial's change SDs, or to accept a higher r for leptin specifically, is the only thing that would settle it. |
| Yu 2015 Dalian liraglutide vs metformin vs sitagliptin | HOMA_IR | **EXPLAINED, no change.** Printed p 0.054 against an implied 0.016. The printed p values of this trial are pairwise comparisons corrected for three treatment groups, as the extraction notes state, while the row's standard error is the uncorrected two arm quantity the meta-analysis needs. A correction for three comparisons moves a p by roughly that factor, and the direction is the expected one: corrected p larger than uncorrected. |
| Yu 2015 Dalian liraglutide vs metformin vs sitagliptin | fasting_glucose | **EXPLAINED, no change.** Printed p 0.117 against an implied 0.044, same cause as the row above. |
| Yu 2015 Dalian liraglutide vs metformin vs sitagliptin | HbA1c | **EXPLAINED, soft only, no change.** Printed p 0.005 against an implied 0.0004, same cause. Listed here because the gate reports soft rows as well and because three rows of one trial with the same explanation is itself the evidence that the explanation is right. |

## Two rows the gate flagged on its first run and no longer does

SOUL total cholesterol (printed 0.03, implied 0.051) and the mazdutide phase 2 LDL row (printed
0.0504, implied 0.0482) crossed the 0.05 line only because the line is drawn there. The gate now has
a dead band: when both values lie between 0.02 and 0.10 it does not call the crossing, because a
printed 0.0504 against an implied 0.0482 is the same number twice and flagging it would teach the
reader to ignore the instrument. Rows whose printed and implied p are both below 0.001 are likewise
not compared, since both are floors rather than values.

## What the gate cannot do

The implied p is computed from the normal approximation, which is what the pooling weights assume.
Printed p values come from ANCOVA, MMRM or t tests with finite degrees of freedom; at the smallest
arm sizes in this corpus, about 20 per group, that difference moves a p of 0.05 by roughly a factor
of two. The tolerances are set an order of magnitude above that so the gate reports disagreements of
kind rather than of method, and the three hard rows above are all disagreements of kind: a different
model, or a multiplicity correction.
