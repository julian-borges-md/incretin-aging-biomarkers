#!/usr/bin/env Rscript
###############################################################################
# harmonise_units.R
#
# Puts every extracted effect onto one scale before anything is pooled across
# biomarkers.
#
# WHY THIS EXISTS
#
# The extraction carries each effect in whatever units its source reported:
# log ratios from the survodutide analyses, percentage change from the
# tirzepatide and SELECT analyses, U/L from the liver enzymes, index points
# from the fatty liver index. Those standard errors are not comparable
# quantities. Weighting by inverse variance across them weights by how small
# the unit happens to be.
#
# Measured on the raw extraction, this was not a subtle distortion. Two
# glucose markers reported as log ratios would have taken 80 percent of the
# composite (fasting glucose 61 percent, glucagon 19 percent), while hsCRP
# from a 17,604 patient trial contributed effectively nothing. A log ratio
# standard error of 0.047 and a percentage change standard error of 0.97
# differ by a factor of twenty for reasons that have nothing to do with
# precision.
#
# THE COMMON SCALE
#
# Percentage change from baseline, placebo corrected. Chosen because it is
# what most of this literature already reports, so the fewest rows need
# transforming, and because it is interpretable without reference to a
# population standard deviation that these papers mostly do not publish.
#
# Hedges' g would be the conventional choice and is what the protocol named.
# It is not available here: standardising requires the pooled baseline
# standard deviation, and biomarker substudies in this literature report
# treatment contrasts without it. Inventing a standard deviation to enable a
# standardised effect would be worse than using a scale the data support.
# This departure from the protocol is recorded in the manuscript rather than
# made silently.
#
# CONVERSIONS
#
#   log ratio        pct = (exp(yi) - 1) * 100
#                    se_pct = exp(yi) * 100 * se      (delta method)
#
#   percent change   already on scale, carried through unchanged
#
#   absolute (U/L,   pct = 100 * yi / baseline_mean
#   index points)    se_pct = 100 * se / baseline_mean
#                    Requires a reported baseline mean. Rows without one are
#                    marked unconvertible and excluded from cross biomarker
#                    pooling rather than guessed at.
#
# WHAT STAYS UNAFFECTED
#
# Pooling WITHIN a biomarker across trials was always valid when those trials
# reported the same units, and remains so. Only the cross biomarker composite
# and any comparison spanning unit families required this.
###############################################################################

suppressPackageStartupMessages({
  library(dplyr); library(readr)
})

IN  <- "analysis/data/extraction_master.csv"
OUT <- "analysis/data/extraction_master_harmonised.csv"

dat <- readr::read_csv(IN, show_col_types = FALSE, progress = FALSE)

# Baseline means for absolute scale biomarkers.
#
# THIS TABLE IS DELIBERATELY EMPTY.
#
# Converting an absolute effect (U/L, index points) to a percentage requires
# the baseline mean. Meyhofer 2026 reports its liver parameter baselines in a
# table that is referenced in the text but was not available in the retrieved
# full text, so those values are NOT in hand.
#
# While writing this script I filled the table with plausible looking numbers
# (ALT 28, AST 23, GGT 34, FLI 77) that no source supplied. They were removed.
# A fabricated denominator would have silently rescaled four real effects and
# produced percentages that looked entirely reasonable and were invented.
#
# The four SELECT liver rows are therefore marked unconvertible and excluded
# from cross biomarker pooling until the baseline table is obtained from the
# published tables or supplementary material. They remain available for
# within biomarker pooling in their native units, where no conversion is
# needed.
#
# To populate: add a row only with a baseline mean read from a named table in
# a named source, with the locator in baseline_source.
# KEYED BY TRIAL AND BIOMARKER (2026-10-15). The first version was keyed by
# biomarker alone, which would have applied one trial's baseline to every
# trial's absolute rows. A denominator is a property of the trial population
# it was measured in. Every entry below is a value read from a named table,
# or the n weighted mean of the two arms' reported baselines, with the
# arithmetic stated; nothing is estimated from outside the paper.
BASELINE <- tibble::tribble(
  ~trial_id,     ~biomarker,        ~baseline_mean, ~baseline_source,
  # Derosa 2012, Table 3, baseline columns at randomisation, n 85 placebo and 86 exenatide
  "Derosa-2012", "hsCRP",             2.0,    "Derosa 2012 Table 3: 2.0 mg/l in both arms at randomisation",
  "Derosa-2012", "TNF_alpha",         2.30,   "Derosa 2012 Table 3: (2.4*85 + 2.2*86)/171 ng/ml",
  "Derosa-2012", "HOMA_IR",           7.152,  "Derosa 2012 Table 3: (6.9*85 + 7.4*86)/171",
  "Derosa-2012", "HOMA_beta",         96.61,  "Derosa 2012 Table 3: (95.0*85 + 98.2*86)/171",
  "Derosa-2012", "C_peptide",         2.850,  "Derosa 2012 Table 3: (2.8*85 + 2.9*86)/171 nmol/l",
  "Derosa-2012", "glucagon",          63.20,  "Derosa 2012 Table 3: (62.5*85 + 63.9*86)/171 pmol/l",
  "Derosa-2012", "adiponectin",       4.801,  "Derosa 2012 Table 3: (4.7*85 + 4.9*86)/171 ug/ml",
  "Derosa-2012", "fasting_glucose",   7.701,  "Derosa 2012 Table 3: (7.6*85 + 7.8*86)/171 mmol/l",
  "Derosa-2012", "fasting_insulin",   143.77, "Derosa 2012 Table 3: (139.6*85 + 147.9*86)/171 pmol/l",
  # Wu 2011, Table 1 and Table 3, n 12 exenatide and 11 placebo
  "Wu-2011",     "hsCRP",             0.496,  "Wu 2011 Table 3: (0.4*12 + 0.6*11)/23 mg/L",
  "Wu-2011",     "HOMA_IR",           2.757,  "Wu 2011 Results text: (2.9*12 + 2.6*11)/23",
  "Wu-2011",     "fasting_glucose",   8.004,  "Wu 2011 Table 1: (8.1*12 + 7.9*11)/23 mmol/L",
  "Wu-2011",     "fasting_insulin",   7.813,  "Wu 2011 Table 1: (8.1*12 + 7.5*11)/23 uU/mL",
  # Wägner 2019 (LIPER2), Tables 4 and 5, n 12 per arm; CRP converted from mg/dL to mg/L
  "LIPER2",      "hsCRP",             5.15,   "Wägner 2019 Table 5: (0.37*12 + 0.66*12)/24 mg/dL = 0.515 mg/dL = 5.15 mg/L",
  "LIPER2",      "NTproBNP",          46.0,   "Wägner 2019 Table 5: (53.7*12 + 38.3*12)/24 pg/mL",
  "LIPER2",      "fasting_glucose",   176.35, "Wägner 2019 Table 4: (162.8*12 + 189.9*12)/24 mg/dL"
)
stopifnot(!any(duplicated(BASELINE[c("trial_id", "biomarker")])))

LOG_RATIO_ROUTES <- c("log_RR_ci", "log_OR_ci")
PCT_BIOMARKERS   <- c("hsCRP", "IL6", "GDF15", "YKL40", "ICAM1", "leptin",
                      "NTproBNP", "liver_fat_pdff")

# UNIT FAMILY IS A PROPERTY OF THE ROW, NOT OF THE BIOMARKER.
#
# The first version assigned percent_change to every row of a biomarker named
# in PCT_BIOMARKERS. That encoded a convention, "hsCRP is reported as percent
# change", which held for the first two hsCRP sources and failed on the third.
# Simo 2015 (EUREXA) reports hsCRP as an absolute change in mg/L: measure MD,
# arm means with SDs, and the row's own notes say the percentage conversion is
# unavailable. The row was carried through as -1.5 per cent with a standard
# error of 0.34, took 89 per cent of the fixed effect weight for hsCRP, moved
# Table 2's hsCRP from -37.8 (k=2, I2 0) to -23.2 (k=3, I2 99.8) and the
# primary composite from +29.3 to +25.7 per cent. All eight gates passed,
# because no gate compared a row's measure with the unit family it received.
#
# A row whose measure is MD is an absolute difference in the biomarker's own
# units and converts only through a reported baseline mean. The biomarker
# name decides nothing on its own. The counterexample is tested on every run
# so the convention cannot be re-encoded silently.
classify_unit <- function(se_route, measure, biomarker, baseline_mean) {
  dplyr::case_when(
    se_route %in% LOG_RATIO_ROUTES                             ~ "log_ratio",
    !is.na(measure) & measure == "PCT"                         ~ "percent_change",
    !is.na(measure) & measure == "MD" & !is.na(baseline_mean)  ~ "absolute",
    !is.na(measure) & measure == "MD"                          ~ "unknown",
    biomarker %in% PCT_BIOMARKERS                              ~ "percent_change",
    !is.na(baseline_mean)                                      ~ "absolute",
    TRUE                                                       ~ "unknown"
  )
}

# Counterexample tests, run every time. Each case is the shape of a real row.
# The first case is the one that got through.
unit_tests <- tibble::tribble(
  ~case,                                   ~se_route,   ~measure, ~biomarker, ~baseline_mean, ~expect,
  "EUREXA hsCRP, MD in mg/L, no baseline", "arm_sds",   "MD",     "hsCRP",    NA_real_,       "unknown",
  "Wilson hsCRP, percent change, SEMs",    "arm_sems",  NA,       "hsCRP",    NA_real_,       "percent_change",
  "SELECT hsCRP, percent change, CI",      "ci_95",     NA,       "hsCRP",    NA_real_,       "percent_change",
  "SELECT ALT, MD in U/L, no baseline",    "ci_95",     "MD",     "ALT",      NA_real_,       "unknown",
  "ALT, MD in U/L, baseline supplied",     "ci_95",     "MD",     "ALT",      28,             "absolute",
  "survodutide HOMA_IR, log ratio",        "log_RR_ci", "RR",     "HOMA_IR",  NA_real_,       "log_ratio",
  "von Scholten TNF_alpha, PCT with CI",   "ci_95",     "PCT",    "TNF_alpha", NA_real_,      "percent_change",
  "Derosa hsCRP, MD with trial baseline",  "arm_change_imputed_r", "MD", "hsCRP", 2.0,       "absolute"
)
unit_tests$got <- classify_unit(unit_tests$se_route, unit_tests$measure,
                                unit_tests$biomarker, unit_tests$baseline_mean)
bad <- unit_tests[unit_tests$got != unit_tests$expect, ]
if (nrow(bad) > 0) {
  for (i in seq_len(nrow(bad))) {
    message(sprintf("  FAIL  %s: expected %s, got %s",
                    bad$case[i], bad$expect[i], bad$got[i]))
  }
  stop("unit family classification failed its counterexample tests")
}
message(sprintf("UNIT FAMILY SELF TEST: %d of %d row shapes classified as expected",
                nrow(unit_tests), nrow(unit_tests)))

if (!"measure" %in% names(dat)) dat$measure <- NA_character_

# Second source of a denominator (2026-10-16, systematic corpus): the row's own baseline means,
# base_mean_tx and base_mean_ctrl, copied by the extractor from the paper's baseline table (the
# extraction brief requires them for every absolute difference row). The pooled baseline is the
# n weighted mean of the two arms when both means and both n are present, the simple mean when the
# n are missing, and the one arm's mean when only one is reported. The hand keyed BASELINE table
# above keeps precedence, so every entry made under amendment R1 is unchanged; the source of each
# denominator is recorded in baseline_source either way.
num <- function(x) suppressWarnings(as.numeric(x))
for (cl in c("base_mean_tx", "base_mean_ctrl", "n_tx", "n_ctrl")) {
  if (!cl %in% names(dat)) dat[[cl]] <- NA_real_
}
dat <- dat |>
  mutate(
    .btx = num(base_mean_tx), .bct = num(base_mean_ctrl), .ntx = num(n_tx), .nct = num(n_ctrl),
    row_baseline = case_when(
      !is.na(.btx) & !is.na(.bct) & !is.na(.ntx) & !is.na(.nct) & (.ntx + .nct) > 0 ~
        (.btx * .ntx + .bct * .nct) / (.ntx + .nct),
      !is.na(.btx) & !is.na(.bct) ~ (.btx + .bct) / 2,
      !is.na(.btx) ~ .btx,
      !is.na(.bct) ~ .bct,
      TRUE ~ NA_real_
    )
  ) |>
  left_join(BASELINE, by = c("trial_id", "biomarker")) |>
  mutate(
    baseline_source = case_when(
      !is.na(baseline_mean) ~ baseline_source,
      !is.na(row_baseline) ~ "row base_mean_tx and base_mean_ctrl from the extraction (n weighted when n given)",
      TRUE ~ NA_character_
    ),
    baseline_mean = coalesce(baseline_mean, row_baseline)
  ) |>
  select(-.btx, -.bct, -.ntx, -.nct, -row_baseline) |>
  mutate(
    se_native = sqrt(vi),
    unit_family = classify_unit(se_route, measure, biomarker, baseline_mean),
    yi_pct = case_when(
      unit_family == "log_ratio"      ~ (exp(yi) - 1) * 100,
      unit_family == "percent_change" ~ yi,
      unit_family == "absolute"       ~ 100 * yi / baseline_mean,
      TRUE                            ~ NA_real_
    ),
    se_pct = case_when(
      unit_family == "log_ratio"      ~ exp(yi) * 100 * se_native,
      unit_family == "percent_change" ~ se_native,
      unit_family == "absolute"       ~ 100 * se_native / baseline_mean,
      TRUE                            ~ NA_real_
    ),
    vi_pct = se_pct^2
  )

# A percent_change row must not carry an MD or RR measure: MD is an absolute
# difference and RR a ratio, and either reaching the percent scale unchanged
# is the EUREXA defect recurring. Fails the run rather than the row.
mislabelled <- filter(dat, unit_family == "percent_change",
                      !is.na(measure), measure %in% c("MD", "RR"))
if (nrow(mislabelled) > 0) {
  for (i in seq_len(nrow(mislabelled))) {
    message(sprintf("  FAIL  %s / %s: measure %s assigned percent_change",
                    mislabelled$trial_id[i], mislabelled$biomarker[i],
                    mislabelled$measure[i]))
  }
  stop("a row with an absolute or ratio measure was assigned the percent scale")
}

unconvertible <- filter(dat, is.na(yi_pct))
if (nrow(unconvertible) > 0) {
  message("\nUNCONVERTIBLE ROWS, excluded from cross biomarker pooling:")
  unconvertible |>
    count(trial_id, biomarker, measure, unit_family, name = "rows") |>
    as.data.frame() |>
    print(row.names = FALSE)
  message("  Reason: absolute units (measure MD) with no reported baseline mean.")
  message("  These rows keep their native yi and se for within biomarker use.")
}

message("\nHARMONISED EFFECTS, one row per biomarker shown")
message(sprintf("%-20s %-15s %10s %9s %10s %9s",
                "biomarker", "unit family", "yi native", "se nat", "yi pct", "se pct"))
message(strrep("-", 78))
dat |>
  group_by(biomarker) |>
  slice(1) |>
  ungroup() |>
  arrange(unit_family, biomarker) |>
  rowwise() |>
  do({
    r <- .
    message(sprintf("%-20s %-15s %10.3f %9.4f %10.2f %9.4f",
                    r$biomarker, r$unit_family, r$yi, r$se_native,
                    ifelse(is.na(r$yi_pct), NA_real_, r$yi_pct),
                    ifelse(is.na(r$se_pct), NA_real_, r$se_pct)))
    data.frame()
  }) |>
  invisible()

# Show the weight redistribution the harmonisation produces. This is the
# diagnostic that exposed the problem and it is kept as a standing check.
share <- function(v) { w <- 1 / v; 100 * w / sum(w, na.rm = TRUE) }

cmp <- dat |>
  filter(!is.na(vi_pct)) |>
  group_by(biomarker) |>
  summarise(vi_nat = 1 / sum(1 / vi, na.rm = TRUE),
            vi_har = 1 / sum(1 / vi_pct, na.rm = TRUE), .groups = "drop") |>
  mutate(before = share(vi_nat), after = share(vi_har)) |>
  arrange(desc(before))

message("\nCOMPOSITE WEIGHT SHARE, before and after harmonisation")
message(sprintf("%-20s %8s %8s", "biomarker", "before", "after"))
message(strrep("-", 40))
for (i in seq_len(nrow(cmp))) {
  message(sprintf("%-20s %7.2f%% %7.2f%%",
                  cmp$biomarker[i], cmp$before[i], cmp$after[i]))
}

readr::write_csv(dat, OUT)
message(sprintf("\nWrote %s  (%d rows, %d convertible)",
                OUT, nrow(dat), sum(!is.na(dat$yi_pct))))
