# 4.10 Strengths and limitations

Written 19 October 2026. This section depends on the design and the provenance record rather than on
the pooled estimates, which is why it is drafted while the decisions that will move those estimates
are still open. Every count in it is traceable to a file in the repository.

## 4.10.1 What the design does well

**The analysis was fixed before the data existed.** The protocol, the five questions, the four
hypotheses with their directions, the estimator, the moderator, the weighting schemes and the
reporting rules were written and committed before any trial was extracted, and the ordering is
checkable in the commit history rather than asserted. One hypothesis, that GDF-15 modification tracks
receptor engagement, was recorded in advance as untestable with available data precisely so that it
could not later be presented as a prediction the corpus had confirmed.

**Reporting rules that bind against the authors' interest.** Three were fixed in advance and have
teeth. A pooled estimate whose direction or significance reverses on removal of one trial is reported
as fragile and is not advanced as a conclusion whatever its nominal p value. A composite ranking is
reported as a finding only where it is stable across every weighting scheme, and where the ranking
moves with the weighting that instability is itself the result. Any composite is reported with the
number of contributing biomarkers beside it, because a score over seven markers is not commensurate
with one over sixteen.

**Provenance is verified mechanically rather than attested.** Fifteen automated gates run over the
corpus on every change. Eight validate the pipeline against its own declarations and recover known
parameters from simulated data. Seven interrogate the corpus: that every pooled figure written in the
narrative is the figure the pipeline produced; that no packet bundles two unrelated studies, which
would silently drop the study nobody read; that each extracted number sits beside its own biomarker
in its source rather than beside a neighbouring table row; that a row's printed p value reconciles
with the p implied by its own effect and standard error; that no two trials report the same run of
values; that a row's arm values and its reported effect agree in sign and magnitude, which is the
signature of a swapped arm; and what the preceding gates are entitled to establish. Three data
integrity exclusions were made on that basis, each recorded with the arithmetic that justified it,
including one trial whose printed paired p values are impossible for its printed means and standard
deviations.

**The gates found defects in the gates.** Five checking errors were discovered and fixed, every one
of which had been suppressing verification rather than raising false alarms, which is the failure mode
a green chain hides. Sources that print the decimal separator as a middle dot had every number of such
a capture miss. A companion capture cited in one row's notes was searched only for that row. A
capture that kept each marker's label at the head of a long block made six correct rows read as weak.
A blindness test was conflated with unknown precision. And the evidence the attachment gate printed
varied between runs with the interpreter's string hash order, so an audit record did not reproduce.

## 4.10.2 Limitations of the evidence base

**The corpus was assembled in two ways that are not equivalent, and the review does not describe
itself as a single systematic search.** The dual, glucagon receptor containing and triple agonist
evidence comes from our own searching of three bibliographic databases and a registry. The mono
agonist comparator pool is adopted from the included study lists of two published reviews, re
screened against this review's criteria but not independently searched. The structure is closer to an
overview of reviews for the comparator arm with original searching for the agents those reviews do not
cover, and the flow diagram shows the two inflows separately rather than merging them.

**Screening agreement at full text was poor and is reported as it is.** Cohen kappa was 0.160 over
556 jointly screened records, with raw agreement of 73.6 per cent, because one reviewer was far more
inclusive than the other and the marginals were therefore extremely unbalanced. Every one of the 149
disagreements was adjudicated, 51 to include and 98 to exclude, and a sensitivity audit at the title
and abstract stage found that 5 of 37 known relevant records had been wrongly excluded by both
reviewers in two recurring criterion misreadings; the criteria were clarified and the exclusions
rescreened, which rescued 24 records including 3 of the 5 known misses. A kappa of that magnitude
does not support a claim of reliable duplicate screening, and the adjudication record rather than the
kappa is what this review relies on.

**Extractable variance was the binding eligibility constraint, and it excluded more studies than
eligibility did.** Of 340 study groups, 188 were closed because no dispersion, interval or exact p
value from which a standard error is recoverable was reported, against 37 closed for an eligibility
failure visible only at extraction. A synthesis of this literature is therefore a synthesis of the
part of it that reports variance, and trials reporting direction without values are absent from every
pooled estimate.

**One prespecified marker has no data at all.** The inventory declares an epigenetic age entry and
the corpus carries no contrast for it, for any agent. The premise that makes this class interesting
in aging terms is randomised evidence that semaglutide moves validated epigenetic clocks, and that
evidence concerns one molecule; no trial in this corpus measured a clock. The review cannot extend
that finding to receptor classes and does not attempt to.

**Off treatment trajectory is published for body weight only.** Nothing comparable exists for hepatic
fat, inflammatory markers or epigenetic age, for any agent, which bounds the normalisation thresholds
of the fifth question to a provisional status they are offered in rather than claimed beyond.

**Aging biomarkers appear in this literature predominantly in post hoc analyses rather than as
prespecified endpoints.** Selective reporting in that setting is not detectable by funnel asymmetry,
because results that were never reported do not enter the literature as small imprecise studies. The
review extracts whether each contrast was a prespecified endpoint so that the extent of post hoc
reporting is at least visible, and no method available here resolves it.

## 4.10.3 Limitations of the analysis

**The pooling scale is percent change rather than the standardised mean difference the protocol
registered.** The standardised mean difference requires arm level means, standard deviations and
sample sizes, which this literature does not publish for most contrasts: those quantities are present
on 160 of 524 rows and complete on fewer. The deviation is disclosed with the five others in the
Methods.

**One arm per trial per biomarker.** Several trials contribute multiple dose arms against one shared
comparator, and pooling those as independent studies counts the comparator patients repeatedly and
narrows every interval that includes them. The highest dose arm is retained, which collapses 483
analysable rows to 389 and drops 94 dose arms. The rule is absent from the registered plan, which
assumed one contrast per trial, and its effect is visible in the pooled k of every biomarker.

**Thirty eight rows cannot be placed on the percent change scale** because no admissible baseline
denominator is printed in any text in hand. For markers whose distribution is strongly skewed a
median baseline is not an acceptable denominator, and those rows stay in native units rather than
being converted on an assumption.

**Four biomarkers are reported with a single contributing trial.** Bone mineral density, intercellular
adhesion molecule 1, YKL-40 and mid regional pro atrial natriuretic peptide appear in the synthesis
table with an estimate and a confidence interval that are one trial's. A row in a meta-analysis table
reads as synthesis, and these are not.

**Several meta-regression models are saturated rather than explanatory.** Where a biomarker
contributes few trials relative to the receptor classes present, a high proportion of between study
variance explained reflects parameters fitting points and not a mechanism identified. The
identifiability rule requires contributing trials to exceed estimated parameters by at least three,
and models meeting that rule only narrowly are read with the fragility rule rather than at face value.
Where the primary estimator did not converge, the estimator that produced the fit is reported per
biomarker rather than presented as uniform.

## 4.10.4 A limitation of the verification itself

The provenance gates compare each number against the text retained for its trial, and that text is of
two kinds. Some is the publisher's own, arriving as text from a retrieval interface or as a saved
dump of a rendered page; against that, agreement is independent verification that the extraction
reproduces the source. The rest was written during this review by reading a page that could not be
retrieved as text, and carries this review's own captions and column labels; against that, agreement
establishes that the extraction reproduces the capture, and a misreading at the capture step would be
reproduced rather than caught.

Of the 524 rows, 295 have their numbers located in publisher text, 101 in a capture alone, 12 in both,
four in a conference abstract or registry entry alone, and 112 in no retained source. So 19 per cent
of the corpus rests on sources made during this review. Nothing indicates that any of those rows is
wrong; the limitation is on what the verification proves for them, and it was invisible until it was
measured. Reducing it requires retrieving publisher text for those trials, which is in progress.

Separately, bibliographic verification of the included studies found that 8 of 76 trials record a
first author naming one publication while the recorded identifier resolves to another, and 6 carry an
identifier that does not resolve in the indexed literature at all. No pooled estimate is in doubt,
since every number was read from a retained text and checked against it; what is in question is which
publication the reference list names.
