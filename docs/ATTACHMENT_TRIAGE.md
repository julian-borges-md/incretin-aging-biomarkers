# Attachment triage, 16 October 2026

## What the attachment check asks, and why it is not the numbers check

`src/extraction_numbers_check.py` asks whether every number an extractor wrote occurs somewhere in
the source text. It cannot ask whether the number was attached to the right biomarker, and a value
lifted from the neighbouring row of a table passes it. `src/extraction_attachment_check.py` asks the
second question over the whole master: it finds the lines of the row's sources that carry the row's
numbers and checks whether a synonym of the row's biomarker is on those lines or within eight lines
of them, which is where a table keeps its row label.

Verdicts over the 518 rows at the 16 October corpus: 404 OK, 2 WEAK, 64 NOLINE, 48 NOTEXT. NOLINE is
a row whose numbers are not on any single line of the retained source, which is the normal shape of
a row read from a vertically fragmented capture or computed by the session from printed values;
NOTEXT is a trial whose source capture is not retained in the repository, which is the normal shape
of a licensed full text that the gitignore keeps out of version control.

Two defects in the check itself were found and fixed while running it, and both had been suppressing
real verification rather than creating false alarms. The first: Lancet style sources print the
decimal separator as a middle dot, so every number of such a capture missed, and fixing it moved 40
rows from NOLINE to OK and cleared the SCALE pressure rows. The second: a companion capture is cited
in the notes of the row that needed it, not of every row of its trial, so the sources of a trial are
now the union over its rows.

## The two WEAK rows, read one by one

| Trial | Marker | Verdict |
|---|---|---|
| MDI-liraglutide study (Sweden) | adiponectin | VERIFIED CORRECT, layout artifact. The capture of this table prints one value per line, so the marker label sits far above its values. The line that carries the row's numbers reads `(-0.13, 1.26) 0.85 (3.26) (-0.37, 2.06) 0.17`, which is the baseline adjusted difference 0.85, 95 per cent CI minus 0.37 to 2.06, p 0.17, exactly as extracted, and the arm baselines 4.47 and 4.39 mg/L appear in the same table block. No change. |
| NCT03131687-BIO | hsCRP | NOT VERIFIABLE FROM THE RETAINED SOURCE, and the only row of the corpus in that state. The row holds the dulaglutide comparator arm of the tirzepatide phase 2 biomarker post hoc (mean change minus 18.2, SEM 10.1 against minus 1.7, SEM 13.2), and those four numbers are on no line of the retained capture, which carries the paper's prose and not the figure or supplementary table the values came from. The row's notes do not name the table it was read from. It must be re-verified against the paper's supplementary material before the manuscript is final; it is kept rather than deleted because nothing suggests the numbers are wrong, and this entry is the record that its provenance is unshown. The same supplementary table is already in the supplement queue for the adiponectin denominators of this trial, so one capture settles both. |

## Five rows cleared by widening the label vocabulary, not by changing an extraction

These were WEAK only because the source writes the marker label in a form the check did not know.
Each was read and each extraction is correct: `Gamma- GT` for GGT (EudraCT 2013-004947-22), `FPI` and
`FINS` for fasting insulin (Derosa 2010, Quan 2017), `TG,` for triglycerides (Suzuki 2014), `THC` for
total cholesterol (Zhu 2017) and `HbA1 c` for HbA1c (PROXYMO, two rows). The vocabulary now holds
them, which is the fix: a label the check cannot read is a check defect, not an extraction defect.

## A capture practice the gate taught, same day

The six SURPASS-3 MRI rows extracted on 16 October were WEAK on their first pass, because the
companion capture kept each marker's label at the head of a fourteen line block while the gate looks
eight lines either side. The fix was not to widen the window. The capture was rewritten so that every
value line names its own marker, in the form `LFC percentage, relative ETD, tirzepatide 10 mg vs
insulin degludec: -35.94 (-51.62 to -20.27)`, and all six rows then verified line by line rather than
by proximity; the vocabulary also gained the `LFC` abbreviation the source uses. Captures written from
now on should label each value line, because a line that states its own marker is verifiable on its
own and a block header is not.
