# Runbook

Full path from an empty checkout to a completed analysis.

## 1. Environment

```
git clone https://github.com/julian-borges-md/incretin-aging-biomarkers.git
cd incretin-aging-biomarkers
make install
```

`make install` installs the reference package set. For an exact reproduction use `renv::restore()` against the committed lockfile instead, which pins versions rather than installing current ones.

R 4.4.1 is the version used in CI. The pipeline needs metafor, netmeta, meta, dmetar, tidyverse, boot, ggplot2, patchwork, knitr, openssl and sessioninfo. `verify.R` needs only dplyr, which is why the CI gate job installs nothing else.

## 2. Gates, before any data

```
make verify
make selftest
```

Both run without data and without network access. `verify` checks that the code still implements the protocol; `selftest` proves `verify` can fail. If either fails on a clean checkout, the repository is internally inconsistent and nothing downstream should be trusted.

The full chain, `make gates`, reads retrieved sources under `work/`, which the gitignore keeps out of version control because they are licensed text. Two of its twenty five gates therefore need a retrieval step first on a clean clone:

```
python3 -I src/corpus_registry_harvest.py
```

retrieves the ClinicalTrials.gov record of every included trial that carries a registry identifier, 53 of 76, into `work/fulltext/registry_corpus/`. Gate twenty five, the timepoint check, reads them; without them its self test fails rather than passing, because a check with nothing to compare would otherwise report a green light for work it did not do. The packet texts gates eleven to twenty four read are rebuilt by the extraction retrieval scripts, which `docs/EXTRACTION_BRIEF.md` documents.

Nine of those 53 identifiers were not in the repository and were resolved from the publishers' own statements of the registration by `python3 -I src/registry_id_resolve.py`, which wrote `analysis/data/trial_registry_ids.csv`. That file is tracked, so a clone does not need to repeat the resolution; re-run it only when trials enter or leave the corpus. `docs/TIMEPOINT_TRIAGE.md` records what the resolution establishes, what it refuses to guess at, and the two pairs of trials an earlier version of it gave one registration each.

## 3. Extraction

This is the step that is not yet done, and it is the only remaining blocker on the Results.

Create `analysis/data/extraction_master.csv` conforming to `analysis/data/extraction_schema.csv`. The schema declares 50 columns; the subset the pipeline reads by name is enforced by gate 1.

Structure: **one row per trial, per arm comparison, per biomarker.** A trial reporting six biomarkers across two dose arms contributes twelve rows. Each row carries the trial metadata and baseline characteristics redundantly, which is deliberate: it keeps every row self-describing and makes subgroup filters a single operation.

Points where extraction most often goes wrong:

| Field | Requirement |
|---|---|
| `aging_direction` | Exactly `+1` or `-1`, never `0` or blank. `+1` means a **decrease** in this biomarker corresponds to younger biological age. Lean mass is `-1`, because a decrease is unfavorable. Resting heart rate is `+1`, because a decrease is favorable |
| `sd_tx`, `sd_ctrl` | Standard deviation of **change from baseline**, not of the baseline value and not a standard error. Where a trial reports SE, convert and record the conversion in a note. Where a trial reports a confidence interval, back-calculate. A zero or negative SD is rejected by the integrity gate |
| `pct_weight_change` | Mean percentage body weight change for that arm. This is the meta-regression covariate and cannot be missing for any row |
| `receptor_class` | One of `GLP1_mono`, `GLP1_GIP`, `GLP1_GCGR`, `GLP1_GIP_GCGR`. Assigned from the molecule, not from the trial's framing |
| `prespecified_endpoint` | `TRUE` only where the biomarker was a pre-specified endpoint. Most aging biomarkers in this literature appear in post hoc analyses, and this field is what makes that visible in the reporting bias discussion |
| `outcome_type` | `continuous` or `binary`. Binary rows need `events_tx` and `events_ctrl` and may leave the mean and SD fields empty |

Run `make verify` after extraction. Gate 1 will catch a schema drift; the integrity function inside the pipeline catches malformed values at run time.

## 4. Analysis

```
make analysis
```

Writes to `analysis/output/`:

| File | Content |
|---|---|
| `table3_primary_results.csv` | Pooled estimate per biomarker per receptor class, with CI, prediction interval, tau-squared, I-squared, Q |
| `table4_metaregression.csv` | Weight adjusted meta-regression, four nested models per biomarker, permutation p values |
| `table4a_hepatic_metaregression.csv` | The hepatic subset, which is the pre-specified primary target |
| `table5_nbais.csv` | Composite score per receptor class under three weighting schemes, with BCa intervals |
| `table5a_nbais_contrasts.csv` | Pairwise class differences, bootstrapped directly, restricted to shared biomarkers |
| `table_nma_coherence.csv` | Network inconsistency diagnostics |
| `table_diagnostics.csv` | Leave one out range, influential trials, Egger where assessable, trim and fill |
| `sensitivity_*.csv` | Nine pre-specified sensitivity analyses |
| `figure*_*.pdf`, `figure*_*.png` | The figure set; the PRISMA diagram is written by `src/prisma_diagram.py` instead, and `docs/FIGURES.md` maps every file stem to its submission number |
| `figure*_*.csv` | The plotted values of each figure, which the figure gate recomputes from the tables and data the figure is drawn from |
| `figure_index.csv` | Each figure's files, plotted values, caption and size, as the run saved them |
| `session_info.txt` | R version, platform, every loaded package version |
| `MANIFEST.csv` | Every output file with its SHA-256 hash |

Runtime is dominated by the bootstraps and permutation tests. Expect tens of minutes rather than seconds; this is the cost of permutation inference at 10,000 iterations across every biomarker, and it is not reducible without weakening the inference.

## 5. Writing up

Populate the Results sections from the output tables. Nothing enters the manuscript that is not in `analysis/output/`.

Two reporting rules, both pre-specified:

**A pooled estimate whose direction or significance reverses when a single trial is removed is reported as fragile** and is not advanced as a conclusion, whatever its nominal p value. `table_diagnostics.csv` carries the leave one out range for every estimate.

**The composite ranking is reported as a finding only where it is stable across all three weighting schemes.** Where the ranking changes with the weighting, that instability is itself the result, because a ranking that depends on an analyst's weighting choice is not a property of the drugs.

## 6. Release

Tag, archive to Zenodo, add the DOI to `CITATION.cff`, and record what the deposit contains.
