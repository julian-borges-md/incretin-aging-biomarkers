# Incretin aging biomarker signatures
#
#   make install    install the reference package set
#   make verify     run the integrity gates on the extraction contract
#   make selftest   prove that verify fails on perturbed input
#   make validate   prove the statistics recover known truth on simulated data
#   make gates      run the full twenty one gate provenance chain
#   make analysis   run the full pipeline (needs analysis/data/extraction_master.csv)
#   make pin        record the exact package versions this run used
#   make clean      remove generated artefacts
#
# verify and selftest need no data and no network. Both run in CI.
# Full reproduction path: docs/RUNBOOK.md

RS := Rscript

.PHONY: install pin gates verify selftest validate extract analysis clean

install:
	$(RS) requirements.R

# Pin the exact package versions a run used, with the R version and platform, to
# analysis/output/environment_pinned.csv. requirements.R claimed renv.lock did this and renv.lock
# has never existed; see that file's header.
pin:
	$(RS) src/pin_environment.R

# The full provenance chain, twenty one gates. It was reachable only as scripts/run_gates.sh, so the
# one command that validates the whole pipeline was the one command the Makefile did not offer.
gates:
	bash scripts/run_gates.sh

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

# Amendment R1 (2026-10-15): mandatory reruns of the imputed pre post
# correlation at 0.3 and 0.7; requires the gate chain to have produced Table 2.
sensitivity:
	$(RS) src/sensitivity_corr.R

# Links the gitignored Embase export to the known corpus and measures the
# recall of the search string; writes counts to search/embase_*/RECALL_AND_DEDUP.md.
dedup:
	python3 -I src/dedup_embase.py

# Same gates and linkage for the CENTRAL export, plus overlap with Embase
dedup-central:
	python3 -I src/dedup_embase.py central

# Title and abstract screening by two blinded local reviewer agents, a third
# adjudicating; models named only in the untracked search/screening/screener_config.json.
screen:
	python3 -I src/screen_titles.py screen
adjudicate:
	python3 -I src/screen_titles.py adjudicate
screen-summary:
	python3 -I src/screen_titles.py summarise

# Second pool: the 51 Embase registry records plus the 200 CENTRAL records not
# in the Embase export; separate decision files (suffix _batch2), same gates.
screen-batch2:
	python3 -I src/screen_titles.py screen --pool batch2 --criteria v2
adjudicate-batch2:
	python3 -I src/screen_titles.py adjudicate --pool batch2 --criteria v2
screen-summary-batch2:
	python3 -I src/screen_titles.py summarise --pool batch2 --criteria v2

# Criteria v2 (clarifications after the audit in search/screening/SCREENING_AUDIT_2026-10-15.md):
# rescreen the pool 1 exclusions under v2; pool 2 runs under v2 from the start.
rescreen-excluded:
	python3 -I src/screen_titles.py rescreen-excluded --criteria v2
screen-summary-v2:
	python3 -I src/screen_titles.py summarise --criteria v2

# Full text screening pool from the screening decisions (per record CSV untracked, summary committed)
fulltext-pool:
	python3 -I src/build_fulltext_pool.py

# Full text access: Europe PMC lookup (no key, no email), open access harvest into work/fulltext/pool, counts summary
fulltext-access:
	python3 -I src/epmc_lookup.py
	python3 -I src/epmc_harvest.py
	python3 -I src/fulltext_access_summary.py

# ClinicalTrials.gov entries for the pool's registry records with an NCT identifier (public API v2, no key)
registry-harvest:
	python3 -I src/ctgov_harvest.py

# Full text screening by the same three agent design (criteria v2 plus the full text addendum)
fulltext-screen:
	python3 -I src/fulltext_screen.py screen
fulltext-adjudicate:
	python3 -I src/fulltext_screen.py adjudicate
fulltext-summary:
	python3 -I src/fulltext_screen.py summarise

# analysis/output became version controlled on 19 October, so the old recipe, `rm -rf
# analysis/output/*`, would now delete tracked results: every pooled estimate the manuscript quotes
# and every figure, recoverable only by `git checkout`. A clean target that silently destroys
# committed work is worse than no clean target. This one removes only untracked and ignored files
# there, which is what cleaning a build directory should mean, and `git clean` refuses to touch
# anything committed. `make clean-all` remains available for the destructive version, named so that
# nobody reaches it by accident.
clean:
	git clean -fdX analysis/output/
	@echo "Removed ignored files from analysis/output/. Tracked results untouched."
	@echo "To discard tracked results as well: make clean-all"

.PHONY: clean-all
clean-all:
	@echo "This deletes VERSION CONTROLLED results in analysis/output/."
	@echo "Recover with: git checkout -- analysis/output/"
	rm -rf analysis/output/*
	touch analysis/output/.gitkeep
