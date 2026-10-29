#!/usr/bin/env Rscript
###############################################################################
# collapse_rule.R
#
# ONE declaration of the shared control collapse: one arm per trial per
# biomarker. Sourced by analysis/M5_AGE_analysis_pipeline.R, src/pool_biomarkers.R,
# src/compute_composite.R and src/receptor_class_contrast.R. Run directly, it is
# the gate on its own property.
#
# WHY THIS FILE EXISTS. The rule was written out four times, identically, in those
# four scripts. The pipeline's own comment at the third of them named the problem
# and left it open: "consolidating the two into one shared step is the remaining
# work on this port, because a rule stated twice is the defect that has bitten
# this repository three times." It was stated four times, not twice.
#
# WHAT THE FOUR COPIES GOT WRONG, which is decision D-X3 of the Director register.
# Each copy read
#
#     slice_max(order_by = dose_mg, n = 1, with_ties = FALSE)
#
# and with_ties = FALSE means that when two rows share the highest dose, the one
# kept is THE FIRST IN FILE ORDER. The retatrutide hepatic trial is that case:
# NCT04881760-MASLD contributes eight liver fat rows, four doses by two series,
# and its assessment_timepoint_weeks is NA on every one, so the two series are
# distinguishable only by duration_weeks, 24 and 48. At the highest dose, 12 mg,
# two rows therefore tied and the pooled value was decided by a row's position in
# a CSV:
#
#     kept before    -82.7 per cent liver fat, 24 week series, weight -17.6
#     kept now       -81.4 per cent liver fat, 48 week series, weight -25.9
#
# The second is the row the extraction brief already prescribes, "the longest on
# treatment timepoint of twelve weeks or more". The first was never chosen; it
# was encountered first. That row is the sole triple agonist contribution in the
# corpus, so it feeds Table 4, Table 4a, Figure 4 and the hepatic model that
# decision A2 turns on.
#
# THE MEASUREMENT, before building, over analysis/data/extraction_master_harmonised.csv:
#
#     392  collapse groups, of trial by biomarker
#      64  groups holding more than one row
#       1  group where the highest dose is shared by more than one row
#       1  of those where duration separates them, which is the rule below
#       0  of those where nothing separates them
#
# So a rule that STOPS on a tie it cannot decide stops on nothing in this corpus
# today. That is the property worth having: it is silent now and it fires the day
# an extraction creates a genuine tie, instead of resolving it by file order and
# reporting a number nobody chose.
#
# THE RULE, in order:
#   1. the highest dose_mg in the group, missing doses ranking below any stated one
#   2. among those, a series that reaches COLLAPSE_MIN_WEEKS outranks one that does
#      not, and among series that reach it the longest wins
#   3. anything still tied is an error naming the group, never a silent pick
###############################################################################

suppressPackageStartupMessages({ library(dplyr) })

# The extraction brief's own floor for an on treatment series.
COLLAPSE_MIN_WEEKS <- 12

collapse_arms <- function(dat, min_weeks = COLLAPSE_MIN_WEEKS, label = "collapse") {
  need <- c("trial_id", "biomarker", "dose_mg", "duration_weeks")
  missing_cols <- setdiff(need, names(dat))
  if (length(missing_cols) > 0) {
    stop(label, ": the collapse needs ", paste(missing_cols, collapse = " and "),
         " and the frame does not carry ", if (length(missing_cols) > 1) "them" else "it",
         call. = FALSE)
  }

  ranked <- dat |>
    dplyr::mutate(
      .dose  = suppressWarnings(as.numeric(dose_mg)),
      .weeks = suppressWarnings(as.numeric(duration_weeks)),
      # A stated dose outranks an unstated one. Leaving NA to the sort would make
      # an all-NA group fall back to file order, which is the defect being removed.
      .dose_rank  = dplyr::coalesce(suppressWarnings(as.numeric(dose_mg)), -Inf),
      .on_treat   = as.integer(!is.na(suppressWarnings(as.numeric(duration_weeks))) &
                                 suppressWarnings(as.numeric(duration_weeks)) >= min_weeks),
      .weeks_rank = dplyr::coalesce(suppressWarnings(as.numeric(duration_weeks)), -Inf)
    ) |>
    dplyr::group_by(trial_id, biomarker) |>
    dplyr::arrange(dplyr::desc(.dose_rank), dplyr::desc(.on_treat), dplyr::desc(.weeks_rank),
                   .by_group = TRUE) |>
    dplyr::mutate(.tied_with_top = .dose_rank == .dose_rank[1] &
                    .on_treat == .on_treat[1] &
                    .weeks_rank == .weeks_rank[1])

  undecided <- ranked |>
    dplyr::summarise(n_top = sum(.tied_with_top), .groups = "drop") |>
    dplyr::filter(n_top > 1)

  if (nrow(undecided) > 0) {
    lines <- paste0("    ", undecided$trial_id, " / ", undecided$biomarker,
                    ": ", undecided$n_top, " rows tied on dose and duration")
    stop(label, ": the collapse cannot choose between rows that tie on both dose and ",
         "duration.\n", paste(lines, collapse = "\n"),
         "\n  Keeping the first would make the pooled value depend on row order. ",
         "Separate them in the extraction, or extend the rule in src/collapse_rule.R ",
         "and say why.", call. = FALSE)
  }

  ranked |>
    dplyr::slice(1) |>
    dplyr::ungroup() |>
    dplyr::select(-dplyr::any_of(c(".dose", ".weeks", ".dose_rank", ".on_treat",
                                   ".weeks_rank", ".tied_with_top")))
}


###############################################################################
# Run directly: the gate.
###############################################################################
if (sys.nframe() == 0L) {
  suppressPackageStartupMessages({ library(readr); library(tibble) })
  fail <- function(...) { message("FAIL: ", ...); quit(status = 1) }
  ok <- function(...) message("  ok   ", ...)
  bad <- 0L

  message("collapse rule, fixtures")

  # The retatrutide pattern: two series at the top dose, NA timepoints, 24 and 48 weeks.
  fx <- tibble::tibble(
    trial_id = "T", biomarker = "liver_fat_pdff",
    dose_mg = c(1, 4, 8, 12, 1, 4, 8, 12),
    duration_weeks = c(24, 24, 24, 24, 48, 48, 48, 48),
    yi_pct = c(-43.2, -57.3, -81.7, -82.7, -46.7, -54.4, -77.1, -81.4)
  )
  got <- collapse_arms(fx)
  if (nrow(got) == 1 && isTRUE(all.equal(got$yi_pct, -81.4))) {
    ok("the longest series at the highest dose is kept, -81.4 and not -82.7")
  } else { bad <- bad + 1L; message("  FAIL kept ", paste(got$yi_pct, collapse = ", ")) }

  # The same fixture in the other file order must give the same row.
  got2 <- collapse_arms(fx[rev(seq_len(nrow(fx))), ])
  if (isTRUE(all.equal(got$yi_pct, got2$yi_pct))) {
    ok("reversing the rows does not change which row is kept")
  } else { bad <- bad + 1L; message("  FAIL order changed the kept row") }

  # A series below the floor loses to one above it even when it is longer in name only.
  fx2 <- tibble::tibble(trial_id = "T", biomarker = "X", dose_mg = c(5, 5),
                        duration_weeks = c(8, 26), yi_pct = c(-10, -20))
  if (isTRUE(all.equal(collapse_arms(fx2)$yi_pct, -20))) {
    ok("a series reaching the twelve week floor outranks one that does not")
  } else { bad <- bad + 1L; message("  FAIL the floor was not applied") }

  # An undecidable tie stops rather than picking.
  fx3 <- tibble::tibble(trial_id = "T", biomarker = "X", dose_mg = c(5, 5),
                        duration_weeks = c(26, 26), yi_pct = c(-10, -20))
  stopped <- tryCatch({ collapse_arms(fx3); FALSE }, error = function(e) TRUE)
  if (stopped) {
    ok("a tie on both dose and duration is an error, not a file order pick")
  } else { bad <- bad + 1L; message("  FAIL an undecidable tie was resolved silently") }

  # A group of one is returned untouched, and an all-NA dose group is still decided.
  fx4 <- tibble::tibble(trial_id = c("A", "B", "B"), biomarker = "X",
                        dose_mg = c(NA, NA, NA), duration_weeks = c(26, 12, 52),
                        yi_pct = c(-1, -2, -3))
  got4 <- collapse_arms(fx4)
  if (nrow(got4) == 2 && isTRUE(all.equal(sort(got4$yi_pct), sort(c(-1, -3))))) {
    ok("a group with no stated dose is decided by duration, not by order")
  } else { bad <- bad + 1L; message("  FAIL ", paste(got4$yi_pct, collapse = ", ")) }

  # Order invariance over the real corpus, which is the property the four copies lacked.
  message("\norder invariance over the harmonised corpus")
  master <- readr::read_csv("analysis/data/extraction_master_harmonised.csv",
                            show_col_types = FALSE, progress = FALSE) |>
    dplyr::filter(!is.na(yi_pct), !is.na(vi_pct), vi_pct > 0)
  base <- collapse_arms(master, label = "reference")
  key <- function(d) paste(d$trial_id, d$biomarker, d$dose_mg, d$duration_weeks, d$yi_pct)
  ref <- sort(key(base))
  message(sprintf("  %d rows in, %d kept", nrow(master), nrow(base)))
  for (s in c(1L, 7L, 20261013L, 99991L)) {
    set.seed(s)
    shuffled <- master[sample.int(nrow(master)), ]
    k <- sort(key(collapse_arms(shuffled, label = paste0("seed ", s))))
    if (!identical(ref, k)) {
      bad <- bad + 1L
      message("  FAIL seed ", s, " kept a different set of rows")
    }
  }
  if (bad == 0L) ok("four permutations of the corpus keep the same rows")

  # The change is confined to the row this file claims it is confined to.
  old <- master |>
    dplyr::group_by(trial_id, biomarker) |>
    dplyr::slice_max(order_by = dose_mg, n = 1, with_ties = FALSE) |>
    dplyr::ungroup()
  moved <- dplyr::anti_join(base, old, by = c("trial_id", "biomarker", "dose_mg",
                                              "duration_weeks"))
  message(sprintf("\nrows the rule moves against the superseded file order pick: %d",
                  nrow(moved)))
  if (nrow(moved) > 0) {
    for (i in seq_len(nrow(moved))) {
      message(sprintf("  %s / %s: now the %s week series at %s mg",
                      moved$trial_id[i], moved$biomarker[i],
                      moved$duration_weeks[i], moved$dose_mg[i]))
    }
  }
  if (nrow(moved) == 1 && moved$trial_id[1] == "NCT04881760-MASLD" &&
      moved$biomarker[1] == "liver_fat_pdff") {
    ok("exactly the one group the measurement found, and no other")
  } else if (nrow(moved) == 0) {
    ok("no row moves; the corpus holds no tie at the highest dose")
  } else {
    bad <- bad + 1L
    message("  FAIL the rule moved rows this file does not account for")
  }

  if (bad > 0L) fail(bad, " collapse rule check(s) failed")
  message("\nAll collapse rule checks passed.")
}
