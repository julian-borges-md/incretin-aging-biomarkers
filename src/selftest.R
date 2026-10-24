###############################################################################
# selftest.R
#
# Proves that verify.R can fail. A gate that always passes is decoration.
#
# Each perturbation damages one thing the protocol commits to, in a temporary
# copy, and asserts verify.R then exits non zero. If a perturbation slips
# through, that gate is not checking what it claims to check and this fails.
# The working tree is never modified.
###############################################################################

fail <- function(...) { message("FAIL: ", ...); quit(status = 1) }

root       <- normalizePath(".")
pipe_rel   <- "analysis/M5_AGE_analysis_pipeline.R"
schema_rel <- "analysis/data/extraction_schema.csv"
nbais_rel  <- "analysis/data/nbais_inclusion_set.csv"
warn_rel   <- "analysis/output/run_warnings.csv"

perturbations <- list(
  list(name = "seed changed", file = pipe_rel,
       edit = function(x) gsub("set.seed(20261013)", "set.seed(1)", x, fixed = TRUE)),
  list(name = "an estimator dropped", file = pipe_rel,
       edit = function(x) gsub('"PM"', '"XX"', x, fixed = TRUE)),
  list(name = "prediction intervals removed", file = pipe_rel,
       edit = function(x) gsub("pi_lb", "zz_lb", x, fixed = TRUE)),
  list(name = "permutation iterations reduced", file = pipe_rel,
       edit = function(x) gsub("n_perm = 10000", "n_perm = 100", x, fixed = TRUE)),
  list(name = "composite turned into a weighted sum", file = pipe_rel,
       edit = function(x) gsub("/ sum(w)", "", x, fixed = TRUE)),
  list(name = "BCa bootstrap downgraded", file = pipe_rel,
       edit = function(x) gsub('type = "bca"', 'type = "norm"', x, fixed = TRUE)),
  list(name = "a schema column the pipeline needs is deleted", file = schema_rel,
       edit = function(x) grep("^aging_direction,", x, invert = TRUE, value = TRUE)),
  # The defect of 24 October 2026: a reason with an unquoted comma gives its row one field more
  # than the header.
  list(name = "a table row holds an unquoted comma", file = nbais_rel,
       edit = function(x) { x[2] <- paste0(x[2], ", with a clause after an unquoted comma"); x }),
  list(name = "a table is emptied", file = nbais_rel, edit = function(x) character(0)),
  list(name = "the reference run records a warning", file = warn_rel,
       edit = function(x) c(x, "a warning that nothing read"))
)

message("Running ", length(perturbations), " perturbations.\n")

copy_tree <- function() {
  tmp <- file.path(tempdir(), paste0("st_", as.integer(runif(1, 1, 1e9))))
  dir.create(file.path(tmp, "analysis/data"), recursive = TRUE, showWarnings = FALSE)
  dir.create(file.path(tmp, "src"), recursive = TRUE, showWarnings = FALSE)
  dir.create(file.path(tmp, "analysis/output"), recursive = TRUE, showWarnings = FALSE)
  for (rel in c(pipe_rel, schema_rel, nbais_rel, warn_rel, "src/verify.R")) {
    if (!file.copy(file.path(root, rel), file.path(tmp, rel))) fail("could not copy ", rel)
  }
  tmp
}
run_verify <- function(tmp) {
  system(sprintf("cd %s && Rscript src/verify.R > /dev/null 2>&1", shQuote(tmp)))
}

# Control, added 24 October 2026. A perturbation proves something only if the copy passes without
# it; otherwise verify.R could fail in the copy for a reason no perturbation introduced, and every
# perturbation below would be counted as caught.
control <- copy_tree()
if (run_verify(control) != 0) fail("verify.R fails on the unperturbed copy, so no perturbation proves anything")
message("  ok   verify.R passes on the unperturbed copy")
unlink(control, recursive = TRUE)

for (p in perturbations) {
  tmp <- copy_tree()

  target  <- file.path(tmp, p$file)
  lines   <- readLines(target, warn = FALSE)
  damaged <- p$edit(lines)
  if (identical(lines, damaged)) {
    fail("perturbation had no effect, so it tests nothing: ", p$name)
  }
  writeLines(damaged, target)

  status <- system(sprintf("cd %s && Rscript src/verify.R > /dev/null 2>&1",
                           shQuote(tmp)))
  if (status == 0) fail("verify.R passed despite: ", p$name)
  message("  ok   verify.R fails when ", p$name)

  unlink(tmp, recursive = TRUE)
}

message("\nEvery gate can fail. verify.R checks what it claims to check.")
