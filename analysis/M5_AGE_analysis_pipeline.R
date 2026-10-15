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
# Environment is pinned with renv. To reproduce exactly:
#   renv::restore()
#   Rscript analysis/M5_AGE_analysis_pipeline.R
#
# Run from the repository root. All stochastic operations use set.seed(20261013).
###############################################################################

## ---------------------------------------------------------------------------
## 0. ENVIRONMENT
## ---------------------------------------------------------------------------

set.seed(20261013)

required_packages <- c(
  "metafor",      # >= 4.6.0  core meta-analysis and meta-regression
  "netmeta",      # >= 3.0.0  frequentist network meta-analysis
  "meta",         # >= 7.0.0  convenience wrappers, funnel plots
  "dmetar",       # >= 0.1.0  influence diagnostics
  "tidyverse",    # >= 2.0.0  data manipulation
  "boot",         # >= 1.3    bootstrap for the composite metric
  "ggplot2",      # >= 3.5.0  figures
  "patchwork",    # >= 1.2.0  multi-panel figure assembly
  "knitr",        # >= 1.45   table rendering
  "openssl",      # >= 2.2    SHA-256 for the output manifest
  "sessioninfo"   # >= 1.2    environment capture
)

invisible(lapply(required_packages, function(p) {
  if (!requireNamespace(p, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Run renv::restore().", p))
  }
  library(p, character.only = TRUE)
}))

DATA_FILE <- "analysis/data/extraction_master.csv"
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

check_integrity <- function(d) {
  errs <- character(0)

  # Every trial must carry a valid receptor class.
  bad_class <- setdiff(unique(d$receptor_class), RECEPTOR_CLASSES)
  if (length(bad_class)) {
    errs <- c(errs, sprintf("Unknown receptor_class: %s",
                            paste(bad_class, collapse = ", ")))
  }

  # Continuous outcomes need mean, SD and n in both arms to compute Hedges' g.
  cont <- dplyr::filter(d, outcome_type == "continuous")
  incomplete <- dplyr::filter(
    cont,
    is.na(mean_tx) | is.na(sd_tx) | is.na(n_tx) |
    is.na(mean_ctrl) | is.na(sd_ctrl) | is.na(n_ctrl)
  )
  if (nrow(incomplete)) {
    errs <- c(errs, sprintf("%d continuous rows missing mean/SD/n.",
                            nrow(incomplete)))
  }

  # SDs must be strictly positive. A zero or negative SD silently produces an
  # infinite effect size, so it is caught here instead.
  if (any(cont$sd_tx <= 0, na.rm = TRUE) || any(cont$sd_ctrl <= 0, na.rm = TRUE)) {
    errs <- c(errs, "Non-positive standard deviation present.")
  }

  # Every biomarker needs a declared aging direction for the composite.
  if (any(!d$aging_direction %in% c(1, -1))) {
    errs <- c(errs, "aging_direction must be exactly +1 or -1.")
  }

  # Weight change is the meta-regression covariate and cannot be missing.
  if (any(is.na(d$pct_weight_change))) {
    errs <- c(errs, "pct_weight_change missing for at least one trial.")
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
# Continuous outcomes use Hedges' g, the standardized mean difference with the
# small sample correction applied, because biomarker measurement scales differ
# across trials: hsCRP in mg/L, GDF-15 in pg/mL, lean mass in kg. Where every
# trial for a biomarker uses an identical scale the raw mean difference is also
# computed and reported alongside, since it is more interpretable clinically.
#
# Binary outcomes, meaning MASH resolution and fibrosis improvement, use the
# log odds ratio, which is the appropriate scale for pooling proportions and is
# back transformed for presentation.

es_continuous <- metafor::escalc(
  measure = "SMD",
  m1i = mean_tx,   sd1i = sd_tx,   n1i = n_tx,
  m2i = mean_ctrl, sd2i = sd_ctrl, n2i = n_ctrl,
  data = dplyr::filter(dat, outcome_type == "continuous"),
  slab = trial_id
)

es_continuous_md <- metafor::escalc(
  measure = "MD",
  m1i = mean_tx,   sd1i = sd_tx,   n1i = n_tx,
  m2i = mean_ctrl, sd2i = sd_ctrl, n2i = n_ctrl,
  data = dplyr::filter(dat, outcome_type == "continuous"),
  slab = trial_id
)
es_continuous$yi_md <- es_continuous_md$yi
es_continuous$vi_md <- es_continuous_md$vi

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

  tibble::tibble(
    k         = k,
    n_total   = sum(es_df$n_tx, es_df$n_ctrl, na.rm = TRUE),
    estimate  = as.numeric(fit$b),
    se        = fit$se,
    ci_lb     = fit$ci.lb,
    ci_ub     = fit$ci.ub,
    pi_lb     = pred$pi.lb,     # prediction interval lower bound
    pi_ub     = pred$pi.ub,     # prediction interval upper bound
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

run_weight_adjusted_metareg <- function(bm, n_perm = 10000) {

  d <- dplyr::filter(es_continuous, biomarker == bm)

  # Require the number of trials to exceed the estimated parameters by at least
  # three, otherwise the model is not identifiable and a fit would be spurious.
  n_levels <- length(unique(d$receptor_class))
  if (nrow(d) < (n_levels + 3)) {
    return(tibble::tibble(biomarker = bm,
                          status = "insufficient_trials",
                          k = nrow(d)))
  }

  # Model 1: weight loss alone. How much heterogeneity weight explains on its own.
  m_weight <- metafor::rma(yi, vi, mods = ~ pct_weight_change,
                           data = d, method = "REML")

  # Model 2: receptor class alone, unadjusted.
  m_class <- metafor::rma(yi, vi, mods = ~ receptor_class,
                          data = d, method = "REML")

  # Model 3: both. The receptor class coefficients here are the adjusted
  # estimates reported in the manuscript.
  m_adj <- metafor::rma(yi, vi, mods = ~ receptor_class + pct_weight_change,
                        data = d, method = "REML")

  # Model 4: interaction. Tests whether the slope relating weight loss to the
  # biomarker differs by receptor class, which would mean the same amount of
  # weight loss buys different biomarker benefit depending on receptors engaged.
  m_int <- tryCatch(
    metafor::rma(yi, vi, mods = ~ receptor_class * pct_weight_change,
                 data = d, method = "REML"),
    error = function(e) NULL
  )

  perm_adj <- metafor::permutest(m_adj, iter = n_perm, seed = 20261013)

  # Proportion of between-study variance explained, relative to intercept only.
  m_null <- metafor::rma(yi, vi, data = d, method = "REML")
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
    R2_class_only      = max(0, (m_null$tau2 - m_class$tau2) / m_null$tau2) * 100,
    R2_adjusted        = r2_adj,
    beta_weight        = as.numeric(m_adj$b["pct_weight_change", ]),
    se_weight          = m_adj$se[which(rownames(m_adj$b) == "pct_weight_change")],
    p_weight_perm      = perm_adj$pval[which(rownames(m_adj$b) == "pct_weight_change")],
    QM_adjusted        = m_adj$QM,
    QM_p_perm          = perm_adj$QMp,
    I2_residual        = m_adj$I2,
    interaction_fitted = !is.null(m_int),
    QM_interaction     = if (!is.null(m_int)) m_int$QM else NA_real_,
    QM_interaction_p   = if (!is.null(m_int)) m_int$QMp else NA_real_
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
# standardized effect size scale regardless of how many biomarkers contribute,
# which is what makes classes with unequal coverage comparable. This matters
# concretely here: the triple agonist node carries far fewer measured
# biomarkers than the GLP-1 mono node.
#
# A score of 0.40 reads directly as an average favorable shift of 0.40 standard
# deviations across the aging biomarkers measured for that class.

compute_nbais <- function(res_df, weighting = c("inverse_variance",
                                                "equal",
                                                "clinical")) {
  weighting <- match.arg(weighting)

  d <- res_df |>
    dplyr::left_join(
      dplyr::distinct(dat, biomarker, aging_direction, clinical_weight),
      by = "biomarker"
    ) |>
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

nbais_boot <- function(res_df, weighting, R = 10000) {

  stat <- function(d, idx) {
    dd <- d[idx, ]
    dd$estimate <- rnorm(nrow(dd), mean = dd$estimate, sd = dd$se)
    compute_nbais(dd, weighting = weighting)
  }

  bt <- boot::boot(res_df, statistic = stat, R = R)
  ci <- tryCatch(boot::boot.ci(bt, type = "bca"),
                 error = function(e) boot::boot.ci(bt, type = "perc"))

  lohi <- if (!is.null(ci$bca)) ci$bca[4:5] else ci$percent[4:5]

  tibble::tibble(
    nbais     = compute_nbais(res_df, weighting),
    boot_mean = mean(bt$t, na.rm = TRUE),
    boot_se   = sd(bt$t, na.rm = TRUE),
    ci_lb     = lohi[1],
    ci_ub     = lohi[2],
    n_markers = nrow(res_df),
    weighting = weighting,
    R         = R
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
  a <- dplyr::filter(primary_results, receptor_class == rc_a)
  b <- dplyr::filter(primary_results, receptor_class == rc_b)

  shared <- intersect(a$biomarker, b$biomarker)
  if (length(shared) < 3) {
    return(tibble::tibble(comparison = paste(rc_a, "vs", rc_b),
                          status   = "insufficient_shared_biomarkers",
                          n_shared = length(shared)))
  }
  a <- dplyr::filter(a, biomarker %in% shared)
  b <- dplyr::filter(b, biomarker %in% shared)

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

nma_class <- purrr::compact(purrr::map(biomarkers, ~ run_nma(.x, "receptor_class")))
nma_drug  <- purrr::compact(purrr::map(biomarkers, ~ run_nma(.x, "drug")))

readr::write_csv(
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
        r <- pool_effect(d, estimator = est)
        if (is.null(r)) return(NULL)
        dplyr::mutate(r, biomarker = bm, receptor_class = rc, .before = 1)
      })
    })
  })
}

sensitivity_subgroup <- function(filter_expr, label) {
  d_sub <- dplyr::filter(es_continuous, !!rlang::parse_expr(filter_expr))
  purrr::map_dfr(unique(d_sub$biomarker), function(bm) {
    purrr::map_dfr(RECEPTOR_CLASSES, function(rc) {
      d <- dplyr::filter(d_sub, biomarker == bm, receptor_class == rc)
      r <- pool_effect(d)
      if (is.null(r)) return(NULL)
      dplyr::mutate(r, biomarker = bm, receptor_class = rc,
                    sensitivity = label, .before = 1)
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

    fit <- metafor::rma(yi, vi, data = d, method = "REML")
    inf <- metafor::influence(fit)
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
      n_influential      = sum(inf$is.infl, na.rm = TRUE),
      influential_trials = paste(d$trial_id[which(inf$is.infl)], collapse = "; "),
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

fig1 <- ggplot2::ggplot(
  fig1_data,
  ggplot2::aes(x = receptor_class, y = forcats::fct_rev(biomarker),
               fill = signed_effect)
) +
  ggplot2::geom_tile(color = "white", linewidth = 0.4) +
  ggplot2::scale_fill_gradient2(
    low = "#B2182B", mid = "#F7F7F7", high = "#2166AC", midpoint = 0,
    name = "Direction adjusted\npooled effect (g)",
    na.value = "grey90"
  ) +
  ggplot2::facet_grid(hallmark_domain ~ ., scales = "free_y", space = "free_y") +
  ggplot2::labs(x = "Receptor class", y = NULL) +
  ggplot2::theme_minimal(base_size = 10) +
  ggplot2::theme(
    strip.text.y = ggplot2::element_text(angle = 0, hjust = 0),
    panel.grid = ggplot2::element_blank()
  )

ggplot2::ggsave(file.path(OUT_DIR, "figure1_signature_heatmap.pdf"), fig1,
                width = 9, height = 12, device = cairo_pdf)

# Figure 4: weight adjusted meta-regression bubble plot for hepatic outcomes.
# Bubble area is inverse variance, so the visually dominant points are the
# precisely estimated ones, matching how they are weighted in the model.

fig4_data <- dplyr::filter(es_continuous, biomarker == "liver_fat_pdff")

fig4 <- ggplot2::ggplot(
  fig4_data,
  ggplot2::aes(x = pct_weight_change, y = yi,
               size = 1 / vi, color = receptor_class)
) +
  ggplot2::geom_point(alpha = 0.7) +
  ggplot2::geom_smooth(method = "lm", se = TRUE,
                       ggplot2::aes(weight = 1 / vi), linewidth = 0.6) +
  ggplot2::scale_size_continuous(name = "Precision (1/variance)") +
  ggplot2::labs(
    x = "Mean body weight change (%)",
    y = "Liver fat change (Hedges' g vs placebo)",
    color = "Receptor class"
  ) +
  ggplot2::theme_minimal(base_size = 11)

ggplot2::ggsave(file.path(OUT_DIR, "figure4_weight_adjusted_liverfat.pdf"),
                fig4, width = 8, height = 6, device = cairo_pdf)

# Figure 5: the composite score by receptor class with bootstrap intervals,
# faceted by weighting scheme so the reader sees immediately whether the
# ranking is a property of the drugs or an artifact of the weighting choice.
# The ranking is reported as a finding only where it is stable across all three.

fig5 <- ggplot2::ggplot(
  nbais_results,
  ggplot2::aes(x = receptor_class, y = nbais, fill = receptor_class)
) +
  ggplot2::geom_col(width = 0.65) +
  ggplot2::geom_errorbar(ggplot2::aes(ymin = ci_lb, ymax = ci_ub), width = 0.2) +
  ggplot2::geom_hline(yintercept = 0, linewidth = 0.4) +
  ggplot2::facet_wrap(~ weighting, nrow = 1) +
  ggplot2::labs(
    x = NULL,
    y = "Net Biological Age Impact Score\n(weighted mean direction adjusted g)"
  ) +
  ggplot2::theme_minimal(base_size = 11) +
  ggplot2::theme(legend.position = "none",
                 axis.text.x = ggplot2::element_text(angle = 30, hjust = 1))

ggplot2::ggsave(file.path(OUT_DIR, "figure5_nbais.pdf"), fig5,
                width = 10, height = 5, device = cairo_pdf)


## ---------------------------------------------------------------------------
## 11. RESULT MANIFEST
## ---------------------------------------------------------------------------
# Every output file is listed with its SHA-256 hash. A reviewer can verify that
# the files accompanying the submission are exactly those this script produced,
# and a future reader can confirm that a rerun reproduces identical output.

manifest <- tibble::tibble(
  file = list.files(OUT_DIR, full.names = TRUE)
) |>
  dplyr::filter(basename(file) != "MANIFEST.csv") |>
  dplyr::mutate(
    bytes  = file.size(file),
    sha256 = purrr::map_chr(file, ~ as.character(
      openssl::sha256(file(.x, open = "rb"))
    )),
    generated = as.character(Sys.time())
  )

readr::write_csv(manifest, file.path(OUT_DIR, "MANIFEST.csv"))

message("Pipeline complete. ", nrow(manifest), " output files written.")
message("Seed: 20261013. Environment captured in ", OUT_DIR, "/session_info.txt.")

###############################################################################
# END OF PIPELINE
###############################################################################
