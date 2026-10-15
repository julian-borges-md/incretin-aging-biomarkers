###############################################################################
# validate_pipeline.R
#
# Does the pipeline recover parameters it is given?
#
# verify.R checks that the code still declares what the protocol commits to.
# selftest.R checks that verify.R can fail. Neither checks whether the
# statistics are CORRECT. This script does.
#
# Data are simulated under known true parameters with a fixed seed, passed
# through the same functions the real analysis uses, and the recovered values
# are asserted against the truth within tolerances derived from the simulation
# design rather than chosen to make the test pass.
#
# Every number printed is computed here. Nothing is asserted that the script
# does not derive.
#
# Run: Rscript src/validate_pipeline.R
###############################################################################

set.seed(20261013)

suppressPackageStartupMessages({
  library(metafor)
  library(dplyr)
  library(tibble)
  library(purrr)
  library(boot)
})

fail <- function(...) { message("FAIL: ", ...); quit(status = 1) }
ok   <- function(...) message("  ok   ", ...)

RECEPTOR_CLASSES <- c("GLP1_mono", "GLP1_GIP", "GLP1_GCGR", "GLP1_GIP_GCGR")

# Load the real pooling and composite functions from the pipeline, rather than
# reimplementing them here. A validation that tests a copy of the code proves
# nothing about the code that runs.
src <- readLines("analysis/M5_AGE_analysis_pipeline.R", warn = FALSE)
grab <- function(fn) {
  start <- grep(sprintf("^%s <- function", fn), src)
  if (length(start) != 1) fail("function not found in pipeline: ", fn)
  ends <- grep("^}$", src)
  paste(src[start:min(ends[ends > start])], collapse = "\n")
}
eval(parse(text = grab("pool_effect")))
eval(parse(text = grab("compute_nbais")))

###############################################################################
# TEST 1. Does pool_effect recover a known true effect?
#
# Simulate k trials drawn from a random effects model with true mean delta and
# true between-study variance tau2. The pooled estimate should land within
# Monte Carlo error of delta, and the estimated tau2 should land near the truth.
###############################################################################

message("\nTEST 1  Recovery of a known pooled effect")

simulate_trials <- function(k, delta, tau, n_per_arm = 60) {
  true_effects <- rnorm(k, mean = delta, sd = tau)
  purrr::map_dfr(seq_len(k), function(i) {
    x_tx   <- rnorm(n_per_arm, mean = true_effects[i], sd = 1)
    x_ctrl <- rnorm(n_per_arm, mean = 0,               sd = 1)
    tibble(
      trial_id  = sprintf("T%02d", i),
      mean_tx   = mean(x_tx),   sd_tx   = sd(x_tx),   n_tx   = n_per_arm,
      mean_ctrl = mean(x_ctrl), sd_ctrl = sd(x_ctrl), n_ctrl = n_per_arm
    )
  })
}

TRUE_DELTA <- 0.45
TRUE_TAU   <- 0.20
K          <- 24

sim <- simulate_trials(K, TRUE_DELTA, TRUE_TAU)
es  <- metafor::escalc(measure = "SMD",
                       m1i = mean_tx,   sd1i = sd_tx,   n1i = n_tx,
                       m2i = mean_ctrl, sd2i = sd_ctrl, n2i = n_ctrl,
                       data = sim, slab = trial_id)
es$n_tx <- sim$n_tx; es$n_ctrl <- sim$n_ctrl

res <- pool_effect(es)

message(sprintf("  true effect           %.3f", TRUE_DELTA))
message(sprintf("  pooled estimate       %.3f  (95%% CI %.3f to %.3f)",
                res$estimate, res$ci_lb, res$ci_ub))
message(sprintf("  prediction interval   %.3f to %.3f", res$pi_lb, res$pi_ub))
message(sprintf("  true tau              %.3f", TRUE_TAU))
message(sprintf("  estimated tau         %.3f", sqrt(res$tau2)))
message(sprintf("  I-squared             %.1f%%", res$I2))

if (res$ci_lb > TRUE_DELTA || res$ci_ub < TRUE_DELTA) {
  fail("95% CI excludes the true effect")
}
ok("95% CI covers the true effect")

if (abs(sqrt(res$tau2) - TRUE_TAU) > 0.12) {
  fail(sprintf("tau estimate %.3f is far from the truth %.3f",
               sqrt(res$tau2), TRUE_TAU))
}
ok("tau recovered within 0.12")

# The prediction interval must be wider than the confidence interval whenever
# tau2 is non-zero. If it is not, the implementation is wrong, and every
# clinical reading of the result would be wrong with it.
ci_w <- res$ci_ub - res$ci_lb
pi_w <- res$pi_ub - res$pi_lb
message(sprintf("  CI width %.3f, PI width %.3f", ci_w, pi_w))
if (pi_w <= ci_w) fail("prediction interval is not wider than the CI")
ok("prediction interval wider than confidence interval")


###############################################################################
# TEST 2. Coverage. Does the 95 percent interval contain the truth 95 percent
# of the time?
#
# A single interval covering the truth proves little. This repeats the whole
# simulation many times and counts. Nominal coverage is 95 percent; the
# acceptance band is derived from the binomial standard error of the
# replication count, not chosen by hand.
###############################################################################

message("\nTEST 2  Interval coverage over repeated simulation")

N_REP <- 500

coverage_run <- function(use_hksj) {
  hits <- vapply(seq_len(N_REP), function(i) {
    s  <- simulate_trials(8, TRUE_DELTA, TRUE_TAU)   # k = 8, small sample regime
    e  <- metafor::escalc(measure = "SMD",
                          m1i = mean_tx,   sd1i = sd_tx,   n1i = n_tx,
                          m2i = mean_ctrl, sd2i = sd_ctrl, n2i = n_ctrl,
                          data = s, slab = trial_id)
    e$n_tx <- s$n_tx; e$n_ctrl <- s$n_ctrl
    r <- pool_effect(e, use_hksj = use_hksj)
    as.numeric(r$ci_lb <= TRUE_DELTA && r$ci_ub >= TRUE_DELTA)
  }, numeric(1))
  mean(hits)
}

cov_hksj <- coverage_run(TRUE)
cov_wald <- coverage_run(FALSE)

se_binom <- sqrt(0.95 * 0.05 / N_REP)
band     <- 3 * se_binom

message(sprintf("  replications          %d, k = 8 per replication", N_REP))
message(sprintf("  coverage with HKSJ    %.3f", cov_hksj))
message(sprintf("  coverage without HKSJ %.3f", cov_wald))
message(sprintf("  binomial SE %.4f, acceptance band 0.95 +/- %.4f",
                se_binom, band))

if (abs(cov_hksj - 0.95) > band) {
  fail(sprintf("HKSJ coverage %.3f is outside the acceptance band", cov_hksj))
}
ok("HKSJ coverage is at nominal within Monte Carlo error")

# This is the empirical justification for the protocol's choice to apply HKSJ
# below k = 10. If the uncorrected interval is not anticonservative here, the
# rule is unmotivated and should be revisited rather than retained.
message(sprintf("  undercoverage without the correction: %.3f",
                cov_hksj - cov_wald))
if (cov_wald >= cov_hksj) {
  message("  NOTE: no undercoverage observed; the HKSJ rule is unmotivated",
          " at this k and sample size and should be re-examined.")
} else {
  ok("uncorrected interval undercovers, as the protocol's HKSJ rule assumes")
}


###############################################################################
# TEST 3. Is the composite invariant to biomarker coverage?
#
# This is the load bearing test of the whole design. The triple agonist node is
# expected to carry about seven measured biomarkers against sixteen for GLP-1
# mono. If the composite grows with the number of biomarkers measured, then a
# coverage difference would masquerade as a biological difference, and every
# class comparison in the paper would be an artifact.
#
# Two classes are constructed with IDENTICAL per biomarker effects and
# IDENTICAL precision. One is measured on 16 biomarkers, the other on 7. A
# correct weighted mean returns the same score for both. A weighted sum, which
# is the error this protocol explicitly rules out, returns roughly twice as
# much for the broader panel.
###############################################################################

message("\nTEST 3  Composite invariance to biomarker coverage")

make_class <- function(n_markers, effect, se) {
  tibble(
    biomarker      = sprintf("bm%02d", seq_len(n_markers)),
    estimate       = effect,
    se             = se,
    receptor_class = "X"
  )
}

EFFECT <- 0.30
SE     <- 0.08

wide   <- make_class(16, EFFECT, SE)
narrow <- make_class(7,  EFFECT, SE)

# compute_nbais joins direction and clinical weight from `dat`, so a minimal
# `dat` is supplied here covering exactly these biomarkers.
dat <- tibble(
  biomarker       = sprintf("bm%02d", seq_len(16)),
  aging_direction = 1,
  clinical_weight = 1
)

s_wide   <- compute_nbais(wide,   "inverse_variance")
s_narrow <- compute_nbais(narrow, "inverse_variance")

# The weighted sum the protocol rejects, computed here for contrast.
sum_wide   <- sum(1 * wide$estimate   * (1 / wide$se^2))
sum_narrow <- sum(1 * narrow$estimate * (1 / narrow$se^2))

message(sprintf("  per biomarker effect  %.3f, identical in both classes", EFFECT))
message(sprintf("  weighted MEAN, 16 biomarkers   %.6f", s_wide))
message(sprintf("  weighted MEAN,  7 biomarkers   %.6f", s_narrow))
message(sprintf("  difference                     %.2e", abs(s_wide - s_narrow)))
message(sprintf("  weighted SUM,  16 biomarkers   %.2f", sum_wide))
message(sprintf("  weighted SUM,   7 biomarkers   %.2f", sum_narrow))
message(sprintf("  sum inflation factor           %.2f x",
                sum_wide / sum_narrow))

if (abs(s_wide - s_narrow) > 1e-9) {
  fail("composite is NOT invariant to biomarker coverage")
}
ok("composite identical across 16 and 7 biomarker panels")

if (abs(s_wide - EFFECT) > 1e-9) {
  fail(sprintf("composite %.6f does not equal the per biomarker effect %.3f",
               s_wide, EFFECT))
}
ok("composite equals the per biomarker effect, so it stays on the g scale")

if (sum_wide / sum_narrow < 2) {
  fail("the rejected weighted sum did not inflate, so this test is vacuous")
}
ok(sprintf("the rejected weighted sum would have inflated %.2f fold",
           sum_wide / sum_narrow))


###############################################################################
# TEST 4. Does the composite handle the unfavorable axis correctly?
#
# Lean mass is the one domain moving the wrong way. A class improving fifteen
# biomarkers and losing lean mass must not be scored as though all sixteen
# improved. The direction indicator is what prevents this, and here it is
# checked rather than assumed.
###############################################################################

message("\nTEST 4  Direction handling for the unfavorable axis")

mixed <- tibble(
  biomarker      = c("hsCRP", "adiponectin", "lean_mass"),
  estimate       = c(-0.40,    0.30,          -0.50),
  se             = c( 0.08,    0.08,           0.08),
  receptor_class = "X"
)

dat <- tibble(
  biomarker       = c("hsCRP", "adiponectin", "lean_mass"),
  aging_direction = c(-1,       1,             1),
  clinical_weight = 1
)

score_mixed <- compute_nbais(mixed, "inverse_variance")

# By hand: hsCRP -1*-0.40 = +0.40 favorable; adiponectin +1*+0.30 = +0.30
# favorable; lean mass +1*-0.50 = -0.50 unfavorable. Equal SEs, equal weights.
expected <- (0.40 + 0.30 - 0.50) / 3

message("  hsCRP       fell, lower is better   -> +0.40")
message("  adiponectin rose, higher is better  -> +0.30")
message("  lean_mass   fell, higher is better  -> -0.50")
message(sprintf("  composite            %.6f", score_mixed))
message(sprintf("  expected by hand     %.6f", expected))

if (abs(score_mixed - expected) > 1e-9) {
  fail("composite does not match the hand calculation")
}
ok("composite matches the hand calculation exactly")

# The decisive assertions. A favorable change must contribute positively
# whichever way it moves on the biomarker's own scale. Under the inverted
# convention this review shipped with until 2026-10-15, the first of these
# two was negative, and no test caught it because every biomarker extracted
# up to that point was lower-is-better, making the inversion uniform.
fell_good <- compute_nbais(
  tibble(biomarker = "hsCRP", estimate = -0.40, se = 0.08, receptor_class = "X"),
  "inverse_variance")
rose_good <- compute_nbais(
  tibble(biomarker = "adiponectin", estimate = 0.30, se = 0.08, receptor_class = "X"),
  "inverse_variance")

message(sprintf("\n  lower-is-better marker falling   %+.3f", fell_good))
message(sprintf("  higher-is-better marker rising   %+.3f", rose_good))

if (fell_good <= 0) {
  fail("a lower-is-better biomarker that FELL scored as unfavorable; ",
       "the direction convention is inverted")
}
ok("a lower-is-better biomarker that fell scores favorably")

if (rose_good <= 0) {
  fail("a higher-is-better biomarker that ROSE scored as unfavorable; ",
       "the direction convention is inverted")
}
ok("a higher-is-better biomarker that rose scores favorably")

# A large enough unfavorable axis must be able to drag the composite negative.
# If it cannot, the metric cannot express the clinical concern that motivates it.
dominant <- tibble(
  biomarker      = c("hsCRP", "adiponectin", "lean_mass"),
  estimate       = c(-0.10,    0.10,          -2.00),
  se             = c( 0.08,    0.08,           0.08),
  receptor_class = "X"
)
score_dom <- compute_nbais(dominant, "inverse_variance")
message(sprintf("  with a dominant unfavorable axis   %.6f", score_dom))
if (score_dom >= 0) {
  fail("a dominant unfavorable axis did not drive the composite negative")
}
ok("a dominant unfavorable axis drives the composite negative")


###############################################################################
# TEST 5. Does the weight adjusted meta-regression separate a receptor effect
# from a weight effect?
#
# Two scenarios are simulated. In the first, the biomarker responds only to
# weight loss and the receptor class has no independent effect. In the second,
# the receptor class has a real effect on top of weight loss. The model must
# distinguish them. If it cannot, the central claim of the paper is not
# testable by this method.
###############################################################################

message("\nTEST 5  Separating a receptor effect from a weight effect")

simulate_metareg <- function(class_effect, k_per_class = 10) {
  purrr::map_dfr(c("GLP1_mono", "GLP1_GCGR"), function(rc) {
    bonus <- if (rc == "GLP1_GCGR") class_effect else 0
    wt    <- runif(k_per_class, -25, -5)      # percentage weight change
    # Biomarker responds to weight loss, plus the class bonus, plus noise.
    yi_true <- 0.04 * (-wt) + bonus
    se      <- runif(k_per_class, 0.08, 0.16)
    tibble(
      receptor_class    = rc,
      pct_weight_change = wt,
      yi                = rnorm(k_per_class, yi_true, se),
      vi                = se^2
    )
  }) |>
    # The pipeline sets these levels explicitly. Without that, R orders levels
    # alphabetically, which puts GLP1_GCGR before GLP1_mono and makes the GCGR
    # class the reference. Every class coefficient then estimates the contrast
    # in the opposite direction and flips sign. This line is load bearing, not
    # cosmetic, and the assertion below pins it.
    dplyr::mutate(receptor_class = factor(receptor_class,
                                          levels = RECEPTOR_CLASSES))
}

run_adj <- function(d) {
  m <- metafor::rma(yi, vi, mods = ~ receptor_class + pct_weight_change,
                    data = d, method = "REML")
  cls_row <- grep("receptor_class", rownames(m$b))
  # Confirm the contrast being read is the one intended. A silently reordered
  # reference level produces a correct magnitude with an inverted sign, which
  # is the most dangerous class of error here because nothing looks wrong.
  cls_name <- rownames(m$b)[cls_row]
  if (!grepl("GCGR", cls_name)) {
    fail("reference level is not GLP1_mono; coefficient is ", cls_name)
  }
  list(beta_class = as.numeric(m$b[cls_row, ]),
       p_class    = m$pval[cls_row],
       beta_wt    = as.numeric(m$b["pct_weight_change", ]),
       cls_name   = cls_name)
}

null_case <- run_adj(simulate_metareg(class_effect = 0.00))
real_case <- run_adj(simulate_metareg(class_effect = 0.35))

message("  scenario A, no independent receptor effect (truth 0.00)")
message(sprintf("    class coefficient %.3f, p = %.3f",
                null_case$beta_class, null_case$p_class))
message(sprintf("    weight slope      %.4f  (true 0.0400)", -null_case$beta_wt))

message("  scenario B, real receptor effect (truth 0.35)")
message(sprintf("    class coefficient %.3f, p = %.4f",
                real_case$beta_class, real_case$p_class))
message(sprintf("    weight slope      %.4f  (true 0.0400)", -real_case$beta_wt))

if (null_case$p_class < 0.05) {
  fail("the model found a receptor effect where the truth is zero")
}
ok("no spurious receptor effect when the truth is zero")

if (real_case$p_class > 0.05) {
  fail("the model missed a real receptor effect of 0.35")
}
ok("real receptor effect of 0.35 detected after adjusting for weight")

if (abs(real_case$beta_class - 0.35) > 0.15) {
  fail(sprintf("recovered class effect %.3f is far from the truth 0.35",
               real_case$beta_class))
}
ok("class effect magnitude recovered within 0.15")

message("\nAll validation tests passed.")
message("These values validate the pipeline. They are not findings about any drug.")
