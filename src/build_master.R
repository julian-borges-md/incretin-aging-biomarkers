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
files <- files[!grepl("extraction_master\\.csv$", files)]
files <- files[!grepl("extraction_schema\\.csv$", files)]

if (length(files) == 0) fail("no per trial extraction files found in ", IN_DIR)

message("Merging ", length(files), " extraction file(s).\n")

raw <- purrr::map_dfr(files, function(f) {
  # Reject ragged rows before anything else. A stray comma inside a free text
  # field produces a row with more columns than the header, which readr will
  # silently absorb into a spill column or drop. It is also what crashed an
  # extraction rewrite and cost rows that had to be restored from git, so it
  # fails loudly here rather than propagating.
  hdr_n  <- length(readr::read_lines(f, n_max = 1) |>
                     strsplit(",") |> unlist())
  all_ln <- readr::read_lines(f)
  body   <- all_ln[-1]
  body   <- body[nzchar(trimws(body))]
  widths <- vapply(strsplit(body, ","), length, integer(1))
  bad    <- which(widths != hdr_n)
  if (length(bad)) {
    stop(sprintf(
      paste0("RAGGED ROWS in %s: header has %d columns but line(s) %s have %s.\n",
             "  Almost always an unquoted comma inside a free text field such ",
             "as `notes`.\n  Fix the source file; do not let this reach the ",
             "master."),
      basename(f), hdr_n,
      paste(bad + 1, collapse = ", "),
      paste(widths[bad], collapse = ", ")))
  }

  # Read every column as character, then coerce the numeric ones by name.
  # Per-file type inference is the problem: `phase` is 2 in one trial and
  # "2a"/"2b" in another, `dose_mg` can be 1.8 or "1.8 BIW", and bind_rows
  # refuses to combine a double column with a character one. Inferring types
  # independently per file guarantees these collisions as the corpus grows.
  d <- readr::read_csv(f, show_col_types = FALSE, progress = FALSE,
                       col_types = readr::cols(.default = readr::col_character()))
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
              "n_tx", "n_ctrl", "clinical_weight")
for (cl in setdiff(optional, names(raw))) raw[[cl]] <- NA

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
## Validate
## ---------------------------------------------------------------------------

message("\nValidation")

errs <- character(0)

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
