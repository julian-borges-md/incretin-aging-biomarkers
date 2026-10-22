# Timepoint triage

Companion to `src/timepoint_check.py`, the twenty fifth gate, and to
`src/corpus_registry_harvest.py`, which retrieves what it reads. Run with
`python3 -I src/timepoint_check.py --self-test` from the repository root, after
`python3 -I src/corpus_registry_harvest.py` has populated `work/fulltext/registry_corpus/`, which is
gitignored like every other retrieved source.

The gate asks, for a row the review records as the trial's prespecified endpoint, whether the
timepoint it was read at is the timepoint the trial REGISTERED as its primary endpoint. A row that is
not so flagged carries no expectation and gets no verdict: most of this corpus's markers are
secondary outcomes reported at whatever visit the paper chose, and a week 24 reading in a week 48
trial is a fact about the paper, not a defect.

## The reach, measured before the gate was built, and the first measurement was wrong

Version 1.1 of the chain document listed this candidate as "stands, unmeasured" and the more fragile
of the two remaining, because it needs registry retrieval. The measurement was run first, under the
rule that a gate which cannot reach enough of its scope does not get a slot.

| Measurement | Comparable rows |
| --- | --- |
| Against the registry records already on disk | 5 of 524 |
| After retrieving the records of the corpus itself | 291 of 524 |

The first number is not a property of the data. 38 registry records were on disk, retrieved during
screening by `src/ctgov_harvest.py`, which is driven by the screening pool and fetches the records of
pool entries whose retrieval route was the registry. Of the 44 included trials that carry a registry
identifier, exactly **one** had a record there. A reach measured against what happened to have been
retrieved is not a reach, and reporting 5 of 524 would have struck the candidate on the strength of a
retrieval gap.

`src/corpus_registry_harvest.py` retrieves the records of the corpus. It resolves a trial to a
registry identifier by three lookups, in order of directness, and records which one each trial rests
on:

| Lookup | Trials |
| --- | --- |
| The identifier is in the trial's own label | 27 |
| An NCT appears in the extraction notes of one of the trial's rows | 14 |
| The extraction ledger's identifiers column, through the group whose reconciled file holds the trial's rows | 3 |
| No registry identifier anywhere in the repository | 32 |

All 44 records retrieved, all 44 state at least one primary outcome.

## A deadline is not a visit, and reading it as one produced six false findings

ClinicalTrials.gov states a primary outcome's time frame as free text, and two shapes occur here:

| Shape | Example from this corpus | What the row's timepoint should do |
| --- | --- | --- |
| A point | `48 weeks`, `6 months` | equal it, within one week |
| A window | `Baseline to end of Period II (up to 4.5 years)` | fall inside it |

The first implementation took the largest quantity in the string as a point. Six EUREXA rows, read at
36 months inside a window stated as up to 4.5 years, were reported as disagreeing with the
registration. A rule that cannot tell a deadline from a visit is not reading the registry, it is
reading numbers out of it. The gate now detects the window phrases (`up to`, `through`, `until`,
`over`, `during`, `within`, `end of`, `by week`, `by month`) and treats every quantity in that time
frame as a window end, which is the conservative reading because it accepts more and therefore
reports less. Both shapes are fixtures in the self test.

## Result

| Verdict | Rows | Meaning |
| --- | --- | --- |
| MATCHES | 234 | the row's timepoint is a registered primary time point, or inside a registered window |
| OUTSIDE | 4 | the row is flagged as the trial's prespecified endpoint and its timepoint is neither |
| CONTEXT | 53 | the row is not flagged, so no expectation applies. Counted, never a verdict |
| UNREACHABLE | 233 | 143 trials with no registry identifier, 68 rows with no timepoint recorded, 22 rows whose registry time frame does not parse to weeks |

The self test shifts every MATCHES row 500 weeks and requires the verdict to change; it does on all
234. The 22 unparsed rows are one trial whose time frame reads `seven months` in words.

## The four OUTSIDE rows, judged

None is an extraction error. All four are the same finding, which is worth the gate on its own.

| Trial | Marker | Reading | Verdict |
| --- | --- | --- | --- |
| NCT01147627 Drum Tower MRS substudy | liver_fat_pdff | Row at 24 weeks. The registration's primary outcome is the between group change in HbA1c at 48 weeks. This row is intrahepatic fat by proton MRS from the trial's MRS substudy report, whose own endpoint is at 24 weeks, and the trial's HbA1c row in this corpus is also at 24 weeks and is not flagged | Judged, no change. The flag records the substudy report's endpoint, not the parent trial's registration |
| STARDUST | hsCRP | Row at 18 months. The registration's primary outcome is peripheral transcutaneous oxygen pressure at 6 months, and every secondary outcome it lists is also at 6 months. The inflammatory markers at 18 months are prespecified by the report, not by the registration | Judged, no change |
| STARDUST | IL6 | As above | Judged, no change |
| STARDUST | TNF_alpha | As above | Judged, no change |

## What the four tell the review, which is the point of the gate

`docs/EXTRACTION_BRIEF.md` defines the field as TRUE "only when the paper **or its registration**
names the biomarker as a prespecified endpoint", and `prespecification/analysis_plan.md` says why it
is extracted at all: aging biomarkers in this literature appear predominantly in industry post hoc
analyses, and the field is what makes the extent of post hoc reporting visible, since no statistical
method available here resolves undetectable reporting bias.

The field therefore conflates two things a reader will not separate on their own: prespecified by the
registration, and prespecified by the paper that reported it. This gate measures the difference for
the first time. Of the rows it can reach, 234 sit at a registered primary endpoint and 4 are
prespecified by their paper at a timepoint the registration does not carry.

| Next action | Status |
| --- | --- |
| State in the Methods that `prespecified_endpoint` means the paper or its registration, and give the gate's two counts, so the reporting bias discussion rests on a measured distinction rather than on the field's name | Open, and it is a writing change rather than a data change |
| Decide whether the field should be split into `prespecified_in_registration` and `prespecified_in_report` | For the Director. Additive to the schema; it would retouch the 256 flagged rows, and the gate's output is the evidence for whether that is worth doing |
| Resolve registry identifiers for the 32 trials that carry none | Measured ceiling: 143 of the 233 unreachable rows. Most are older single centre studies; one records a EudraCT number instead of an NCT, which this gate cannot read |

## Scope limit, stated as every gate in this chain states its own

The comparison is against the registry, which is independent of both the paper and this review, so
an agreement is evidence that the row was read at the endpoint the trial declared. It establishes
nothing about whether the VALUE at that timepoint was read correctly, which is what gates nine to
twenty four are for. It also cannot see a trial that registered no primary outcome time frame in
weeks, a trial with no registry record, or a row the extraction left without a timepoint.
