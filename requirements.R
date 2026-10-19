# Reference package set.
#
# Corrected 19 October 2026. This header previously read "Exact versions are pinned in renv.lock",
# and renv.lock has never existed in this repository, so a reader following that sentence found
# nothing. Versions are pinned by `make pin`, which writes the exact version of every declared
# package and of all 148 of their dependencies, with the R version and platform, to
# analysis/output/environment_pinned.csv. That file is version controlled.
#
# Install with: make install
# Pin with:    make pin
packages <- c(
  "metafor",      # core meta-analysis and meta-regression
  "netmeta",      # frequentist network meta-analysis
  "meta",         # funnel plots, convenience wrappers
  "dmetar",       # influence diagnostics
  "tidyverse",    # data manipulation
  "boot",         # BCa bootstrap for the composite metric
  "ggplot2",
  "patchwork",
  "knitr",
  "openssl",      # SHA-256 for the output manifest
  "sessioninfo"
)
install.packages(setdiff(packages, rownames(installed.packages())),
                 repos = "https://cloud.r-project.org")
