# Arm attribution triage

Companion to `src/arm_attribution_check.py`. **This is a probe, not a chain gate.** It is committed,
it runs, it is correct where it speaks, and it is deliberately not wired into `scripts/run_gates.sh`,
for the reason in the last section. Run it with
`python3 -I src/arm_attribution_check.py --self-test` from the repository root.

## The hole it was built for

Gate fourteen compares a row's arm values with its reported effect, which is possible only where the
paper printed both: 38 of 524 rows. On the 122 rows whose effect was **derived** from the arm values
there is nothing to compare, because a swapped arm flips the derived effect too and the two then agree
by construction. Those 122 rows are the corpus's orientation blind spot.

## The candidate named in the chain document is struck, for a structural reason

Version 1.0 of `M5-AGE-provenance-gate-chain` named, as its third candidate, a sign check between a
row's direction and the direction its source states in words. That candidate cannot work, and the
reason is structural rather than technical: **a derived row exists precisely because the paper never
computed the between group contrast, so the paper's text cannot state that contrast's sign.**

The probe that established this is worth keeping. Of eight derived rows sampled, seven had at least
one sentence pairing the marker with a direction word, and not one of those sentences was about the
contrast. They were about each arm's own change, as in "HbA1c was significantly reduced to a similar
extent among three groups (exenatide delta = -2.9 vs insulin delta = -2.8)". A direction word about
one arm says nothing about the sign of a difference between two arms: here both arms fell and the
contrast is -0.10, near zero. A keyword gate built on those sentences would have mapped "reduced" to
an expected negative contrast and been right only by luck. Most matched sentences were worse than
that, being background or methods prose that merely contained a marker name and a direction word.

## What replaced it, and what it achieves

The same probe showed what the sources *do* state: narrative text names each arm immediately before
its value. So the check asks, per derived row, which arm name the source puts in front of each of the
two values it recorded.

| Verdict | Rows | Meaning |
| --- | --- | --- |
| ALIGNED | 3 | the drug's name precedes the treatment value and the comparator's the control value |
| REVERSED | 0 | the opposite, which would be a swapped arm in the extraction |
| UNCLEAR | 119 | no attribution available from the text |

The self test swaps the arms of each ALIGNED row and the verdict flips to REVERSED on all three, so
the check does discriminate. No arm is reversed in any row it can read.

## REVERSED rows

| Trial | Marker | Verdict | Reading |
| --- | --- | --- | --- |

None.

## The three rows it reads, with their evidence

| Trial | Marker | Line that attributes the values |
| --- | --- | --- |
| NCT01147627 Drum Tower MRS substudy | HbA1c | "...among three groups (exenatide delta = -2.9 +/- 0.4 % vs. insulin delta = -2.8 +/- 0.3 %..." |
| NCT01147627 Drum Tower MRS substudy | TNF_alpha | "...significantly decreased plasma TNFalpha levels (exenatide delta = -62 +/- 19 %, P = 0.012; insulin delta = -60 +/- 17 %..." |
| Dutour 2016 | liver_fat_pdff | "Exenatide induced significant reduction in EAT (-8.8+/-2.1%), and HTGC (-23.8+/-9.5%), compared to reference treated group, respectively (-1.2+/-1.6%... and +12.5+/-9.6%..." |

A note on the third, because it cost a near miss. The capture holds that entire abstract as one line
of 1825 characters, and the first draft of the report printed the first 160 characters of the matching
line as its evidence. That showed background prose beside a verdict drawn from text 1100 characters
to the right, and on reading it the row looked like a false positive and was nearly discarded. The
attribution was correct; the audit line was wrong. The report now shows the region around the two
matches. An audit record that misrepresents its own evidence is worse than none, because it is
trusted.

## Why the other 119 are unreadable, and why this is not wired into the chain

| Reason | Rows |
| --- | --- |
| An arm name does not precede its value on the line | 80 |
| The two values never share a line within 200 characters | 29 |
| Both values are preceded by the same arm's name | 7 |
| The two arms print the same value, so no attribution is possible | 3 |

The 80 are the decisive group and they are not a tuning problem. They are table captures, where the
line holds `marker  7.2 +/- 0.8  7.5 +/- 0.9` and the arm names live in a header line well above it.
No lookback along the same line can reach a header, so widening the window would add false
attributions without adding true ones.

A gate that classifies 3 of 122 rows and prints 119 unclassifiable on every run is a green light that
means almost nothing, and the chain's own design rule is that a gate people learn to ignore is worse
than no gate. So this one stays out of `scripts/run_gates.sh` until its reach justifies the slot.

## What would make it viable, measured rather than assumed

The extension is to read the header above the value line. The measurement was run before building
anything, over the 80 rows whose arm name does not precede its value:

| Header within 25 lines above the value line | Rows |
| --- | --- |
| Names both arms | 69 |
| Names one arm | 1 |
| Names neither | 10 |

So the extension would lift the gate's reach from 3 rows to roughly 72 of 122, from 2.5 per cent of
the blind spot to about 59 per cent. That is worth a chain slot.

It is also simpler than character column geometry. These captures separate arms with a delimiter
rather than aligning columns, so the rule is an **order** rule: the order in which the header names
the arms fixes the order of the values on the line. The Davies 2013 rows are the pattern, header then
values:

    Outcome measures, exenatide once weekly against insulin detemir, baseline to week 26
    -1.32 (0.076), n 95 | -0.91 (0.077), n 96   [mixed models analysis]

## The caveat that extension must carry, and it is the important finding here

Not all headers are equal evidence, and the difference decides what the gate proves.

| Capture provenance | What a header check establishes |
| --- | --- |
| Raw publisher text, for example a full text fetched from EuropePMC | Independent verification: the header is the journal's, so agreement means the extraction matches the source |
| A capture written by this session from a page it read, for example the exenatide against detemir registry results | Internal consistency only: the header is the session's own caption, so agreement means the spec matches the capture, and both could be wrong together |

The Davies 2013 header above is a caption this session wrote. Checking the spec against it catches a
transcription slip between capture and spec, which is a real error class and one no existing gate
sees, but it is not fidelity to the publisher and must not be reported as such. A gate built on this
must therefore classify each row by its capture's provenance and report the two counts separately,
and the chain's reading of a green result must be correspondingly narrower for the second kind.

That distinction is not currently recorded anywhere in the corpus: nothing in the capture files or
the notes marks which are publisher text and which are session written. Establishing that marking is
a prerequisite for the extension, and a governance item in its own right, since every gate that reads
captures inherits the same ambiguity.
