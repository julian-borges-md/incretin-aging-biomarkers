# PROSPERO submission content

Paste ready. Field names follow the PROSPERO registration form in order.

Prepared 2026-10-15. Derived from `prespecification/analysis_plan.md`, which was fixed before extraction began.

---

## Review title

Aging biomarker signatures of incretin and glucagon receptor agonism across receptor classes: a systematic review and network meta-analysis

## Original language title

(leave blank)

## Anticipated or actual start date

2026-10-14

## Anticipated completion date

2027-04-30

## Stage of review at time of this submission

Preliminary searches: Started
Piloting of the study selection process: Started
Formal screening of search results against eligibility criteria: Not started
Data extraction: Started
Risk of bias (quality) assessment: Not started
Data analysis: Not started

**Note on honesty of this field.** Preliminary PubMed searches have been run, the extraction schema has been piloted on one trial (Sanyal 2024, PMID 38858523), and that single extraction is complete. Formal screening has not begun. These selections reflect the actual state. The analysis plan was fixed and published publicly, with a timestamped commit history, before any extraction took place.

## Named contact

Julian Borges

## Named contact email

jyborges@bu.edu

## Named contact address

Department of Computer Science, Boston University, Boston, Massachusetts, United States

## Organisational affiliation of the review

Boston University

## Review team members and their organisational affiliations

Dr Julian Borges, Boston University

**TEAM MEMBER CONSTRAINT.** PROSPERO has previously required a minimum of two named team members. If the form rejects a single entry, this is the decision point, and it is yours rather than mine. Three options, in the order I would rank them:

1. Add a methodologist in a protocol review role only, not as a manuscript co-author. Preserves the sole author default.
2. Add a senior co-author now, binding them to authorship. Breaks the sole author default and should not be done without deliberate intent.
3. Contact PROSPERO to register as a sole reviewer, citing the independent agent review design.

Do not resolve this by naming someone who has not agreed.

## Funding sources / sponsors

None. No external funding was received for this review.

## Conflicts of interest

None.

## Collaborators

None.

## Review question

Which established aging biomarkers are modified by incretin and glucagon receptor containing peptide therapies, in which direction, and does the resulting biomarker signature differ by receptor class rather than by individual molecule?

Specifically:

1. Which of a pre-specified set of 26 biomarkers spanning seven aging hallmark domains are reported in randomised trials of these agents, and in which direction do they change?
2. Does the signature differ across four receptor classes: GLP-1 mono-agonists, GLP-1 and GIP dual agonists, GLP-1 and glucagon receptor dual agonists, and GLP-1, GIP and glucagon receptor triple agonists?
3. Is the hepatic aging signal with glucagon receptor containing agents independent of the magnitude of weight loss?
4. Can a composite Net Biological Age Impact Score compare receptor classes on a single scale?
5. What thresholds would define metabolic age normalisation sufficient to justify a structured treatment discontinuation trial?

## Searches

PubMed/MEDLINE, Embase via Ovid, Cochrane CENTRAL, Web of Science Core Collection, ClinicalTrials.gov and the WHO ICTRP, from inception, with no language or date restriction.

Supplemented by: reference lists of included trials and of prior systematic reviews in this area; forward citation searches of anchor publications; conference proceedings of EASD, ADA, The Obesity Society and ObesityWeek 2024 to 2026; and sponsor maintained disclosure registries for Eli Lilly, Novo Nordisk, Boehringer Ingelheim, Altimmune and Innovent Biologics.

Search terms combine drug specific terms for ten molecules with body composition, metabolic, hepatic, inflammatory and aging biomarker terms, and randomised design filters. Receptor class is not a search filter; it is an analytical operation applied to extracted data.

Full search strategies will be published as a supplement.

## URL to search strategy

https://github.com/julian-borges-md/incretin-aging-biomarkers

## Condition or domain being studied

Overweight, obesity, type 2 diabetes mellitus, and metabolic dysfunction associated steatotic liver disease or steatohepatitis.

## Participants / population

Adults aged 18 years or older with overweight (BMI 25 to 29.9), obesity (BMI 30 or greater), type 2 diabetes, MASLD or MASH.

Excluded: children and adolescents; type 1 diabetes; post bariatric surgery populations.

## Intervention(s), exposure(s)

Semaglutide, liraglutide, tirzepatide, retatrutide, survodutide, pemvidutide, mazdutide, cotadutide, amycretin, cagrilintide or CagriSema, at any dose, any formulation, administered for at least 12 weeks.

Each is assigned to a receptor class on the basis of its receptor pharmacology: GLP-1 mono (semaglutide, liraglutide); GLP-1 and GIP dual (tirzepatide); GLP-1 and glucagon dual (survodutide, mazdutide, pemvidutide, cotadutide); GLP-1, GIP and glucagon triple (retatrutide).

## Comparator(s) / control

Placebo, lifestyle modification, or an active comparator.

## Types of study to be included

Randomised controlled trials only. Observational studies, single arm studies, retrospective cohorts and case reports are excluded.

## Context

(leave blank)

## Main outcome(s)

1. Aging biomarker change by receptor class, adjusted for percentage body weight change by meta-regression.
2. The composite Net Biological Age Impact Score per receptor class, a weighted mean of direction adjusted standardised effects across all measured aging biomarkers.

### Measures of effect

Hedges' g for continuous outcomes; log odds ratio for binary outcomes. Every pooled estimate is reported with a 95% confidence interval **and** a 95% prediction interval, since under non-negligible heterogeneity these can support opposite conclusions and the prediction interval is the clinically relevant quantity.

## Additional outcome(s)

The receptor class differential in GDF-15, the strongest blood based predictor of biological aging; MASH resolution and fibrosis improvement by receptor class adjusted for weight loss; lean mass change as the unfavourable aging axis by receptor class; and off treatment regain kinetics by domain where data exist.

### Measures of effect

As above.

## Data extraction (selection and coding)

Trials are screened and extracted into a pre-specified schema covering trial metadata, baseline characteristics, 26 aging biomarkers mapped to hallmark domains, cardiometabolic outcomes and safety.

Screening, full text assessment and extraction use two independent reviewers blinded to each other and to prior decisions, with a third reviewer adjudicating disagreements. Agreement is logged per stage.

Effect sizes are resolved from whichever form each trial reports, through a documented conversion with its route recorded per row, so the provenance of every variance is visible in the dataset. A p value reported as a bound rather than an exact value yields no recoverable variance; such rows are flagged and excluded from pooling rather than being assigned the threshold, which would understate variance and overstate precision.

## Risk of bias (quality) assessment

Cochrane Risk of Bias 2, across all five domains, with an overall judgement per trial. Certainty of evidence by GRADE for each primary and secondary outcome.

## Strategy for data synthesis

Random effects meta-analysis, REML primary, with DerSimonian-Laird, Paule-Mandel and Sidik-Jonkman as sensitivity. Hartung-Knapp-Sidik-Jonkman correction applied where fewer than ten trials contribute, a rule validated empirically rather than assumed.

Heterogeneity reported as tau-squared primary, with I-squared for comparability. Every estimate carries a prediction interval.

Weight adjusted meta-regression of biomarker change on receptor class and percentage weight change, with the interaction, fitted only where trials exceed estimated parameters by at least three. All p values from permutation tests at 10,000 iterations, since Wald inference is anticonservative at these trial counts.

Network meta-analysis, frequentist graph theoretical, with a four node receptor class network primary and a ten node drug level network fitted in parallel. Node splitting and the design by treatment interaction test assess consistency. Material disagreement between the two networks would invalidate class level pooling, and would be reported as such.

The composite score is a weighted mean rather than a weighted sum, so it cannot inflate with the number of biomarkers a class happens to have measured. Confidence intervals by two level BCa bootstrap at 10,000 resamples, resampling biomarkers and perturbing each pooled estimate by its own standard error. Pairwise class differences are bootstrapped directly rather than inferred from overlapping intervals, and are restricted to biomarkers measured in both classes.

Three reporting rules fixed in advance: an estimate whose direction or significance reverses on removal of a single trial is reported as fragile and not advanced as a conclusion; the composite ranking is reported as a finding only where stable across all three weighting schemes; and any composite or contrast is reported with its biomarker coverage stated alongside it.

The complete analysis pipeline is public and was written before the extraction file existed.

## Analysis of subgroups or subsets

Nine pre-specified: drug level versus receptor class network; type 2 diabetes versus non-diabetes; MASH versus non-MASH; dose stratification within class; trial duration under 26 weeks, 26 to 52 weeks, over 52 weeks; industry versus non-industry funding; DXA only versus combined body composition methods; exclusion of trials at high risk of bias; and the four estimator sweep.

## Type and method of review

Systematic review with meta-analysis and network meta-analysis.

## Language

English

## Country

United States

## Other registration details

None.

## Reference and/or URL for published protocol

https://github.com/julian-borges-md/incretin-aging-biomarkers

## Dissemination plans

Peer reviewed publication, open access. Analysis code, extraction dataset and environment lockfile deposited on Zenodo with a DOI on acceptance.

## Keywords

Aging biomarkers; biological age; geroscience; GLP-1 receptor agonists; tirzepatide; retatrutide; survodutide; GDF-15; inflammaging; receptor class; network meta-analysis; metabolic age normalisation

## Details of final report / publication(s)

(leave blank)

---

## Three fields to check before submitting

**Stage of review.** The selections above are honest rather than convenient. One trial has been extracted, so "Data extraction: Started" is the accurate answer. Marking everything "Not started" would be the easier route and would be false.

**Team members.** Unresolved. See the constraint above. This is a decision only you can make.

**Repository URL.** The repository is public and the protocol is timestamped in its commit history, which is what makes the "fixed before extraction" claim checkable. Confirm you want it cited before it goes into a permanent public record.
