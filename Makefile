# Incretin aging biomarker signatures
#
#   make install    install the reference package set
#   make verify     run the integrity gates on the extraction contract
#   make selftest   prove that verify fails on perturbed input
#   make validate   prove the statistics recover known truth on simulated data
#   make analysis   run the full pipeline (needs analysis/data/extraction_master.csv)
#   make clean      remove generated artefacts
#
# verify and selftest need no data and no network. Both run in CI.
# Full reproduction path: docs/RUNBOOK.md

RS := Rscript

.PHONY: install verify selftest validate extract analysis clean

install:
	$(RS) requirements.R

verify:
	$(RS) src/verify.R

selftest:
	$(RS) src/selftest.R

validate:
	$(RS) src/validate_pipeline.R

extract:
	$(RS) src/build_master.R

analysis:
	$(RS) analysis/M5_AGE_analysis_pipeline.R

clean:
	rm -rf analysis/output/*
	touch analysis/output/.gitkeep
