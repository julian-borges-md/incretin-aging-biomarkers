###############################################################################
# build_master.R
#
# Assemble extraction_master.csv from per trial extraction files.
#
# Extraction happens one trial at a time, into
# analysis/data/extraction_<author><year>_<drug>.csv. This script merges them,
# resolves every row to yi and vi through extraction_tools.R, validates the
# result, and writes the single file the analysis pipeline consumes.
#
# It refuses to write a master file containing rows it could not resolve. A
# silently dropped row is a trial that quietly left the synthesis, which is the
# kind of error that never announces itself and changes the answer.
#
# Run from the repository root: Rscript src/build_master.R
###############################################################################

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(purrr)
  library(tibble)
})

source("src/extraction_tools.R")

IN_DIR  <- "analysis/data"
OUT     <- file.path(IN_DIR, "extraction_master.csv")
REPORT  <- "analysis/output/extraction_report.csv"

dir.create("analysis/output", showWarnings = FALSE, recursive = TRUE)

fail <- function(...) { message("\nFAIL: ", ...); quit(status = 1) }

files <- list.files(IN_DIR, pattern = "^extraction_.*\\.csv$", full.names = TRUE)
# Exclude this script's own outputs and anything downstream of them. The
# pattern above matches extraction_master.csv, extraction_master_harmonised.csv
# and extraction_schema.csv, none of which are per-trial extraction files.
#
# This bit: harmonise_units.R writes extraction_master_harmonised.csv into this
# same directory, and an earlier version of this filter named only
# extraction_master.csv and extraction_schema.csv. build_master therefore
# ingested its own harmonised output as if it were a seventh trial, which
# duplicated every row and collided on the yi/se/se_route columns that the
# harmonised file already carries. It failed loudly rather than silently, which
# is the only reason it was caught.
files <- files[!grepl("extraction_master", basename(files))]
files <- files[!grepl("extraction_schema", basename(files))]

if (length(files) == 0) fail("no per trial extraction files found in ", IN_DIR)

message("Merging ", length(files), " extraction file(s).\n")

raw <- purrr::map_dfr(files, function(f) {
  # Reject ragged rows. A stray UNQUOTED comma inside a free text field makes a
  # row wider than the header; readr absorbs it silently, and it once crashed a
  # rewrite script and cost rows that had to be restored from git.
  #
  # The check must be quote aware. An earlier version split each line on commas
  # and compared counts, which flagged every correctly quoted field containing a
  # comma as ragged. readr's own parser handles quoting properly, so the check
  # is delegated to it and its problem report is read rather than reimplemented.
  d <- readr::read_csv(f, show_col_types = FALSE, progress = FALSE,
                       col_types = readr::cols(.default = readr::col_character()))
  probs <- readr::problems(d)
  if (nrow(probs) > 0) {
    detail <- paste(
      sprintf("    row %s, col %s: expected %s but got %s",
              probs$row, probs$col, probs$expected, probs$actual),
      collapse = "\n")
    stop(sprintf(
      paste0("MALFORMED ROWS in %s:\n%s\n",
             "  Usually an unquoted comma inside a free text field such as ",
             "`notes`.\n  Quote the field or remove the comma. Do not let this ",
             "reach the master."),
      basename(f), detail))
  }

  d$source_file <- basename(f)
  message(sprintf("  %-52s %3d rows", basename(f), nrow(d)))
  d
})

# Coerce the columns that must be numeric. Anything that fails to parse
# becomes NA and is caught by the validation below rather than silently
# flowing into an effect size.
numeric_cols <- c("yi_reported", "ci_lb_reported", "ci_ub_reported",
                  "se_reported", "p_reported",
                  "mean_tx", "sd_tx", "sem_tx", "n_tx",
                  "mean_ctrl", "sd_ctrl", "sem_ctrl", "n_ctrl",
                  "base_mean_tx", "base_sd_tx", "final_mean_tx", "final_sd_tx",
                  "base_mean_ctrl", "base_sd_ctrl", "final_mean_ctrl", "final_sd_ctrl",
                  "corr_assumed",
                  "events_tx", "events_ctrl",
                  "aging_direction", "clinical_weight",
                  "pct_weight_change", "duration_weeks", "year")
for (cl in intersect(numeric_cols, names(raw))) {
  before <- sum(!is.na(raw[[cl]]) & trimws(raw[[cl]]) != "NA")
  raw[[cl]] <- suppressWarnings(as.numeric(raw[[cl]]))
  after  <- sum(!is.na(raw[[cl]]))
  if (after < before) {
    message(sprintf("  NOTE  %s: %d value(s) did not parse as numeric",
                    cl, before - after))
  }
}

# Columns a per trial file may omit. Adding them as NA keeps resolve_effect
# able to test for them without every file having to carry every route's
# fields.
optional <- c("yi_reported", "ci_lb_reported", "ci_ub_reported", "se_reported",
              "p_reported", "p_is_bound", "measure",
              "mean_tx", "sd_tx", "sem_tx", "mean_ctrl", "sd_ctrl", "sem_ctrl",
              "base_mean_tx", "base_sd_tx", "final_mean_tx", "final_sd_tx",
              "base_mean_ctrl", "base_sd_ctrl", "final_mean_ctrl", "final_sd_ctrl",
              "corr_assumed", "comparator_type",
              "n_tx", "n_ctrl", "clinical_weight")
for (cl in setdiff(optional, names(raw))) raw[[cl]] <- NA

# p_is_bound arrives as text because every column is read as character.
# resolve_effect tests it with isTRUE(), and isTRUE("TRUE") is FALSE, so a
# bound flagged in a file would have been converted to a standard error from
# the threshold value, the exact error the flag exists to prevent. No row had
# used a p value route before 2026-10-15, so this never fired. Coerced here,
# with the counterexample asserted.
to_flag <- function(x) toupper(trimws(as.character(x))) %in% c("TRUE", "T", "1", "YES")
stopifnot(isTRUE(to_flag("TRUE")), !isTRUE(to_flag("FALSE")), !isTRUE(to_flag(NA)))
raw$p_is_bound <- to_flag(raw$p_is_bound)

## ---------------------------------------------------------------------------
## Resolve every row
## ---------------------------------------------------------------------------

resolved <- purrr::map_dfr(seq_len(nrow(raw)), function(i) {
  r <- as.list(raw[i, ])
  e <- resolve_effect(r)
  tibble(yi = e$yi, se = e$se, se_route = e$route)
})

dat <- bind_cols(raw, resolved) |>
  mutate(vi = se^2)

## ---------------------------------------------------------------------------
## Risk of bias: the RoB-2 file is the assessment of record
## ---------------------------------------------------------------------------
# rob_overall was typed into each extraction file at extraction time. The
# domain level RoB-2 assessment with its justifications lives in
# analysis/data/risk_of_bias.csv and was completed afterwards. Checked on
# 2026-10-15, the two disagreed on every trial: the four post hoc and open
# label analyses rated high overall in RoB-2 carried some_concerns in the
# extraction files, SELECT carried low against some_concerns, and Sanyal 2024
# carried both low and some_concerns within a single trial. A sensitivity
# analysis keyed on rob_overall would have selected rows RoB-2 does not rate
# low, and would have excluded nothing as high.
#
# The master therefore takes rob_overall from the RoB-2 file, keeps the typed
# value as rob_overall_extraction for provenance, and reports every override.
# This is a set from a canonical map, idempotent by construction. A trial
# without a RoB-2 row is an error: nothing enters the master unappraised.
ROB_FILE <- file.path(IN_DIR, "risk_of_bias.csv")
if (!file.exists(ROB_FILE)) fail("risk of bias file not found: ", ROB_FILE)
rob <- readr::read_csv(ROB_FILE, show_col_types = FALSE, progress = FALSE,
                       col_types = readr::cols(.default = readr::col_character())) |>
  select(trial_id, rob2_overall = overall)
ROB_LEVELS <- c("low", "some_concerns", "high")
if (any(duplicated(rob$trial_id))) fail("duplicated trial_id in ", ROB_FILE)
if (any(!rob$rob2_overall %in% ROB_LEVELS))
  fail("RoB-2 overall must be one of ", paste(ROB_LEVELS, collapse = ", "))
unappraised <- setdiff(unique(dat$trial_id), rob$trial_id)
if (length(unappraised) > 0)
  fail("trial(s) in the extraction with no RoB-2 row: ",
       paste(unappraised, collapse = ", "))
if (!"rob_overall" %in% names(dat)) dat$rob_overall <- NA_character_
dat <- dat |>
  left_join(rob, by = "trial_id") |>
  mutate(rob_overall_extraction = rob_overall,
         rob_overall = rob2_overall) |>
  select(-rob2_overall)

## ---------------------------------------------------------------------------
## Validate
## ---------------------------------------------------------------------------

message("\nValidation")

errs <- character(0)

rob_diff <- dat |>
  filter(is.na(rob_overall_extraction) | rob_overall_extraction != rob_overall) |>
  count(trial_id, rob_overall_extraction, rob_overall, name = "rows")
if (nrow(rob_diff) > 0) {
  message(sprintf("  NOTE  rob_overall set from RoB-2 on %d row(s) where the",
                  sum(rob_diff$rows)))
  message("        extraction file disagreed (typed value -> RoB-2 overall):")
  for (i in seq_len(nrow(rob_diff))) {
    message(sprintf("          %-24s %-14s -> %-14s %3d rows",
                    rob_diff$trial_id[i],
                    ifelse(is.na(rob_diff$rob_overall_extraction[i]), "NA",
                           rob_diff$rob_overall_extraction[i]),
                    rob_diff$rob_overall[i], rob_diff$rows[i]))
  }
}

unresolved <- filter(dat, se_route == "unresolvable")
if (nrow(unresolved) > 0) {
  errs <- c(errs, sprintf(
    "%d row(s) could not be resolved to an effect size. First: %s / %s",
    nrow(unresolved), unresolved$trial_id[1], unresolved$biomarker[1]))
}

bounds <- filter(dat, se_route == "p_bound_unusable")
if (nrow(bounds) > 0) {
  # Not fatal, but these rows cannot enter a pooled analysis and the extractor
  # must know which trials need a different reported quantity chasing down.
  message(sprintf("  NOTE  %d row(s) report a p value bound with no interval.",
                  nrow(bounds)))
  message("        These carry no recoverable variance and are excluded from")
  message("        pooling. Seek the confidence interval or arm level data.")
  for (i in seq_len(min(5, nrow(bounds)))) {
    message(sprintf("          %s / %s", bounds$trial_id[i], bounds$biomarker[i]))
  }
}

bad_se <- filter(dat, !is.na(se), se <= 0)
if (nrow(bad_se) > 0) {
  errs <- c(errs, sprintf("%d row(s) have a non-positive standard error",
                          nrow(bad_se)))
}

if (!"aging_direction" %in% names(dat) || any(!dat$aging_direction %in% c(1, -1))) {
  errs <- c(errs, "aging_direction must be exactly +1 or -1 on every row")
}

RECEPTOR_CLASSES <- c("GLP1_mono", "GLP1_GIP", "GLP1_GCGR", "GLP1_GIP_GCGR")
bad_class <- setdiff(unique(dat$receptor_class), RECEPTOR_CLASSES)
if (length(bad_class) > 0) {
  errs <- c(errs, paste("unknown receptor_class:", paste(bad_class, collapse = ", ")))
}

# comparator_type is a controlled vocabulary and amendment A13 made the
# placebo controlled restriction of the class contrast read it instead of the
# free text comparator. A cell spelled ACTIVE rather than active therefore
# decides an analysis by its capitalisation: two rows of EUREXA carried that
# spelling and were silently outside the vocabulary until this check was
# written. Case is part of the vocabulary, so the check is exact, not folded.
COMPARATOR_TYPES <- c("placebo", "active", "lifestyle", "NA")
comparator_type_outside <- function(x) {
  v <- ifelse(is.na(x), "NA", as.character(x))
  sort(unique(v[!v %in% COMPARATOR_TYPES & nzchar(v)]))
}
stopifnot(
  length(comparator_type_outside(c("placebo", "active", "lifestyle", NA, "", "NA"))) == 0,
  identical(comparator_type_outside(c("active", "ACTIVE", "Placebo", "placebo ")),
            c("ACTIVE", "Placebo", "placebo "))
)
bad_comparator_type <- comparator_type_outside(dat$comparator_type)
if (length(bad_comparator_type) > 0) {
  errs <- c(errs, paste("comparator_type outside the controlled vocabulary (case is part of it):",
                        paste(sprintf("%s", bad_comparator_type), collapse = ", ")))
}

if (any(is.na(dat$pct_weight_change))) {
  # NOT a fatal error. pct_weight_change is the meta-regression covariate, and
  # rows lacking it are simply excluded from that model. They remain perfectly
  # usable for the primary pooled estimates, which do not involve weight.
  #
  # Requiring it on every row, as an earlier version of this script did, would
  # have discarded the SELECT hsCRP analysis (n=17,604) and the entire Wilson
  # tirzepatide biomarker panel, because biomarker substudies routinely report
  # the biomarker without restating the parent trial's weight change, and the
  # parent paper does not always give it per arm in percentage terms.
  #
  # The honest handling is to carry the rows, exclude them from the one model
  # that needs the covariate, and report how much of the evidence that model
  # is therefore blind to.
  n_miss <- sum(is.na(dat$pct_weight_change))
  message(sprintf("  NOTE  %d of %d row(s) lack pct_weight_change.",
                  n_miss, nrow(dat)))
  message("        These pool normally but are excluded from the weight")
  message("        adjusted meta-regression. Affected trials:")
  miss_by_trial <- dat |>
    dplyr::filter(is.na(pct_weight_change)) |>
    dplyr::count(trial_id, name = "rows")
  for (i in seq_len(nrow(miss_by_trial))) {
    message(sprintf("          %-24s %3d rows",
                    miss_by_trial$trial_id[i], miss_by_trial$rows[i]))
  }
}

# A biomarker whose direction is coded inconsistently across trials would
# silently flip that trial's contribution to the composite. Caught here.
dir_check <- dat |>
  group_by(biomarker) |>
  summarise(n_dir = n_distinct(aging_direction), .groups = "drop") |>
  filter(n_dir > 1)
if (nrow(dir_check) > 0) {
  errs <- c(errs, paste("aging_direction differs between rows for:",
                        paste(dir_check$biomarker, collapse = ", ")))
}

# Duplicate rows for the same trial, arm, biomarker and timepoint would
# double count that arm in the pool.
dup <- dat |>
  count(trial_id, dose_mg, biomarker, duration_weeks) |>
  filter(n > 1)
if (nrow(dup) > 0) {
  errs <- c(errs, sprintf("%d duplicated trial/dose/biomarker/timepoint combination(s)",
                          nrow(dup)))
}

if (length(errs) > 0) {
  for (e in errs) message("  ERROR  ", e)
  fail("extraction did not validate; master file not written.")
}

message("  ok   every row resolved to an effect size")
message("  ok   aging_direction consistent within each biomarker")
message("  ok   no duplicated trial, dose, biomarker and timepoint rows")
message("  ok   receptor classes recognised")
message(sprintf("  ok   rob_overall taken from RoB-2 for every row (%s)",
                paste(sprintf("%s %d", names(table(dat$rob_overall)),
                              as.integer(table(dat$rob_overall))), collapse = ", ")))

## ---------------------------------------------------------------------------
## Write
## ---------------------------------------------------------------------------

poolable <- filter(dat, !is.na(vi))
readr::write_csv(poolable, OUT)

report <- dat |>
  count(source_file, trial_id, se_route, name = "rows") |>
  arrange(source_file, se_route)
readr::write_csv(report, REPORT)

message("\nSummary")
message(sprintf("  %d rows merged, %d poolable, %d excluded for lack of variance",
                nrow(dat), nrow(poolable), nrow(dat) - nrow(poolable)))
message(sprintf("  %d trials, %d biomarkers, %d receptor classes",
                n_distinct(dat$trial_id), n_distinct(dat$biomarker),
                n_distinct(dat$receptor_class)))

message("\n  Variance provenance")
for (r in sort(unique(dat$se_route))) {
  message(sprintf("    %-22s %3d rows", r, sum(dat$se_route == r)))
}

message("\n  Coverage by receptor class")
cov <- dat |> count(receptor_class, name = "rows") |> arrange(desc(rows))
for (i in seq_len(nrow(cov))) {
  message(sprintf("    %-16s %3d rows, %2d biomarkers",
                  cov$receptor_class[i], cov$rows[i],
                  n_distinct(dat$biomarker[dat$receptor_class == cov$receptor_class[i]])))
}

message("\nWrote ", OUT)
message("Provenance report: ", REPORT)
