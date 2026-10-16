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

clean:
	rm -rf analysis/output/*
	touch analysis/output/.gitkeep
