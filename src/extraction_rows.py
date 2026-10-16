#!/usr/bin/env python3
"""
extraction_rows.py

Writes an extraction for one study group into the staging directory from a compact JSON spec,
so that the session (extractor id S) or an agent can record rows without typing the 53 column
header by hand. The inventory supplies hallmark_domain, aging_direction and clinical_weight from
the biomarker key; everything else is copied from the spec. No arithmetic is done here.

Spec (JSON on stdin or in a file passed as the second argument)
  {"group": "246", "extractor": "S",
   "study": {trial_id, pmid, doi, first_author, year, journal, phase, drug, receptor_class, dose_mg,
             comparator, comparator_type, duration_weeks, population, n_tx, n_ctrl,
             assessment_timepoint_weeks, pct_weight_change, prespecified_endpoint, industry_funded,
             rob_overall, notes},                      # defaults for every row
   "rows": [{"biomarker": "hsCRP", "measure": "MD", "unit": "mg/L", "mean_tx": ..., "sd_tx": ..., ...,
             "notes": "..."}, ...],                     # per row overrides and route fields
   "json": {"status": "extracted", "molecule": "...", "design": "...", "reason": "...",
            "biomarkers_reported_no_variance": [...], "other_markers": [...], "tables_used": [...],
            "rob": {d1_randomisation, d2_deviations, d3_missing, d4_measurement, d5_selection,
                    overall, justification}, "doubts": [...]}}

Usage
  python3 -I src/extraction_rows.py GROUP spec.json
  python3 -I src/extraction_rows.py GROUP < spec.json
"""
import csv
import json
import os
import sys

ROOT = os.getcwd()
STAGING = os.path.join(ROOT, "work", "extraction", "staging")
INVENTORY = os.path.join(ROOT, "analysis", "data", "biomarker_inventory.csv")
HEADER = ("trial_id,pmid,doi,first_author,year,journal,phase,drug,receptor_class,dose_mg,comparator,comparator_type,"
          "duration_weeks,population,n_tx,n_ctrl,biomarker,hallmark_domain,aging_direction,clinical_weight,outcome_type,"
          "measure,unit,yi_reported,ci_lb_reported,ci_ub_reported,se_reported,p_reported,p_is_bound,se_source,mean_tx,sem_tx,"
          "sd_tx,mean_ctrl,sem_ctrl,sd_ctrl,base_mean_tx,base_sd_tx,final_mean_tx,final_sd_tx,base_mean_ctrl,"
          "base_sd_ctrl,final_mean_ctrl,final_sd_ctrl,corr_assumed,events_tx,events_ctrl,assessment_timepoint_weeks,"
          "pct_weight_change,prespecified_endpoint,industry_funded,rob_overall,notes").split(",")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    group = argv[0]
    spec = json.load(open(argv[1])) if len(argv) > 1 else json.load(sys.stdin)
    ext = spec.get("extractor", "S")
    inv = {}
    with open(INVENTORY, newline="") as fh:
        for r in csv.DictReader(fh):
            inv[r["biomarker"]] = r
    study = spec.get("study", {})
    rows = []
    for spec_row in spec.get("rows", []):
        b = spec_row["biomarker"]
        if b not in inv:
            sys.exit(f"biomarker {b!r} is not in the inventory")
        row = {k: "" for k in HEADER}
        row.update({k: v for k, v in study.items() if k in row})
        row.update({k: v for k, v in spec_row.items() if k in row})
        row["hallmark_domain"] = inv[b]["hallmark_domain"]
        row["aging_direction"] = inv[b]["aging_direction"]
        row["clinical_weight"] = inv[b]["clinical_weight"]
        row["outcome_type"] = row.get("outcome_type") or inv[b]["outcome_type"]
        if study.get("notes") and spec_row.get("notes"):
            row["notes"] = f"{spec_row['notes']} | {study['notes']}"
        rows.append(row)
    d = os.path.join(STAGING, str(group))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{ext}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    j = dict(group=str(group), extractor=ext)
    j.update(spec.get("json", {}))
    j["rows"] = len(rows)
    j.setdefault("trial_id", study.get("trial_id", ""))
    j.setdefault("molecule", study.get("drug", ""))
    j.setdefault("receptor_class", study.get("receptor_class", ""))
    with open(os.path.join(d, f"{ext}.json"), "w") as fh:
        json.dump(j, fh, indent=1)
    print(f"group {group}: {len(rows)} row(s) written to staging as extractor {ext}; status {j.get('status', '')}")


if __name__ == "__main__":
    main(sys.argv[1:])
