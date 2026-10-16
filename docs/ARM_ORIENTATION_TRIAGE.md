# Arm orientation triage

Companion to `src/arm_orientation_check.py`, the fourteenth gate of the provenance chain and the
fourth of the gates that compare a row against itself rather than against its source. This document
doubles as the gate's allowlist: the gate exits non zero when a HARD row is not written up below.

Run `python3 -I src/arm_orientation_check.py --self-test` from the repository root.

## The question

A swapped treatment and control arm leaves every number present, attached to the right biomarker and
internally consistent with its own interval and p value. The three gates before this one therefore
cannot see it, and it inverts the finding. Where a row carries both a reported effect and both
printed arm values, the two can be compared, and that is the whole of this gate's scope.

## Result, 16 October 2026

| Quantity | Rows |
| --- | --- |
| Master rows | 524 |
| In scope, reported effect and both arm values printed | 38 |
| HARD, the arms and the reported effect do not reconcile | 0 |
| SOFT, a gap beyond rounding but short of the hard threshold | 0 |
| OK | 38 |
| Of the OK rows, those where an injected swap is detected | 32 |
| Of the OK rows, those where a swap is undetectable | 6 |
| Out of scope, effect derived from the arm values | 122 |
| Out of scope, no printed arm values | 364 |

No arm is swapped in any row the gate can see. The self test confirms the gate fires: an injected
swap is classified HARD on 32 of the 38 rows, and a tenfold digit shift in the treatment arm is
classified HARD on all 12 rows tested.

## HARD rows

| Trial | Marker | Verdict | Reading |
| --- | --- | --- | --- |

None.

## What the gate found about the data model

The four PCT rows of NCT04822181 are extracted with the correct between group contrast for a ratio
scale, and the first draft of this gate was wrong about it. A percent change is a ratio, so the
contrast of two percent changes is not their arithmetic difference but

    (1 + tx/100) / (1 + ctrl/100) - 1

The four rows match that form to the last printed digit and none of them match the arithmetic form.
On the hsCRP row the two forms differ by 8.4 percentage points on a 42 per cent effect, which is the
difference between a correct row and a wrong one. The gate now computes the contrast by measure and
propagates the printed precision through the ratio rather than the difference.

The limit is stated rather than hidden. The self test injects the arithmetic contrast into each PCT
row and the gate rejects one of four. The two forms diverge in proportion to how far the comparator
arm moved, so where the comparator barely changed they agree to within a few per cent and no
numerical check can separate them. The gate catches the error on the row where it changes the answer.

## Rows whose reported effect is model adjusted

These three rows pass, but their gap exceeds the rounding bound, which means the reported effect is
an adjusted estimate and not the raw arm difference. Their arm values must not be used to re derive
the effect or a standard error for it; the reported interval is the only admissible route.

| Trial | Marker | Reported | Arms | Implied | Gap | Bound |
| --- | --- | --- | --- | --- | --- | --- |
| SCALE Obesity and Prediabetes 3 year | DBP | -0.60 | -2.30 / -1.90 | -0.40 | 0.200 | 0.150 |
| DUAL II | fasting_glucose | -0.73 | -3.50 / -2.60 | -0.90 | 0.170 | 0.105 |
| SCALE Obesity and Prediabetes 3 year | resting_heart_rate | 2.00 | 2.10 / -0.02 | 2.12 | 0.120 | 0.060 |

## Rows the gate cannot protect

On these six rows the two arms sit within the rounding bound of each other, so a swap would turn one
effect indistinguishable from zero into another effect indistinguishable from zero. All six carry a
reported effect of 0.1 or less in absolute value. The gate reports them as unprotected rather than
counting them as passes.

| Trial | Marker | Reported | Arms | Bound |
| --- | --- | --- | --- | --- |
| 4B trial | HbA1c | -0.04 | -1.13 / -1.10 | 0.060 |
| DURATION-3 | DBP | 0.00 | -1 / -1 | 1.500 |
| 4B trial | TC | -0.10 | -0.1 / -0.0 | 0.150 |
| 4B trial | LDL | -0.10 | -0.1 / -0.0 | 0.150 |
| EUREXA | TC | 0.00 | 0.1 / 0.1 | 0.150 |
| EUREXA | LDL | 0.10 | 0.2 / 0.1 | 0.150 |

## Defect found in the master, not in the rows

On four of the 38 rows all three numbers reach the master without a decimal point, so the gate cannot
read their printed precision and falls back to the most conservative assumption, a half width of 0.5.
The cause is upstream: the master normalises numbers, so a source that printed -1.0 is stored as -1,
and a source that printed -3.0 and -1.0 for the two arms of DURATION-3 systolic pressure yields a
bound of 1.5 where the true bound is 0.15. The gate is ten times too permissive on those rows.

The fix belongs in the extraction writer, which should preserve the printed form of each value as a
string beside its numeric form rather than discarding it. That is a change to a shared schema and
therefore additive, not a rewrite, and it would re-touch all 524 rows; it is recorded here as an
amendment candidate for the Director rather than applied. Within a row the gate already uses the
finest precision that any of the three numbers does carry, which recovers the bound wherever one of
them survived normalisation; the four rows listed are those where none did.

| Trial | Marker | Bound used | Bound the source supports |
| --- | --- | --- | --- |
| DURATION-3 | SBP | 1.500 | 0.150 |
| DURATION-3 | DBP | 1.500 | 0.150 |
| DURATION-3 | resting_heart_rate | 1.500 | 0.150 |
| 4B trial | adiponectin | 1.500 | 1.500, the source prints integers |

## Scope limit, stated plainly

The 122 rows whose effect was derived from their own arm values are outside this gate and cannot be
brought inside it. A swap there flips the derived effect as well, so the two agree by construction
and the comparison is empty. Orientation on those rows is decided by what the source states in
words, which is the third of the gate candidates named in the gate chain document and not yet built.
