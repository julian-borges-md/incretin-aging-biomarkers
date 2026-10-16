#!/usr/bin/env Rscript
###############################################################################
# pool_biomarkers.R
#
# First pooled estimates. Answers one question only: by how much does this
# drug class move each aging biomarker, as a placebo corrected percentage
# change from baseline?
#
# THREE DECISIONS THAT CONSTRAIN WHAT THIS CAN CLAIM
#
# 1. One arm per trial per biomarker. Several trials contribute multiple dose
#    arms against a single shared control. Treating those as independent
#    observations would count the same control patients repeatedly and
#    overstate precision. The highest dose arm is retained, which is the
#    arm the literature and any future guidance would be interested in, and
#    the discarded arms are reported so the choice is visible.
#
# 2. Random effects, REML, with Hartung-Knapp when k < 10. Validation showed
#    HK coverage of 0.952 against 0.924 uncorrected at k = 8, and nearly every
#    biomarker here sits far below 10.
#
# 3. Prediction intervals wherever tau is estimable (k >= 3). A confidence
#    interval describes the mean effect; a prediction interval describes what
#    the next trial might see. With this much heterogeneity the two differ,
#    and the second is the honest one to quote.
#
# WHAT THIS DELIBERATELY DOES NOT DO
#
# No composite score across biomarkers. No receptor class contrast. Both need
# more than one or two trials per cell, and at present most cells hold one.
# Computing them now would produce numbers that look like findings and are
# arithmetic on a single study.
###############################################################################

suppressPackageStartupMessages({
  library(dplyr); library(readr); library(metafor)
})

set.seed(20261013)

dat <- readr::read_csv("analysis/data/extraction_master_harmonised.csv",
                       show_col_types = FALSE, progress = FALSE) |>
  filter(!is.na(yi_pct), !is.na(vi_pct), vi_pct > 0)

message(sprintf("Harmonised rows available: %d", nrow(dat)))

# ---- Decision 1: collapse shared control arms -------------------------------
before <- nrow(dat)
dat <- dat |>
  group_by(trial_id, biomarker) |>
  slice_max(order_by = dose_mg, n = 1, with_ties = FALSE) |>
  ungroup()
message(sprintf("After keeping the highest dose arm per trial and biomarker: %d (%d dropped)",
                nrow(dat), before - nrow(dat)))

# ---- Pool within biomarker ---------------------------------------------------
pool_one <- function(d) {
  k <- nrow(d)
  if (k == 1) {
    return(tibble(k = 1L,
                  est = d$yi_pct, se = sqrt(d$vi_pct),
                  lo = d$yi_pct - 1.96 * sqrt(d$vi_pct),
                  hi = d$yi_pct + 1.96 * sqrt(d$vi_pct),
                  pi_lo = NA_real_, pi_hi = NA_real_,
                  tau2 = NA_real_, i2 = NA_real_, p = NA_real_,
                  note = "single trial, not pooled; interval is that trial's own"))
  }
  m <- tryCatch(
    metafor::rma(yi = d$yi_pct, vi = d$vi_pct, method = "REML",
                 test = if (k < 10) "knha" else "z"),
    error = function(e) NULL)
  if (is.null(m)) {
    return(tibble(k = k, est = NA_real_, se = NA_real_, lo = NA_real_, hi = NA_real_,
                  pi_lo = NA_real_, pi_hi = NA_real_, tau2 = NA_real_,
                  i2 = NA_real_, p = NA_real_, note = "model failed to converge"))
  }
  pi <- if (k >= 3) tryCatch(predict(m), error = function(e) NULL) else NULL
  # se is the model's standard error of the pooled estimate (the Hartung Knapp
  # adjusted one when knha is in force). compute_composite.R takes est and se
  # from here, so the composite is built on the plan's primary estimator.
  tibble(k = k, est = as.numeric(m$beta), se = as.numeric(m$se),
         lo = m$ci.lb, hi = m$ci.ub,
         pi_lo = if (!is.null(pi)) pi$pi.lb else NA_real_,
         pi_hi = if (!is.null(pi)) pi$pi.ub else NA_real_,
         tau2 = m$tau2, i2 = m$I2, p = m$pval,
         note = if (k < 3) "k<3, tau poorly estimated, no prediction interval" else "")
}

res <- dat |>
  group_by(biomarker, hallmark_domain, aging_direction) |>
  group_modify(~ pool_one(.x)) |>
  ungroup() |>
  mutate(favourable = aging_direction * est > 0) |>
  arrange(hallmark_domain, biomarker)

message("\nPOOLED EFFECT BY BIOMARKER")
message("placebo corrected percentage change from baseline\n")
message(sprintf("%-18s %-26s %2s %9s %18s %7s %s",
                "biomarker", "domain", "k", "estimate", "95% CI", "I2", "direction"))
message(strrep("-", 104))
for (i in seq_len(nrow(res))) {
  r <- res[i, ]
  dir <- if (is.na(r$est)) "?" else if (r$favourable) "favourable" else "UNFAVOURABLE"
  message(sprintf("%-18s %-26s %2d %8.1f%% %8.1f to %-7.1f %6s  %s",
                  r$biomarker, r$hallmark_domain, r$k, r$est, r$lo, r$hi,
                  ifelse(is.na(r$i2), "-", sprintf("%.0f%%", r$i2)), dir))
}

message("\nPREDICTION INTERVALS, where tau is estimable (k >= 3)")
pi_rows <- filter(res, !is.na(pi_lo))
if (nrow(pi_rows) == 0) {
  message("  NONE. No biomarker has three or more independent trials.")
  message("  Every interval above is a confidence interval for a mean estimated")
  message("  from one or two studies, not a prediction for a future trial.")
} else {
  for (i in seq_len(nrow(pi_rows))) {
    r <- pi_rows[i, ]
    message(sprintf("  %-18s %7.1f%%   PI %.1f to %.1f", r$biomarker, r$est, r$pi_lo, r$pi_hi))
  }
}

message("\nEVIDENCE DEPTH")
message(sprintf("  biomarkers with 1 trial only : %d", sum(res$k == 1)))
message(sprintf("  biomarkers with 2 trials     : %d", sum(res$k == 2)))
message(sprintf("  biomarkers with 3 or more    : %d", sum(res$k >= 3)))

readr::write_csv(res, "analysis/output/table2_pooled_by_biomarker.csv")
message("\nWrote analysis/output/table2_pooled_by_biomarker.csv")
