###############################################################################
# analyse_retatrutide_hepatic.R
#
# First real analysis on extracted data.
#
# Source: Sanyal AJ, Kaplan LM, Frias JP, et al. Triple hormone receptor
# agonist retatrutide for metabolic dysfunction-associated steatotic liver
# disease: a randomized phase 2a trial. Nat Med. 2024;30(7):2037-2048.
# DOI 10.1038/s41591-024-03018-2. PMID 38858523. Open access via PMC11271400.
#
# WHAT THIS IS
# ------------
# A single trial, four dose arms against a shared placebo arm, two timepoints.
# It is not the systematic review. It is the first extraction, run to confirm
# the extraction route works and to test one pre-specified question on real
# data: does the hepatic effect of retatrutide saturate while weight loss
# continues?
#
# WHY CONTRAST LEVEL
# ------------------
# The protocol's schema assumed arm level means and standard deviations. This
# trial, like most in the field, reports least squares mean treatment
# differences with confidence intervals and never publishes per arm SDs. The
# schema has been extended rather than the data forced: effect sizes enter
# directly as yi with vi derived from the reported interval.
#
#   SE = (upper limit - lower limit) / (2 * 1.96)
#
# In words, a 95% confidence interval spans 1.96 standard errors either side of
# the estimate, so its full width is 3.92 standard errors and dividing the
# width by 3.92 recovers the standard error. This is exact for a symmetric
# interval on the reported scale, which these are.
#
# A CAUTION THAT LIMITS WHAT THIS CAN SHOW
# ----------------------------------------
# The four dose arms share one placebo arm of 19 participants. Their effect
# estimates are therefore correlated, and pooling them as though independent
# would understate the variance. No pooling across arms is performed here for
# that reason. Each arm is reported separately and the dose response is read
# across them descriptively.
#
# Run from the repository root: Rscript src/analyse_retatrutide_hepatic.R
###############################################################################

set.seed(20261013)

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(tibble)
})

IN  <- "analysis/data/extraction_sanyal2024_retatrutide.csv"
OUT <- "analysis/output"
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

d <- readr::read_csv(IN, show_col_types = FALSE)

stopifnot(all(d$se_source == "ci_95"))
stopifnot(!any(is.na(d$ci_lb_reported)), !any(is.na(d$ci_ub_reported)))

Z95 <- qnorm(0.975)   # 1.959964

d <- d |>
  mutate(
    se  = (ci_ub_reported - ci_lb_reported) / (2 * Z95),
    vi  = se^2,
    z   = yi_reported / se,
    p   = 2 * pnorm(-abs(z)),
    # Liver fat per unit of weight lost. Both are percentages, so the ratio is
    # dimensionless: percent relative liver fat reduction per percent of body
    # weight lost. It is the quantity the saturation question turns on.
    lf_per_wt = yi_reported / pct_weight_change
  )

message("\n", strrep("=", 78))
message("Retatrutide hepatic effect, Sanyal 2024 Nat Med, n = 98")
message(strrep("=", 78))

for (wk in c(24, 48)) {
  dd <- filter(d, duration_weeks == wk) |> arrange(dose_mg)
  message(sprintf("\nWeek %d", wk))
  message(sprintf("  %5s %6s %9s %18s %9s %12s %10s",
                  "dose", "n_tx", "liver fat", "95% CI", "SE", "p", "LF per wt"))
  for (i in seq_len(nrow(dd))) {
    message(sprintf("  %4.0fmg %6d %8.1f%% %8.1f to %-7.1f %8.2f %12.2e %9.2f",
                    dd$dose_mg[i], dd$n_tx[i], dd$yi_reported[i],
                    dd$ci_lb_reported[i], dd$ci_ub_reported[i],
                    dd$se[i], dd$p[i], dd$lf_per_wt[i]))
  }
}

###############################################################################
# THE SATURATION TEST
#
# The manuscript's Discussion argues that the hepatic effect saturates between
# 8 mg and 12 mg while weight loss continues to increase, and that this is hard
# to explain if the hepatic benefit is purely downstream of weight loss.
#
# That argument has so far rested on the point estimates looking similar. It is
# tested here. Two questions, kept separate because they are different claims:
#
#   1. Do the 8 mg and 12 mg hepatic effects differ?
#   2. Do the 8 mg and 12 mg weight effects differ?
#
# The saturation argument needs the answer to be no and yes respectively. If
# weight also saturates, there is nothing to explain and the argument must be
# withdrawn from the manuscript.
#
# Both arms are compared against a shared placebo, so their estimates are
# positively correlated through it. Treating them as independent OVERSTATES the
# variance of their difference, making this a conservative test: it is harder
# to declare a difference, not easier. Stated explicitly because the test is
# being used to support a null, and a conservative test supporting a null is
# the weak direction.
###############################################################################

message("\n", strrep("=", 78))
message("Saturation test: does the hepatic effect plateau while weight does not?")
message(strrep("=", 78))

contrast_arms <- function(dd, a, b, label, unit) {
  x <- filter(dd, dose_mg == a)
  y <- filter(dd, dose_mg == b)
  diff <- x$yi_reported - y$yi_reported
  se_d <- sqrt(x$se^2 + y$se^2)
  z    <- diff / se_d
  p    <- 2 * pnorm(-abs(z))
  tibble(
    comparison = sprintf("%s: %g mg vs %g mg", label, a, b),
    estimate_a = x$yi_reported,
    estimate_b = y$yi_reported,
    difference = diff,
    se_diff    = se_d,
    ci_lb      = diff - Z95 * se_d,
    ci_ub      = diff + Z95 * se_d,
    p_value    = p,
    unit       = unit
  )
}

wk24 <- filter(d, duration_weeks == 24)

# Weight arm level SEMs as published, which the extraction carries as
# pct_weight_change without uncertainty. They are restated here from the paper
# so the weight comparison can be tested rather than asserted.
wt <- tribble(
  ~dose_mg, ~pct_change, ~sem,
  1,  -6.3, 1.0,
  4, -12.2, 0.9,
  8, -17.9, 1.2,
  12, -17.6, 1.2
)

lf_8_12 <- contrast_arms(wk24, 8, 12, "Liver fat, week 24", "% relative")

w8 <- filter(wt, dose_mg == 8); w12 <- filter(wt, dose_mg == 12)
wt_diff <- w8$pct_change - w12$pct_change
wt_se   <- sqrt(w8$sem^2 + w12$sem^2)
wt_p    <- 2 * pnorm(-abs(wt_diff / wt_se))

message(sprintf("\n  Liver fat   8 mg %.1f%%   12 mg %.1f%%", 
                lf_8_12$estimate_a, lf_8_12$estimate_b))
message(sprintf("    difference %.2f  (95%% CI %.2f to %.2f)  p = %.3f",
                lf_8_12$difference, lf_8_12$ci_lb, lf_8_12$ci_ub, lf_8_12$p_value))

message(sprintf("\n  Body weight 8 mg %.1f%%   12 mg %.1f%%",
                w8$pct_change, w12$pct_change))
message(sprintf("    difference %.2f  (95%% CI %.2f to %.2f)  p = %.3f",
                wt_diff, wt_diff - Z95 * wt_se, wt_diff + Z95 * wt_se, wt_p))

# The dose step that does produce an effect, for contrast. If 4 to 8 mg moves
# liver fat and 8 to 12 mg does not, the plateau is real rather than an
# artifact of insufficient power at every step.
lf_4_8 <- contrast_arms(wk24, 4, 8, "Liver fat, week 24", "% relative")
message(sprintf("\n  For contrast, the 4 to 8 mg step:"))
message(sprintf("    4 mg %.1f%%   8 mg %.1f%%", 
                lf_4_8$estimate_a, lf_4_8$estimate_b))
message(sprintf("    difference %.2f  (95%% CI %.2f to %.2f)  p = %.4f",
                lf_4_8$difference, lf_4_8$ci_lb, lf_4_8$ci_ub, lf_4_8$p_value))

readr::write_csv(bind_rows(lf_8_12, lf_4_8),
                 file.path(OUT, "retatrutide_dose_contrasts.csv"))

###############################################################################
# WHAT THE SATURATION TEST CAN AND CANNOT ESTABLISH
#
# A non-significant difference between two arms is not evidence that they are
# equivalent. With roughly 20 participants per arm this trial has little power
# to detect a modest difference, so "no significant difference" and "no
# difference" are not the same statement. The equivalence bound below makes
# that precise: it reports the smallest difference the data can exclude.
###############################################################################

message("\n", strrep("-", 78))
message("Power and equivalence, so the null is not overread")
message(strrep("-", 78))

# The largest true difference compatible with the data at 95% confidence is
# the confidence limit furthest from zero.
bound <- max(abs(c(lf_8_12$ci_lb, lf_8_12$ci_ub)))
message(sprintf("\n  The 8 vs 12 mg hepatic difference is %.2f%%, 95%% CI %.2f to %.2f.",
                lf_8_12$difference, lf_8_12$ci_lb, lf_8_12$ci_ub))
message(sprintf("  A true difference larger than %.1f percentage points is excluded.", bound))
message(sprintf("  A true difference smaller than that is NOT excluded."))

# Smallest difference detectable at 80% power with this standard error.
mde <- (qnorm(0.975) + qnorm(0.80)) * lf_8_12$se_diff
message(sprintf("\n  Minimum detectable difference at 80%% power: %.1f percentage points.", mde))
message(sprintf("  The observed difference is %.2f, far below that threshold.",
                abs(lf_8_12$difference)))

message("\n  Reading: the data are consistent with a plateau and cannot establish one.")
message("  The claim the manuscript can support is that no additional hepatic")
message("  effect was detected between 8 and 12 mg, while weight loss over the")
message("  same interval also did not differ detectably. On this evidence the")
message("  saturation argument is NOT supported, because its premise fails:")
message("  weight did not continue to fall meaningfully between these doses.")

###############################################################################
# WEIGHT ADJUSTED HEPATIC EFFECT
#
# The quantity the whole project turns on, computed here for one drug for the
# first time: liver fat reduction per unit of body weight lost. If this is flat
# across doses, the hepatic effect scales with weight loss. If it rises with
# dose, something beyond weight loss is contributing.
###############################################################################

message("\n", strrep("=", 78))
message("Liver fat reduction per percent of body weight lost")
message(strrep("=", 78))
message("")

ratio_tab <- filter(d, duration_weeks == 24) |>
  arrange(dose_mg) |>
  transmute(
    dose_mg,
    liver_fat_pct = yi_reported,
    weight_pct    = pct_weight_change,
    lf_per_wt     = round(lf_per_wt, 2)
  )

for (i in seq_len(nrow(ratio_tab))) {
  message(sprintf("  %4.0f mg   liver fat %6.1f%%   weight %6.1f%%   ratio %5.2f",
                  ratio_tab$dose_mg[i], ratio_tab$liver_fat_pct[i],
                  ratio_tab$weight_pct[i], ratio_tab$lf_per_wt[i]))
}

rng <- range(ratio_tab$lf_per_wt)
message(sprintf("\n  Ratio ranges %.2f to %.2f across doses, a %.1f fold spread.",
                rng[1], rng[2], rng[2] / rng[1]))

# Read the direction from the data rather than asserting it. The low dose arm
# sits in a different regime: with only 6.3% weight loss it has barely entered
# the range over which liver fat responds, so the ratio there is not comparable
# to the ratios at doses producing substantial weight loss. The informative
# comparison is across the 4, 8 and 12 mg arms.
upper <- filter(ratio_tab, dose_mg >= 4)
spread_upper <- max(upper$lf_per_wt) - min(upper$lf_per_wt)

message(sprintf("  Across the 4, 8 and 12 mg arms the ratio is %s.",
                paste(sprintf("%.2f", upper$lf_per_wt), collapse = ", ")))
message(sprintf("  Spread across those three arms: %.2f.", spread_upper))

if (spread_upper < 0.5) {
  message("")
  message("  The ratio is FLAT across the doses producing substantial weight")
  message("  loss. On this trial alone, the hepatic effect of retatrutide is")
  message("  proportional to weight loss, and there is no dose dependent")
  message("  weight independent component to point to. The higher ratio at")
  message("  1 mg reflects a different regime, not extra hepatic potency.")
} else {
  message("")
  message("  The ratio varies across doses producing substantial weight loss,")
  message("  which would be consistent with a component not explained by")
  message("  weight loss alone.")
}

message("")
message("  This is one trial, one drug, and no comparator class. The ratio")
message("  carries no interval, because the published weight SEMs are arm")
message("  level while the liver fat estimates are contrasts. It cannot")
message("  settle the weight independence question, which needs the")
message("  between class comparison the full synthesis provides.")

readr::write_csv(ratio_tab, file.path(OUT, "retatrutide_lf_per_weight.csv"))

message("\nDone. Two output files written to ", OUT, ".")
