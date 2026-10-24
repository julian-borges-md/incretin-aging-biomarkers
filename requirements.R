# Reference package set.
#
# Corrected 19 October 2026. This header previously read "Exact versions are pinned in renv.lock",
# and renv.lock has never existed in this repository, so a reader following that sentence found
# nothing. Versions are pinned by `make pin`, which writes the exact version of every declared
# package and of every package they depend on, with the R version and platform, to
# analysis/output/environment_pinned.csv. That file is version controlled. (The count of
# dependencies stood here as 148 until 24 October, when the figure packages were declared; the file
# states the count, so this header no longer does.)
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
  "ragg",         # 600 dpi PNG figures without cairo or X11
  "showtext",     # PDF figures with every glyph drawn as an outline
  "sysfonts",     # registers the vendored typeface for showtext
  "systemfonts",  # registers the vendored typeface for ragg, and measures text for the PRISMA boxes
  "scales",       # true minus signs and percent labels on figure axes
  "jsonlite",     # reads docs/prisma_counts.json for the PRISMA diagram
  "knitr",
  "openssl",      # SHA-256 for the output manifest
  "sessioninfo"
)
install.packages(setdiff(packages, rownames(installed.packages())),
                 repos = "https://cloud.r-project.org")
