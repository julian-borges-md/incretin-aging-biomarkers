# Duplicate number triage, 16 October 2026

## What this gate asks

Does the same contrast appear under two different trial identifiers? Two papers reporting the same
patients under different names is duplicate publication, and pooling both counts those patients
twice while shrinking the interval as though the evidence had doubled. `src/duplicate_numbers_check.py`
(gate thirteen) fingerprints every row by the values a paper would have to repeat for a duplication
to be real, compares fingerprints only between different trial identifiers, and reports a pair when
two rows of the same biomarker share at least two of those values exactly as printed.

Result over the 524 rows of the 16 October corpus: **no hard pair**, and 14 soft pairs, all read and
all coincidence.

## The soft pairs, and why each is a coincidence rather than a duplication

| Pair | Marker | Why it is coincidence |
|---|---|---|
| Fan 2013 and PIONEER 1 | hsCRP | The shared values are 0.59 and 0.89. In Fan 2013 they are an absolute change of minus 0.89 mg/L with an SD of 0.59; in PIONEER 1 they are the two bounds of a ratio interval, 0.59 to 0.89. Different quantities, different scales, same digits. Worth stating because Fan 2013 is already under a duplication question for a different reason, its post treatment ALT means, and this pair is not evidence for that question. |
| Derosa 2011, DUAL II and Yu 2015 (three pairs) | HbA1c | The shared values are baseline HbA1c of 8.7 and 8.8 per cent. Three unrelated trials in type 2 diabetes uncontrolled on oral agents enrol at the same entry criterion, so they report the same baseline to one decimal. |
| SCALE 3 year with STEP UP, and with STEP 1 | HbA1c | Baseline HbA1c of 5.7 per cent in obesity trials without diabetes, plus one change value of 0.24 or 0.32. Both are the expected values for a normoglycaemic entry criterion. |
| Dutour 2016, Quan 2017 and Savvidou 2016 (three pairs) | TG, LDL | Triglycerides of 1.6 to 1.9 mmol/L and LDL of 2.4 to 2.7 mmol/L are the central values of the distribution these populations draw from. |
| NCT01761318 and the 4B trial | LDL | 2.5 and 2.6 mmol/L, same reason. |
| NCT05564117 and STEP UP | LDL | 0.89 and 0.95, which are ratio values on the relative scale in both cases and sit where a 5 to 10 per cent reduction sits. |
| Derosa 2011 and Derosa-2012 | adiponectin | 4.7 and 4.9. These are two trials by the same group in the same population, so shared baseline values are expected rather than suspicious; the trials differ in comparator and duration. |
| NCT03951753 and NCT04844918 | adiponectin | 3.8 and 4.3, two tirzepatide trials in the same population. |
| Derosa 2010 and Derosa-2012 | HOMA_IR | 6.9 and 7.4, the same group's baseline insulin resistance in comparable cohorts. |

## The scope limit, which matters for the case that prompted the gate

This gate sees the pooled rows. The duplication already on the Director's decision list was found in
a record that never entered the master: a 2018 report whose post treatment ALT means of 39.82 and
51.48 U/L are, to two decimals, the values Fan 2013 reports for a different drug in the same
population. That record was excluded at extraction, so its numbers are in the ledger's reason field
and not in any row, and no fingerprint comparison over the master can reach it. A gate that covered
excluded records would have to extract them first, which is the opposite of what exclusion means.

The honest statement is therefore narrow and worth keeping: among the contrasts that are pooled, no
two trials report the same numbers. Whether Fan 2013's own rows stay in the analysis remains a
Director decision, and this gate neither supports nor weakens it.
