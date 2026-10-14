# Reference package set. Exact versions are pinned in renv.lock.
# Install with: make install
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
