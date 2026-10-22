# Arm attribution triage

Companion to `src/arm_attribution_check.py` and, since 22 October, to
`src/arm_header_attribution_check.py`. Run them with
`python3 -I src/arm_attribution_check.py --self-test` and
`python3 -I src/arm_header_attribution_check.py --self-test` from the repository root.

**Status, amended 2026-10-22.** Both are now chain gates, twenty three and twenty four, and the
chain went from twenty two gates to twenty four. Everything below the heading "Why the other 119 are
unreadable" was written when the first gate stood alone and its reach of 3 rows did not justify a
chain slot. The extension specified there has been built and attributes 15 rows; building it also
found and fixed a defect in the first gate's value locator, which took that gate from 3 rows to 8.
The pair attributes 23 of the 122 derived rows and finds no swapped arm. The section "The extension,
built 2026-10-22" records what the new gate does, what it refuses, the four false findings that
building it produced and the guards that removed them, and the locator fix. The earlier sections are
left as written where they are the record of a decision taken on the evidence then available, with
the counts updated and both states shown where a count changed.

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
| ALIGNED | 8 | the drug's name precedes the treatment value and the comparator's the control value |
| REVERSED | 0 | the opposite, which would be a swapped arm in the extraction |
| UNCLEAR | 114 | no attribution available from the text |

The self test swaps the arms of each ALIGNED row and the verdict flips to REVERSED on all eight, so
the check does discriminate. No arm is reversed in any row it can read.

**These were 3 and 119 until the locator was replaced on 22 October**, which is recorded in full
under "A defect in the first gate" below. The string locator required the row's printed value to
occur verbatim: a master value of `-4` did not match a source printing `-4.0`, and `+12.5` did not
match `12.5`. Matching numbers rather than strings recovered five rows and, in the other direction,
removed 25 rows from the same line reason into "the two values never share a line", because those
25 had been matched on a digit inside another number.

## REVERSED rows

| Trial | Marker | Verdict | Reading |
| --- | --- | --- | --- |

None.

## The eight rows it reads, with their evidence

The first three were the whole of its reach until 22 October; the last five arrived with the numeric
locator. Each of the five was read against the row's own extraction notes to confirm that the
sentence the gate matched is the source the row was taken from, or states the same values as it.

| Trial | Marker | Line that attributes the values |
| --- | --- | --- |
| NCT01147627 Drum Tower MRS substudy | HbA1c | "...among three groups (exenatide delta = -2.9 +/- 0.4 % vs. insulin delta = -2.8 +/- 0.3 %..." |
| NCT01147627 Drum Tower MRS substudy | TNF_alpha | "...significantly decreased plasma TNFalpha levels (exenatide delta = -62 +/- 19 %, P = 0.012; insulin delta = -60 +/- 17 %..." |
| NCT01147627 Drum Tower MRS substudy | liver_fat_pdff | "...IHF significantly reduced with three treatments (exenatide delta = -68 %, insulin delta = -58 %, pioglit..." |
| Dutour 2016 | liver_fat_pdff | "Exenatide induced significant reduction in EAT (-8.8+/-2.1%), and HTGC (-23.8+/-9.5%), compared to reference treated group, respectively (-1.2+/-1.6%... and +12.5+/-9.6%..." |
| BELIEVE, semaglutide 2.4 mg | SBP | "...at week 48 (bimagrumab: -3.1 mmHg to -4.6 mmHg; semaglutide: -7.9 mmHg to -8.6 mmHg; combination: ...; placebo: -6.9 mmHg)" |
| BELIEVE, semaglutide 1.0 mg | SBP | the same sentence, on the 1.0 mg value |
| NCT04844918 SURMOUNT-J, 10 mg | hsCRP | "...at week 72 following tirzepatide 10 mg and 15 mg (-55.1% [4.7] and -65.3% [3.4], respectively) compared with placebo (-17.7% [8.0]..." |
| NCT04844918 SURMOUNT-J, 15 mg | hsCRP | the same sentence, on the 15 mg value |

Three of the five sit in a sentence naming three or four arms, which the adjacent label rule handles
correctly and the header order rule cannot: the name immediately to the left of a value attributes
that value whatever else the sentence names. The BELIEVE rows were checked with particular care,
because the sentence states a range for each arm and the extraction took its numbers from Table 2;
the sentence's first value for each arm is the week 48 change the table reports, so the arm names in
it are evidence for the assignment even though the numbers were read from the table.

A note on the Dutour row, because it cost a near miss. The capture holds that entire abstract as one line
of 1825 characters, and the first draft of the report printed the first 160 characters of the matching
line as its evidence. That showed background prose beside a verdict drawn from text 1100 characters
to the right, and on reading it the row looked like a false positive and was nearly discarded. The
attribution was correct; the audit line was wrong. The report now shows the region around the two
matches. An audit record that misrepresents its own evidence is worse than none, because it is
trusted.

## Why the other 119 are unreadable, and why this is not wired into the chain

| Reason | Rows, as first measured | Rows, after the numeric locator |
| --- | --- | --- |
| An arm name does not precede its value on the line | 80 | 55 |
| The two values never share a line within 200 characters | 29 | 50 |
| Both values are preceded by the same arm's name | 7 | 6 |
| The two arms print the same value, so no attribution is possible | 3 | 3 |

The second column is the state since 22 October. The 25 rows that moved out of the first row of the
table are rows whose two values appeared to share a line only because the string locator matched a
digit inside another number; they share no line in fact. The first column is left in place because
the paragraphs below, and the extension built from them, were reasoned from it.

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

## The extension, built 2026-10-22

`src/arm_header_attribution_check.py`. Scope is the 80 rows above whose arm name does not precede
its value, taken from the first gate's own verdict rather than re-derived, so the two scopes are
complementary by construction and a change to that gate's wording empties this one rather than
silently shifting it.

The rule is the order rule this document specified: the order in which the header names the arms is
the order in which their values print below. Per row, every line carrying both values is a
candidate; the nearest header above each candidate, in the same file, must name both arms; and the
arm named first owns the value that prints first.

### Result

| Verdict | Independent source | Session capture | Total |
| --- | --- | --- | --- |
| ALIGNED | 9 | 6 | 15 |
| REVERSED | 0 | 0 | 0 |
| UNCLEAR | | | 40 |

Scope is 55 rows, not the 80 of the first measurement, because the numeric locator moved 25 rows out
of this gate's scope and into "the two values never share a line" above. All 15 attributions survived
that change, so the gate's reach is unchanged in rows and higher as a fraction of what it examines.

The self test injects a swapped pair into each of the 15 and the verdict flips on all 15, so the
gate discriminates. The two provenance columns are not added together anywhere in the output, for
the reason the caveat section above gives: against publisher text agreement verifies the extraction
against the source, and against a caption this review wrote it establishes only that the extraction
reproduces the capture. The 6 session rows are all Davies 2013.

| Why a row is unclassifiable | Rows |
| --- | --- |
| One of the two values coincides with a dispersion or a count rather than a column value | 15 |
| The two values are not adjacent columns on any line that carries both | 14 |
| The nearest line naming both arms names one of them more than once | 6 |
| No line within 25 lines above the values names both arms | 4 |
| The nearest line naming both arms is prose rather than a row of column labels | 1 |

### The projection was wrong, and by how much

This document projected that the extension would lift reach "from 3 rows to roughly 72 of 122". The
two gates reach 23: the header gate's 15 and, after the locator was replaced the same day, the
adjacent gate's 8. The projection measured one thing, whether a header within 25 lines names both arms, and
an order rule needs four more things to be true before it attributes anything. The first
implementation, which measured only what the projection measured, reported **five REVERSED rows, and
all five were artefacts of the rule rather than defects in the extraction.** Each is now a fixture in
the gate's self test.

| Artefact | What it was | The guard |
| --- | --- | --- |
| Light On liver fat, HbA1c, LDL, SBP | A three arm table. The row compares liraglutide against insulin glargine, columns one and three of nine fields, with the sitagliptin columns between them. No order rule can say which column either value came from | Every numeric token between the two matched values must be attached to a value, as a dispersion after a plus or minus sign, a count in brackets or a p value. A bare number between them is another column |
| Light On LDL, a second mechanism | The row records -0.01 against 0.2. On the HDL line below, 0.2 is the standard deviation of the liraglutide baseline and prints immediately before the HDL change of -0.01. Nothing stands between them, so the pair reads as two adjacent columns in the wrong order | Both ends must themselves be column values by the same attachment test |
| NCT02660047 GDF15, NCT04844918 leptin and hsCRP | The nearest line naming both arms was a figure caption and an abstract's randomisation sentence. A sentence names the arms in the order the sentence needs | A header must be a row of column labels: it splits into fields on a tab, a pipe or a run of spaces and names the two arms in different fields. A line that is not columnar is admitted only where the value line itself has exactly two fields, which is the two arm case and the shape this review's own captures use |
| Kelly 2012 triglycerides | Found while replacing the guard above. A length threshold of 110 characters admitted the paper's 101 character title, which names exenatide before metformin while the table prints metformin first, so the title inverted every verdict it attributed. Lowering the threshold to 90 then admitted a 78 character sentence that did the same | Length was the wrong test. The structural test above replaced it, and the row is now attributed from the real tab delimited header nine lines above it |
| Several, silently | The first implementation chose the single line on which the two values sat closest together, which is the first gate's rule. A spuriously tight pair elsewhere in the same paper beats the true pair sixty characters apart | Every candidate is classified and they must agree. A disagreement is reported as unclassifiable, which is what an ambiguous attribution is |

### A defect in the first gate, found by building the second, and resolved the same day

`src/arm_attribution_check.py` located a value as a **string**, and where the signed string missed it
fell back to the unsigned one. On this corpus that fallback matches the row value -4 against the
printed dispersion 4.5, because the digit 4 occurs in it standalone by the function's own test. The
second gate could not reuse that locator and carried a numeric one of its own for the length of one
commit: numeric tokens with their positions, compared as numbers, so 4.5 is the number 4.5 and
nothing else.

Two gates differing in a definition they should share was recorded as a next action rather than
fixed in the same pass, because the first gate's output was already in the commit record and in
Methods 2.11. It was then done, in the next pass, in the order that record requires:

| Step | Result |
| --- | --- |
| The locator moved into `arm_attribution_check`, which both gates now import | One definition, two callers, as the chain's standing rule requires |
| Both gates rerun and their outputs compared against the previous run | The adjacent gate goes from 3 attributed rows to 8 and from 119 unclassifiable to 114. The header gate attributes the same 15 over a scope reduced from 80 rows to 55 |
| The five new attributions read against their rows' extraction notes | All five genuine. Three sit in a sentence naming three or four arms, which the adjacent rule reads correctly; the two BELIEVE rows state in narrative the same week 48 values the extraction took from Table 2 |
| Methods 2.11 updated | The paragraph now states 8 and 15 attributed of 122, 99 unattributable, and the six reasons with their counts over the header gate's 55 row scope |

What the change did NOT do is report a new swapped arm. Both gates still find none, and the 25 rows
that left the header gate's scope left it because their two values never shared a line in the first
place.

### Why both now hold a chain slot

The stated rule for this chain is that a gate people learn to ignore is worse than no gate, and 3 of
122 did not clear it. Twenty three of 122 is still a minority, and each gate prints the reason for
every row it cannot read, which is the form in which a partial reach is honest rather than
misleading. What decides it is that the 23 are checked on every run rather than on the day someone
remembers to look, and that both gates carry a self test that fails the chain if their discrimination
stops working. The Methods state the 23 and the 99 explicitly, so the manuscript claims no more than
this.
