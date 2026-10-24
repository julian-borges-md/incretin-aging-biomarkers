###############################################################################
# verify.R
#
# Gate checks that run without data and without network access.
#
# At this stage of the project there are no pooled estimates to re-derive, so
# this script does not verify numbers. It verifies the contract: that the
# extraction schema is well formed, that the analysis pipeline declares the
# estimators and seed the protocol commits to, and that the integrity function
# the pipeline depends on rejects malformed input.
#
# A green badge here means the repository is internally consistent with its own
# protocol. It does not mean results exist. See docs/MANIFEST.md.
###############################################################################

fail <- function(...) { message("FAIL: ", ...); quit(status = 1) }
pass <- function(...) message("  ok   ", ...)

message("Gate 1: extraction schema")

schema_path <- "analysis/data/extraction_schema.csv"
if (!file.exists(schema_path)) fail("extraction schema missing")
schema <- utils::read.csv(schema_path, stringsAsFactors = FALSE)

expected_cols <- c("column", "type", "required", "description")
if (!identical(names(schema), expected_cols)) {
  fail("schema header is ", paste(names(schema), collapse = ","))
}
pass("schema header")

if (anyDuplicated(schema$column)) {
  fail("duplicate column names: ",
       paste(schema$column[duplicated(schema$column)], collapse = ", "))
}
pass("no duplicate columns (", nrow(schema), " declared)")

# Columns the pipeline reads by name. If the schema and the pipeline drift
# apart, the pipeline fails at runtime on real data; this catches it earlier.
required_by_pipeline <- c(
  "trial_id", "receptor_class", "biomarker", "hallmark_domain",
  "aging_direction", "clinical_weight", "outcome_type",
  "mean_tx", "sd_tx", "n_tx", "mean_ctrl", "sd_ctrl", "n_ctrl",
  "events_tx", "events_ctrl", "pct_weight_change",
  "population", "duration_weeks", "rob_overall", "industry_funded", "drug"
)
missing <- setdiff(required_by_pipeline, schema$column)
if (length(missing)) fail("schema is missing: ", paste(missing, collapse = ", "))
pass("every column the pipeline reads is declared")

message("Gate 2: analysis pipeline declarations")

pipe_path <- "analysis/M5_AGE_analysis_pipeline.R"
if (!file.exists(pipe_path)) fail("pipeline missing")
pipe <- paste(readLines(pipe_path, warn = FALSE), collapse = "\n")

# The protocol commits to a fixed seed. A changed or absent seed breaks the
# reproducibility claim in the README, so it is asserted literally.
if (!grepl("set.seed(20261013)", pipe, fixed = TRUE)) {
  fail("pipeline does not set the pre-specified seed 20261013")
}
pass("pre-specified seed present")

# The protocol commits to four between-study variance estimators.
for (est in c("REML", "DL", "PM", "SJ")) {
  if (!grepl(sprintf('"%s"', est), pipe, fixed = TRUE)) {
    fail("estimator not referenced in pipeline: ", est)
  }
}
pass("all four pre-specified estimators referenced")

# The protocol commits to prediction intervals on every pooled estimate.
if (!grepl("pi_lb", pipe, fixed = TRUE) || !grepl("pi_ub", pipe, fixed = TRUE)) {
  fail("pipeline does not emit prediction interval bounds")
}
pass("prediction intervals emitted")

# The protocol commits to permutation inference at 10,000 iterations.
if (!grepl("permutest", pipe, fixed = TRUE)) {
  fail("pipeline does not use permutation inference")
}
if (!grepl("n_perm = 10000", pipe, fixed = TRUE)) {
  fail("permutation iterations are not the pre-specified 10,000")
}
pass("permutation inference at 10,000 iterations")

# The composite must be a weighted MEAN. A weighted sum would inflate with
# biomarker coverage, which is the specific error the protocol rules out.
if (!grepl("sum(w)", pipe, fixed = TRUE)) {
  fail("composite is not normalised by the sum of weights (weighted sum, not mean)")
}
pass("composite normalised by total weight")

if (!grepl('type = "bca"', pipe, fixed = TRUE)) {
  fail("bootstrap does not request BCa intervals")
}
pass("BCa bootstrap requested")

message("Gate 3: integrity function rejects malformed input")

# Extract and evaluate check_integrity from the pipeline in isolation, then
# confirm it rejects each failure mode the protocol names. This is the gate
# that matters: it proves the pipeline cannot silently pool bad data.
suppressWarnings(suppressMessages({
  ok <- require(dplyr, quietly = TRUE)
}))
if (!ok) {
  message("  skip  dplyr unavailable; integrity function not exercised")
} else {
  src <- readLines(pipe_path, warn = FALSE)

  # The function closes over RECEPTOR_CLASSES, which the pipeline defines at
  # top level. Extract that definition from the pipeline too, rather than
  # restating it here, so the two cannot drift apart.
  rc_line <- grep("^RECEPTOR_CLASSES <- ", src)
  if (length(rc_line) != 1) fail("RECEPTOR_CLASSES not found in pipeline")
  eval(parse(text = src[rc_line]))

  # The integrity function also closes over CONTINUOUS_TYPES, added when the pipeline was ported
  # onto the harmonised master. Extracted from the pipeline for the same reason as the line above:
  # restating it here would let the gate and the pipeline drift apart silently.
  ct_line <- grep("^CONTINUOUS_TYPES <- ", src)
  if (length(ct_line) != 1) fail("CONTINUOUS_TYPES not found in pipeline")
  eval(parse(text = src[ct_line]))

  start <- grep("^check_integrity <- function", src)
  if (length(start) != 1) fail("check_integrity not found in pipeline")
  # Function body runs to the first line that closes it at column zero.
  ends <- grep("^}$", src)
  stop_at <- min(ends[ends > start])
  eval(parse(text = paste(src[start:stop_at], collapse = "\n")))

  # The fixture follows the contract the pipeline actually enforces since the port of 16 October:
  # a continuous row needs an effect and a variance on the percent change scale, not arm level
  # means and standard deviations, which this literature mostly does not publish. The arm columns
  # are kept because real rows carry them when the source prints them, and their presence must not
  # by itself make a row acceptable or unacceptable.
  good <- data.frame(
    receptor_class = "GLP1_mono", outcome_type = "continuous",
    mean_tx = 1, sd_tx = 1, n_tx = 10,
    mean_ctrl = 0, sd_ctrl = 1, n_ctrl = 10,
    yi_pct = -10, vi_pct = 4,
    aging_direction = 1, pct_weight_change = -10,
    stringsAsFactors = FALSE
  )

  if (!isTRUE(tryCatch({ check_integrity(good); TRUE },
                       error = function(e) FALSE))) {
    fail("integrity function rejects well formed input")
  }
  pass("accepts well formed input")

  # Each case is a failure mode the protocol names, restated against the ported contract. The three
  # that tested arm level completeness were replaced rather than deleted: the protocol's concern was
  # never arm standard deviations as such but that a row reach the estimator without a usable effect
  # or with a weight that is not a weight, and these cases test that concern on the scale the
  # pipeline now pools.
  cases <- list(
    "unknown receptor class"     = transform(good, receptor_class = "GLP1_BOGUS"),
    "harmonised columns absent"  = good[, setdiff(names(good), c("yi_pct", "vi_pct"))],
    "no usable continuous row"   = transform(good, yi_pct = NA_real_),
    "non-positive variance"      = transform(good, vi_pct = 0),
    "undeclared aging direction" = transform(good, aging_direction = 0),
    "weight covariate absent throughout" = transform(good, pct_weight_change = NA_real_)
  )
  for (nm in names(cases)) {
    rejected <- tryCatch({ check_integrity(cases[[nm]]); FALSE },
                         error = function(e) TRUE)
    if (!rejected) fail("integrity function accepted: ", nm)
    pass("rejects ", nm)
  }
}

message("Gate 4: every tracked table is rectangular")

# Added 24 October 2026. Two reasons in analysis/data/nbais_inclusion_set.csv held unquoted commas,
# so two rows had five fields under a four column header; readr kept four and dropped the rest with
# a parsing warning that the run printed and nothing stopped on. The marker names were unaffected,
# so no number moved and nothing failed. A table of the wrong shape that happens not to move a
# number is still the wrong shape, and the next one may move a number, so the shape of every table
# is checked here, where CI sees it, instead of being left to a warning. count.fields applies the
# quoting rules read.csv applies: a field holding a comma must be quoted. An empty file is refused:
# a table without even a header row is a table that nothing wrote (analysis/output held one, the
# network diagnostics written from an empty list, until the same day).
table_dirs <- c("analysis/data", "analysis/output", "search")
tables <- unlist(lapply(table_dirs[dir.exists(table_dirs)], list.files, pattern = "\\.csv$",
                        recursive = TRUE, full.names = TRUE))
for (path in tables) {
  if (file.size(path) == 0) fail(path, " is empty: a table names at least its columns")
  n <- utils::count.fields(path, sep = ",", quote = "\"", comment.char = "",
                           blank.lines.skip = FALSE)
  if (anyNA(n)) {
    fail(path, ": line ", which(is.na(n))[1], " opens a quoted field that does not close on it; ",
         "either a quote is unbalanced or a record spans lines, and tables here keep one record ",
         "per line")
  }
  bad <- which(n != n[1])
  if (length(bad)) {
    fail(path, ": line ", paste(head(bad, 5), collapse = ", "), " has ",
         paste(head(n[bad], 5), collapse = ", "), " fields against ", n[1], " in the header")
  }
}
pass("each of ", length(tables), " tables has as many fields on every line as in its header")

message("Gate 5: the reference run raised no warning")

# Added 24 October 2026. The pipeline records every warning it raises in
# analysis/output/run_warnings.csv (its section 0); see the pipeline header of that section for the
# runs whose one warning that mattered was buried among the others. Once a reference run exists, its
# manifest and its warning record exist together, and the record must be empty.
warn_path <- "analysis/output/run_warnings.csv"
if (file.exists("analysis/output/MANIFEST.csv") && !file.exists(warn_path)) {
  fail("the reference run has a manifest and no warning record at ", warn_path)
}
if (file.exists(warn_path)) {
  w <- utils::read.csv(warn_path, stringsAsFactors = FALSE)
  if (!identical(names(w), "warning")) fail(warn_path, " does not have the single column warning")
  if (nrow(w) > 0) fail("the reference run raised ", nrow(w), " warnings; the first: ", w$warning[1])
  pass("the reference run raised no warning")
} else {
  pass("no reference run is recorded in this tree; nothing to check")
}

message("")
message("All gates passed.")
message("Note: no pooled estimates exist at this stage. See docs/MANIFEST.md.")
