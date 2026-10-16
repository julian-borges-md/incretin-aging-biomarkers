###############################################################################
# extraction_tools.R
#
# Conversion and validation helpers for contrast level extraction.
#
# WHY THIS FILE EXISTS
# --------------------
# Trials in this literature report a treatment effect in whichever form the
# journal preferred: an estimate with a confidence interval, an estimate with a
# standard error, an estimate with an exact p value, or least squares means per
# arm with standard errors of the mean. Each must be converted to a point
# estimate yi and its sampling variance vi before anything can be pooled.
#
# Doing that conversion by hand, once per row, across forty trials is where
# extraction errors come from. Every conversion lives here instead, each with
# its formula stated in words, and each returning the route it took so the
# provenance of every variance in the dataset is recorded in the dataset.
#
# Sourced by build_master.R. Not run directly.
###############################################################################

suppressPackageStartupMessages({
  library(dplyr)
  library(tibble)
})

Z95 <- qnorm(0.975)   # 1.959964, the normal quantile a 95% interval spans

## ---------------------------------------------------------------------------
## Standard error from a 95% confidence interval
##
## A 95% interval reaches 1.96 standard errors either side of the estimate, so
## its total width is 3.92 standard errors. Dividing the width by 3.92 recovers
## the standard error. This is exact when the interval is symmetric on the
## reported scale, which is the case for mean differences and for least squares
## mean contrasts. It is NOT valid for a ratio reported on the natural scale:
## an odds ratio or risk ratio must be logged first, which log_ratio_ci does.
## ---------------------------------------------------------------------------
se_from_ci <- function(lb, ub, level = 0.95) {
  z <- qnorm(1 - (1 - level) / 2)
  (ub - lb) / (2 * z)
}

## ---------------------------------------------------------------------------
## Standard error from an exact two sided p value
##
## Invert the p value to the z statistic that produced it, then divide the
## estimate by that z. For a two sided p, the z is the quantile at 1 - p/2.
##
## This requires an EXACT p. A reported bound such as "p < 0.001" carries no
## recoverable standard error, because any z above 3.29 is consistent with it.
## Passing a bound here returns NA rather than silently using the threshold,
## which would understate the variance and overstate the precision.
## ---------------------------------------------------------------------------
se_from_p <- function(estimate, p, is_bound = FALSE) {
  if (isTRUE(is_bound)) return(NA_real_)
  if (is.na(p) || p <= 0 || p >= 1) return(NA_real_)
  z <- qnorm(1 - p / 2)
  if (z == 0) return(NA_real_)
  abs(estimate) / z
}

## ---------------------------------------------------------------------------
## Standard error of a difference between two independent arms
##
## The variance of a difference between independent quantities is the sum of
## their variances, so the standard error is the square root of the sum of the
## squared standard errors.
##
## INDEPENDENCE IS AN ASSUMPTION, and in dose ranging trials it is usually
## false: several active arms are compared against one shared placebo arm,
## which correlates their estimates. Treating them as independent OVERSTATES
## the variance of their difference. That is conservative when testing for a
## difference and anticonservative when claiming equivalence, so the direction
## of the error must be stated wherever this is used.
## ---------------------------------------------------------------------------
se_of_difference <- function(se_a, se_b) sqrt(se_a^2 + se_b^2)

## ---------------------------------------------------------------------------
## Standard error from arm level standard errors of the mean
##
## Where a trial reports least squares means per arm with their standard
## errors, the contrast against the control arm has the standard error above.
## The same independence caveat applies when several active arms share a
## control.
## ---------------------------------------------------------------------------
contrast_from_arms <- function(mean_tx, sem_tx, mean_ctrl, sem_ctrl) {
  tibble(
    yi = mean_tx - mean_ctrl,
    se = se_of_difference(sem_tx, sem_ctrl)
  )
}

## ---------------------------------------------------------------------------
## Ratio measures reported on the natural scale
##
## An odds ratio or risk ratio is asymmetric on its natural scale, so the
## interval width method cannot be applied to it directly. Log the estimate and
## both limits first; the interval is symmetric on the log scale, where the
## standard error is recoverable. Pooling then happens on the log scale and the
## result is exponentiated for presentation.
## ---------------------------------------------------------------------------
log_ratio_ci <- function(estimate, lb, ub) {
  if (any(c(estimate, lb, ub) <= 0, na.rm = TRUE)) {
    stop("ratio measures must be positive; got ",
         paste(c(estimate, lb, ub), collapse = ", "))
  }
  tibble(
    yi = log(estimate),
    se = se_from_ci(log(lb), log(ub))
  )
}

## ---------------------------------------------------------------------------
## Change score contrast when a trial reports baseline and final arm means
## with SDs but no SD of change (amendment R1, 2026-10-15)
##
## Several parallel group trials in this literature (Derosa 2012, Wu 2011,
## Wägner 2019) tabulate each arm at baseline and at end of study, mean (SD),
## and report nothing about the within patient change. Two things go wrong if
## final values are used directly. First, in a 24 patient trial a chance
## baseline imbalance (Wägner: CRP 0.37 against 0.66 mg/dL at entry) becomes
## the "treatment effect" at exit. Second, the schema defines mean_tx and
## sd_tx as CHANGE quantities, so entering final values there would be a
## silent redefinition of the column.
##
## The change score SD is therefore imputed from the two reported SDs and an
## assumed pre post correlation r (Cochrane Handbook 6.5.2.8):
##
##   sd_change = sqrt(sd_base^2 + sd_final^2 - 2 r sd_base sd_final)
##
## and the contrast is the difference of mean changes, with the pooled SD
## formula of the arm_sds route. r must be RECORDED on the row (corr_assumed);
## the primary analysis uses 0.5 and the sensitivity analyses rerun with 0.3
## and 0.7. Direction of the assumption: a smaller r gives a larger sd_change
## and a wider interval, so if 0.5 overstates the true correlation the primary
## result is anticonservative, which is why the 0.3 rerun is mandatory.
## ---------------------------------------------------------------------------
sd_change_imputed <- function(sd_base, sd_final, r) {
  if (!is.finite(r) || r <= -1 || r >= 1) stop("corr_assumed must lie strictly between -1 and 1")
  sqrt(sd_base^2 + sd_final^2 - 2 * r * sd_base * sd_final)
}

change_contrast_imputed <- function(base_mean_tx, base_sd_tx, final_mean_tx, final_sd_tx, n_tx,
                                    base_mean_ctrl, base_sd_ctrl, final_mean_ctrl, final_sd_ctrl,
                                    n_ctrl, r) {
  sd_tx   <- sd_change_imputed(base_sd_tx,   final_sd_tx,   r)
  sd_ctrl <- sd_change_imputed(base_sd_ctrl, final_sd_ctrl, r)
  s_p <- sqrt(((n_tx - 1) * sd_tx^2 + (n_ctrl - 1) * sd_ctrl^2) / (n_tx + n_ctrl - 2))
  tibble(
    yi = (final_mean_tx - base_mean_tx) - (final_mean_ctrl - base_mean_ctrl),
    se = s_p * sqrt(1 / n_tx + 1 / n_ctrl)
  )
}

# Counterexamples run at source time, so the formula cannot drift silently.
# Equal SDs of 1 and r = 0.5 give a change SD of exactly 1; r = 0 gives
# sqrt(2); a lower r must always give a larger SE (the direction of bias
# stated above); and a baseline imbalance must not enter the contrast when
# the within arm changes are equal.
stopifnot(
  abs(sd_change_imputed(1, 1, 0.5) - 1) < 1e-12,
  abs(sd_change_imputed(1, 1, 0.0) - sqrt(2)) < 1e-12,
  sd_change_imputed(1, 1, 0.3) > sd_change_imputed(1, 1, 0.7),
  abs(change_contrast_imputed(0.37, 0.24, 0.31, 0.29, 12,
                              0.66, 0.30, 0.64, 0.30, 12, 0.5)$yi - (-0.04)) < 1e-12,
  abs(change_contrast_imputed(10, 2, 8, 2, 20, 10, 2, 8, 2, 20, 0.5)$yi) < 1e-12
)

## ---------------------------------------------------------------------------
## Resolve a row to yi and vi, by whichever route its reported form allows
##
## Routes are tried in order of how much information they preserve. A
## confidence interval is preferred to an exact p value, because the interval
## uses both limits while the p value compresses them into one number and
## discards any asymmetry. The route taken is returned in se_route so the
## provenance of every variance is visible in the dataset itself.
## ---------------------------------------------------------------------------
resolve_effect <- function(row) {

  has <- function(x) !is.null(x) && length(x) == 1 && !is.na(x)

  # Route 1: estimate with a 95% confidence interval, continuous measure.
  if (has(row$yi_reported) && has(row$ci_lb_reported) && has(row$ci_ub_reported) &&
      (!has(row$measure) || row$measure %in% c("MD", "SMD", "PCT"))) {
    se <- se_from_ci(row$ci_lb_reported, row$ci_ub_reported)
    return(list(yi = row$yi_reported, se = se, route = "ci_95"))
  }

  # Route 2: ratio measure with an interval, logged before conversion.
  if (has(row$yi_reported) && has(row$ci_lb_reported) && has(row$ci_ub_reported) &&
      has(row$measure) && row$measure %in% c("OR", "RR", "HR")) {
    lr <- log_ratio_ci(row$yi_reported, row$ci_lb_reported, row$ci_ub_reported)
    return(list(yi = lr$yi, se = lr$se, route = paste0("log_", row$measure, "_ci")))
  }

  # Route 3: estimate with a standard error given directly.
  if (has(row$yi_reported) && has(row$se_reported)) {
    return(list(yi = row$yi_reported, se = row$se_reported, route = "se_reported"))
  }

  # Route 4: estimate with an exact p value. Bounds are refused.
  if (has(row$yi_reported) && has(row$p_reported)) {
    bound <- isTRUE(row$p_is_bound)
    se <- se_from_p(row$yi_reported, row$p_reported, is_bound = bound)
    if (!is.na(se)) return(list(yi = row$yi_reported, se = se, route = "exact_p"))
    return(list(yi = row$yi_reported, se = NA_real_, route = "p_bound_unusable"))
  }

  # Route 5: arm level means with standard errors of the mean.
  if (has(row$mean_tx) && has(row$sem_tx) && has(row$mean_ctrl) && has(row$sem_ctrl)) {
    cc <- contrast_from_arms(row$mean_tx, row$sem_tx, row$mean_ctrl, row$sem_ctrl)
    return(list(yi = cc$yi, se = cc$se, route = "arm_sems"))
  }

  # Route 5b (2026-10-16, systematic corpus): per arm mean changes with no dispersion, and an
  # exact two sided p value for the between arm comparison. Conference abstracts print this
  # shape constantly ("-11.3 vs 1.7 nmol/L, p = 0.01"). The contrast is the difference of the
  # arm means and its standard error is recovered from the p value exactly as in Route 4, so the
  # same bound rule applies: a p bound or a rounded zero gives no row. The subtraction is done
  # here, not by the extractor (brief rule 8), so the route is recorded for every such row.
  if (has(row$mean_tx) && has(row$mean_ctrl) && has(row$p_reported) &&
      !has(row$sem_tx) && !has(row$sd_tx)) {
    yi <- row$mean_tx - row$mean_ctrl
    bound <- isTRUE(row$p_is_bound)
    se <- se_from_p(yi, row$p_reported, is_bound = bound)
    if (!is.na(se)) return(list(yi = yi, se = se, route = "arm_means_exact_p"))
    return(list(yi = yi, se = NA_real_, route = "p_bound_unusable"))
  }

  # Route 6: baseline and final arm means with SDs, change score SD imputed
  # through the recorded pre post correlation (amendment R1). The correlation
  # is mandatory on the row; a row that reaches this route without it stops
  # the build rather than silently taking a default.
  if (has(row$base_mean_tx) && has(row$base_sd_tx) && has(row$final_mean_tx) &&
      has(row$final_sd_tx) && has(row$n_tx) &&
      has(row$base_mean_ctrl) && has(row$base_sd_ctrl) && has(row$final_mean_ctrl) &&
      has(row$final_sd_ctrl) && has(row$n_ctrl)) {
    if (!has(row$corr_assumed)) {
      stop("corr_assumed must be recorded on every row that uses the change score ",
           "imputation route: ", row$trial_id, " / ", row$biomarker)
    }
    cc <- change_contrast_imputed(row$base_mean_tx, row$base_sd_tx,
                                  row$final_mean_tx, row$final_sd_tx, row$n_tx,
                                  row$base_mean_ctrl, row$base_sd_ctrl,
                                  row$final_mean_ctrl, row$final_sd_ctrl, row$n_ctrl,
                                  row$corr_assumed)
    return(list(yi = cc$yi, se = cc$se, route = "arm_change_imputed_r"))
  }

  # Route 7: arm level CHANGE means with standard deviations, the original schema.
  if (has(row$mean_tx) && has(row$sd_tx) && has(row$n_tx) &&
      has(row$mean_ctrl) && has(row$sd_ctrl) && has(row$n_ctrl)) {
    s_p <- sqrt(((row$n_tx - 1) * row$sd_tx^2 + (row$n_ctrl - 1) * row$sd_ctrl^2) /
                (row$n_tx + row$n_ctrl - 2))
    se  <- s_p * sqrt(1 / row$n_tx + 1 / row$n_ctrl)
    return(list(yi = row$mean_tx - row$mean_ctrl, se = se, route = "arm_sds"))
  }

  list(yi = NA_real_, se = NA_real_, route = "unresolvable")
}
