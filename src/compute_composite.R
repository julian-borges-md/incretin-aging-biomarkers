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

INCLUDED <- c("hsCRP","IL6","YKL40","GDF15","ICAM1","GGT",
              "liver_fat_pdff","leptin","HOMA_IR","NTproBNP","lean_mass")

DIR <- c(hsCRP=-1, IL6=-1, YKL40=-1, GDF15=-1, ICAM1=-1, GGT=-1,
         liver_fat_pdff=-1, leptin=-1, HOMA_IR=-1, NTproBNP=-1,
         lean_mass=1, adiponectin=1, HOMA_beta=1,
         fasting_glucose=-1, fasting_insulin=-1, C_peptide=-1,
         glucagon=-1, ALT=-1, AST=-1, fatty_liver_index=-1)

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

composite <- function(d, label, weighting = "equal") {
  d <- d |> filter(biomarker %in% names(DIR))
  if (nrow(d) == 0)
    return(tibble(analysis=label, k=0L, score=NA_real_, lo=NA_real_,
                  hi=NA_real_, max_share=NA_real_, dominant=NA_character_))
  per <- d |>
    group_by(biomarker) |>
    summarise(yi = weighted.mean(yi_pct, 1/vi_pct),
              vi = 1/sum(1/vi_pct), .groups="drop") |>
    mutate(signed = DIR[biomarker] * yi,
           w = if (weighting == "equal") 1 else 1/vi,
           share = 100 * w / sum(w))
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

per <- dat |>
  filter(biomarker %in% AVAILABLE) |>
  group_by(biomarker) |>
  summarise(yi = weighted.mean(yi_pct, 1/vi_pct), vi = 1/sum(1/vi_pct), .groups="drop") |>
  mutate(signed = DIR[biomarker]*yi,
         w_eq = 1, share_eq = 100/n(),
         w_iv = 1/vi, share_iv = 100*w_iv/sum(w_iv)) |>
  arrange(desc(share_iv))

message("\nPER MARKER, primary analysis")
message(sprintf("%-18s %10s %10s %10s %10s", "biomarker", "effect", "signed", "eq wt", "iv wt"))
message(strrep("-", 62))
for (i in seq_len(nrow(per))) {
  r <- per[i,]
  message(sprintf("%-18s %9.1f%% %9.1f%% %9.1f%% %9.1f%%",
                  r$biomarker, r$yi, r$signed, r$share_eq, r$share_iv))
}

readr::write_csv(results, "analysis/output/table5_composite.csv")
readr::write_csv(per, "analysis/output/table5b_composite_contributions.csv")
message("\nWrote table5_composite.csv and table5b_composite_contributions.csv")
