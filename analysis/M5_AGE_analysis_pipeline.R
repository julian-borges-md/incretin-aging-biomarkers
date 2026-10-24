###############################################################################
# Aging Biomarker Signatures of Incretin and Glucagon Receptor Agonism
# Complete Reproducible Analysis Pipeline
#
# Author:  Julian Borges, MD, MS
#          Department of Computer Science, Boston University
#          jyborges@bu.edu | ORCID 0009-0001-9929-3135
#
# Version: 1.0
# Date:    2026-10-14
#
# REPRODUCIBILITY CONTRACT
# -------------------------
# This script is the sole source of every numerical result reported in the
# manuscript. No value appears in the text, a table, or a figure that is not
# produced by a line of code below. Running this script end to end against
# analysis/data/extraction_master.csv regenerates every result, table and
# figure.
#
# The package set is installed by `make install` (requirements.R). The exact version of every
# package a run used, with the R version and platform, is recorded by `make pin` in
# analysis/output/environment_pinned.csv. To reproduce:
#   make install
#   Rscript analysis/M5_AGE_analysis_pipeline.R
# (Corrected 24 October 2026: this header said the environment was pinned with renv and to run
# renv::restore(); no renv lockfile has ever existed in this repository, see requirements.R.)
#
# Run from the repository root. All stochastic operations use set.seed(20261013).
###############################################################################

## ---------------------------------------------------------------------------
## 0. ENVIRONMENT
## ---------------------------------------------------------------------------

set.seed(20261013)

# Every warning the run raises is recorded (added 24 October 2026). The run printed 34 and then 35
# warnings until 23 October and one until 24 October, and each time the warning that mattered, a
# figure dropping two arms or a table read short, was one line among the others. The warnings are
# written to analysis/output/run_warnings.csv before the manifest, and src/verify.R gate 5 requires
# that table to be empty, so a warning reaches CI as a failure instead of scrolling past. A warning
# that is understood and accepted is handled where it arises, with the reason beside it.
RUN_WARNINGS <- character(0)
globalCallingHandlers(warning = function(w) {
  RUN_WARNINGS <<- c(RUN_WARNINGS, conditionMessage(w))
})

required_packages <- c(
  "metafor",      # >= 4.6.0  core meta-analysis and meta-regression
  "netmeta",      # >= 3.0.0  frequentist network meta-analysis
  "meta",         # >= 7.0.0  convenience wrappers, funnel plots
  "dmetar",       # >= 0.1.0  influence diagnostics
  "tidyverse",    # >= 2.0.0  data manipulation
  "boot",         # >= 1.3    bootstrap for the composite metric
  "ggplot2",      # >= 3.5.0  figures
  "ragg",         # >= 1.3    raster figure device that does not depend on cairo or X11
  "patchwork",    # >= 1.2.0  multi-panel figure assembly
  "knitr",        # >= 1.45   table rendering
  "openssl",      # >= 2.2    SHA-256 for the output manifest
  "sessioninfo"   # >= 1.2    environment capture
)

invisible(lapply(required_packages, function(p) {
  if (!requireNamespace(p, quietly = TRUE)) {
    stop(sprintf(paste("Package '%s' is required. Run make install; the versions the reference",
                       "run used are in analysis/output/environment_pinned.csv."), p))
  }
  library(p, character.only = TRUE)
}))

# The packages figure style 2 draws with (section 10 and analysis/figure_style.R), checked here so
# that a missing one stops the run before twenty minutes of computation rather than at the first
# figure. They are called with :: and not attached, so nothing computed before section 10 runs on a
# different search path.
figure_packages <- c(
  "showtext",     # >= 0.9    glyphs drawn as outlines in the PDF
  "sysfonts",     # >= 0.8    registers the vendored typeface for showtext
  "systemfonts",  # >= 1.1    registers the vendored typeface for ragg
  "scales"        # >= 1.3    true minus signs and percent labels on the axes
)
figure_missing <- figure_packages[!vapply(figure_packages, requireNamespace, logical(1),
                                          quietly = TRUE)]
if (length(figure_missing) > 0) {
  stop("Package(s) required for the figures: ", paste(figure_missing, collapse = ", "),
       ". Run make install.", call. = FALSE)
}

# Ported 2026-10-16 from the arm level master to the harmonised one, resolving the divergence
# recorded in docs/PIPELINE_DIVERGENCE_2026-10-15.md as option A. The reason is in that document and
# in docs/LESSONS.md: this literature reports between group contrasts with intervals, not arm level
# means and standard deviations, so the standardised mean difference this pipeline was written around
# cannot be computed for most rows. The harmonised master carries the analysis ready quantity,
# yi_pct and vi_pct on the percent change scale, for 486 of the 524 rows.
#
# This port does not change the analysis the manuscript reports. The gate scripts have been pooling
# percent change since the schema correction, and every number in the Results already comes from that
# scale. What the port changes is that there is now ONE implementation rather than two, and the
# prespecified features the gate scripts never implemented, the permutation meta regression, the
# bias corrected and accelerated composite intervals, the estimator sweep, the influence diagnostics
# and the output manifest, run on the real data instead of on a pipeline that could not start.
#
# The departure from the registered plan is the pooling scale, percent change rather than Hedges' g.
# That departure is already present in the reported numbers and is a protocol deviation for the
# Director to approve and the manuscript to disclose; it is not introduced here.
DATA_FILE <- "analysis/data/extraction_master_harmonised.csv"
OUT_DIR   <- "analysis/output"

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

# Capture the exact environment into the output directory for the reviewer.
writeLines(capture.output(sessioninfo::session_info()),
           file.path(OUT_DIR, "session_info.txt"))


## ---------------------------------------------------------------------------
## 1. DATA INGESTION AND INTEGRITY CHECKS
## ---------------------------------------------------------------------------
# The extraction file holds one row per trial-arm-outcome triplet. Integrity
# checks run before any analysis so that a malformed extraction fails loudly
# rather than producing a plausible but wrong pooled estimate.

RECEPTOR_CLASSES <- c("GLP1_mono", "GLP1_GIP", "GLP1_GCGR", "GLP1_GIP_GCGR")

# The outcome_type values that pool on the continuous scale. The schema grew two further values
# after this pipeline was written, "contrast" for a row carrying a published between group effect
# and "arm_means" for one carrying both arms, and both pool exactly as "continuous" does once the
# harmonisation layer has put them on one scale. Naming the set here rather than testing equality
# against "continuous" is what keeps a schema addition from silently dropping rows: the earlier
# equality test would have pooled 453 rows and ignored 68 without saying so.
CONTINUOUS_TYPES <- c("continuous", "contrast", "arm_means")

check_integrity <- function(d) {
  errs <- character(0)

  # Every trial must carry a valid receptor class.
  bad_class <- setdiff(unique(d$receptor_class), RECEPTOR_CLASSES)
  if (length(bad_class)) {
    errs <- c(errs, sprintf("Unknown receptor_class: %s",
                            paste(bad_class, collapse = ", ")))
  }

  # Continuous outcomes need an effect and a variance on the percent change scale. The original
  # rule required arm level mean, SD and n in both arms, which the standardised mean difference
  # needs but this literature does not report: 392 of the 453 continuous rows failed it, which is
  # what stopped this pipeline. The rule now matches what the analysis actually consumes, which is
  # the principle build_master.R adopted on 2026-10-15, require only what the analysis needs where
  # it needs it. Rows without a convertible effect are not an integrity failure; they are the
  # documented 38 row limitation and are dropped at the effect size step with a count.
  cont <- dplyr::filter(d, outcome_type %in% CONTINUOUS_TYPES)
  if (!all(c("yi_pct", "vi_pct") %in% names(d))) {
    errs <- c(errs, "Harmonised columns yi_pct and vi_pct are absent: run src/harmonise_units.R.")
  } else {
    usable <- dplyr::filter(cont, !is.na(yi_pct), !is.na(vi_pct))
    if (nrow(usable) == 0) {
      errs <- c(errs, "No continuous row carries both yi_pct and vi_pct.")
    }
    # A non-positive variance silently produces an infinite weight, so it is caught here.
    if (any(usable$vi_pct <= 0, na.rm = TRUE)) {
      errs <- c(errs, "Non-positive variance present on the percent change scale.")
    }
  }

  # Every biomarker needs a declared aging direction for the composite.
  if (any(!d$aging_direction %in% c(1, -1))) {
    errs <- c(errs, "aging_direction must be exactly +1 or -1.")
  }

  # Weight change is the meta regression covariate, so it is required where that regression runs and
  # not on every row of the corpus. The original rule failed the whole pipeline when any row lacked
  # it, which is the same over-requirement as above: a trial reporting a biomarker but no weight
  # change is a trial the weight adjusted analysis excludes, not a corrupt record. The count is
  # reported so the exclusion is visible, and the regression itself filters and states its own n.
  n_no_weight <- sum(is.na(d$pct_weight_change))
  if (n_no_weight == nrow(d)) {
    errs <- c(errs, "pct_weight_change is missing on every row: the covariate is absent.")
  } else if (n_no_weight > 0) {
    message(sprintf(paste0("  note: %d of %d rows carry no pct_weight_change and are excluded ",
                           "from the weight adjusted meta regression only."),
                    n_no_weight, nrow(d)))
  }

  if (length(errs)) stop(paste(c("EXTRACTION INTEGRITY FAILURE:", errs),
                               collapse = "\n  "))
  invisible(TRUE)
}

if (!file.exists(DATA_FILE)) {
  stop("Extraction file not found: ", DATA_FILE,
       "\n  Extraction is not complete. See docs/RUNBOOK.md.")
}

dat <- readr::read_csv(DATA_FILE, show_col_types = FALSE)
check_integrity(dat)
dat$receptor_class <- factor(dat$receptor_class, levels = RECEPTOR_CLASSES)


## ---------------------------------------------------------------------------
## 2. EFFECT SIZE COMPUTATION
## ---------------------------------------------------------------------------
# SUPERSEDED, retained as the registered description. The plan read: continuous outcomes use
# Hedges' g, the standardized mean difference with the small sample correction applied, because
# biomarker measurement scales differ across trials: hsCRP in mg/L, GDF-15 in pg/mL, lean mass in
# kg. Where every trial for a biomarker uses an identical scale the raw mean difference is also
# computed and reported alongside, since it is more interpretable clinically. The second half of
# that rule stands and is implemented below as yi_md. The first half does not: the pooling scale
# is percent change, for the reason given in the next paragraph and declared as a protocol
# deviation at the top of this file. The paragraph is kept rather than deleted so that the
# registered wording and its replacement sit side by side, and so that no reader of this file can
# conclude that g was pooled.
#
# Binary outcomes, meaning MASH resolution and fibrosis improvement, use the
# log odds ratio, which is the appropriate scale for pooling proportions and is
# back transformed for presentation.

# The effect size is read from the harmonisation layer rather than recomputed here. escalc with
# measure "SMD" needs m1i, sd1i, n1i and their comparator counterparts; those are present on 160 of
# the 524 rows and complete on fewer, because the trials in this corpus publish a between group
# contrast with an interval. src/harmonise_units.R already converts each row's native effect to the
# percent change scale by its declared route and records which route it used, so recomputing here
# would either reproduce that work or disagree with it. Reading it keeps one definition.
#
# yi is therefore a percent change in the biomarker, not a standardised mean difference, and vi its
# variance on that scale. Every downstream function in this pipeline takes a frame of yi and vi and
# is indifferent to which scale they are on; what changes is the interpretation of the pooled number,
# which is the protocol deviation named at the top of this file.
es_continuous <- dplyr::filter(dat, outcome_type %in% CONTINUOUS_TYPES,
                               !is.na(yi_pct), !is.na(vi_pct), vi_pct > 0)
n_dropped <- sum(dat$outcome_type %in% CONTINUOUS_TYPES) - nrow(es_continuous)
message(sprintf(paste0("  effect sizes: %d continuous rows on the percent change scale, ",
                       "%d dropped for lacking a convertible effect"),
                nrow(es_continuous), n_dropped))
# The raw mean difference is retained where the row's native scale was already absolute, which is
# the only case in which it means the same thing across trials of one biomarker. It is taken from
# the native columns BEFORE yi is overwritten below, since the native effect lives in yi itself.
es_continuous$yi_md <- ifelse(es_continuous$unit_family == "absolute", es_continuous$yi, NA)
es_continuous$vi_md <- ifelse(es_continuous$unit_family == "absolute",
                              es_continuous$se_native^2, NA)
es_continuous$yi <- es_continuous$yi_pct
es_continuous$vi <- es_continuous$vi_pct

# Collapse to one arm per trial per biomarker, keeping the highest dose. Several trials contribute
# multiple dose arms against a single shared control, and pooling those as independent studies
# overstates precision: the first run of this port pooled 18 liver fat rows where the analysis pools
# 9, 44 HbA1c rows where it pools 38, and every interval came out too narrow. The rule and its
# justification are defined in src/pool_biomarkers.R, decision 1, which is the operational analysis;
# this is the same rule applied here so that the two implementations pool the same rows. It is NOT a
# second definition on purpose, and consolidating the two into one shared step is the remaining work
# on this port, because a rule stated twice is the defect that has bitten this repository three times.
#
# This rule is absent from the registered plan, which assumed one contrast per trial. It is a real
# analytic decision, it is visible in the pooled k of every biomarker, and it needs to be disclosed
# in the Methods rather than left implicit in a script.
n_before <- nrow(es_continuous)
es_continuous <- es_continuous |>
  dplyr::group_by(trial_id, biomarker) |>
  dplyr::slice_max(order_by = dose_mg, n = 1, with_ties = FALSE) |>
  dplyr::ungroup()
message(sprintf(paste0("  shared control collapse: %d rows kept, %d dose arms dropped ",
                       "(one arm per trial per biomarker, highest dose)"),
                nrow(es_continuous), n_before - nrow(es_continuous)))

es_binary <- metafor::escalc(
  measure = "OR",
  ai = events_tx,   n1i = n_tx,
  ci = events_ctrl, n2i = n_ctrl,
  data = dplyr::filter(dat, outcome_type == "binary"),
  slab = trial_id,
  add = 0.5, to = "only0"   # continuity correction applied only to zero cells
)


## ---------------------------------------------------------------------------
## 3. PRIMARY POOLING FUNCTION
## ---------------------------------------------------------------------------
# Every pooled estimate in the manuscript is produced by this single function,
# so the estimator, the small sample correction and the reported diagnostics
# are identical everywhere.
#
# The prediction interval is returned alongside the confidence interval and is
# mandatory in this analysis. A confidence interval describes uncertainty about
# the location of the mean true effect across the population of trials. A
# prediction interval describes the range within which the true effect of a new
# trial is expected to fall. Under non-negligible heterogeneity these can lead
# to opposite conclusions, and the second is the quantity a clinician needs.

pool_effect <- function(es_df, estimator = "REML", use_hksj = NULL) {

  k <- nrow(es_df)
  if (k < 2) return(NULL)

  # The Hartung-Knapp-Sidik-Jonkman adjustment widens the confidence interval
  # to account for uncertainty in the estimate of between-study variance. It is
  # applied by default when fewer than 10 trials contribute, where the standard
  # normal approximation is known to be anticonservative.
  if (is.null(use_hksj)) use_hksj <- (k < 10)

  fit <- metafor::rma(
    yi = es_df$yi,
    vi = es_df$vi,
    method = estimator,
    test = if (use_hksj) "knha" else "z"
  )

  pred <- predict(fit)

  # A prediction interval needs tau to be estimable, which takes at least three studies. metafor
  # will return one from two, where it is an interval around a between study variance estimated from
  # a single degree of freedom and means nothing a reader should act on. Suppressed below k = 3, the
  # rule src/pool_biomarkers.R states as decision 3; without this the port disagreed with the
  # analysis on exactly the two biomarkers that have two trials, body fat percentage and lean mass.
  pi_estimable <- k >= 3

  tibble::tibble(
    k         = k,
    n_total   = sum(es_df$n_tx, es_df$n_ctrl, na.rm = TRUE),
    estimate  = as.numeric(fit$b),
    se        = fit$se,
    ci_lb     = fit$ci.lb,
    ci_ub     = fit$ci.ub,
    pi_lb     = if (pi_estimable) pred$pi.lb else NA_real_,
    pi_ub     = if (pi_estimable) pred$pi.ub else NA_real_,
    p_value   = fit$pval,
    tau2      = fit$tau2,
    tau2_se   = fit$se.tau2,
    I2        = fit$I2,
    H2        = fit$H2,
    Q         = fit$QE,
    Q_df      = fit$k - 1,
    Q_p       = fit$QEp,
    estimator = estimator,
    hksj      = use_hksj
  )
}


## ---------------------------------------------------------------------------
## 4. PRIMARY ANALYSIS: BIOMARKER BY RECEPTOR CLASS
## ---------------------------------------------------------------------------
# For each aging biomarker, pool separately within each receptor class. This
# produces the master results table and the input to the signature heatmap and
# the composite score.

biomarkers <- unique(es_continuous$biomarker)

primary_results <- purrr::map_dfr(biomarkers, function(bm) {
  purrr::map_dfr(RECEPTOR_CLASSES, function(rc) {
    subset_df <- dplyr::filter(es_continuous,
                               biomarker == bm, receptor_class == rc)
    res <- pool_effect(subset_df)
    if (is.null(res)) return(NULL)
    dplyr::mutate(res, biomarker = bm, receptor_class = rc, .before = 1)
  })
})

readr::write_csv(primary_results, file.path(OUT_DIR, "table3_primary_results.csv"))

# Table 2 is the overall pooling per biomarker, across receptor classes, and is what the manuscript
# reports as the primary result; the class stratified Table 3 above is the receptor class signature.
# This pipeline produced only the stratified table, which is why the gate scripts grew their own
# pooling and the two implementations diverged. Producing both here, from the one pool_effect, is
# what allows the port to be checked rather than asserted: table2_pipeline.csv must reproduce the
# gate scripts' table2_pooled_by_biomarker.csv to the last decimal, and
# src/table2_reproduction_check.py is the comparison.
table2_pipeline <- purrr::map_dfr(biomarkers, function(bm) {
  res <- pool_effect(dplyr::filter(es_continuous, biomarker == bm))
  if (is.null(res)) return(NULL)
  dplyr::mutate(res, biomarker = bm, .before = 1)
})
readr::write_csv(table2_pipeline, file.path(OUT_DIR, "table2_pipeline.csv"))


## ---------------------------------------------------------------------------
## 5. WEIGHT-ADJUSTED META-REGRESSION
## ---------------------------------------------------------------------------
# This is the inferential core. The question is whether receptor class predicts
# an aging biomarker change after the degree of weight loss is accounted for.
#
# Three constraints govern interpretation and are implemented here rather than
# only described in the manuscript.
#
# First, this is an aggregate level regression. An association between trial
# mean weight loss and trial mean biomarker change describes trials, not
# patients. The ecological fallacy is a genuine threat and conclusions are
# framed about drug classes only.
#
# Second, the number of trials per biomarker is small relative to the number of
# moderators, so Wald inference is anticonservative. All reported p values come
# from permutation tests under a fixed seed.
#
# Third, adjusting for weight introduces overadjustment if weight loss lies on
# the causal path. Both unadjusted and adjusted coefficients are returned so the
# attenuation is visible, and the adjusted estimate is read as a conservative
# lower bound on the total receptor class effect.

# Fisher scoring for restricted maximum likelihood does not always converge on a moderator model.
# It failed here on the second biomarker of the loop the first time this pipeline ever executed,
# which stopped the whole weight adjusted analysis, because models one to three carried no error
# handling and one non convergence therefore destroyed the inferential core rather than one row of
# it. Wrapping every fit in tryCatch and moving on would be worse: it would drop biomarkers from
# the analysis silently.
#
# So the fallback is explicit, ordered, and recorded. It first retries the prespecified estimator
# with a halved step size and a raised iteration cap, which is a numerical remedy and not a change
# of method. Only if that fails does it fall back to Paule and Mandel and then DerSimonian and
# Laird, both of which the protocol already names as sensitivity estimators, so a fallback stays
# inside the registered plan. The estimator actually used is returned on the fit and reported per
# biomarker, so the manuscript can state where the primary estimator did not converge instead of
# presenting a mixture as though it were uniform. A biomarker on which none converge is reported
# with that status, never omitted.
ESTIMATOR_ATTEMPTS <- list(
  list(method = "REML", control = list(),                            label = "REML"),
  list(method = "REML", control = list(stepadj = 0.5, maxiter = 1000), label = "REML (stepadj 0.5)"),
  list(method = "PM",   control = list(),                            label = "PM fallback"),
  list(method = "DL",   control = list(),                            label = "DL fallback")
)

fit_rma <- function(formula_mods, data) {
  for (a in ESTIMATOR_ATTEMPTS) {
    fit <- tryCatch(
      suppressWarnings(
        if (is.null(formula_mods)) {
          metafor::rma(yi = data$yi, vi = data$vi, method = a$method, control = a$control)
        } else {
          metafor::rma(yi = data$yi, vi = data$vi, mods = formula_mods, data = data,
                       method = a$method, control = a$control)
        }
      ),
      error = function(e) NULL
    )
    if (!is.null(fit)) {
      attr(fit, "estimator_used") <- a$label
      return(fit)
    }
  }
  NULL
}


run_weight_adjusted_metareg <- function(bm, n_perm = 10000) {

  d <- dplyr::filter(es_continuous, biomarker == bm)
  # The covariate is required by this model and not by the review, so rows without it are dropped
  # here with the count carried into the output rather than silently.
  n_all <- nrow(d)
  d <- dplyr::filter(d, !is.na(pct_weight_change))
  n_no_cov <- n_all - nrow(d)

  # Require the number of trials to exceed the estimated parameters by at least
  # three, otherwise the model is not identifiable and a fit would be spurious.
  n_levels <- length(unique(d$receptor_class))
  if (nrow(d) < (n_levels + 3)) {
    return(tibble::tibble(biomarker = bm,
                          status = "insufficient_trials",
                          k = nrow(d)))
  }

  # Model 1: weight loss alone. How much heterogeneity weight explains on its own.
  m_weight <- fit_rma(~ pct_weight_change, d)

  # Model 2: receptor class alone, unadjusted.
  m_class <- fit_rma(~ receptor_class, d)

  # Model 3: both. The receptor class coefficients here are the adjusted
  # estimates reported in the manuscript.
  m_adj <- fit_rma(~ receptor_class + pct_weight_change, d)

  if (is.null(m_weight) || is.null(m_class) || is.null(m_adj)) {
    return(tibble::tibble(
      biomarker = bm,
      status = "no_estimator_converged",
      k = nrow(d),
      n_dropped_no_covariate = n_no_cov
    ))
  }

  # Model 4: interaction. Tests whether the slope relating weight loss to the
  # biomarker differs by receptor class, which would mean the same amount of
  # weight loss buys different biomarker benefit depending on receptors engaged.
  m_int <- fit_rma(~ receptor_class * pct_weight_change, d)

  perm_adj <- tryCatch(metafor::permutest(m_adj, iter = n_perm, seed = 20261013),
                       error = function(e) NULL)
  # The weight only model gets its own permutation test so that the unadjusted weight coefficient
  # can be reported with the inference the protocol requires rather than with a Wald p value. Until
  # 22 October only the adjusted coefficient was written out, under the name beta_weight, directly
  # beside R2_weight_only; a reader comparing the two would have read the adjusted slope as the
  # slope of the weight only model whose R2 sits next to it. For liver fat those two quantities
  # have opposite signs, which is the discrepancy decision A2 turns on, so both are now named and
  # both are reported.
  perm_weight <- tryCatch(metafor::permutest(m_weight, iter = n_perm, seed = 20261013),
                          error = function(e) NULL)

  # Proportion of between-study variance explained, relative to intercept only.
  m_null <- fit_rma(NULL, d)
  if (is.null(m_null)) {
    return(tibble::tibble(biomarker = bm, status = "no_estimator_converged_null",
                          k = nrow(d), n_dropped_no_covariate = n_no_cov))
  }
  r2_adj <- max(0, (m_null$tau2 - m_adj$tau2) / m_null$tau2) * 100

  tibble::tibble(
    biomarker          = bm,
    status             = "fitted",
    k                  = nrow(d),
    tau2_null          = m_null$tau2,
    tau2_weight_only   = m_weight$tau2,
    tau2_class_only    = m_class$tau2,
    tau2_adjusted      = m_adj$tau2,
    R2_weight_only     = max(0, (m_null$tau2 - m_weight$tau2) / m_null$tau2) * 100,
    # The weight coefficient of the weight only model, which is the model R2_weight_only measures.
    beta_weight_unadjusted = as.numeric(m_weight$b["pct_weight_change", ]),
    se_weight_unadjusted   = m_weight$se[which(rownames(m_weight$b) == "pct_weight_change")],
    p_weight_perm_unadjusted = if (!is.null(perm_weight))
                                 perm_weight$pval[
                                   which(rownames(m_weight$b) == "pct_weight_change")]
                               else NA_real_,
    R2_class_only      = max(0, (m_null$tau2 - m_class$tau2) / m_null$tau2) * 100,
    R2_adjusted        = r2_adj,
    # The weight coefficient of the adjusted model, which is the model R2_adjusted measures and
    # the model whose receptor class coefficients the manuscript reports. These three columns were
    # named beta_weight, se_weight and p_weight_perm until 22 October; the names carried no model.
    beta_weight_adjusted = as.numeric(m_adj$b["pct_weight_change", ]),
    se_weight_adjusted   = m_adj$se[which(rownames(m_adj$b) == "pct_weight_change")],
    # Permutation inference is the protocol's reported p value. Where the permutation test itself
    # cannot run, the field is left empty rather than quietly filled with the Wald p value, which
    # the plan rejects as anticonservative at these sample sizes.
    p_weight_perm_adjusted = if (!is.null(perm_adj))
                               perm_adj$pval[which(rownames(m_adj$b) == "pct_weight_change")]
                             else NA_real_,
    QM_adjusted        = m_adj$QM,
    QM_p_perm          = if (!is.null(perm_adj)) perm_adj$QMp else NA_real_,
    permutation_run    = !is.null(perm_adj),
    permutation_run_weight_only = !is.null(perm_weight),
    I2_residual        = m_adj$I2,
    # The interaction model is only reported as fitted when its interaction terms SURVIVED. At these
    # sample sizes metafor routinely drops them as redundant and returns a model whose moderator
    # test is identical to the adjusted model's, and the first run did exactly that for liver fat:
    # QM_interaction equalled QM_adjusted to fifteen digits while QM_interaction_p read 4.3e-10
    # against a permutation p of 0.320 on the same statistic. Reported as it stood, that would have
    # become a claim of a highly significant weight by class interaction in the hepatic domain,
    # which is the opposite of what the data support. Survival is detected by coefficient count, and
    # the p value is the permutation p the protocol requires rather than the Wald p, which is
    # anticonservative at this k and is what produced the nine order of magnitude discrepancy.
    interaction_fitted = !is.null(m_int) && nrow(m_int$b) > nrow(m_adj$b),
    QM_interaction     = if (!is.null(m_int) && nrow(m_int$b) > nrow(m_adj$b))
                           m_int$QM else NA_real_,
    QM_interaction_p   = if (!is.null(m_int) && nrow(m_int$b) > nrow(m_adj$b)) {
                           pi <- tryCatch(metafor::permutest(m_int, iter = n_perm, seed = 20261013),
                                          error = function(e) NULL)
                           if (!is.null(pi)) pi$QMp else NA_real_
                         } else NA_real_,
    interaction_terms_dropped = !is.null(m_int) && nrow(m_int$b) == nrow(m_adj$b),
    # Which estimator actually produced the adjusted model, so that a fallback is disclosed per
    # biomarker instead of a mixture being presented as uniform REML.
    estimator_adjusted = attr(m_adj, "estimator_used"),
    estimator_null     = attr(m_null, "estimator_used"),
    n_dropped_no_covariate = n_no_cov
  )
}

metareg_results <- purrr::map_dfr(biomarkers, run_weight_adjusted_metareg)
readr::write_csv(metareg_results, file.path(OUT_DIR, "table4_metaregression.csv"))

# Hepatic biomarkers are the pre-specified primary target of this analysis.
hepatic_biomarkers <- c("liver_fat_pdff", "ALT", "AST",
                        "MASH_resolution", "fibrosis_improvement")
readr::write_csv(dplyr::filter(metareg_results, biomarker %in% hepatic_biomarkers),
                 file.path(OUT_DIR, "table4a_hepatic_metaregression.csv"))


## ---------------------------------------------------------------------------
## 6. NET BIOLOGICAL AGE IMPACT SCORE
## ---------------------------------------------------------------------------
# The score collapses the biomarker signature for a receptor class into a
# single signed number. For each biomarker the pooled standardized effect is
# multiplied by a direction indicator, and the products are combined as a
# WEIGHTED MEAN:
#
#   NBAIS = sum_k ( d_k * g_k * w_k ) / sum_k ( w_k )
#
# DEFINITION OF d_k, stated carefully because an earlier version of this
# comment was wrong in a way that inverted most of the score.
#
# d_k is THE SIGN THAT THE EFFECT g_k TAKES WHEN THE CHANGE IS FAVOURABLE.
# It is a property of the biomarker, fixed before any data are seen, and does
# not depend on what a trial actually found.
#
#   hsCRP, HOMA-IR, liver fat, resting heart rate   lower is better    d = -1
#   adiponectin, HOMA-beta, lean mass               HIGHER is better   d = +1
#
# The product d_k * g_k is then positive whenever the biomarker moved toward
# younger biological age, whichever way that is on its own scale. hsCRP
# falling by 0.38 contributes -1 * -0.38 = +0.38. Adiponectin rising by 0.31
# contributes +1 * +0.31 = +0.31. Lean mass falling by 0.50 contributes
# +1 * -0.50 = -0.50, correctly unfavourable.
#
# The error this replaces defined d_k as +1 when "a decrease corresponds to
# younger biological age", which produced a NEGATIVE product for every
# lower-is-better biomarker and so inverted the sign of most of the composite.
# It survived because every biomarker extracted up to that point was
# lower-is-better, making the inversion uniform and therefore invisible, until
# adiponectin became the first higher-is-better marker extracted.
# The division is deliberate. A weighted sum would grow mechanically with the
# number of biomarkers measured, so a receptor class studied with a broader
# panel would score higher purely as an artifact of measurement coverage rather
# than of biological effect. Dividing by the total weight keeps the score on the
# scale of a single pooled estimate regardless of how many biomarkers contribute,
# which is what makes classes with unequal coverage comparable. This matters
# concretely here: the triple agonist node carries far fewer measured
# biomarkers than the GLP-1 mono node.
#
# The score carries the units of the pooled estimates it averages, which in this pipeline is
# percent change in the biomarker relative to the comparator, not a standardised mean difference.
# A score of 8.5 therefore reads as an average favorable shift of 8.5 percent across the aging
# biomarkers measured for that class. The original comment here read "0.40 standard deviations",
# which belonged to the registered Hedges' g scale and was left behind by the scale deviation
# recorded at the top of this file; a score read on the wrong scale is wrong by a factor of
# roughly twenty in this corpus.

# AMENDMENT 2026-10-19, inclusion rule. This function averaged every biomarker that pooled within a
# class. prespecification/nbais_inclusion_rule.md, written on 15 October and before any composite was
# computed, names eleven markers and excludes ten of the twenty originally specified: glucagon as
# pharmacological target engagement rather than an aging process, derived indices that share inputs
# with markers already in the set, markers whose assumed favourable direction is contradicted by
# outcome evidence, and markers that restate adiposity. The rule states its own reason for existing:
# a composite over the unfiltered set "would have produced a number, and the number would have been
# uninterpretable. Worse, it would have been uninterpretable in ways that favour the review's
# hypothesis, because most of the defective markers are ones the drug moves strongly."
#
# The per class composite in this pipeline was computed over the unfiltered set: 28 markers for
# GLP-1 mono against the rule's eleven, including glucagon, which the rule excludes by name, and
# both HOMA indices, which share inputs with fasting insulin and fasting glucose, also included. The
# figure built from it would have presented exactly the quantity the prespecification forbids, under
# the name the prespecification gives the compliant one.
#
# The marker set is read from analysis/data/nbais_inclusion_set.csv, the single declaration of
# prespecification/nbais_inclusion_rule.md in the repository, which src/compute_composite.R reads
# from the same file. A rule stated twice is the defect that has bitten this repository three times,
# and this is the same rule. Between 19 and 22 October this pipeline parsed the literal vector out
# of src/compute_composite.R, which kept one declaration but made a statistical script depend on the
# source text of another; the data file is the end state that was recorded as a next action then and
# is now in place. The file carries each marker's hallmark domain, surrogacy grade and the reason it
# is retained, so the rule and its justification travel together and neither script restates either.

NBAIS_INCLUSION_SET <- "analysis/data/nbais_inclusion_set.csv"

read_included_markers <- function(path = NBAIS_INCLUSION_SET) {
  if (!file.exists(path)) {
    stop("the composite inclusion set is missing at ", path,
         "; the rule in prespecification/nbais_inclusion_rule.md is declared there and nowhere else",
         call. = FALSE)
  }
  tbl <- readr::read_csv(path, show_col_types = FALSE, progress = FALSE)
  # A row the parser cannot fit to the header is a defect of the declaration, not a warning to read
  # past: until 24 October 2026 two reasons held unquoted commas and were truncated this way, with a
  # warning and no stop. src/verify.R gate 4 checks the shape of every tracked table in CI as well.
  if (nrow(readr::problems(tbl)) > 0) {
    stop(path, " does not parse to its header (", nrow(readr::problems(tbl)), " problems, the ",
         "first at row ", readr::problems(tbl)$row[1], "); a field holding a comma is quoted",
         call. = FALSE)
  }
  if (!"biomarker" %in% names(tbl)) {
    stop(path, " has no biomarker column; the composite inclusion set must name its markers",
         call. = FALSE)
  }
  v <- as.character(tbl$biomarker)
  v <- v[!is.na(v) & nzchar(trimws(v))]
  if (length(v) < 2) {
    stop(path, " declares fewer than two markers; a composite over one marker is a single marker",
         call. = FALSE)
  }
  if (any(duplicated(v))) {
    stop(path, " names a marker twice: ", paste(unique(v[duplicated(v)]), collapse = ", "),
         call. = FALSE)
  }
  v
}

NBAIS_INCLUDED <- read_included_markers()
# The floor is the one this pipeline already uses for a composite comparison: nbais_contrast
# requires three shared biomarkers before it will report a difference. A mean of one or two markers
# is not a composite, and a bar drawn from one marker invites a comparison the data cannot support.
NBAIS_MIN_MARKERS <- 3L
message(sprintf("  composite inclusion rule: %d markers read from %s (%s)",
                length(NBAIS_INCLUDED), NBAIS_INCLUSION_SET,
                paste(NBAIS_INCLUDED, collapse = ", ")))

# The direction and clinical weight of each marker are properties of the marker, not of a
# resample, so they are joined once per frame rather than once per bootstrap replicate.
# compute_nbais performed the join itself until 22 October, which was correct and slow: with three
# weighting schemes, four receptor classes, six class pairs and 10 000 replicates for each of the
# percentile and BCa procedures, the join ran on the order of 1.8e5 times on a frame of at most
# eleven rows, and the composite section accounted for roughly eight of the twenty minutes of a
# full run. Hoisting it changes no arithmetic: the join is a lookup keyed on biomarker, and the
# duplicate guard below is what makes that claim checkable rather than assumed. Without the guard
# a marker carrying two aging_direction values in the harmonised data would silently duplicate
# rows inside a mean, which inflates the weight of that marker instead of failing.
NBAIS_WEIGHT_LOOKUP <- dplyr::distinct(dat, biomarker, aging_direction, clinical_weight)
if (any(duplicated(NBAIS_WEIGHT_LOOKUP$biomarker))) {
  stop("the harmonised data gives more than one direction or clinical weight to: ",
       paste(unique(NBAIS_WEIGHT_LOOKUP$biomarker[
         duplicated(NBAIS_WEIGHT_LOOKUP$biomarker)]), collapse = ", "),
       call. = FALSE)
}

# attach_nbais_weights is the join, and it is also the assertion that the join is a lookup: a
# left_join that changes the row count has matched one row to several, and a composite computed
# over that frame is a mean with a repeated term.
attach_nbais_weights <- function(res_df, lookup = NBAIS_WEIGHT_LOOKUP) {
  out <- dplyr::left_join(res_df, lookup, by = "biomarker")
  if (nrow(out) != nrow(res_df)) {
    stop("attaching marker weights changed the row count from ", nrow(res_df),
         " to ", nrow(out), "; the weight lookup is not one row per biomarker", call. = FALSE)
  }
  out
}

# The admitted set is a parameter with the rule as its default, not a global this function reaches
# for. src/validate_pipeline.R extracts this function and calls it on synthetic markers named bm01
# to bm16 to prove the composite is a weighted mean rather than a weighted sum; a function that
# silently filtered against the real marker names would have returned an empty set for every
# synthetic panel and the invariance test would have compared zero with zero. The validator passes
# its own set explicitly, which is also the honest contract: the caller says which markers it means.
compute_nbais <- function(res_df, weighting = c("inverse_variance",
                                                "equal",
                                                "clinical"),
                          included = NBAIS_INCLUDED) {
  weighting <- match.arg(weighting)

  # The direction and clinical weight must already be on the frame. This is a stop rather than a
  # fallback join: a function that quietly joined when the columns were missing would be the slow
  # path again, and one that quietly treated them as absent would compute a mean of unsigned
  # changes, which is the defect of 15 October in a new place. attach_nbais_weights is the join.
  missing_cols <- setdiff(c("aging_direction", "clinical_weight"), names(res_df))
  if (length(missing_cols) > 0) {
    stop("compute_nbais needs ", paste(missing_cols, collapse = " and "),
         " on its input; call attach_nbais_weights() once before resampling", call. = FALSE)
  }

  d <- res_df |>
    dplyr::filter(biomarker %in% included) |>
    dplyr::filter(!is.na(estimate), !is.na(se), se > 0)

  if (nrow(d) == 0) return(NA_real_)

  w <- switch(
    weighting,
    inverse_variance = 1 / (d$se^2),
    equal            = rep(1, nrow(d)),
    clinical         = d$clinical_weight
  )

  sum(d$aging_direction * d$estimate * w) / sum(w)
}

# Bootstrap confidence intervals. Resampling is at the biomarker level, and
# within each resample every pooled estimate is additionally perturbed by a
# draw from its own sampling distribution. This two level procedure propagates
# both sources of uncertainty that matter: the uncertainty in each pooled
# biomarker estimate, and the uncertainty arising from which biomarkers
# happened to be measured at all. An interval built from the point estimates
# alone would understate the true uncertainty by ignoring the second source.

#
# AMENDMENT 2026-10-19, interval method. The first implementation of this function passed the
# two level statistic to boot::boot and asked for the bias corrected and accelerated interval,
# which the registered plan names. That combination is not computable and its output was wrong,
# demonstrably so: for GLP1_GCGR under equal weighting it printed 15.97 (19.51 to 39.73), an
# estimate outside its own interval. The cause is that BCa is defined for a statistic that is a
# deterministic function of the resample, and this statistic is not one. The inner rnorm draw
# makes t0, the statistic on the unresampled data, a single random draw rather than the estimate,
# so the bias correction constant z0 = qnorm(mean(t < t0)) is computed against a random reference
# point; and the acceleration constant a comes from empirical influence values that, for a random
# statistic, are dominated by the draw rather than by the data. The reported point estimate,
# compute_nbais on the unperturbed frame, was a third quantity again. Nothing reconciled.
#
# Rather than choose between the registered interval and the two level design, both are computed
# and both are reported, because the choice is the Director's and not this script's:
#
#   primary    percentile interval of the two level bootstrap. Well defined for a stochastic
#              statistic, propagates both sources of uncertainty, and refers to the same quantity
#              as the reported point estimate. Columns ci_lb, ci_ub, ci_type.
#   registered BCa on the deterministic statistic, biomarker resampling only, no inner draw. This
#              is the interval the plan names, computable because the statistic is now a function
#              of the resample alone, and narrower because it ignores the uncertainty in each
#              pooled biomarker estimate. Columns bca_lb, bca_ub, bca_status.
#
# boot::boot is used only for the second, where t0 means what boot assumes it means. The first is
# written out explicitly so that the two levels are legible to a reader of the Methods, and so
# that nothing depends on a t0 this design cannot supply.
#
# point_inside_ci records the check whose failure exposed the original defect. It is a column
# rather than a stop so that a run still produces its outputs for inspection; src/composite_
# interval_check.py fails the gate chain on a FALSE, which is where a number that cannot be
# reported must be caught.

nbais_boot <- function(res_df, weighting, R = 10000) {

  # The resample is over the markers the inclusion rule admits, which is also the set the point
  # estimate averages. Resampling the unfiltered frame would have drawn excluded markers into the
  # interval of a filtered estimate.
  res_df <- dplyr::filter(res_df, biomarker %in% NBAIS_INCLUDED,
                          !is.na(estimate), !is.na(se), se > 0)
  # Joined here, once, rather than inside each of the 20 000 calls to compute_nbais below.
  res_df <- attach_nbais_weights(res_df)
  n <- nrow(res_df)

  if (n < NBAIS_MIN_MARKERS) {
    return(tibble::tibble(
      nbais = NA_real_, boot_mean = NA_real_, boot_se = NA_real_, boot_bias = NA_real_,
      ci_lb = NA_real_, ci_ub = NA_real_, ci_type = "not_computed",
      point_inside_ci = NA, bca_lb = NA_real_, bca_ub = NA_real_,
      bca_status = sprintf("not_computable: %d included marker(s), floor is %d",
                           n, NBAIS_MIN_MARKERS),
      n_markers = n, weighting = weighting, R = 0L,
      status = sprintf("not_computed: %d of the %d markers named by the inclusion rule pool in this class",
                       n, length(NBAIS_INCLUDED))))
  }

  point <- compute_nbais(res_df, weighting)

  # Primary: two level bootstrap, percentile interval.
  reps <- replicate(R, {
    dd <- res_df[sample.int(n, n, replace = TRUE), , drop = FALSE]
    dd$estimate <- rnorm(nrow(dd), mean = dd$estimate, sd = dd$se)
    compute_nbais(dd, weighting = weighting)
  })
  lo <- unname(quantile(reps, 0.025, na.rm = TRUE))
  hi <- unname(quantile(reps, 0.975, na.rm = TRUE))

  # Registered: BCa on the deterministic statistic. Fails by design at small marker counts, which
  # is recorded rather than worked around; the primary interval does not depend on it.
  det_stat <- function(d, idx) compute_nbais(d[idx, , drop = FALSE], weighting = weighting)
  bca <- tryCatch({
    bt <- boot::boot(res_df, statistic = det_stat, R = R)
    ci <- boot::boot.ci(bt, type = "bca")
    list(lb = ci$bca[4], ub = ci$bca[5], status = "computed")
  }, error = function(e) list(lb = NA_real_, ub = NA_real_,
                              status = paste("not_computable:", conditionMessage(e))),
     warning = function(w) list(lb = NA_real_, ub = NA_real_,
                                status = paste("not_computable:", conditionMessage(w))))

  tibble::tibble(
    nbais           = point,
    boot_mean       = mean(reps, na.rm = TRUE),
    boot_se         = sd(reps, na.rm = TRUE),
    boot_bias       = mean(reps, na.rm = TRUE) - point,
    ci_lb           = lo,
    ci_ub           = hi,
    ci_type         = "percentile_two_level",
    point_inside_ci = !is.na(point) && point >= lo && point <= hi,
    bca_lb          = bca$lb,
    bca_ub          = bca$ub,
    bca_status      = bca$status,
    n_markers       = n,
    weighting       = weighting,
    R               = R,
    status          = "computed"
  )
}

nbais_results <- purrr::map_dfr(RECEPTOR_CLASSES, function(rc) {
  rc_res <- dplyr::filter(primary_results, receptor_class == rc)
  if (nrow(rc_res) == 0) return(NULL)
  purrr::map_dfr(c("inverse_variance", "equal", "clinical"), function(w) {
    dplyr::mutate(nbais_boot(rc_res, w), receptor_class = rc, .before = 1)
  })
})

readr::write_csv(nbais_results, file.path(OUT_DIR, "table5_nbais.csv"))

# Pairwise comparison between receptor classes. The difference is bootstrapped
# directly, rather than being inferred from whether two confidence intervals
# overlap, which is a well known inferential error. Comparisons are restricted
# to biomarkers measured in both classes, so a difference cannot be
# manufactured by one class having been studied with a more favorable panel.

nbais_contrast <- function(rc_a, rc_b, weighting = "inverse_variance",
                           R = 10000) {
  # The inclusion rule is applied before the shared set is counted, not after. Counting first
  # reported "n_shared 14, computed" for a pair whose computation rested on one marker, because
  # thirteen of the fourteen are excluded by the rule and compute_nbais drops them: the contrast was
  # a difference of two single marker means carrying a fourteen marker label. n_shared now counts
  # the markers that enter the arithmetic.
  a <- dplyr::filter(primary_results, receptor_class == rc_a, biomarker %in% NBAIS_INCLUDED)
  b <- dplyr::filter(primary_results, receptor_class == rc_b, biomarker %in% NBAIS_INCLUDED)

  shared <- intersect(a$biomarker, b$biomarker)
  if (length(shared) < NBAIS_MIN_MARKERS) {
    return(tibble::tibble(comparison = paste(rc_a, "vs", rc_b),
                          status   = "insufficient_shared_biomarkers",
                          n_shared = length(shared)))
  }
  a <- dplyr::filter(a, biomarker %in% shared)
  b <- dplyr::filter(b, biomarker %in% shared)

  # Joined once per arm, rather than inside each of the 20 000 calls to compute_nbais below.
  a <- attach_nbais_weights(a)
  b <- attach_nbais_weights(b)

  diffs <- replicate(R, {
    aa <- a; bb <- b
    aa$estimate <- rnorm(nrow(aa), aa$estimate, aa$se)
    bb$estimate <- rnorm(nrow(bb), bb$estimate, bb$se)
    compute_nbais(aa, weighting) - compute_nbais(bb, weighting)
  })

  tibble::tibble(
    comparison  = paste(rc_a, "vs", rc_b),
    status      = "computed",
    n_shared    = length(shared),
    diff        = compute_nbais(a, weighting) - compute_nbais(b, weighting),
    ci_lb       = quantile(diffs, 0.025, na.rm = TRUE),
    ci_ub       = quantile(diffs, 0.975, na.rm = TRUE),
    p_two_sided = 2 * min(mean(diffs <= 0, na.rm = TRUE),
                          mean(diffs >= 0, na.rm = TRUE))
  )
}

class_pairs <- utils::combn(RECEPTOR_CLASSES, 2, simplify = FALSE)
readr::write_csv(purrr::map_dfr(class_pairs, ~ nbais_contrast(.x[1], .x[2])),
                 file.path(OUT_DIR, "table5a_nbais_contrasts.csv"))


## ---------------------------------------------------------------------------
## 7. NETWORK META-ANALYSIS
## ---------------------------------------------------------------------------
# The receptor class network has four treatment nodes plus placebo. It is run
# as a sensitivity analysis rather than as the primary approach, because
# pooling chemically distinct molecules into a single node assumes within node
# exchangeability that must itself be tested. Survodutide, pemvidutide,
# mazdutide and cotadutide differ substantially in relative glucagon receptor
# potency despite sharing a class. The drug level network is therefore fitted
# in parallel, and material disagreement between the two would invalidate the
# class level simplification on which the paper rests.

run_nma <- function(bm, node_var = "receptor_class") {

  d <- dplyr::filter(es_continuous, biomarker == bm)
  if (length(unique(d[[node_var]])) < 2) return(NULL)

  nm <- netmeta::netmeta(
    TE = d$yi, seTE = sqrt(d$vi),
    treat1 = d[[node_var]], treat2 = "placebo",
    studlab = d$trial_id,
    sm = "SMD",
    common = FALSE, random = TRUE,
    reference.group = "placebo"
  )

  # Global inconsistency by the design by treatment interaction test, local
  # inconsistency by node splitting. A network failing either is reported as
  # inconsistent and its rankings are not interpreted.
  decomp <- netmeta::decomp.design(nm)
  splits <- tryCatch(netmeta::netsplit(nm), error = function(e) NULL)

  list(
    biomarker       = bm,
    node_var        = node_var,
    netmeta         = nm,
    p_scores        = netmeta::netrank(nm, small.values = "desirable"),
    Q_total         = nm$Q,
    Q_heterogeneity = nm$Q.heterogeneity,
    Q_inconsistency = nm$Q.inconsistency,
    p_inconsistency = decomp$Q.inc.random$p.value,
    netsplit        = splits
  )
}

# The network block is GATED OFF, and not because it fails to run. It does fail: netmeta is called
# with treat1 as a vector of class labels and treat2 as the scalar string "placebo", so the two
# arguments have different lengths and the call errors, which is what halted the pipeline before the
# figures and the manifest on 16 October. But making the lengths agree would produce a worse outcome
# than an error, because it would force every comparator in this corpus into a single placebo node.
# The corpus is 217 placebo controlled rows against 240 ACTIVE controlled rows across 36 distinct
# comparators: insulin glargine, insulin degludec, metformin, glimepiride, gliclazide, sitagliptin,
# lifestyle. A contrast of tirzepatide against insulin degludec and one of semaglutide against
# placebo do not share a reference treatment, and pooling them as though they did would be a
# methodological error that the numbers would not reveal.
#
# A network meta-analysis needs a connected graph over the real comparators, which would mean nodes
# for each comparator class and enough closed loops to estimate inconsistency. Whether this corpus
# supports one is an open question and the Lab Director's standing instruction is that the method is
# NOT described as a network meta-analysis; the registered title against the method is his decision
# and is unresolved. So the block is gated rather than repaired, the reason is recorded as an output
# the Methods can cite, and nothing downstream silently depends on a network that was never fitted.
RUN_NMA <- FALSE

if (RUN_NMA) {
  nma_class <- purrr::compact(purrr::map(biomarkers, ~ run_nma(.x, "receptor_class")))
  nma_drug  <- purrr::compact(purrr::map(biomarkers, ~ run_nma(.x, "drug")))
} else {
  nma_class <- list()
  nma_drug  <- list()
  readr::write_csv(
    tibble::tibble(
      analysis = "network meta-analysis, class level and drug level",
      status = "not run",
      reason = paste("Comparators are not a single node: 217 placebo controlled rows against 240",
                     "active controlled rows over 36 distinct comparators. A connected network over",
                     "the real comparators has not been established, and the method is not described",
                     "as a network meta-analysis pending the registered title decision."),
      placebo_rows = sum(dat$comparator_type == "placebo", na.rm = TRUE),
      active_rows = sum(dat$comparator_type == "active", na.rm = TRUE),
      distinct_comparators = length(unique(dat$comparator))
    ),
    file.path(OUT_DIR, "table7_network_not_run.csv")
  )
  message("  network block gated off; reason written to table7_network_not_run.csv")
  # With the block gated off there are no inconsistency diagnostics, and until 24 October 2026 the
  # call below still wrote table_nma_coherence.csv from the empty list: a file of zero bytes, not
  # even a header, which the manifest hashed and the runbook described as the diagnostics. The table
  # is now written only when the network runs, and a file left by an earlier run is removed.
  unlink(file.path(OUT_DIR, "table_nma_coherence.csv"))
}

if (RUN_NMA) readr::write_csv(
  purrr::map_dfr(nma_class, function(x) {
    tibble::tibble(
      biomarker        = x$biomarker,
      Q_total          = x$Q_total,
      Q_heterogeneity  = x$Q_heterogeneity,
      Q_inconsistency  = x$Q_inconsistency,
      p_inconsistency  = x$p_inconsistency,
      network_coherent = is.na(x$p_inconsistency) || x$p_inconsistency > 0.05
    )
  }),
  file.path(OUT_DIR, "table_nma_coherence.csv")
)


## ---------------------------------------------------------------------------
## 8. SENSITIVITY ANALYSES
## ---------------------------------------------------------------------------
# Nine pre-specified analyses, each re-running the primary pooling under a
# different assumption. A result that reverses sign or loses significance under
# any of these is flagged as fragile and is not advanced as a conclusion.
#
# The estimator sweep addresses a specific vulnerability of this evidence base:
# with few trials per biomarker, different between-study variance estimators
# can yield materially different pooled estimates and intervals. Reporting four
# demonstrates whether a conclusion is a property of the data or of the
# estimator chosen.

sensitivity_estimator <- function() {
  purrr::map_dfr(c("REML", "DL", "PM", "SJ"), function(est) {
    purrr::map_dfr(biomarkers, function(bm) {
      purrr::map_dfr(RECEPTOR_CLASSES, function(rc) {
        d <- dplyr::filter(es_continuous, biomarker == bm, receptor_class == rc)
        # One estimator failing on one cell must not destroy the sweep. The sweep exists to show
        # how much a pooled estimate moves when the between study variance estimator changes, so a
        # cell that cannot be fitted is itself part of the answer and is recorded as such. The first
        # complete run stopped here on "Value of tau2.max too low", which is Paule and Mandel or
        # Sidik and Jonkman reaching its search bound on a cell whose heterogeneity is extreme.
        # Raising tau2.max to make the error disappear would change the estimator's behaviour
        # silently and make the sweep agree with itself by construction, so the bound is left alone
        # and the failure is reported against the cell and the estimator that produced it.
        r <- tryCatch(suppressWarnings(pool_effect(d, estimator = est)),
                      error = function(e) {
                        structure(list(message = conditionMessage(e)), class = "pool_failure")
                      })
        if (inherits(r, "pool_failure")) {
          return(tibble::tibble(biomarker = bm, receptor_class = rc, k = nrow(d),
                                estimator = est, status = "did_not_converge",
                                failure = r$message))
        }
        if (is.null(r)) return(NULL)
        dplyr::mutate(r, biomarker = bm, receptor_class = rc, status = "fitted",
                      failure = NA_character_, .before = 1)
      })
    })
  })
}

sensitivity_subgroup <- function(filter_expr, label) {
  d_sub <- dplyr::filter(es_continuous, !!rlang::parse_expr(filter_expr))
  purrr::map_dfr(unique(d_sub$biomarker), function(bm) {
    purrr::map_dfr(RECEPTOR_CLASSES, function(rc) {
      d <- dplyr::filter(d_sub, biomarker == bm, receptor_class == rc)
      # Same guard as the estimator sweep above, and more necessary here: a subgroup cell holds
      # fewer trials than the whole, so an estimator is likelier to fail on it. A subgroup analysis
      # that stops on its first unfittable cell reports nothing about any of the others.
      r <- tryCatch(suppressWarnings(pool_effect(d)),
                    error = function(e) {
                      structure(list(message = conditionMessage(e)), class = "pool_failure")
                    })
      if (inherits(r, "pool_failure")) {
        return(tibble::tibble(biomarker = bm, receptor_class = rc, k = nrow(d),
                              sensitivity = label, status = "did_not_converge",
                              failure = r$message))
      }
      if (is.null(r)) return(NULL)
      dplyr::mutate(r, biomarker = bm, receptor_class = rc,
                    sensitivity = label, status = "fitted", failure = NA_character_,
                    .before = 1)
    })
  })
}

sens <- list(
  estimator      = sensitivity_estimator(),
  t2d_only       = sensitivity_subgroup("population == 'T2D'", "T2D only"),
  non_t2d        = sensitivity_subgroup("population != 'T2D'", "non-T2D"),
  mash_only      = sensitivity_subgroup("population == 'MASH'", "MASH only"),
  duration_short = sensitivity_subgroup("duration_weeks < 26", "under 26 weeks"),
  duration_mid   = sensitivity_subgroup(
                     "duration_weeks >= 26 & duration_weeks <= 52", "26 to 52 weeks"),
  duration_long  = sensitivity_subgroup("duration_weeks > 52", "over 52 weeks"),
  low_rob_only   = sensitivity_subgroup("rob_overall == 'low'", "low RoB only"),
  non_industry   = sensitivity_subgroup("industry_funded == FALSE", "non-industry")
)

purrr::iwalk(sens, ~ readr::write_csv(
  .x, file.path(OUT_DIR, sprintf("sensitivity_%s.csv", .y))))


## ---------------------------------------------------------------------------
## 9. INFLUENCE AND SMALL STUDY DIAGNOSTICS
## ---------------------------------------------------------------------------
# Leave one out influence identifies whether any single trial drives a pooled
# result. The full range of leave one out estimates is reported so a reader can
# see directly whether removing one trial changes the conclusion.
#
# Egger's test and funnel plots are computed only where at least 10 trials
# contribute. Below that the test has essentially no power, so a non
# significant result would be uninformative rather than reassuring; such
# analyses are reported as not assessable rather than as showing no bias.

diagnostics <- purrr::map_dfr(biomarkers, function(bm) {
  purrr::map_dfr(RECEPTOR_CLASSES, function(rc) {
    d <- dplyr::filter(es_continuous, biomarker == bm, receptor_class == rc)
    if (nrow(d) < 3) return(NULL)

    # fit_rma rather than a bare rma call, for the same reason as the meta regression: one cell on
    # which the prespecified estimator does not converge must not destroy the diagnostics for every
    # other cell. A NULL means no estimator converged and the cell is skipped with that recorded.
    fit <- fit_rma(NULL, d)
    if (is.null(fit)) {
      return(tibble::tibble(biomarker = bm, receptor_class = rc, k = nrow(d),
                            n_influential = NA_integer_,
                            influential_trials = "no estimator converged"))
    }
    # `metafor::influence` does not exist: influence() is the generic from stats and metafor supplies
    # the influence.rma.uni method for it, so the namespaced call fails with "not an exported object"
    # and halted the pipeline here the first time the diagnostics were ever reached. The generic is
    # called instead. The protocol names leave one out as the influence analysis, and leave1out IS
    # exported, so it carries the requirement; influence() adds metafor's own influential case flags
    # on top and is wrapped because it is the optional part.
    inf <- tryCatch(influence(fit), error = function(e) NULL)
    loo <- metafor::leave1out(fit)

    egger <- if (nrow(d) >= 10) {
      e <- metafor::regtest(fit, model = "lm", predictor = "sei")
      list(z = e$zval, p = e$pval)
    } else list(z = NA_real_, p = NA_real_)

    tf <- if (nrow(d) >= 10) {
      t <- tryCatch(metafor::trimfill(fit), error = function(e) NULL)
      if (!is.null(t)) list(k0 = t$k0, adj = as.numeric(t$b))
      else list(k0 = NA_real_, adj = NA_real_)
    } else list(k0 = NA_real_, adj = NA_real_)

    tibble::tibble(
      biomarker          = bm,
      receptor_class     = rc,
      k                  = nrow(d),
      n_influential      = if (!is.null(inf)) sum(inf$is.infl, na.rm = TRUE) else NA_integer_,
      influential_trials = if (!is.null(inf))
                             paste(d$trial_id[which(inf$is.infl)], collapse = "; ")
                           else "influence flags unavailable; leave one out range reported",
      loo_min            = min(loo$estimate, na.rm = TRUE),
      loo_max            = max(loo$estimate, na.rm = TRUE),
      egger_z            = egger$z,
      egger_p            = egger$p,
      egger_assessable   = nrow(d) >= 10,
      trimfill_k0        = tf$k0,
      trimfill_adjusted  = tf$adj
    )
  })
})
readr::write_csv(diagnostics, file.path(OUT_DIR, "table_diagnostics.csv"))


## ---------------------------------------------------------------------------
## 10. FIGURES
## ---------------------------------------------------------------------------
# AMENDMENT 2026-10-19, figure devices. Every figure in this section was written with
# device = cairo_pdf and no figure had ever existed. capabilities()["cairo"] reports TRUE on the
# analysis machine, and the cairo shared object then fails to load at run time because the X11
# libraries it links against are absent. cairo_pdf emitted a warning rather than an error, ggsave
# returned normally, no file was created, and the script went on to print "Pipeline complete. 35
# output files written". A device chosen for its font handling cost the manuscript its figures for
# five days, and the run reported success each time.
#
# Two consequences are built in here. First, figures are written with grDevices::pdf, which has no
# external dependency, and with ragg::agg_png, which rasterises without cairo; both are checked in
# by the repository, so a clone reproduces the figures rather than the warning. Second,
# save_figure verifies that each file exists and is larger than a plausible empty device before it
# reports anything, and stops the run when a figure produced no file on any device. A capability
# that a library reports is a claim; a file on disk is evidence.
#
# AMENDMENT 2026-10-24, figure style 2. The figures were drawn at a size chosen for each in inches,
# 9.5 by 12 for the heatmap among them, in the device's default face, at 300 dpi, with a caption
# printed inside the image. A journal reduces such a figure to its column width, so its text reached
# the page at whatever size the reduction left, and the caption appeared twice, once in the image
# and once in the legend. At the Director's decision of 24 October for more resolution and a more
# modern style, the figures follow figure style 2, the laboratory's standard for the figures it
# publishes: each figure is drawn at its final
# journal width, 89, 120 or 183 mm, at most 170 mm high, in the vendored Inter typeface verified by
# its SHA-256, with text between 5.8 and 7 pt, written as a vector PDF whose glyphs are outlines and
# as a 600 dpi PNG, and with no title or caption inside it: the caption is written to
# figure_index.csv and carried by the manuscript legend. The standard, the twin writer and
# save_figure live in analysis/figure_style.R, which this section sources, so that
# src/prisma_figure.R draws the flow diagram the same way. The restyle changes what a figure looks
# like and not what it plots: every twin is still recomputed from its sources by the figure gate.
#
# Colour follows the data visualisation standard in use: one hue for a single series, hue order
# fixed and never cycled, a diverging ramp only for a signed quantity with a neutral midpoint, and
# identity never carried by colour alone. The four receptor classes cannot be separated by colour
# in a scatter: no four hue set from the reference palette clears the all pairs colour vision
# deficiency and normal vision floors, which was measured rather than judged, so Figure 4 carries
# class by point shape and spends no colour on it. Figure 5 needs no class colour at all, since the
# axis names each class. The heatmap's diverging ramp runs from a dark orange through a grey with
# no hue to a dark blue, the pair of figure style 2. It replaced the ColorBrewer RdBu poles on
# 24 October, because their red arm is the colour this submission reserves for a high risk of bias.

source(file.path("analysis", "figure_style.R"))

# Display vocabulary. The analysis keys are snake case because they index data; a printed figure
# is read by a person, and `body_fat_pct` and `GLP1_GIP_GCGR` are keys rather than names. The
# biomarker names come from the inventory's own table1_name column, which Table 1 already prints,
# so the figures and Table 1 cannot drift apart into two spellings of one marker.
CLASS_LABELS <- c(GLP1_mono     = "GLP-1 mono",
                  GLP1_GIP      = "GLP-1 / GIP",
                  GLP1_GCGR     = "GLP-1 / GCG",
                  GLP1_GIP_GCGR = "GLP-1 / GIP / GCG")
# The heatmap's columns are narrower at its journal width than the longest class name, so its
# column headers break the names over two lines.
CLASS_LABELS_STACKED <- c(GLP1_mono     = "GLP-1\nmono",
                          GLP1_GIP      = "GLP-1 /\nGIP",
                          GLP1_GCGR     = "GLP-1 /\nGCG",
                          GLP1_GIP_GCGR = "GLP-1 /\nGIP / GCG")
WEIGHTING_LEVELS <- c("inverse_variance", "equal", "clinical")
WEIGHTING_LABELS <- c(inverse_variance = "Inverse variance weighted",
                      equal            = "Equally weighted",
                      clinical         = "Clinically weighted")

biomarker_inventory <- readr::read_csv("analysis/data/biomarker_inventory.csv",
                                       show_col_types = FALSE)
BIOMARKER_LABELS <- stats::setNames(biomarker_inventory$table1_name,
                                    biomarker_inventory$biomarker)
label_biomarker <- function(x) ifelse(is.na(BIOMARKER_LABELS[x]), x, BIOMARKER_LABELS[x])
label_domain <- function(x) sub("^(.)", "\\U\\1", gsub("_", " ", x), perl = TRUE)

# A rounded value of zero prints as "-0" for any small negative, which reads as a quantity that does
# not exist. Values that round to zero print as 0 with no sign, and a negative value carries a true
# minus sign rather than a hyphen.
fmt_signed <- function(v) {
  r <- round(v)
  ifelse(is.na(r), NA_character_,
         ifelse(r == 0, "0", sub("^-", "−", sprintf("%+d", as.integer(r)))))
}

ROB_LEVELS <- c("low", "some_concerns", "high")
ROB_LABELS <- c(low = "Low risk", some_concerns = "Some concerns", high = "High risk")
ROB_FILL   <- FIG_STATUS
ROB_TEXT   <- FIG_STATUS_TEXT
ROB_GLYPH  <- c(low = "+", some_concerns = "?", high = "×")
# The legend carries the glyph beside each label, so the key is read the same way as the cells.
ROB_KEY    <- stats::setNames(paste(ROB_GLYPH, ROB_LABELS[names(ROB_GLYPH)], sep = "  "),
                              names(ROB_GLYPH))

# Figure 1: the signature heatmap. Rows are the biomarkers grouped by aging
# hallmark domain, columns are the four receptor classes, and cell fill is the
# direction adjusted pooled effect, so a positive value always means a shift
# toward younger biological age regardless of whether the underlying biomarker
# should rise or fall.

fig1_data <- primary_results |>
  dplyr::left_join(
    dplyr::distinct(dat, biomarker, aging_direction, hallmark_domain),
    by = "biomarker") |>
  dplyr::mutate(signed_effect = aging_direction * estimate)

# The grid is completed to every biomarker by class cell, so that a cell with no pooled estimate is
# drawn as an absent cell rather than omitted, which would otherwise let a reader take a short row
# for a narrow panel. Absence is marked by a glyph as well as by fill, because the former fill for
# missing cells, grey90, is three per cent away from the neutral midpoint of the diverging ramp:
# "no estimate" and "no effect" were the same colour.
# The completion is over the declared receptor classes, not over the classes that happen to appear
# in the results. The triple agonist node has no pooled estimate for any biomarker, because within
# that class every biomarker is carried by a single trial after the dose collapse and pool_effect
# requires two. Completing over the observed classes drops that column entirely and the figure then
# shows a three class signature without saying that the fourth class was studied and pooled nowhere,
# which is a coverage finding in its own right and the first thing a reader of this figure should
# see. Completed to the declared four, the column is present and empty.
fig1_data <- tidyr::complete(
    fig1_data,
    biomarker,
    receptor_class = factor(RECEPTOR_CLASSES, levels = RECEPTOR_CLASSES)) |>
  dplyr::group_by(biomarker) |>
  dplyr::mutate(hallmark_domain = dplyr::first(stats::na.omit(hallmark_domain))) |>
  dplyr::ungroup() |>
  dplyr::mutate(
    biomarker_label = label_biomarker(biomarker),
    # complete() combines a character column with the factor it is completed against and the result
    # is character, so the declared order is lost and the columns come out alphabetical. The factor
    # is reapplied here, after the completion rather than before it.
    receptor_class = factor(as.character(receptor_class), levels = RECEPTOR_CLASSES))

fig1_empty_classes <- fig1_data |>
  dplyr::group_by(receptor_class) |>
  dplyr::summarise(n = sum(!is.na(signed_effect)), .groups = "drop") |>
  dplyr::filter(n == 0) |>
  dplyr::pull(receptor_class)
fig1_empty_note <- if (length(fig1_empty_classes) > 0) {
  sprintf(" No biomarker pools within %s, so that column is empty throughout.",
          paste(CLASS_LABELS[as.character(fig1_empty_classes)], collapse = " or "))
} else ""

# The value is printed in every estimable cell. The pooled effects here run from about minus 5 to
# plus 50 per cent, so a diverging ramp centred on zero spends almost all of its range on one arm
# and most cells read as a pale blue that cannot be told from its neighbour. Printing the number
# makes the figure exact and leaves colour to do what colour is good at, which is sorting the cells
# at a glance rather than carrying the quantity.
#
# The ramp passes through the steps of the validated sequential blue on the positive arm and through
# the orange slot to its dark step on the negative arm, with the hueless grey at zero. A ramp drawn
# straight from the grey to the dark blue passes through greyed violets on its way, which read as a
# third hue; through the sequential steps it stays blue. The stops sit where the lightness of those
# steps falls evenly with the magnitude, and both arms are scaled by the largest magnitude on either
# side, so a cell of minus 5 is as far from the grey as a cell of plus 5. The colour bar spans the
# observed range only. The number in each cell takes white or ink by its contrast with the cell's
# own colour, computed here with the scale's own palette, so the darkest blues carry white numbers.
fig1_reach <- max(abs(fig1_data$signed_effect), na.rm = TRUE)
fig1_from <- range(fig1_data$signed_effect, na.rm = TRUE)
fig1_colours <- c(FIG_DIV_LOW, FIG_ORANGE, FIG_DIV_MID, FIG_SEQ)
fig1_values <- scales::rescale(c(-1, -0.73, 0, 0.38, 0.54, 0.73, 1) * fig1_reach, from = fig1_from)
fig1_palette <- scales::pal_gradient_n(fig1_colours, fig1_values)
fig1_cells <- fig1_data |>
  dplyr::mutate(
    label = ifelse(is.na(signed_effect), "n/e", fmt_signed(signed_effect)),
    ink = ifelse(is.na(signed_effect), FIG_INK_SOFT,
                 fig_text_on(fig1_palette(scales::rescale(signed_effect, from = fig1_from)))))

fig1 <- ggplot2::ggplot(
  fig1_cells,
  ggplot2::aes(x = receptor_class, y = forcats::fct_rev(biomarker_label))
) +
  ggplot2::geom_tile(ggplot2::aes(fill = signed_effect), colour = "white",
                     linewidth = fig_lw(0.8)) +
  ggplot2::geom_text(ggplot2::aes(label = label, colour = ink), size = fig_size(FIG_PT$note)) +
  ggplot2::scale_colour_identity() +
  ggplot2::scale_fill_gradientn(
    colours = fig1_colours, values = fig1_values, limits = fig1_from,
    na.value = FIG_NA_FILL, labels = fig_axis_number,
    name = "Direction adjusted pooled change, % (positive, toward younger)",
    guide = ggplot2::guide_colourbar(theme = ggplot2::theme(
      legend.title.position = "top",
      legend.key.width = grid::unit(46, "mm"), legend.key.height = grid::unit(2.2, "mm"),
      legend.ticks = ggplot2::element_line(colour = "white", linewidth = fig_lw(0.5))))) +
  ggplot2::scale_x_discrete(position = "top", drop = FALSE, labels = CLASS_LABELS_STACKED,
                            expand = c(0, 0)) +
  ggplot2::scale_y_discrete(expand = c(0, 0)) +
  ggplot2::facet_grid(hallmark_domain ~ ., scales = "free_y", space = "free_y",
                      labeller = ggplot2::as_labeller(label_domain)) +
  ggplot2::labs(x = "Receptor class", y = NULL) +
  theme_figure() +
  ggplot2::theme(
    axis.line          = ggplot2::element_blank(),
    axis.ticks         = ggplot2::element_blank(),
    panel.grid.major   = ggplot2::element_blank(),
    axis.text.x.top    = ggplot2::element_text(colour = FIG_INK, lineheight = 0.95, vjust = 0,
                                               margin = ggplot2::margin(0, 0, 1.2, 0, "mm")),
    axis.text.y        = ggplot2::element_text(colour = FIG_INK, hjust = 1,
                                               margin = ggplot2::margin(0, 1.2, 0, 0, "mm")),
    strip.text.y.right = ggplot2::element_text(family = "Inter Medium", size = FIG_PT$tick,
                                               colour = FIG_INK_SOFT, angle = 0, hjust = 0,
                                               margin = ggplot2::margin(0, 0, 0, 1.6, "mm")),
    panel.spacing.y    = grid::unit(0.9, "mm"),
    legend.justification = "left",
    legend.title       = ggplot2::element_text(size = FIG_PT$tick, colour = FIG_INK,
                                               margin = ggplot2::margin(0, 0, 1, 0, "mm"))
  )

save_figure("figure1_signature_heatmap", fig1,
            width_mm = FIG_WIDTHS_MM[["one_and_a_half"]], height_mm = 150,
            caption = paste0("Receptor class signature across aging biomarkers, grouped by ",
                             "hallmark domain. Cell colour and the printed value are the pooled ",
                             "percent change multiplied by the biomarker's aging direction, so a ",
                             "positive value is a shift toward a younger profile whether the marker ",
                             "should rise or fall. n/e, not estimable: fewer than two trials for ",
                             "that biomarker in that class.", fig1_empty_note),
            data = fig1_data |>
              dplyr::arrange(hallmark_domain, biomarker_label, receptor_class) |>
              dplyr::select(hallmark_domain, biomarker, biomarker_label, receptor_class,
                            signed_effect))

# Figure 4: weight adjusted meta-regression bubble plot for hepatic outcomes.
# Bubble area is inverse variance, so the visually dominant points are the
# precisely estimated ones, matching how they are weighted in the model.

fig4_data <- dplyr::filter(es_continuous, biomarker == "liver_fat_pdff")

# Two corrections of 2026-10-19. The fitted line was geom_smooth with method "lm", grouped by the
# colour aesthetic, so the figure drew one ordinary least squares line per receptor class, one of
# them through a single point, and none of them the random effects meta-regression that Table 4a
# reports. The line now comes from that model: fit_rma on this biomarker with the weight covariate,
# with its own confidence band from predict. A figure whose line is fitted by a different method
# from the table beneath it is an unforced disagreement inside one manuscript. The y axis was
# labelled "Hedges' g vs placebo", which is the registered scale and not the scale pooled here; on
# the percent change scale the printed numbers are roughly twenty times the g values a reader would
# infer from that label.
fig4_fit <- fit_rma(~ pct_weight_change, fig4_data)
fig4_line <- if (!is.null(fig4_fit) && nrow(fig4_fit$b) == 2) {
  xs <- seq(min(fig4_data$pct_weight_change, na.rm = TRUE),
            max(fig4_data$pct_weight_change, na.rm = TRUE), length.out = 100)
  p <- predict(fig4_fit, newmods = xs)
  tibble::tibble(pct_weight_change = xs, yi = p$pred, lo = p$ci.lb, hi = p$ci.ub)
} else NULL

# Two of the nine pooled liver fat arms carry no body weight covariate, so the model and the figure
# both rest on seven. ggplot dropped them with a warning that the run buried among 35 others, which
# is how a figure comes to show less data than its caption claims. The counts are computed and
# printed, and the arms are set aside here on purpose rather than by the geom by default.
# Since 24 October 2026 the caption names the arms set aside as well as counting them: the Results
# say they are named in the caption, and until then the caption only counted them.
fig4_set_aside <- fig4_data$trial_id[is.na(fig4_data$pct_weight_change) | is.na(fig4_data$vi)]
fig4_n_all <- nrow(fig4_data)
fig4_n_cov <- fig4_n_all - length(fig4_set_aside)
fig4_named <- if (length(fig4_set_aside) < 2) fig4_set_aside else
  paste(paste(fig4_set_aside[-length(fig4_set_aside)], collapse = ", "), "and",
        fig4_set_aside[length(fig4_set_aside)])
fig4_coverage <- if (length(fig4_set_aside) == 0) {
  sprintf("All %d pooled liver fat arms carry the body weight covariate and are plotted.", fig4_n_all)
} else {
  sprintf("%d of the %d pooled liver fat arms carry the body weight covariate and are plotted; %s %s.",
          fig4_n_cov, fig4_n_all,
          if (length(fig4_set_aside) == 1) "the one that does not is" else
            sprintf("the %d that do not are", length(fig4_set_aside)),
          fig4_named)
}
fig4_points <- dplyr::filter(fig4_data, !is.na(pct_weight_change), !is.na(vi))

fig4_slope <- if (!is.null(fig4_line)) {
  sprintf("Meta-regression slope %.2f per cent liver fat per per cent body weight (95%% CI %.2f to %.2f), p = %.3f, k = %d, estimator %s.",
          fig4_fit$b[2], fig4_fit$ci.lb[2], fig4_fit$ci.ub[2], fig4_fit$pval[2],
          fig4_fit$k, attr(fig4_fit, "estimator_used"))
} else "Meta-regression not estimable on this subset."

fig4 <- ggplot2::ggplot(fig4_points,
                        ggplot2::aes(x = pct_weight_change, y = yi)) +
  ggplot2::geom_hline(yintercept = 0, colour = FIG_INK_SOFT, linetype = "22",
                      linewidth = fig_lw(FIG_LW$ref)) +
  {if (!is.null(fig4_line))
    ggplot2::geom_ribbon(data = fig4_line, ggplot2::aes(ymin = lo, ymax = hi),
                         fill = FIG_BAND, colour = NA)} +
  {if (!is.null(fig4_line))
    ggplot2::geom_line(data = fig4_line, colour = FIG_BLUE, linewidth = fig_lw(FIG_LW$data))} +
  # Point area is proportional to inverse variance, with zero precision at zero area, as the caption
  # states; the former size range started at a floor, which made area an affine function of it.
  ggplot2::geom_point(ggplot2::aes(size = 1 / vi, shape = receptor_class),
                      fill = FIG_BLUE, colour = "white", stroke = fig_stroke(0.6)) +
  ggplot2::scale_shape_manual(values = c(GLP1_mono = 21, GLP1_GIP = 22,
                                         GLP1_GCGR = 23, GLP1_GIP_GCGR = 24),
                              drop = FALSE, name = "Receptor class",
                              labels = CLASS_LABELS) +
  ggplot2::scale_size_area(name = "Precision, 1 / variance", max_size = 5.4,
                           breaks = scales::breaks_pretty(n = 3)) +
  ggplot2::scale_x_continuous(labels = fig_axis_number) +
  ggplot2::scale_y_continuous(labels = fig_axis_number) +
  ggplot2::guides(
    shape = ggplot2::guide_legend(order = 1, override.aes = list(size = 2.6, fill = FIG_BLUE,
                                                                 colour = "white")),
    # The size key drew black circles beside blue points, so the legend named a colour the figure
    # does not use.
    size = ggplot2::guide_legend(order = 2, override.aes = list(shape = 21, fill = FIG_BLUE,
                                                                colour = "white"))) +
  ggplot2::labs(x = "Mean body weight change, %",
                y = "Liver fat change vs comparator, %") +
  theme_figure() +
  ggplot2::theme(legend.position = "right", legend.justification = "top",
                 legend.box.just = "left", legend.spacing.y = grid::unit(2.5, "mm"),
                 legend.title = ggplot2::element_text(size = FIG_PT$tick, colour = FIG_INK,
                                                      margin = ggplot2::margin(0, 0, 0.8, 0, "mm")))

save_figure("figure4_weight_adjusted_liverfat", fig4,
            width_mm = FIG_WIDTHS_MM[["one_and_a_half"]], height_mm = 82,
            caption = paste("Liver fat percent change against mean body weight change, one point",
                            "per pooled trial arm that carries the body weight covariate.", fig4_coverage,
                            "Point area is proportional to inverse variance and point shape is",
                            "receptor class. The line and band are the random effects",
                            "meta-regression reported in Table 4a and its 95 per cent confidence",
                            "band.", fig4_slope),
            # The points are the arms drawn, the two without the covariate set aside; the line layer
            # is the model's prediction and confidence band.
            data = Filter(Negate(is.null), list(
              points = fig4_points |>
                dplyr::select(trial_id, receptor_class, pct_weight_change, yi, vi),
              line = fig4_line)))

# Figure 5: the composite score by receptor class with bootstrap intervals,
# faceted by weighting scheme so the reader sees immediately whether the
# ranking is a property of the drugs or an artifact of the weighting choice.
# The ranking is reported as a finding only where it is stable across all three.

# The fill was mapped to receptor class with the legend suppressed, which spends the identity
# channel on something the x axis already names and leaves four hues on the page carrying nothing.
# One series, one hue. The interval is the percentile interval of the two level bootstrap, which is
# the quantity the point estimate belongs to; the registered BCa interval is reported in
# table5_nbais.csv alongside and is not drawn, because an interval that excluded its own estimate
# is what prompted the amendment above and the reader is owed the one that does not.
# Both orderings were alphabetical, which put the clinically weighted panel first and sorted the
# receptor classes as strings. The weighting panels now run in the order the protocol states them,
# inverse variance first as the primary, and the classes in the declared receptor order, with the
# class that has no composite kept as a labelled empty position rather than dropped: a reader of a
# three bar figure cannot tell that a fourth class was studied.
fig5_all <- nbais_results |>
  dplyr::mutate(
    receptor_class = factor(receptor_class, levels = RECEPTOR_CLASSES),
    weighting = factor(weighting, levels = WEIGHTING_LEVELS))
fig5_data <- dplyr::filter(fig5_all, status == "computed")

# A class is absent from this figure for one of two reasons, and the caption distinguishes them,
# because "no composite" and "a composite over too few markers" are different facts about the
# evidence. The counts come from the table rather than from prose.
fig5_no_pool <- setdiff(RECEPTOR_CLASSES, as.character(unique(fig5_all$receptor_class)))
fig5_too_few <- fig5_all |>
  dplyr::filter(status != "computed") |>
  dplyr::distinct(receptor_class, n_markers)

fig5_absent_note <- ""
if (length(fig5_no_pool) > 0) {
  fig5_absent_note <- paste0(
    fig5_absent_note,
    sprintf(" %s: no biomarker pools within the class, so there is nothing to average.",
            paste(CLASS_LABELS[fig5_no_pool], collapse = " and ")))
}
if (nrow(fig5_too_few) > 0) {
  fig5_absent_note <- paste0(
    fig5_absent_note,
    sprintf(" %s: fewer than %d of the %d markers named by the composite inclusion rule pool within the class, so no composite is computed.",
            paste(sprintf("%s (%d)", CLASS_LABELS[as.character(fig5_too_few$receptor_class)],
                          fig5_too_few$n_markers), collapse = "; "),
            NBAIS_MIN_MARKERS, length(NBAIS_INCLUDED)))
}
# Every class without a composite keeps its row in every panel, marked rather than left blank.
fig5_absent <- tidyr::expand_grid(
    weighting = factor(WEIGHTING_LEVELS, levels = WEIGHTING_LEVELS),
    receptor_class = factor(RECEPTOR_CLASSES, levels = RECEPTOR_CLASSES)) |>
  dplyr::anti_join(fig5_data, by = c("weighting", "receptor_class"))
fig5_resamples <- unique(fig5_data$R)
# Ticks cover the drawn values; the axis runs on beyond them to hold the printed values.
fig5_breaks <- pretty(c(min(0, fig5_data$ci_lb), max(fig5_data$ci_ub)), n = 4)

fig5 <- ggplot2::ggplot(
  fig5_data,
  ggplot2::aes(x = nbais, y = receptor_class)
) +
  ggplot2::geom_vline(xintercept = 0, colour = FIG_AXIS, linewidth = fig_lw(FIG_LW$axis)) +
  ggplot2::geom_col(width = 0.62, fill = FIG_BLUE, orientation = "y") +
  ggplot2::geom_errorbar(ggplot2::aes(xmin = ci_lb, xmax = ci_ub), width = 0.3,
                         orientation = "y", colour = FIG_INK, linewidth = fig_lw(0.6)) +
  # The value sat just above the bar top, which is exactly where the error bar runs, so every
  # number was struck through by its own interval. It stands beyond the upper bound instead.
  ggplot2::geom_text(ggplot2::aes(x = ci_ub,
                                  label = sprintf("%s  (k = %d)", fig_num(nbais), n_markers)),
                     hjust = 0, nudge_x = 1.6, size = fig_size(FIG_PT$note), colour = FIG_INK) +
  ggplot2::geom_text(data = fig5_absent,
                     ggplot2::aes(x = 0, y = receptor_class, label = "no composite"),
                     hjust = 0, nudge_x = 1.6, size = fig_size(FIG_PT$note),
                     colour = FIG_INK_SOFT, fontface = "italic") +
  ggplot2::scale_y_discrete(limits = rev(RECEPTOR_CLASSES), labels = CLASS_LABELS) +
  ggplot2::scale_x_continuous(labels = fig_axis_number, breaks = fig5_breaks,
                              expand = ggplot2::expansion(mult = c(0, 0.5))) +
  ggplot2::facet_wrap(~ weighting, nrow = 1,
                      labeller = ggplot2::as_labeller(WEIGHTING_LABELS)) +
  ggplot2::labs(
    x = "Net Biological Age Impact Score, weighted mean direction adjusted change, %",
    y = NULL) +
  theme_figure() +
  ggplot2::theme(panel.grid.major.y = ggplot2::element_blank(),
                 axis.line.y = ggplot2::element_blank(),
                 axis.ticks.y = ggplot2::element_blank(),
                 axis.text.y = ggplot2::element_text(colour = FIG_INK),
                 panel.spacing.x = grid::unit(4, "mm"))

save_figure("figure5_nbais", fig5,
            width_mm = FIG_WIDTHS_MM[["double"]], height_mm = 60,
            caption = paste0("Net Biological Age Impact Score by receptor class under three ",
                             "weighting schemes, computed over the ", length(NBAIS_INCLUDED),
                             " markers named by prespecification/nbais_inclusion_rule.md; k is how ",
                             "many of them pool within the class. Bars are the weighted mean ",
                             "direction adjusted percent change, positive toward a younger ",
                             "biomarker profile; error bars are the 2.5th to 97.5th percentiles of ",
                             "the two level bootstrap (",
                             format(fig5_resamples, big.mark = " ", scientific = FALSE),
                             " resamples, seed 20261013).", fig5_absent_note),
            data = fig5_data |>
              dplyr::arrange(weighting, receptor_class) |>
              dplyr::select(weighting, receptor_class, nbais, ci_lb, ci_ub, n_markers))


# Figure 2: the forest plot of the overall pooled effect per biomarker, which is the primary result
# the manuscript reports. Table 2 is the table of these numbers; this is the same numbers seen at
# once. There was no forest plot in this pipeline: a systematic review of 76 trials reported its
# primary synthesis in a table only, and a reader could not see which markers move together or how
# wide the intervals are relative to each other without reconstructing the figure by hand.
#
# The favourable direction differs by biomarker, so each row carries it. Printing it in a column
# rather than colouring the point by it keeps the identity channel free and keeps the figure
# readable in print and under colour vision deficiency, where a red and blue point are the same
# point.
#
# The figure is a table with a plot in it, three panels on one row grid: the names, favourable
# directions and k on the left, the estimates and intervals in the middle, and the printed estimate
# with its interval and I2 on the right. The printed column stood inside the plot until 24 October,
# at an x beyond the largest upper bound, so the axis had to be extended to hold text and the
# numbers sat in data coordinates; in a panel of its own the column has its own width and the axis
# describes only the data. Rows run from the most negative effect at the top to the most positive
# at the bottom, and every second row carries a light band across all three panels so a row can be
# followed from its name to its numbers.

fig2_data <- table2_pipeline |>
  dplyr::left_join(
    dplyr::distinct(dat, biomarker, aging_direction, hallmark_domain),
    by = "biomarker") |>
  dplyr::mutate(
    biomarker_label = label_biomarker(biomarker),
    favourable = ifelse(aging_direction < 0, "lower", "higher")) |>
  dplyr::arrange(estimate) |>
  dplyr::mutate(row = dplyr::row_number(),
                interval = sprintf("%s (%s to %s)", fig_num(estimate), fig_num(ci_lb),
                                   fig_num(ci_ub)),
                heterogeneity = ifelse(is.na(I2), "n/e", sprintf("%.0f%%", I2)))

fig2_n <- nrow(fig2_data)
fig2_bands <- dplyr::filter(fig2_data, row %% 2 == 0)
# One row grid for the three panels: row 1 at the top, and a header line above it. The panels abut,
# so the bands and the rules under the header and below the last row run unbroken across the page.
fig2_rows <- ggplot2::scale_y_reverse(limits = c(fig2_n + 0.5, -0.7), expand = c(0, 0))
fig2_header_y <- -0.15
fig2_band_layer <- ggplot2::geom_rect(
  data = fig2_bands, inherit.aes = FALSE,
  ggplot2::aes(xmin = -Inf, xmax = Inf, ymin = row - 0.5, ymax = row + 0.5), fill = FIG_ROW)
fig2_header_rule <- ggplot2::geom_hline(yintercept = 0.5, colour = FIG_RULE,
                                        linewidth = fig_lw(FIG_LW$axis))
fig2_bottom_rule <- ggplot2::geom_hline(yintercept = fig2_n + 0.5, colour = FIG_AXIS,
                                        linewidth = fig_lw(FIG_LW$axis))
fig2_text_theme <- ggplot2::theme_void(base_family = "Inter") +
  ggplot2::theme(plot.margin = ggplot2::margin(1.5, 0, 1.5, 0, "mm"),
                 plot.background = ggplot2::element_rect(fill = "white", colour = NA))
# The ticks cover the intervals drawn; the gridlines and the zero line stop at the rows, so the
# header line stays clear.
fig2_breaks <- Filter(function(v) v >= min(fig2_data$ci_lb) && v <= max(fig2_data$ci_ub),
                      pretty(c(min(fig2_data$ci_lb), max(fig2_data$ci_ub)), n = 6))
fig2_head <- function(x, label, hjust) {
  ggplot2::annotate("text", x = x, y = fig2_header_y, label = label, hjust = hjust,
                    family = "Inter Medium", size = fig_size(FIG_PT$tick), colour = FIG_INK)
}

fig2_left <- ggplot2::ggplot(fig2_data, ggplot2::aes(y = row)) +
  fig2_band_layer + fig2_header_rule + fig2_bottom_rule +
  ggplot2::geom_text(ggplot2::aes(x = 0.02, label = biomarker_label), hjust = 0,
                     size = fig_size(FIG_PT$tick)) +
  ggplot2::geom_text(ggplot2::aes(x = 0.68, label = favourable), hjust = 0,
                     size = fig_size(FIG_PT$tick), colour = FIG_INK_SOFT) +
  ggplot2::geom_text(ggplot2::aes(x = 0.97, label = k), hjust = 1,
                     size = fig_size(FIG_PT$tick)) +
  fig2_head(0.02, "Biomarker", 0) + fig2_head(0.68, "Better", 0) + fig2_head(0.97, "k", 1) +
  ggplot2::scale_x_continuous(limits = c(0, 1), expand = c(0, 0)) +
  fig2_rows + fig2_text_theme

fig2_mid <- ggplot2::ggplot(fig2_data, ggplot2::aes(x = estimate, y = row)) +
  fig2_band_layer + fig2_header_rule +
  ggplot2::annotate("segment", x = fig2_breaks, xend = fig2_breaks, y = 0.5, yend = fig2_n + 0.5,
                    colour = FIG_GRID, linewidth = fig_lw(FIG_LW$grid)) +
  ggplot2::annotate("segment", x = 0, xend = 0, y = 0.5, yend = fig2_n + 0.5,
                    colour = FIG_AXIS, linewidth = fig_lw(FIG_LW$ref)) +
  ggplot2::geom_linerange(ggplot2::aes(xmin = ci_lb, xmax = ci_ub), orientation = "y",
                          colour = FIG_BLUE, linewidth = fig_lw(1.0)) +
  ggplot2::geom_point(shape = 22, size = 2.0, fill = FIG_BLUE, colour = "white",
                      stroke = fig_stroke(0.5)) +
  ggplot2::scale_x_continuous(name = "Pooled change vs comparator, %", labels = fig_axis_number,
                              breaks = fig2_breaks) +
  fig2_rows +
  theme_figure() +
  ggplot2::theme(axis.title.y = ggplot2::element_blank(),
                 axis.text.y = ggplot2::element_blank(),
                 axis.ticks.y = ggplot2::element_blank(),
                 axis.line.y = ggplot2::element_blank(),
                 panel.grid.major = ggplot2::element_blank(),
                 plot.margin = ggplot2::margin(1.5, 0, 1.5, 0, "mm"))

fig2_right <- ggplot2::ggplot(fig2_data, ggplot2::aes(y = row)) +
  fig2_band_layer + fig2_header_rule + fig2_bottom_rule +
  ggplot2::geom_text(ggplot2::aes(x = 0.03, label = interval), hjust = 0,
                     size = fig_size(FIG_PT$tick)) +
  ggplot2::geom_text(ggplot2::aes(x = 0.97, label = heterogeneity), hjust = 1,
                     size = fig_size(FIG_PT$tick), colour = FIG_INK_SOFT) +
  fig2_head(0.03, "Change, % (95% CI)", 0) + fig2_head(0.97, "I²", 1) +
  ggplot2::scale_x_continuous(limits = c(0, 1), expand = c(0, 0)) +
  fig2_rows + fig2_text_theme

fig2 <- patchwork::wrap_plots(fig2_left, fig2_mid, fig2_right, nrow = 1,
                              widths = c(62, 74, 44))

save_figure("figure2_forest_overall", fig2,
            width_mm = FIG_WIDTHS_MM[["double"]], height_mm = 20 + 4.4 * fig2_n,
            caption = paste("Forest plot of the overall pooled percent change per aging biomarker",
                            "across all incretin receptor classes, ordered by effect. Squares are",
                            "pooled estimates and bars 95 per cent confidence intervals, from",
                            "random effects pooling relative to comparator. Better, the direction",
                            "of change favourable for the marker; k, contributing trial arms after",
                            "dose collapse; I², heterogeneity. Estimator, prediction interval",
                            "and heterogeneity statistics per biomarker are in table2_pipeline.csv."),
            # In the order drawn, top to bottom, which is ascending order of effect.
            data = fig2_data |>
              dplyr::select(biomarker, biomarker_label, favourable, k, estimate, ci_lb, ci_ub, I2))


# Figure 6 and its supplement: risk of bias. The RoB-2 assessment of every trial existed in
# analysis/data/risk_of_bias.csv and had never been drawn, so a reviewer could read the judgement
# only by opening the data file. Two figures are produced, which is the convention the Cochrane
# tool itself uses: the domain summary for the main text, and the per trial traffic light for the
# supplement, since 77 rows do not belong in a printed results section.
#
# Risk of bias is a status scale, not a series, so it takes the reserved status palette and ships
# with a glyph and a label in every cell. Colour alone never carries the judgement: a monochrome
# print of this figure remains readable.

rob <- readr::read_csv("analysis/data/risk_of_bias.csv", show_col_types = FALSE)

# The assessed set is larger than the contributing set by exactly the trials held under amendment
# A6 pending the Director's eligibility decision, whose extractions stay in staging. The counts are
# computed here and printed in the caption rather than written into it, so that a figure cannot go
# on claiming 77 contributing trials after a held trial is admitted or dropped.
rob_contributing <- sum(rob$trial_id %in% unique(dat$trial_id))
rob_held <- nrow(rob) - rob_contributing
rob_held_note <- if (rob_held == 1) {
  " One of them contributes no pooled estimate, being held pending an eligibility decision."
} else if (rob_held > 1) {
  sprintf(" %d of them contribute no pooled estimate, being held pending an eligibility decision.",
          rob_held)
} else ""

rob_long <- rob |>
  dplyr::select(trial_id, first_author, year,
                D1 = d1_randomisation, D2 = d2_deviations, D3 = d3_missing,
                D4 = d4_measurement, D5 = d5_selection, Overall = overall) |>
  tidyr::pivot_longer(c(D1, D2, D3, D4, D5, Overall),
                      names_to = "domain", values_to = "judgement") |>
  dplyr::mutate(
    domain = factor(domain, levels = c("D1", "D2", "D3", "D4", "D5", "Overall")),
    judgement = factor(judgement, levels = ROB_LEVELS))

rob_unknown <- dplyr::filter(rob_long, is.na(judgement))
if (nrow(rob_unknown) > 0) {
  stop("risk_of_bias.csv carries ", nrow(rob_unknown), " judgement(s) outside ",
       paste(ROB_LEVELS, collapse = ", "), "; the figure will not invent a level for them",
       call. = FALSE)
}

rob_summary <- rob_long |>
  dplyr::count(domain, judgement) |>
  dplyr::group_by(domain) |>
  dplyr::mutate(share = n / sum(n)) |>
  dplyr::ungroup()

# The overall judgement is set apart from the five domains by a gap, since it is their summary and
# not a sixth domain.
rob_group <- function(domain) ifelse(as.character(domain) == "Overall", "overall", "domains")

fig6 <- ggplot2::ggplot(dplyr::mutate(rob_summary, group = rob_group(domain)),
                        ggplot2::aes(x = share, y = forcats::fct_rev(domain),
                                     fill = judgement)) +
  # reverse = TRUE puts low risk at the left. position_stack stacks in the reverse of the factor
  # order, so the first draft ran high risk first and read right to left against the convention the
  # Cochrane tool itself prints, which costs a reader a second look at every bar.
  ggplot2::geom_col(width = 0.68, colour = "white", linewidth = fig_lw(0.8),
                    position = ggplot2::position_stack(reverse = TRUE)) +
  # Every segment carries its glyph and count, including the three and four trial segments that the
  # first draft left blank because they fell under a six per cent threshold: a status colour with no
  # label beside it is the one thing the status palette may not do. The label takes the ink that
  # contrasts with its segment, white on the high risk red.
  ggplot2::geom_text(ggplot2::aes(label = sprintf("%s %d", ROB_GLYPH[as.character(judgement)], n),
                                  colour = judgement),
                     position = ggplot2::position_stack(vjust = 0.5, reverse = TRUE),
                     size = fig_size(FIG_PT$note), show.legend = FALSE) +
  ggplot2::scale_fill_manual(values = ROB_FILL, labels = ROB_KEY, name = NULL, drop = FALSE) +
  ggplot2::scale_colour_manual(values = ROB_TEXT, guide = "none") +
  ggplot2::scale_x_continuous(labels = scales::label_percent(), breaks = seq(0, 1, 0.25),
                              expand = c(0, 0), name = "Share of assessed trials") +
  ggplot2::scale_y_discrete(labels = c(D1 = "D1 randomisation", D2 = "D2 deviations",
                                       D3 = "D3 missing outcome data",
                                       D4 = "D4 outcome measurement",
                                       D5 = "D5 selective reporting",
                                       Overall = "Overall")) +
  ggplot2::facet_grid(group ~ ., scales = "free_y", space = "free_y") +
  ggplot2::labs(y = NULL) +
  theme_figure() +
  ggplot2::theme(strip.text = ggplot2::element_blank(),
                 panel.grid.major.y = ggplot2::element_blank(),
                 axis.line.y = ggplot2::element_blank(),
                 axis.ticks.y = ggplot2::element_blank(),
                 axis.text.y = ggplot2::element_text(colour = FIG_INK),
                 panel.spacing.y = grid::unit(1.8, "mm"),
                 legend.justification = "left",
                 plot.margin = ggplot2::margin(1.5, 4, 1.5, 1.5, "mm"))

save_figure("figure6_rob_summary", fig6,
            width_mm = FIG_WIDTHS_MM[["double"]], height_mm = 52,
            caption = paste0("Risk of bias across the five RoB-2 domains and the overall ",
                             "judgement, as the share of the ", nrow(rob), " assessed trials.",
                             rob_held_note, " Each segment carries its glyph and trial count, + ",
                             "low, ? some concerns, × high, so the judgement does not depend ",
                             "on colour."),
            data = rob_summary)

fig6s <- ggplot2::ggplot(dplyr::mutate(rob_long, group = rob_group(domain)),
                         ggplot2::aes(x = domain,
                                      y = forcats::fct_rev(factor(trial_id)),
                                      fill = judgement)) +
  ggplot2::geom_tile(colour = "white", linewidth = fig_lw(0.8)) +
  ggplot2::geom_text(ggplot2::aes(label = ROB_GLYPH[as.character(judgement)],
                                  colour = judgement),
                     size = fig_size(FIG_PT$small), show.legend = FALSE) +
  ggplot2::scale_fill_manual(values = ROB_FILL, labels = ROB_KEY, name = NULL, drop = FALSE) +
  ggplot2::scale_colour_manual(values = ROB_TEXT, guide = "none") +
  ggplot2::scale_x_discrete(position = "top", expand = c(0, 0)) +
  ggplot2::scale_y_discrete(expand = c(0, 0)) +
  ggplot2::facet_grid(. ~ group, scales = "free_x", space = "free_x") +
  ggplot2::labs(x = NULL, y = NULL) +
  theme_figure() +
  ggplot2::theme(strip.text = ggplot2::element_blank(),
                 panel.grid.major = ggplot2::element_blank(),
                 axis.line = ggplot2::element_blank(),
                 axis.ticks = ggplot2::element_blank(),
                 axis.text.x.top = ggplot2::element_text(colour = FIG_INK,
                                                         margin = ggplot2::margin(0, 0, 1, 0, "mm")),
                 axis.text.y = ggplot2::element_text(size = FIG_PT$small, colour = FIG_INK,
                                                     margin = ggplot2::margin(0, 1, 0, 0, "mm")),
                 panel.spacing.x = grid::unit(1.4, "mm"),
                 legend.justification = "right")

# A supplementary figure of its own page may take the full page depth: 77 rows do not fit 170 mm at
# a readable size.
save_figure("figureS1_rob_traffic_light", fig6s,
            width_mm = FIG_WIDTHS_MM[["one_and_a_half"]], height_mm = 240,
            max_height_mm = FIG_PAGE_DEPTH_MM,
            caption = paste0("Per trial RoB-2 traffic light for all ", nrow(rob), " assessed ",
                             "trials, supplementary to Figure 6: domains D1 to D5 and the overall ",
                             "judgement, + low, ? some concerns, × high."),
            data = dplyr::select(rob_long, trial_id, domain, judgement))

readr::write_csv(dplyr::bind_rows(FIGURE_INDEX),
                 file.path(OUT_DIR, "figure_index.csv"))


## ---------------------------------------------------------------------------
## 11. RESULT MANIFEST
## ---------------------------------------------------------------------------
# Every output file is listed with its SHA-256 hash. A reviewer can verify that
# the files accompanying the submission are exactly those this script produced,
# and a future reader can confirm that a rerun reproduces identical output.
#
# The writer moved to src/write_manifest.R on 22 October and is sourced here, so that the manifest
# can be refreshed without a twenty minute pipeline run when a generator other than this one
# legitimately rewrites an output. The seventeenth gate regenerates Table 1 from the biomarker
# inventory, and a display name change there left the manifest describing a file that no longer
# existed. That script's header records the whole of it, including why refreshing the manifest does
# not weaken the gate that checks it.

# The warnings of the run, one row each, written before the manifest so that the manifest hashes it;
# a run without warnings writes the header alone (section 0).
readr::write_csv(tibble::tibble(warning = gsub("[\r\n]+", " ", RUN_WARNINGS)),
                 file.path(OUT_DIR, "run_warnings.csv"))
message("  warnings raised by this run: ", length(RUN_WARNINGS))

source(file.path("src", "write_manifest.R"))
manifest <- write_result_manifest(OUT_DIR)

message("Pipeline complete. ", nrow(manifest), " output files written.")
message("Seed: 20261013. Environment captured in ", OUT_DIR, "/session_info.txt.")

###############################################################################
# END OF PIPELINE
###############################################################################
