#!/usr/bin/env Rscript
###############################################################################
# sensitivity_corr.R
#
# Amendment R1 (2026-10-15) makes the 0.3 and 0.7 reruns of the pre post
# correlation mandatory wherever a change score SD was imputed. This script
# runs them. It never touches the working tree: for each r it copies the
# extraction files, the RoB file, the schema and the three stage scripts into
# a temporary directory, rewrites corr_assumed on the rows that carry one,
# runs build_master, harmonise_units and pool_biomarkers there, and reads the
# resulting Table 2. The primary (r = 0.5) figures are read from the real
# analysis/output/table2_pooled_by_biomarker.csv, so the comparison is
# against what the gate chain actually produced, not a re-computation.
#
# Only markers with at least one imputed row are reported; the others cannot
# move. Direction of the assumption, restated: a lower r widens every
# imputed interval, so the r = 0.3 column is the conservative bound.
###############################################################################

suppressPackageStartupMessages({ library(dplyr); library(readr) })

root  <- normalizePath(".")
RS    <- c(0.3, 0.7)
PRIM  <- 0.5
t2_primary_path <- file.path(root, "analysis/output/table2_pooled_by_biomarker.csv")
if (!file.exists(t2_primary_path)) stop("run the gate chain first; the primary Table 2 is missing")
t2_primary <- read_csv(t2_primary_path, show_col_types = FALSE, progress = FALSE)

master <- read_csv(file.path(root, "analysis/data/extraction_master.csv"),
                   show_col_types = FALSE, progress = FALSE)
imputed_markers <- master |>
  filter(se_route == "arm_change_imputed_r") |>
  distinct(biomarker) |> pull(biomarker)
imputed_trials <- master |>
  filter(se_route == "arm_change_imputed_r") |>
  distinct(trial_id) |> pull(trial_id)
message(sprintf("Imputed route in use on %d trial(s): %s",
                length(imputed_trials), paste(imputed_trials, collapse = ", ")))
message(sprintf("Markers that can move: %s\n", paste(imputed_markers, collapse = ", ")))
if (length(imputed_markers) == 0) {
  message("No row uses the change score imputation; nothing to rerun.")
  quit(status = 0)
}

run_with_r <- function(r) {
  tmp <- file.path(tempdir(), sprintf("corr_%s_%d", gsub("\\.", "", as.character(r)),
                                      as.integer(runif(1, 1, 1e9))))
  dir.create(file.path(tmp, "analysis/data"),   recursive = TRUE, showWarnings = FALSE)
  dir.create(file.path(tmp, "analysis/output"), recursive = TRUE, showWarnings = FALSE)
  dir.create(file.path(tmp, "src"),             recursive = TRUE, showWarnings = FALSE)
  for (f in c("extraction_tools.R", "build_master.R", "harmonise_units.R", "pool_biomarkers.R"))
    file.copy(file.path(root, "src", f), file.path(tmp, "src", f))
  for (f in c("extraction_schema.csv", "risk_of_bias.csv"))
    file.copy(file.path(root, "analysis/data", f), file.path(tmp, "analysis/data", f))
  files <- list.files(file.path(root, "analysis/data"), pattern = "^extraction_.*\\.csv$",
                      full.names = TRUE)
  files <- files[!grepl("extraction_master|extraction_schema", basename(files))]
  n_rewritten <- 0L
  for (f in files) {
    d <- read_csv(f, show_col_types = FALSE, progress = FALSE,
                  col_types = cols(.default = col_character()))
    if ("corr_assumed" %in% names(d)) {
      has_r <- !is.na(d$corr_assumed) & d$corr_assumed != "NA"
      d$corr_assumed[has_r] <- as.character(r)
      n_rewritten <- n_rewritten + sum(has_r)
    }
    write_csv(d, file.path(tmp, "analysis/data", basename(f)), na = "NA")
  }
  if (n_rewritten == 0) stop("no corr_assumed value was rewritten; the rerun would test nothing")
  for (s in c("build_master", "harmonise_units", "pool_biomarkers")) {
    status <- system(sprintf("cd %s && Rscript src/%s.R > /dev/null 2>&1", shQuote(tmp), s))
    if (status != 0) stop(sprintf("%s failed under r = %s", s, r))
  }
  out <- read_csv(file.path(tmp, "analysis/output/table2_pooled_by_biomarker.csv"),
                  show_col_types = FALSE, progress = FALSE)
  unlink(tmp, recursive = TRUE)
  message(sprintf("  r = %.1f: %d corr_assumed value(s) rewritten, chain rerun, Table 2 read", r, n_rewritten))
  out |> select(biomarker, k, est, lo, hi, i2) |> mutate(r = r)
}

alt <- bind_rows(lapply(RS, run_with_r))
prim <- t2_primary |> select(biomarker, k, est, lo, hi, i2) |> mutate(r = PRIM)
all <- bind_rows(prim, alt) |>
  filter(biomarker %in% imputed_markers) |>
  arrange(biomarker, r)

message("\nTABLE 2 UNDER THE THREE CORRELATIONS, markers with an imputed row")
message(sprintf("%-18s %2s %5s %9s %20s %6s", "biomarker", "k", "r", "estimate", "95% CI", "I2"))
message(strrep("-", 66))
for (i in seq_len(nrow(all))) {
  x <- all[i, ]
  message(sprintf("%-18s %2d %5.1f %8.1f%% %8.1f to %-8.1f %5s",
                  x$biomarker, x$k, x$r, x$est, x$lo, x$hi,
                  ifelse(is.na(x$i2), "-", sprintf("%.0f%%", x$i2))))
}

# A sign change or a change in whether the interval excludes zero between
# r = 0.3 and r = 0.7 is the thing a reader needs to know.
flip <- all |>
  group_by(biomarker) |>
  summarise(sign_stable = n_distinct(sign(est)) == 1,
            excl0_stable = n_distinct(lo > 0 | hi < 0) == 1, .groups = "drop") |>
  filter(!sign_stable | !excl0_stable)
message("")
if (nrow(flip) == 0) {
  message("Sign and zero exclusion unchanged across r for every imputed marker.")
} else {
  for (i in seq_len(nrow(flip))) {
    what <- c(if (!flip$sign_stable[i])  "the sign of the estimate changes with r",
              if (!flip$excl0_stable[i]) "whether the interval excludes zero changes with r")
    message(sprintf("  NOTE  %s: %s", flip$biomarker[i], paste(what, collapse = "; ")))
  }
}

write_csv(all, file.path(root, "analysis/output/table2_sensitivity_corr.csv"))
message("\nWrote analysis/output/table2_sensitivity_corr.csv")
