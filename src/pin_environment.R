#!/usr/bin/env Rscript
# pin_environment.R
#
# Writes the exact versions of every package the analysis loads, plus the R version and platform,
# to analysis/output/environment_pinned.csv and a human readable summary.
#
# Why this exists. requirements.R has said "Exact versions are pinned in renv.lock" since the
# repository was created, and renv.lock has never existed. A reader following that sentence finds
# nothing. That is the same class of defect as a brief describing a reconciler step that was never
# implemented and a status file listing manuscript sections that were never written: a document
# asserting a mechanism rather than a mechanism.
#
# This script does not replace renv. It records what a run actually used, which is the minimum a
# reader needs to reproduce a number and is something renv.lock cannot give retrospectively for runs
# already made. Initialising renv rewrites the project profile and library and must not be done while
# an analysis is executing, so it is a separate step recorded in docs/RUNBOOK.md.
#
# Usage
#   Rscript src/pin_environment.R
#   make pin

OUT_DIR <- "analysis/output"
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

# The set the analysis declares, read from requirements.R rather than restated here so the two
# cannot drift apart. The same discipline the gate chain applies to RECEPTOR_CLASSES.
req_src <- readLines("requirements.R", warn = FALSE)
start <- grep("^packages <- c\\(", req_src)
if (length(start) != 1) stop("packages vector not found in requirements.R")
ends <- grep("^\\)", req_src)
stop_at <- min(ends[ends > start])
eval(parse(text = paste(req_src[start:stop_at], collapse = "\n")))

inst <- as.data.frame(installed.packages(), stringsAsFactors = FALSE)
rows <- do.call(rbind, lapply(sort(unique(packages)), function(p) {
  hit <- inst[inst$Package == p, , drop = FALSE]
  data.frame(
    package  = p,
    version  = if (nrow(hit)) hit$Version[1] else NA_character_,
    priority = if (nrow(hit)) (if (is.na(hit$Priority[1])) "" else hit$Priority[1]) else "",
    installed = nrow(hit) > 0,
    stringsAsFactors = FALSE
  )
}))

# Dependencies of the declared set matter too: a pooled estimate can move with a change in a
# dependency the analysis never names. Recorded separately so the declared set stays readable.
deps <- unique(unlist(tools::package_dependencies(
  intersect(packages, inst$Package), db = inst, recursive = TRUE)))
dep_rows <- do.call(rbind, lapply(sort(setdiff(deps, packages)), function(p) {
  hit <- inst[inst$Package == p, , drop = FALSE]
  data.frame(package = p,
             version = if (nrow(hit)) hit$Version[1] else NA_character_,
             priority = "", installed = nrow(hit) > 0, stringsAsFactors = FALSE)
}))

rows$role <- "declared"
if (!is.null(dep_rows) && nrow(dep_rows)) {
  dep_rows$role <- "dependency"
  rows <- rbind(rows, dep_rows)
}
rows$r_version <- paste(R.version$major, R.version$minor, sep = ".")
rows$platform  <- R.version$platform
rows$pinned_on <- format(Sys.Date())

write.csv(rows, file.path(OUT_DIR, "environment_pinned.csv"), row.names = FALSE)

missing <- rows$package[rows$role == "declared" & !rows$installed]
cat(sprintf("pinned %d package(s): %d declared, %d dependencies\n",
            nrow(rows), sum(rows$role == "declared"), sum(rows$role == "dependency")))
cat(sprintf("R %s on %s\n", rows$r_version[1], rows$platform[1]))
if (length(missing)) {
  cat("DECLARED BUT NOT INSTALLED: ", paste(missing, collapse = ", "), "\n")
}
cat(sprintf("written %s\n", file.path(OUT_DIR, "environment_pinned.csv")))
quit(status = if (length(missing)) 1 else 0)
