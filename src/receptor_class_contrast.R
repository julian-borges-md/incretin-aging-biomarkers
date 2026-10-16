#!/usr/bin/env Rscript
###############################################################################
# receptor_class_contrast.R
#
# Q2: does the aging biomarker signature differ by receptor class?
#
# This is the review's central claim to novelty. Neither existing meta-analysis
# of this drug class (Ren 2025, 52 RCTs; Alrasheed 2026, 40 RCTs) stratifies by
# receptor pharmacology.
#
# The script reports what the current corpus can and cannot support, by
# biomarker, rather than producing a class contrast wherever arithmetic is
# possible. A contrast computed from one trial per class is a difference
# between two studies, not a class effect, and will be labelled as such.
###############################################################################

suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
set.seed(20261013)

dat <- readr::read_csv("analysis/data/extraction_master_harmonised.csv",
                       show_col_types = FALSE, progress = FALSE) |>
  filter(!is.na(yi_pct), !is.na(vi_pct), vi_pct > 0) |>
  group_by(trial_id, biomarker) |>
  slice_max(order_by = dose_mg, n = 1, with_ties = FALSE) |>
  ungroup()

## ---------------------------------------------------------------------------
## 0. Comparator restriction, protocol amendment of 2026-10-15
## ---------------------------------------------------------------------------
# Class contrasts are computed within placebo controlled trials only
# (docs/COMPARATOR_PROBLEM.md). Glimepiride causes weight gain, so an active
# controlled contrast is larger than a placebo controlled one for any marker
# that tracks adiposity, and the mono class is mostly active controlled while
# every dual and triple row is placebo controlled. Pooling across comparator
# types would measure comparator choice, not receptor pharmacology.
#
# The amendment was written on 2026-10-15 and, until this block, had no code
# behind it: EUREXA (exenatide vs glimepiride) was being counted toward mono
# class coverage. Declarative rules do not restrict anything. This does.
# A13 (2026-10-16): the first version of this test compared the free text comparator field with the
# single word "placebo", which silently excluded four placebo controlled trials whose comparator text
# is descriptive ("placebo added to standard care", "visually matching placebo", "placebo
# (canagliflozin and combination arms not entered)") and so dropped 18 mono class rows from every
# class contrast. The schema already carries the controlled vocabulary in comparator_type, so that
# column decides when it is present and the string test remains the fallback for rows that predate
# the column. Deciding a restriction from free text is the error; the vocabulary exists for this.
is_placebo_controlled <- function(comparator, comparator_type = NULL) {
  txt <- !is.na(comparator) & grepl("^placebo\\b", tolower(trimws(comparator)))
  if (is.null(comparator_type)) return(txt)
  ty <- tolower(trimws(ifelse(is.na(comparator_type), "", comparator_type)))
  ifelse(ty %in% c("placebo", "active", "lifestyle"), ty == "placebo", txt)
}
# Counterexamples in both senses, run every time.
stopifnot(identical(is_placebo_controlled(c("placebo", "glimepiride", NA, "Placebo ")),
                    c(TRUE, FALSE, FALSE, TRUE)))
stopifnot(identical(
  is_placebo_controlled(
    c("placebo added to standard care", "visually matching placebo", "glimepiride",
      "insulin glargine titrated", "placebo", "lifestyle counselling", "placebo"),
    c("placebo", "placebo", "active", "ACTIVE", NA, "lifestyle", "active")),
  c(TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, FALSE)))
# The last pair is the one that matters: a row whose text says placebo but whose type says active is
# an active controlled row (a third arm recorded against the wrong text) and must be excluded.

excluded <- filter(dat, !is_placebo_controlled(comparator, comparator_type))
if (nrow(excluded) > 0) {
  message("EXCLUDED FROM CLASS CONTRASTS, active or unstated comparator (amendment 2026-10-15):")
  ex <- excluded |> count(trial_id, receptor_class, comparator, name = "rows")
  for (i in seq_len(nrow(ex))) {
    message(sprintf("  %-20s %-14s vs %-14s %3d row(s)",
                    ex$trial_id[i], ex$receptor_class[i],
                    ifelse(is.na(ex$comparator[i]), "NA", ex$comparator[i]),
                    ex$rows[i]))
  }
  message("")
} else {
  message("Comparator restriction: every row is placebo controlled; nothing excluded.\n")
}
dat <- filter(dat, is_placebo_controlled(comparator, comparator_type))
stopifnot(all(is_placebo_controlled(dat$comparator, dat$comparator_type)))

CLASSES <- c("GLP1_mono","GLP1_GIP","GLP1_GCGR","GLP1_GIP_GCGR")

## ---------------------------------------------------------------------------
## 1. What is actually comparable
## ---------------------------------------------------------------------------
cov <- dat |>
  group_by(biomarker, receptor_class) |>
  summarise(n_trials = n_distinct(trial_id), .groups = "drop")

grid <- cov |>
  pivot_wider(names_from = receptor_class, values_from = n_trials, values_fill = 0)

for (cl in setdiff(CLASSES, names(grid))) grid[[cl]] <- 0L
grid <- grid |>
  mutate(classes_present = rowSums(across(all_of(CLASSES)) > 0))

message("COVERAGE: trials per biomarker per receptor class\n")
message(sprintf("%-18s %10s %9s %10s %14s %8s",
                "biomarker","GLP1_mono","GLP1_GIP","GLP1_GCGR","GLP1_GIP_GCGR","classes"))
message(strrep("-", 76))
for (i in seq_len(nrow(grid))) {
  r <- grid[i,]
  message(sprintf("%-18s %10d %9d %10d %14d %8d",
                  r$biomarker, r$GLP1_mono, r$GLP1_GIP, r$GLP1_GCGR,
                  r$GLP1_GIP_GCGR, r$classes_present))
}

## ---------------------------------------------------------------------------
## 2. Which contrasts are supportable, and at what strength
## ---------------------------------------------------------------------------
# A class effect needs replication WITHIN each class being compared. With one
# trial per class, any difference is confounded with every other way those two
# trials differ: population, duration, assay, era, sponsor.
message("\nCONTRAST SUPPORT")
message(strrep("-", 76))
# A14 (2026-10-16): two counts, because one of them has a perverse property. The strict count
# requires EVERY class present to have two or more trials, so adding a single trial of a third class
# to a marker that already had two well populated classes REMOVES it from the count: data reduces
# the tally. The pairwise count asks whether at least two classes have two or more trials each, which
# is the condition that makes the contrast between THOSE two classes free of single trial
# confounding, and it is monotone in the data. Both are printed; the manuscript reports both and
# names the definition it uses.
n_repl_strict <- 0
n_repl_pair <- 0
for (i in seq_len(nrow(grid))) {
  r <- grid[i,]
  present <- CLASSES[c(r$GLP1_mono, r$GLP1_GIP, r$GLP1_GCGR, r$GLP1_GIP_GCGR) > 0]
  reps    <- c(r$GLP1_mono, r$GLP1_GIP, r$GLP1_GCGR, r$GLP1_GIP_GCGR)
  reps    <- reps[reps > 0]
  well    <- CLASSES[c(r$GLP1_mono, r$GLP1_GIP, r$GLP1_GCGR, r$GLP1_GIP_GCGR) >= 2]
  if (length(present) < 2) {
    v <- sprintf("only %s", paste(present, collapse=", "))
  } else if (all(reps >= 2)) {
    v <- sprintf("REPLICATED in every class present: %s", paste(present, collapse=" vs "))
    n_repl_strict <- n_repl_strict + 1
    n_repl_pair <- n_repl_pair + 1
  } else if (length(well) >= 2) {
    v <- sprintf("REPLICATED PAIRWISE: %s have two or more trials each; %s has one",
                 paste(well, collapse=" and "),
                 paste(setdiff(present, well), collapse=", "))
    n_repl_pair <- n_repl_pair + 1
  } else {
    v <- sprintf("CONFOUNDED: %s, one trial per class",
                 paste(present, collapse=" vs "))
  }
  message(sprintf("  %-18s %s", r$biomarker, v))
}

message(sprintf("\nBiomarkers supporting a replicated class contrast: %d of %d with every class replicated, %d of %d with at least two classes replicated",
                n_repl_strict, nrow(grid), n_repl_pair, nrow(grid)))

## ---------------------------------------------------------------------------
## 3. Descriptive class signature, explicitly not a contrast
## ---------------------------------------------------------------------------
DIR <- c(hsCRP=-1, IL6=-1, YKL40=-1, GDF15=-1, ICAM1=-1, GGT=-1,
         liver_fat_pdff=-1, leptin=-1, HOMA_IR=-1, NTproBNP=-1,
         lean_mass=1, adiponectin=1, HOMA_beta=1, fasting_glucose=-1,
         fasting_insulin=-1, C_peptide=-1, glucagon=-1, ALT=-1, AST=-1,
         fatty_liver_index=-1, TNF_alpha=-1, MR_proANP=-1)
INCLUDED <- c("hsCRP","IL6","YKL40","GDF15","ICAM1","GGT",
              "liver_fat_pdff","leptin","HOMA_IR","NTproBNP","lean_mass")

sig <- dat |>
  filter(biomarker %in% INCLUDED) |>
  group_by(receptor_class, biomarker) |>
  summarise(yi = weighted.mean(yi_pct, 1/vi_pct), .groups="drop") |>
  mutate(signed = DIR[biomarker] * yi) |>
  group_by(receptor_class) |>
  summarise(n_markers = n(),
            n_domains = n_distinct(biomarker),
            mean_signed = mean(signed), .groups="drop")

message("\nDESCRIPTIVE SIGNATURE BY CLASS")
message("NOT a contrast. Each class is summarised over a DIFFERENT marker set,")
message("so the means are not comparable to one another.\n")
message(sprintf("%-16s %9s %28s", "class", "markers", "mean signed change"))
message(strrep("-", 56))
for (i in seq_len(nrow(sig))) {
  r <- sig[i,]
  message(sprintf("%-16s %9d %26.1f%%", r$receptor_class, r$n_markers, r$mean_signed))
}

readr::write_csv(grid, "analysis/output/table3_class_coverage.csv")
readr::write_csv(sig,  "analysis/output/table3b_class_signature_descriptive.csv")
message("\nWrote table3_class_coverage.csv and table3b_class_signature_descriptive.csv")
