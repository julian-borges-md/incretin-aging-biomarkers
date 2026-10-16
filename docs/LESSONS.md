# Lessons from this review

Written 2026-10-15, after four extractions. Recorded because three of the four contradicted something we had already written, and because several of the failures share a root worth naming.

This is not a list of mistakes. It is a list of the ones that were **invisible at the time**, which are the only ones worth encoding.

---

## The root pattern: a uniform error looks like no error

Three separate failures here had the same shape. Something was wrong everywhere at once, so nothing looked inconsistent, and every check we had agreed with the thing it was supposed to check.

**The composite sign convention.** The direction indicator was defined so that a favourable change in a lower-is-better biomarker produced a negative contribution. Every biomarker in the corpus was lower-is-better, so the whole composite inverted together. Nothing looked odd. It surfaced only when adiponectin, the first higher-is-better marker, was extracted and sat visibly wrong next to the others.

**The validation test that agreed with the bug.** `validate_pipeline` Test 4 existed precisely to check direction handling. It passed. It passed because its cases were all constructed with positive effects and `+1` directions, encoding the same assumption as the code. A test whose cases all share one sign cannot detect a sign error.

**The GDF-15 differential.** Two papers each reported their own within-arm result accurately. Joining them into a between-class claim was the error, and neither source showed any sign of it, because neither source was wrong.

The existing lab standard says *a check that cannot fail is not a check*. This extends it:

> **A check that encodes the same assumption as the thing it checks cannot fail in the way that matters.** Every convention needs a test case that would break if the convention were inverted, not merely a case that confirms it when correct.

Concretely: any signed quantity needs a counterexample in both senses. Any contrast needs a case where the naive version gives the wrong answer.

---

## Evidence synthesis

**Within-arm changes from different trials are not a contrast.** Comparing "drug A fell versus its own baseline in trial 1" against "drug B did not fall versus its own baseline in trial 2" has no common control and licenses nothing. This produced the GDF-15 receptor-class claim, which collapsed when the trial containing both arms showed the between-group difference was not significant, and that a GLP-1 mono-agonist had outperformed the dual agonist. All pooled estimates must be contrasts against concurrent controls within trial.

**Read the column next to the one you are interested in.** The retatrutide saturation argument held that the hepatic effect plateaued while weight kept falling. The liver fat numbers were right. The weight numbers, one column over, showed weight plateaued too. The claim survived several drafts because nobody read across.

**Check PMC before declaring a paywall.** Early in the extraction I told the Lab Director that full-text retrieval was the hard blocker. A single ID conversion call then showed that six of the highest-value papers were open access, including the SELECT substudy and the only GCGR-class biomarker analysis. The blocker was real for the NEJM MASH trials and false for everything else, and I had generalised from the first failure.

**A reported p value bound carries no variance.** `P < 0.001` is a bound, not a value. Treating it as `p = 0.001` understates the variance and overstates precision. Such rows are flagged and excluded from pooling rather than assigned the threshold.

---

## Registration

**Register before touching any trial data.** PROSPERO refuses an initial registration once data extraction has begun and enforces it in the form. One trial was extracted beforehand to pilot the extraction schema; that pilot found a genuine schema defect and refuted a draft argument, and it still cost the registration. Schema testing is done against simulated data matching the schema, never a real trial. Full statement in `prespecification/registration_gate.md`.

---

## Engineering

**Any script that rewrites files in place must write atomically.** A rewrite script crashed partway through and truncated extraction files, twice, costing rows that had to be restored from git. Write to a temporary file and `os.replace`. A crash then leaves the original intact.

**Any transformation applied to data must be idempotent, or it must be a set rather than a flip.** The first correction attempt flipped signs. The script crashed after processing some files, and the rerun flipped those a second time back to wrong. Setting values from a canonical map is safe to run any number of times; flipping is not.

**Do not let per-file type inference decide column types across a merge.** `phase` was `2` in one trial and `"2a"` in another, and the merge refused to combine a double with a character column. As a corpus grows this collision is guaranteed. Read everything as character and coerce named numeric columns explicitly, reporting anything that fails to parse.

**An unquoted comma in a free text field makes a row ragged.** It was silently absorbed by the CSV reader and crashed a downstream script. Ragged rows are now rejected by file and line number before parsing.

**A unit is a property of the row, never of the biomarker.** The harmoniser assigned percent change to every hsCRP row because the first two hsCRP sources reported percent change. The third reported an absolute change in mg/L, and its own notes said so. The row passed through as −1.5 per cent with a standard error of 0.34, took 89 per cent of the fixed effect weight for hsCRP, and moved Table 2, the composite and its core sensitivity analysis, with all eight gates passing. Added 2026-10-15. The classification now reads each row's measure, and the EUREXA row shape is one of six counterexamples run on every execution. The general form: any rule written as "marker X is reported as Y" is the uniform error pattern waiting for its third source.

**A documented amendment with no code behind it restricts nothing.** The placebo only rule for class contrasts was written into `docs/COMPARATOR_PROBLEM.md` and the contrast script went on counting the active controlled trial toward mono class coverage. Added 2026-10-15. The rule now lives in `receptor_class_contrast.R` with an excluded rows report.

**A column typed at extraction time drifts from the assessment of record.** `rob_overall` was typed into the extraction files before the RoB-2 assessment was done; afterwards the two disagreed on 44 of 48 rows and the master carried no `high` rating while RoB-2 rated four of seven trial analyses high. Any sensitivity analysis keyed on the column would have excluded nothing. Added 2026-10-15. The master now sets the column from `risk_of_bias.csv` at build time and refuses a trial that has no RoB-2 row.

---

## Verification

**"Repository not found" is an identity result before it is an existence result.** A private repository answers "not found" to any identity without access. On a workstation holding two GitHub identities, the keychain helper serves whichever account the CLI last made active, so `git ls-remote` from an interactive session can fail against a repository that an unattended job pushes to successfully every few hours. Two repositories were recorded as non-existent on this basis on 2026-10-15; both exist. Added 2026-10-15. The test that settles existence runs with the helper chain reset to the credential that the job itself uses, and a successful push in the job's own log outranks a failed lookup from elsewhere.

**Run the gates, then read the gate output before writing the summary.** The session close record stated that every claim had been checked by running the command, and its results table still carried figures from the corpus of an hour earlier, because the gates were run and the summary was written from memory. Added 2026-10-15. The numbers in a summary are copied from the log of the run that produced them, never typed.

---

## Analysis design

**Require only what the analysis needs, where it needs it.** `pct_weight_change` was made mandatory on every extraction row. It is the meta-regression covariate and is irrelevant to the primary pooled estimates. The rule would have discarded the SELECT hsCRP analysis of 17,604 participants and the entire tirzepatide biomarker panel, because biomarker substudies report the biomarker without restating the parent trial's weight change. Rows now pool normally, drop out of the one model that needs the covariate, and the script reports which trials that model is blind to.

**Never hardcode an interpretation a script can compute.** An analysis script printed the conclusion that a ratio was highest at the top dose. It was highest at the lowest dose, for a reason that had nothing to do with potency. The script now computes the direction and branches on it.

---

## What worked, and why it is worth keeping

**Extracting rather than citing.** Four extractions found three errors in our own prior work. Reading abstracts and trusting them would have found none, and all three would have reached a reviewer.

**Publishing the protocol and pipeline before the data.** The analysis plan is timestamped in a public commit history, so no estimator, moderator or weighting choice can have been made after seeing estimates. This does not replace registry registration and is not claimed to.

**Gates that have been shown to fail.** `selftest.R` perturbs each gate and asserts the gate catches it. A gate that has never been observed failing is a gate nobody has tested.

**Stating the direction of bias for each choice.** The weight-adjusted estimate is reported as a conservative lower bound because the covariate plausibly sits on the causal path. Saying so costs nothing and is the first thing a reviewer would otherwise say.
