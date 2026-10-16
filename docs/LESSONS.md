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

**"Strings are drafted" is a claim about a file; find the file.** PRISMA_FLOW.md said the CENTRAL and Web of Science strings were drafted. Nothing in the repository or the vault contained one; the Embase lines existed only in the log written when they were run. The CENTRAL strategy therefore had to be written on the day as a translation, and is recorded as that, with every difference from the Embase string listed. A search described as prespecified that has to be written at run time is a methods statement waiting to be caught by a reviewer.

**A browser download is complete when the record count says so, not when the browser says so.** Chrome on the workstation wrote both exports to its temporary download name and never finalised them. The content was complete (TY, ER and identifier counts equal to the search count; identical SHA-256 across two attempts). Taking the file from the temporary copy and gating it on counts is sound; waiting for a rename that never comes is not.

**A tool's blocklist matches tokens, not intent.** Desktop Commander refused two commands with "Command not allowed" and no reason. The common element was a three letter variable name, `reg`, which sits on its blocked command list (a Windows registry tool). Name variables for what they are (`is_registry`) and treat an unexplained refusal as a string match before treating it as a policy.

**Guest and authenticated views of the same database differ in what they let you do, not only in what they show.** The Cochrane Library returned the same 460 count as a guest and through the institutional proxy; only the proxied session offered selection and export. The proxied page also needs its scripts loaded before any key is sent, or Enter inserts a newline instead of running the line. Reproduce the counts in the authenticated session before exporting, so the export is provably the logged search.

---

## Retrieval

**Ask an index for an open access location before calling a record closed.** The Europe PMC open access flag covers PMC only. Of 27 records left as partial pages or nothing after the publisher route, OpenAlex returned an open access location for 10 in one pass (no key, no email); the J-STAGE and Spandidos PDFs rendered to complete texts within minutes, and the record that had cost the most browser time (Endocrine Journal 2017) was open the whole time. Order of routes for the next review: Europe PMC open access, then OpenAlex and PMC author manuscripts, then the institutional proxy, then repositories by title; the proxy is the expensive route and goes last. Added 2026-10-16.

**Section headings prove nothing about completeness.** A structured abstract carries Methods and Results, and an abstract page carries a reference list, so three abstract pages (Springer, AHA, yiigle) passed a rule of three section marks and more than 12,000 characters. Heading rules were then tested across all 115 captures and did not generalise: Springer repeats the Abstract heading at the foot of the page, ScienceDirect lists References in its outline, Wiley brief reports have no Discussion heading. The rule stays simple, the borderline captures are read, and each exception is named in the script with its reason. Fitting a rule to the case in front of you is how the next false positive is made. Added 2026-10-16.

**The browser allows what a hand does and blocks what a script does.** Chrome refuses script triggered downloads after the first per origin, and blocked a local HTTP sink under its local network access permission. A real click on an injected anchor holding a Blob URL downloads every time, with "Ask where to save" off. The visible page text captured through that click, with a KEY header for the harvest script, is the route that survived; the captures are licensed content and stay out of git with their manifest. Added 2026-10-16.

**A proxied hostname proves authentication; it does not prove access.** Through the proxy a DOI lands on the publisher's abstract page whenever the library has no subscription (Hormones, Circulation: Cardiovascular Imaging), and that page reads as a full text to a length rule. Confirm the hostname, then confirm the text, and record "no subscription" as an outcome of its own rather than as a retrieval failure; it is the input to an interlibrary request. Added 2026-10-16.

**Each publisher has one working door, and it is rarely the DOI.** NEJM needs the hyphenated proxy host and `/doi/full/`; ClinicalKey journals are reached through the ScienceDirect PII page; Thieme through its ejournals html path; Springer through `/article/<doi>` on the proxied host; Ovid gives the abstract only; CNKI is not configured in the proxy at all. Each door is recorded when found (`FULLTEXT_ACCESS_SUMMARY.md`), so the next review starts from the table and not from the DOI. Added 2026-10-16.

**No DOI does not mean no copy.** Dokkyo Journal of Medical Sciences 2014 had no DOI and no PubMed record; a plain title search found the university repository PDF. Japanese and Chinese journals keep their own repositories and index pages. Try the title before recording a report as not retrieved. Added 2026-10-16.

**A partial bucket holds two different things, and the reader must be told which.** Abstract pages and complete short documents (letters, comments, reviews without methods sections) both fail a methods and results rule. Rather than pretend the rule can separate them, the full text screen labels such captures as "may be the complete document or only the abstract; judge from what is present", and the reviewers' reasons say which it was. Added 2026-10-16.

**An example list in a prompt becomes an answer.** The full text addendum asked the reviewers for the biomarkers with numerical results and gave nine names as examples of the form. On the first 300 records both reviewers named hsCRP in 22 texts that never mention C reactive protein, and twice returned the nine examples verbatim for a document that reports none of them. The field is auxiliary (inclusion is judged separately), but a biomarker map built from it would have been fiction. Added 2026-10-16. The lexicon scan (`src/biomarker_scan.py`) now runs over the exact text each reviewer received and only a name that the text also mentions counts; the next version of the addendum describes the form without naming any marker. The prompt is unchanged for the running screen so that records screened before and after it stay comparable.

**Trim the capture, never the article.** Publisher pages carry navigation, reading assistants, image download lines and reference lists; 40 of 91 captures exceeded the context cap before trimming and 15 after. The trimming is three patterns applied identically to every capture (navigation before the abstract heading, the reference list after 40 percent of the page, a short list of boilerplate lines) and the characters kept are logged per record. No capture is edited by hand. Added 2026-10-16.

---

## Unattended execution

**A job that is alive is not a job that is progressing, and a session is not a supervisor.** The full text chain stopped at 08:33 on 16 October on a transient Ollama 500 during a model swap (three attempts inside 15 seconds) and was relaunched six minutes later only because the session happened to be active; the steps behind it in that chain would otherwise have stayed undone until the next check in. A hung request is worse: it looks healthy in the process table for the whole 600 s HTTP timeout, six times over. Added 2026-10-16. The control is built into the pipeline rather than added as a separate supervising process (the Director's choice: fewer moving parts, and restarts stay a human act): the chain's step wrapper retries a failed step three times before the chain stops, and `python3 -I src/fulltext_screen.py check` reads the state of every chain from its log and the process table with progress measured on the artefacts (a decision row per record), never on process liveness, and exits 1 when a chain is stale, stopped or dead. A stopped chain is relaunched by hand and resumes where it stopped; a chain whose remaining work moved elsewhere carries a "retired" line with the reason, so the check never flags it. A first version as a daemon with its own kill and relaunch ladder was written, tested and withdrawn the same morning.

**Two pollers that look for each other never finish.** Chains 4 and 3d each waited with `while pgrep -f "<the names of the chains ahead>"; do sleep 60; done`, launched in the same second. Chain 3c completed at 11:51 and chain 4 was still waiting at 12:00: its `pgrep` ran in the same instant as chain 3d's, and each `pgrep` matched the other's own argument list, which spells out the names it waits for. Nothing in the process table showed it, because the match lives for milliseconds, and `check` reported both chains as waiting, which was true. Found by sampling at 1 Hz and seeing no match, which left only a match that exists for less than a second. Added 2026-10-16. A `pgrep -f` pattern must not match its own text (`[s]creen_chain4.sh`), and a chain that waits for another should wait on an artefact (the "complete" line in the log) rather than on a process name. A script under execution is not edited in place: zsh reads it as it goes, so the change shifts what it reads next; the waiting shells were killed and relaunched on the corrected scripts (eight minutes lost, nothing undone).

**A rerun of a harvester is a write, not a lookup.** When pool 3 joined the full text pool, `make fulltext-access` and `src/direct_fetch.py` were rerun to fetch texts for the 29 new records. Both rewrite their manifests from scratch: the Europe PMC harvester wrote the size of every kept file as 0 (the screen admits a text only above 2,000 characters), which demoted 108 full texts to the proxy or to "awaiting" without an error; the direct fetcher reclassified three pages and overwrote the hand added row of a record found by title (Fan 2013 on SciELO), so its group lost the text it had been screened and extracted from. Caught by the inventory count (`fulltext_screen.py inventory`: 13 Europe PMC texts where there had been 108) and by comparing each screened record's source with the source it was screened from. Added 2026-10-16. Both scripts now keep the rows of files already on disk and read sizes from the files; the check that every screened record still resolves to the source it was screened from is the test to run after any retrieval step. Companion papers are looked up in the pool before they are fetched: three of the nine fetched today (Kelly 2012, Dutour 2016, Derosa 2011) were already in the pool as their own full text records, waiting for the screen.

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
