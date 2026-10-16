#!/usr/bin/env python3
"""
baseline_hunt.py

Finds candidate baseline values for the rows that the harmoniser cannot put on the percent change
scale. A row is unconvertible when neither the hand keyed BASELINE table of src/harmonise_units.R
nor the row's own base_mean_tx and base_mean_ctrl supply a denominator. Some of those denominators
are already inside the packet text the row was extracted from and were simply never recorded; those
are free to recover and need no new capture. This script separates that case from the case that
needs a supplement or a new source, and it proposes nothing: every candidate line is printed with
its file so that a human or the session reads the number from the source.

Method
  1. read the harmonised master, keep the rows with no yi_pct
  2. map each trial_id to the study groups whose ledger reconciled_file holds that trial
  3. for every (trial, biomarker) pair, grep the group's packet texts and any companion capture
     named in the row notes for lines that mention a synonym of the biomarker and carry a number
  4. print the candidates, and mark a pair as NO CANDIDATE IN PACKET when nothing matches

Usage
  python3 -I src/baseline_hunt.py                 (all unconvertible pairs)
  python3 -I src/baseline_hunt.py TRIAL_SUBSTRING (one trial)
"""
import csv
import json
import os
import re
import sys

ROOT = os.getcwd()
HARMONISED = os.path.join(ROOT, "analysis", "data", "extraction_master_harmonised.csv")
LEDGER = os.path.join(ROOT, "analysis", "data", "EXTRACTION_LEDGER.csv")
PACKETS = os.path.join(ROOT, "work", "extraction", "packets")

SYNONYMS = {
    "hsCRP": ["hs-crp", "hscrp", "c-reactive", "c reactive", "crp"],
    "IL6": ["il-6", "il6", "interleukin-6", "interleukin 6"],
    "TNF_alpha": ["tnf", "tumour necrosis", "tumor necrosis"],
    "adiponectin": ["adiponectin"],
    "leptin": ["leptin"],
    "ALT": ["alt", "alanine"],
    "AST": ["ast", "aspartate"],
    "GGT": ["ggt", "gamma-glutamyl", "gamma glutamyl", "γ-glutamyl"],
    "fatty_liver_index": ["fatty liver index", "fli"],
    "SBP": ["systolic"],
    "DBP": ["diastolic"],
    "TC": ["total cholesterol", "cholesterol, total", "total-c"],
    "LDL": ["ldl"],
    "TG": ["triglyceride", "triacylglycerol"],
    "fasting_glucose": ["fasting plasma glucose", "fasting glucose", "fasting serum glucose", "fpg"],
    "fasting_insulin": ["fasting insulin", "fasting serum insulin", "insulin, fasting"],
    "resting_heart_rate": ["heart rate", "pulse"],
    "HOMA_IR": ["homa-ir", "homa ir"],
    "HOMA_beta": ["homa-b", "homa-beta", "homa b"],
    "C_peptide": ["c-peptide", "c peptide"],
    "eGFR": ["egfr", "glomerular filtration"],
    "VAT": ["visceral"],
    "lean_mass": ["lean"],
    "body_fat_pct": ["body fat", "fat mass percent", "fat percentage"],
    "liver_fat_pdff": ["liver fat", "pdff", "intrahepatic", "hepatic fat", "steatosis"],
    "NTproBNP": ["nt-probnp", "ntprobnp", "natriuretic"],
    "glucagon": ["glucagon"],
    "GDF15": ["gdf-15", "gdf15"],
    "HbA1c": ["hba1c", "a1c", "glycated"],
}
NUMBER = re.compile(r"\d+\.?\d*")
BASELINE_HINT = re.compile(r"baseline|before|pre[- ]treatment|screening|week 0|visit", re.I)


def group_map():
    out = {}
    with open(LEDGER, newline="") as fh:
        for r in csv.DictReader(fh):
            f = (r.get("reconciled_file") or "").strip()
            if f:
                out.setdefault(f, []).append(r["study_group"])
    return out


def texts_for(groups, extra):
    files = []
    for g in groups:
        pj = os.path.join(PACKETS, str(g), "packet.json")
        if os.path.exists(pj):
            for t in json.load(open(pj))["texts"]:
                p = os.path.join(ROOT, t["file"])
                if os.path.exists(p):
                    files.append(p)
    for p in extra:
        if os.path.exists(p):
            files.append(p)
    return files


def companions(notes):
    return [os.path.join(ROOT, m) for m in re.findall(r"work/fulltext/[^\s,;)]+\.txt", notes or "")]


def main(argv):
    want = argv[0].lower() if argv else None
    rows = [r for r in csv.DictReader(open(HARMONISED, newline=""))
            if (r.get("yi_pct") or "").strip() in ("", "NA")]
    if want:
        rows = [r for r in rows if want in r["trial_id"].lower()]
    gm = group_map()
    # which extraction file holds each trial
    file_of = {}
    for name in os.listdir(os.path.join(ROOT, "analysis", "data")):
        if not (name.startswith("extraction_") and name.endswith(".csv")) or "master" in name:
            continue
        path = os.path.join("analysis", "data", name)
        with open(os.path.join(ROOT, path), newline="") as fh:
            rd = csv.DictReader(fh)
            if "trial_id" not in (rd.fieldnames or []):
                continue  # not a row file (an index or a scan output shares the prefix)
            for r in rd:
                if r.get("trial_id"):
                    file_of.setdefault(r["trial_id"], path)
    seen = set()
    n_free, n_needs = 0, 0
    for r in sorted(rows, key=lambda r: r["trial_id"]):
        key = (r["trial_id"], r["biomarker"])
        if key in seen:
            continue
        seen.add(key)
        groups = gm.get(file_of.get(r["trial_id"], ""), [])
        files = texts_for(groups, companions(r.get("notes", "")))
        syns = SYNONYMS.get(r["biomarker"], [r["biomarker"].lower()])
        hits = []
        for p in files:
            for ln in open(p, errors="replace").read().split("\n"):
                low = ln.lower()
                if any(s in low for s in syns) and NUMBER.search(ln) and len(ln) < 400:
                    score = 2 if BASELINE_HINT.search(ln) else 1
                    hits.append((score, os.path.relpath(p, ROOT), ln.strip()))
        hits.sort(key=lambda x: -x[0])
        print(f"\n=== {r['trial_id']} | {r['biomarker']} | groups {','.join(groups) or 'none'} "
              f"| {len(files)} text(s)")
        if not hits:
            n_needs += 1
            print("    NO CANDIDATE IN PACKET: a supplement or a new source is needed")
        else:
            n_free += 1
            for score, p, ln in hits[:4]:
                print(f"    [{score}] {p}: {ln[:220]}")
    print(f"\npairs with at least one candidate line in hand: {n_free}; pairs needing a new source: {n_needs}")


if __name__ == "__main__":
    main(sys.argv[1:])
