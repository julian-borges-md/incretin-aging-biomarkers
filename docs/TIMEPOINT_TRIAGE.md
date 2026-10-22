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
| After resolving nine further registrations from the publishers' own statements of them | 316 of 524 |

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
| `analysis/data/trial_registry_ids.csv`, resolved and verified by `src/registry_id_resolve.py` on 22 October | 9 |
| No registry identifier that any of the four lookups can find | 23 |

Fifty three trials have an identifier, 50 distinct records, every one stating at least one primary
outcome. The fourth lookup is the subject of the next section.

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
| MATCHES | 259 | the row's timepoint is a registered primary time point, or inside a registered window |
| OUTSIDE | 4 | the row is flagged as the trial's prespecified endpoint and its timepoint is neither |
| CONTEXT | 53 | the row is not flagged, so no expectation applies. Counted, never a verdict |
| UNREACHABLE | 208 | 118 rows in trials with no registry identifier, 68 rows with no timepoint recorded, 22 rows whose registry time frame does not parse to weeks |

The self test shifts every MATCHES row 500 weeks and requires the verdict to change; it does on all
259. The 22 unparsed rows are one trial whose time frame reads `seven months` in words. The counts
were 234 and 233 before the nine registrations below were resolved: 25 of the 40 rows those nine
trials hold reached a verdict, and the other 15 carry no timepoint or no parseable time frame.

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
the first time. Of the rows it can reach, 259 sit at a registered primary endpoint and 4 are
prespecified by their paper at a timepoint the registration does not carry.

| Next action | Status |
| --- | --- |
| State in the Methods that `prespecified_endpoint` means the paper or its registration, and give the gate's two counts, so the reporting bias discussion rests on a measured distinction rather than on the field's name | Open, and it is a writing change rather than a data change |
| Decide whether the field should be split into `prespecified_in_registration` and `prespecified_in_report` | For the Director, as D1 of the register. Additive to the schema; it would retouch the 256 flagged rows, and the gate's output is the evidence for whether that is worth doing |
| Resolve registry identifiers for the trials that carry none | **Done for 9 of the 32.** The section below records how, and what the attempt found. The remaining 23 hold 118 of the 208 unreachable rows |

## Resolving the missing registrations, and what the attempt found

`src/registry_id_resolve.py`, written for decision D2 of the Director register. It takes a
registration from the publisher's own statement of it, never from a search of the registry, because a
search finds a plausible record for almost every trial and plausible is the failure this gate exists
to avoid. Two routes: Europe PMC's indexed accession annotation of the article, which carries the
sentence the identifier was found in and the section it was in, and a scan of the retained source
text accepting an NCT only where the surrounding 120 characters say that it is a registration.

| Verdict | Trials | Rows |
| --- | --- | --- |
| verified | 9 | 40 |
| none_found, no registration in the article's annotation or its retained text | 23 | 154 |
| unverified or ambiguous | 0 | 0 |

### The first version resolved two pairs of trials to one registration each, and the drug check could not see it

This is the finding worth keeping. The first version accepted a candidate when the registration named
the trial's drug. That check passed for every candidate in two cases and therefore separated nothing:

| Case | What the first version did | Why the check could not see it |
| --- | --- | --- |
| STEP 2 and STEP 3 | Gave both `NCT03548935` | Both trials are semaglutide against placebo, and both are reported in one article that annotates several registrations. The drug check passes for each candidate |
| 1404-0002 and 1404-0036 | Gave both `NCT04667377` | Both are survodutide against placebo, reported in one article |

Two trials cannot share a registration, and the loser of each pair would have been given another
trial's primary endpoint for every one of its rows. **A verification that passes for every candidate
is not a verification.** Three checks now run, in order of what they establish:

| Check | What it establishes | Where it decided a case |
| --- | --- | --- |
| identifier | the registry's own `orgStudyIdInfo.id` or a secondary id EQUALS the review's label for the trial, punctuation removed. Verifies on its own | `NCT04153929` is registered as 1404-0002 and `NCT04667377` as 1404-0036, which separates and verifies the survodutide pair in one step |
| label | the label appears inside an identifier, the acronym or a title, with the match not followed by another digit so that `STEP 2` does not match `STEP 25`. Separates candidates; does not verify | `NCT03552757` and `NCT03611582` carry their STEP numbers in their titles, which separates the STEP pair; the drug check then verifies each |
| drug | the registration's interventions or arm labels name the trial's drug, or a development code the registry itself declares to be that drug | Six of the nine |

Where none of the three singles out one candidate, nothing is resolved and the trial is recorded as
ambiguous. On this corpus that happens zero times now and would have happened four times without the
first two checks.

### The synonym table is derived from the registry, not asserted here

`NCT04153929` names its intervention `BI 456906` and nothing else, so a check for `survodutide` fails
against the correct record. The equivalences are read out of the `otherNames` the registry states
beside each intervention, over every record the repository holds and every record the run fetches,
and are then restricted to the nine drug words this corpus actually studies. That yields five
entries, each one a statement a registry record makes:

| Drug | Code the registry declares to be that drug |
| --- | --- |
| survodutide | BI 456906, from the sibling trial NCT04667377, which names both |
| tirzepatide | LY3298176 |
| dulaglutide | LY2189265 |
| cotadutide | MEDI0382 |
| liraglutide | SUB25238, the EU substance code |

Before the restriction the same derivation produced entries keyed on `holder`, `number` and
`marketing`, from a record whose `otherNames` carry a marketing authorisation block. They were
harmless to a check that only ever asks about a trial's own drug, and they were removed anyway: a
derived table that states things nobody means is a table the next reader has to disbelieve in parts.

### The 23 that stay unresolved

Their articles state no registration, in the annotation or in the retained text. Most are older
single centre studies and one records a EudraCT number rather than an NCT, which this gate cannot
read. The honest reading is the one the limitations section should carry: for those trials the
prespecification cannot be verified at all, which is a stronger statement about the corpus than any
count of matching timepoints.

## Scope limit, stated as every gate in this chain states its own

The comparison is against the registry, which is independent of both the paper and this review, so
an agreement is evidence that the row was read at the endpoint the trial declared. It establishes
nothing about whether the VALUE at that timepoint was read correctly, which is what gates nine to
twenty four are for. It also cannot see a trial that registered no primary outcome time frame in
weeks, a trial with no registry record, or a row the extraction left without a timepoint.
