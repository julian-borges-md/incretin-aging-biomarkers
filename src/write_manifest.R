#!/usr/bin/env Rscript
###############################################################################
# write_manifest.R
#
# Writes analysis/output/MANIFEST.csv: every output file with its size and its
# SHA-256 digest. A reviewer can verify that the files accompanying the
# submission are exactly the ones these scripts produced, and a future reader
# can confirm that a rerun reproduces identical output.
#
# WHY THIS IS A SCRIPT AND NOT A SECTION OF THE PIPELINE. It was section 11 of
# analysis/M5_AGE_analysis_pipeline.R until 22 October, which made the manifest
# refreshable only by a twenty minute run of the whole pipeline. That is a
# problem because the pipeline is not the only thing that writes to
# analysis/output: the gate chain's seventeenth gate regenerates Table 1 from
# the biomarker inventory on every run. So a change to the inventory's display
# names, which is a change to a tracked data file and not to any statistic,
# left the manifest describing a Table 1 that no longer existed, and the
# manifest gate failed on a file that was correctly regenerated. The options
# were to run the pipeline again for a column heading, or to refresh the
# manifest by hand, which is the untracked step this repository keeps removing.
# A script is the third option: the pipeline sources it, the Makefile exposes
# it as `make manifest`, and the refresh is reproducible from a clone.
#
# WHAT THIS DOES NOT WEAKEN. src/manifest_check.py exists to catch an output
# that changed WITHOUT a run that explains it. Refreshing the manifest after a
# generator has legitimately rewritten an output is the workflow that gate
# assumes, not a way around it: the commit then carries the regenerated file
# and its new digest together, where a reviewer sees both. Refreshing it to
# silence a digest mismatch nobody can account for would be the abuse, and it
# is not what this script is for.
###############################################################################

suppressPackageStartupMessages({
  library(dplyr); library(purrr); library(readr); library(tibble); library(openssl)
})

write_result_manifest <- function(out_dir) {
  manifest <- tibble::tibble(
    file = list.files(out_dir, full.names = TRUE)
  ) |>
    dplyr::filter(basename(file) != "MANIFEST.csv") |>
    dplyr::mutate(
      bytes  = file.size(file),
      sha256 = purrr::map_chr(file, ~ as.character(
        openssl::sha256(file(.x, open = "rb"))
      )),
      generated = as.character(Sys.time())
    )
  readr::write_csv(manifest, file.path(out_dir, "MANIFEST.csv"))
  manifest
}

# Run directly, rather than sourced by the pipeline, when there is no OUT_DIR in
# the calling environment.
if (!exists("OUT_DIR")) {
  OUT_DIR <- file.path("analysis", "output")
  m <- write_result_manifest(OUT_DIR)
  message("MANIFEST.csv rewritten: ", nrow(m), " output file(s) hashed.")
}
