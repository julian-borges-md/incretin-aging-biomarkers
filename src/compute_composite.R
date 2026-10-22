#!/usr/bin/env Rscript
###############################################################################
# compute_composite.R
#
# Computes the composite under prespecification/nbais_inclusion_rule.md,
# with the sensitivity analyses that rule requires.
#
# TWO DESIGN POINTS, both forced by what the first run revealed.
#
# COVERAGE. The inclusion rule names 11 markers. Two (lean_mass, GGT) are not
# in the harmonised data: lean mass has never been extracted, GGT is present
# but unconvertible for want of a baseline mean. The first version computed a
# 9 marker composite while reporting 11, and its "without lean mass"
# sensitivity returned a figure identical to the primary because lean mass was
# never in it. Both looked like clean output. k is now reported on every row
# and absent markers are named.
#
# WEIGHTING. Inverse variance across BIOMARKERS weights by how precisely each
# happened to be measured, not by importance. hsCRP comes from SELECT with
# 17,604 participants and takes 85 per cent of the composite, making the score
# hsCRP with decoration. Equal weighting answers the question the composite is
# for: across the aging domains measured, how far did they move on average.
# Equal weighting is primary; inverse variance is reported alongside so the
# difference is visible.
###############################################################################

suppressPackageStartupMessages({ library(dplyr); library(readr) })
set.seed(20261013)

dat <- readr::read_csv("analysis/data/extraction_master_harmonised.csv",
                       show_col_types = FALSE, progress = FALSE) |>
  filter(!is.na(yi_pct), !is.na(vi_pct), vi_pct > 0) |>
  group_by(trial_id, biomarker) |>
  slice_max(order_by = dose_mg, n = 1, with_ties = FALSE) |>
  ungroup()

# The admitted marker set is read from analysis/data/nbais_inclusion_set.csv, which is the one
# declaration of prespecification/nbais_inclusion_rule.md in the repository. It was a literal vector
# here until 22 October, and the analysis pipeline read that vector out of this file by parsing it,
# because restating eleven marker names in a second script is the defect that has bitten this
# repository three times. Parsing a sibling script was a working arrangement and not the right one:
# a declaration that two programs depend on belongs in data that both read, not in the source of one
# of them. The file carries the hallmark domain and surrogacy grade of each marker and the reason it
# is retained, so the rule and its justification travel together.
INCLUDED <- readr::read_csv("analysis/data/nbais_inclusion_set.csv",
                            show_col_types = FALSE, progress = FALSE)$biomarker
stopifnot(length(INCLUDED) >= 2, !any(duplicated(INCLUDED)))

DIR <- c(hsCRP=-1, IL6=-1, YKL40=-1, GDF15=-1, ICAM1=-1, GGT=-1,
         liver_fat_pdff=-1, leptin=-1, HOMA_IR=-1, NTproBNP=-1,
         lean_mass=1, adiponectin=1, HOMA_beta=1,
         fasting_glucose=-1, fasting_insulin=-1, C_peptide=-1,
         glucagon=-1, ALT=-1, AST=-1, fatty_liver_index=-1,
         # added 2026-10-15 (amendment R2): both lower is better; neither is in
         # the composite inclusion rule, so they affect S3 only
         TNF_alpha=-1, MR_proANP=-1)

missing   <- setdiff(INCLUDED, unique(dat$biomarker))
AVAILABLE <- intersect(INCLUDED, unique(dat$biomarker))

message("COVERAGE")
message(sprintf("  inclusion rule names %d markers; %d available, %d absent",
                length(INCLUDED), length(AVAILABLE), length(missing)))
if (length(missing)) {
  for (m in missing) {
    why <- if (m == "lean_mass") "never extracted" else "unconvertible, no baseline mean"
    message(sprintf("    ABSENT  %-16s %s", m, why))
  }
}

# PER MARKER INPUTS COME FROM TABLE 2 (2026-10-15).
#
# The first version pooled each marker's trials with a fixed effect inverse
# variance mean inside this script. The analysis plan names REML random
# effects with the Hartung Knapp correction as the primary estimator, and
# pool_biomarkers.R already produces exactly that in Table 2. Once a marker
# had heterogeneous trials the two diverged (hsCRP: fixed effect -36.9 against
# REML -26.4 with five trials), which means the composite was being built on
# an estimator the plan does not name. Each marker's estimate and standard
# error are now read from Table 2, so the composite and Table 2 cannot
# disagree, and the fixed effect figure is kept only as a printed diagnostic.
t2_path <- "analysis/output/table2_pooled_by_biomarker.csv"
if (!file.exists(t2_path)) {
  stop("Table 2 not found: run pool_biomarkers.R first; the composite is built on its REML estimates")
}
T2 <- readr::read_csv(t2_path, show_col_types = FALSE, progress = FALSE) |>
  select(biomarker, k_t2 = k, est_t2 = est, se_t2 = se)
if (any(is.na(T2$se_t2) & !is.na(T2$est_t2))) stop("Table 2 carries an estimate without a standard error")

composite <- function(d, label, weighting = "equal") {
  d <- d |> filter(biomarker %in% names(DIR))
  if (nrow(d) == 0)
    return(tibble(analysis=label, k=0L, score=NA_real_, lo=NA_real_,
                  hi=NA_real_, max_share=NA_real_, dominant=NA_character_))
  per <- T2 |>
    filter(biomarker %in% unique(d$biomarker), !is.na(est_t2)) |>
    transmute(biomarker, yi = est_t2, vi = se_t2^2) |>
    mutate(signed = DIR[biomarker] * yi,
           w = if (weighting == "equal") 1 else 1/vi,
           share = 100 * w / sum(w))
  dropped <- setdiff(unique(d$biomarker), per$biomarker)
  if (length(dropped) > 0)
    message(sprintf("  NOTE  %s: no Table 2 estimate for %s; excluded from this analysis",
                    label, paste(dropped, collapse = ", ")))
  score <- sum(per$signed * per$w) / sum(per$w)
  se <- if (weighting == "equal") sqrt(sum(per$vi))/nrow(per) else sqrt(1/sum(per$w))
  # with_ties = FALSE: under equal weighting every share is identical, and
  # slice_max would otherwise return every marker, duplicating the result row
  # once per marker.
  top <- per |> slice_max(share, n=1, with_ties=FALSE)
  tibble(analysis=label, k=nrow(per), score=score,
         lo=score-1.96*se, hi=score+1.96*se,
         max_share=top$share, dominant=top$biomarker)
}

results <- bind_rows(
  composite(filter(dat, biomarker %in% AVAILABLE), "Primary, equal weights"),
  composite(filter(dat, biomarker %in% AVAILABLE), "Primary, inverse variance", "inverse_variance"),
  composite(filter(dat, biomarker %in% c("hsCRP","IL6","NTproBNP")), "S2 B0-B2 core only"),
  composite(dat, "S3 all markers, original spec"),
  composite(filter(dat, biomarker %in% c(AVAILABLE,"adiponectin")), "S4 plus adiponectin")
)

message("\nCOMPOSITE, placebo corrected percentage change, direction adjusted")
message("positive = favourable\n")
message(sprintf("%-32s %3s %9s %19s %22s", "analysis", "k", "score", "95% CI", "largest contributor"))
message(strrep("-", 92))
for (i in seq_len(nrow(results))) {
  r <- results[i,]
  message(sprintf("%-32s %3d %8.2f%% %8.2f to %-7.2f %12s %5.1f%%",
                  r$analysis, r$k, r$score, r$lo, r$hi, r$dominant, r$max_share))
}

message("\nS1 without lean mass: NOT EVALUABLE, lean mass is absent from the data.")

per <- T2 |>
  filter(biomarker %in% AVAILABLE, !is.na(est_t2)) |>
  transmute(biomarker, k = k_t2, yi = est_t2, vi = se_t2^2) |>
  mutate(signed = DIR[biomarker]*yi,
         w_eq = 1, share_eq = 100/n(),
         w_iv = 1/vi, share_iv = 100*w_iv/sum(w_iv)) |>
  arrange(desc(share_iv))

# Fixed effect inverse variance means, kept as a diagnostic against Table 2.
fe <- dat |>
  filter(biomarker %in% AVAILABLE) |>
  group_by(biomarker) |>
  summarise(yi_fe = weighted.mean(yi_pct, 1/vi_pct), .groups="drop")

message("\nPER MARKER, primary analysis (estimates from Table 2, REML plus Hartung Knapp)")
message(sprintf("%-18s %10s %10s %10s %10s", "biomarker", "effect", "signed", "eq wt", "iv wt"))
message(strrep("-", 62))
for (i in seq_len(nrow(per))) {
  r <- per[i,]
  message(sprintf("%-18s %9.1f%% %9.1f%% %9.1f%% %9.1f%%",
                  r$biomarker, r$yi, r$signed, r$share_eq, r$share_iv))
}

# ESTIMATOR CONSISTENCY WITH TABLE 2.
#
# The per marker input to the composite is a fixed effect inverse variance
# mean across trials. Table 2 (pool_biomarkers.R) reports a REML random
# effects estimate with the Hartung Knapp adjustment. The two coincide when a
# marker has one trial or I2 is zero, and diverge otherwise. Found on
# 2026-10-15 when a mis-harmonised hsCRP row gave -5.5 here against -23.2 in
# Table 2 with nothing in the output to show the two disagreed. The divergence
# is now printed on every run so it can never be silent again. It is a NOTE,
# not a failure: which estimator should feed the composite is a protocol
# decision, recorded in prespecification/, not something this script decides.
cmp <- per |>
  inner_join(fe, by = "biomarker") |>
  mutate(diff = yi_fe - yi) |>
  filter(k >= 2)
message("\nFIXED EFFECT MEAN vs TABLE 2 INPUT, markers pooled from two or more trials")
message(sprintf("%-18s %3s %12s %12s %10s", "biomarker", "k", "FE mean", "T2 REML/HK", "diff"))
message(strrep("-", 60))
for (i in seq_len(nrow(cmp))) {
  r <- cmp[i,]
  flag <- if (abs(r$diff) > 1) "  NOTE divergent, I2 > 0; Table 2 value used" else ""
  message(sprintf("%-18s %3d %11.1f%% %11.1f%% %9.1f%%%s",
                  r$biomarker, r$k, r$yi_fe, r$yi, r$diff, flag))
}
if (nrow(cmp) == 0) message("  none")

readr::write_csv(results, "analysis/output/table5_composite.csv")
readr::write_csv(per, "analysis/output/table5b_composite_contributions.csv")
message("\nWrote table5_composite.csv and table5b_composite_contributions.csv")
