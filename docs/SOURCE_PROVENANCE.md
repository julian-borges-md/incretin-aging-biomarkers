# Source provenance

Companion to `src/source_provenance.py`, the fifteenth gate of the chain. This document doubles as
the gate's allowlist for captures whose making is no longer recoverable.

Run `python3 -I src/source_provenance.py` from the repository root. Outputs
`analysis/data/source_provenance.csv` (one line per retained file) and
`analysis/data/row_source_provenance.csv` (one line per master row).

## The question, and why it was not asked earlier

Gates nine, ten and eleven compare a row's numbers against the text retained for its trial, and
their results were reported as though "the source" were one kind of thing. It is not. Some retained
files are the publisher's own words, arriving as text from an interface or as a saved dump of a
rendered page. Others were written during this review by a session reading a page it could not
retrieve as text, and those carry the session's captions, its column labels and its choice of what to
transcribe.

The difference decides what a match proves. Against publisher text, a match is independent
verification that the extraction reproduces the source. Against a session capture, a match
establishes that the extraction reproduces the capture, and a misreading at the capture step is
reproduced rather than caught. Nothing recorded which was which, so every gate's count mixed them,
and the manuscript's attachment figure claimed the stronger thing for both.

This came to light while measuring a different gate, not from an audit of these gates.

## Result, 16 October 2026

Classification is from the packet manifest's own record of the retrieval route where there is one,
from signatures in the file otherwise, and from the file's directory only as a last resort. The
retained set is the 86 files the master's 76 trials actually cite, not the 439 files under `work/`:
most of the rest are search-stage fetches no row depends on.

| Provenance class | Files | Evidence |
| --- | --- | --- |
| publisher_page | 31 | manifest route `proxy_fulltext`, or a fetch header with the saved page text |
| publisher_api | 23 | manifest route `epmc_fulltext` or `direct_fulltext` |
| indexed_abstract | 19 | manifest route `conference_abstract` |
| session_capture | 11 | the file's own `CAPTURED` header or capture preamble |
| session_capture_undeclared | 2 | in the companion directory with no preamble; see below |

No retained file holds a retrieval failure, and no packet records a full text whose saved file holds
none. Those checks run on every pass because the manifest records what was attempted while the file
records what arrived, and the two can disagree.

## What this does to the gates' counts

Each row is attributed to the file whose lines actually carry its numbers, under the same matching
rule gate eleven uses, imported rather than reimplemented. The first draft attributed each row to the
strongest source its trial retained, which would have reported the six SURPASS-3 MRI rows as resting
on a conference abstract when their numbers are in a session capture and nowhere else.

| The source a row's numbers were located in | Rows |
| --- | --- |
| Publisher full text | 295 |
| Session capture only | 101 |
| Mixed, capture and publisher | 12 |
| Abstract or registry only | 4 |
| Numbers not located in any retained source | 112 |

The last figure reconciles exactly with gate eleven's 64 unlocated plus 48 without retained text,
which is the check that this registry and that gate mean the same thing by a row's source.

**So 101 of 524 rows, 19 per cent of the corpus, rest on session written captures alone.** That is
the figure the manuscript must carry. It is not a defect in those rows and nothing suggests any of
them is wrong; it is a limit on what the provenance gates establish for them, and it was previously
invisible. Nineteen per cent is too large to leave inside an unqualified claim.

Rows resting on captures alone, by trial: 4B trial (11), NCT04019561 (many, dose arms duplicated),
DURATION-3 (10), Dutour 2016 (12), SCALE Obesity and Prediabetes 3 year (10), EUREXA (7), Davies 2013
exenatide against detemir (6), SURPASS-3 MRI (6), NCT04822181 (6), Derosa 2011 exenatide against
glimepiride (6), DUAL II (2), NCT01761318 (1), Yu 2015 Dalian (1). The full list is in
`analysis/data/row_source_provenance.csv`.

## The capture convention, now enforced

A capture must state when it was read, from where, and by what means. Most do, in a `CAPTURED` header
or a prose preamble, and those preambles are the reason this classification was possible at all.
From this gate onward the convention is enforced: a capture without a preamble is classified
`session_capture_undeclared` and fails the chain unless it is written up here.

Two pre-existing files are allowed, because their making cannot be reconstructed now and inventing a
declaration for them would be worse than recording the gap.

| File | Why it is allowed rather than declared |
| --- | --- |
| `work/fulltext/companion/simo2015_eurexa_hscrp.txt` | Opens with section markers of the kind the text retrieval route produces, so it may be publisher text filed in the companion directory rather than a capture at all. Neither reading can be confirmed from the file, and the stricter of the two is recorded. |
| `work/fulltext/companion/yu2015_jem304w_tables1_3.txt` | A transcription of Tables 1 and 3 of the Journal of Endocrinology and Metabolism article, written without a preamble. The route is not recorded in the file and is not reconstructed here. |

Both are treated as session captures in every count above, which is the conservative reading. The
single row sourced from the second, the Yu 2015 Dalian HOMA-beta row, is already on the verifier's
list for other reasons.

## What this does not establish

The registry classifies the retained file, not the care taken when it was made. A declared capture is
not thereby a correct capture; the declaration only tells a reader what kind of evidence they are
looking at and lets the 101 rows be counted. Verifying those rows against the publisher's own text
requires retrieving that text, which for most of them means the supplement and appendix pass, and
that is the Director's call on downloads.
