#!/usr/bin/env python3
"""Lexicon scan of every text given to the full text screen, and a text based audit of the
reviewers' biomarkers_reported field.

Deterministic: one regular expression per inventory biomarker (criterion O), case insensitive,
applied to the same text the reviewer agents received (src/fulltext_screen.load_items). No model
is called. Two outputs:

  search/screening/biomarker_scan_2026-10-16.csv   per record mention counts (untracked, beside
                                                   the other per record files)
  search/screening/BIOMARKER_SCAN_SUMMARY.md       records with a mention per biomarker and text
                                                   source; where both reviewers have screened a
                                                   record, the biomarkers they named that have no
                                                   mention in the text, and the biomarkers with
                                                   three or more mentions that neither named

A mention is evidence that the marker is discussed, not that a result is reported; the audit
therefore flags, it does not decide. Usage, from the repository root:
  python3 -I src/biomarker_scan.py
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.argv = [sys.argv[0]]
import fulltext_screen as fs  # noqa: E402

OUT_CSV = os.path.join(fs.OUTDIR, "biomarker_scan_2026-10-16.csv")
OUT_MD = os.path.join(fs.OUTDIR, "BIOMARKER_SCAN_SUMMARY.md")
MENTION_FLOOR = 3  # mentions at or above which an unnamed marker is flagged

# inventory biomarkers of criterion O, in the order of the criteria text
LEXICON = [
    ("crp", r"\b(?:hs[- ]?crp|c[- ]reactive protein|crp)\b"),
    ("il6", r"\b(?:il[- ]?6|interleukin[- ]?6)\b"),
    ("tnf", r"\b(?:tnf[- ]?(?:α|alpha|a)?|tumou?r necrosis factor)\b"),
    ("gdf15", r"\b(?:gdf[- ]?15|growth differentiation factor[- ]?15)\b"),
    ("ykl40", r"\b(?:ykl[- ]?40|chitinase[- ]3[- ]like)\b"),
    ("icam1", r"\b(?:icam[- ]?1|intercellular adhesion molecule)\b"),
    ("leptin", r"\bleptin\b"),
    ("adiponectin", r"\badiponectin\b"),
    ("insulin", r"\b(?:fasting (?:plasma |serum )?insulin|insulin levels?|serum insulin|plasma insulin|insulin concentrations?)\b"),
    ("homa_ir", r"\bhoma[- ]?ir\b"),
    ("homa_beta", r"\bhoma[- ]?(?:β|beta|b|%?b)\b"),
    ("cpeptide", r"\bc[- ]peptide\b"),
    ("glucagon", r"\bglucagon(?! ?like)(?!-like)\b"),
    ("glucose", r"\b(?:fasting (?:plasma |blood |serum )?glucose|fpg|fbg)\b"),
    ("hba1c", r"\b(?:hba1c|hb a1c|a1c|glycated ha?emoglobin|glycosylated ha?emoglobin)\b"),
    ("liver_fat", r"\b(?:liver fat|hepatic fat|intrahepatic (?:lipid|fat|triglyceride)|mri[- ]pdff|pdff|hepatic steatosis|controlled attenuation parameter)\b"),
    ("alt", r"\b(?:alt|alanine (?:amino)?transferase)\b"),
    ("ast", r"\b(?:ast|aspartate (?:amino)?transferase)\b"),
    ("ggt", r"\b(?:ggt|gamma[- ]glutamyl ?transferase|γ[- ]?gt)\b"),
    ("mash", r"\b(?:mash|nash|steatohepatitis|fibrosis (?:stage|improvement|score)|liver fibrosis)\b"),
    ("tg", r"\b(?:triglycerides?|tg)\b"),
    ("ldl", r"\b(?:ldl(?:[- ]c)?|ldl cholesterol|low[- ]density lipoprotein)\b"),
    ("tc", r"\b(?:total cholesterol)\b"),
    ("lean_mass", r"\b(?:lean (?:body )?mass|fat[- ]free mass|ffm|skeletal muscle mass|appendicular lean)\b"),
    ("body_fat", r"\b(?:body fat|fat mass|total fat|percent(?:age)? (?:body )?fat)\b"),
    ("vat", r"\b(?:visceral (?:adipose|fat|adiposity)|vat)\b"),
    ("bmd", r"\b(?:bmd|bone mineral density)\b"),
    ("egfr", r"\b(?:egfr|estimated glomerular filtration)\b"),
    ("heart_rate", r"\b(?:resting )?heart rate\b|\bpulse rate\b"),
    ("bp", r"\b(?:blood pressure|sbp|dbp|systolic|diastolic)\b"),
    ("ntprobnp", r"\b(?:nt[- ]?pro[- ]?bnp|n[- ]terminal pro[- ]?b[- ]type natriuretic)\b"),
    ("mrproanp", r"\b(?:mr[- ]?pro[- ]?anp)\b"),
    ("epigenetic_age", r"\b(?:epigenetic (?:age|clock)|dna methylation age|grimage|phenoage|dunedinpace)\b"),
]
PATTERNS = [(k, re.compile(p, re.I)) for k, p in LEXICON]

# reviewer vocabulary to lexicon keys; names outside this map are counted as "other"
ALIASES = {
    "hscrp": "crp", "hs-crp": "crp", "hs crp": "crp", "crp": "crp", "c-reactive protein": "crp", "c reactive protein": "crp",
    "high-sensitivity c-reactive protein": "crp", "high sensitivity crp": "crp", "hs-crp (high-sensitivity c-reactive protein)": "crp",
    "il-6": "il6", "il6": "il6", "interleukin-6": "il6", "interleukin 6": "il6", "il-6 (interleukin-6)": "il6",
    "tnf-alpha": "tnf", "tnf-α": "tnf", "tnfα": "tnf", "tnf": "tnf", "tnf alpha": "tnf", "tnf-a": "tnf", "tumor necrosis factor-alpha": "tnf",
    "tumor necrosis factor alpha": "tnf", "tnf-alpha (tumor necrosis factor alpha)": "tnf",
    "gdf-15": "gdf15", "gdf15": "gdf15", "gdf 15": "gdf15", "ykl-40": "ykl40", "icam-1": "icam1", "sicam-1": "icam1",
    "leptin": "leptin", "adiponectin": "adiponectin", "insulin": "insulin", "fasting insulin": "insulin", "serum insulin": "insulin",
    "homa-ir": "homa_ir", "homa ir": "homa_ir", "homa_ir": "homa_ir", "homa-beta": "homa_beta", "homa-b": "homa_beta", "homa-β": "homa_beta",
    "c-peptide": "cpeptide", "c peptide": "cpeptide", "glucagon": "glucagon",
    "fasting glucose": "glucose", "glucose": "glucose", "fasting plasma glucose": "glucose", "fpg": "glucose", "fasting blood glucose": "glucose", "blood glucose": "glucose", "plasma glucose": "glucose",
    "hba1c": "hba1c", "a1c": "hba1c", "glycated hemoglobin": "hba1c", "glycated haemoglobin": "hba1c", "hemoglobin a1c": "hba1c",
    "liver fat": "liver_fat", "hepatic fat": "liver_fat", "liver fat content": "liver_fat", "mri-pdff": "liver_fat", "pdff": "liver_fat", "hepatic steatosis": "liver_fat", "liver fat by imaging": "liver_fat", "intrahepatic lipid": "liver_fat",
    "alt": "alt", "ast": "ast", "ggt": "ggt", "mash resolution": "mash", "nash resolution": "mash", "fibrosis": "mash", "liver fibrosis": "mash", "fibrosis improvement": "mash",
    "triglycerides": "tg", "triglyceride": "tg", "tg": "tg", "ldl": "ldl", "ldl-c": "ldl", "ldl cholesterol": "ldl", "ldl-cholesterol": "ldl",
    "total cholesterol": "tc", "cholesterol": "tc", "tc": "tc",
    "lean mass": "lean_mass", "lean body mass": "lean_mass", "fat-free mass": "lean_mass", "fat free mass": "lean_mass", "ffm": "lean_mass",
    "body fat": "body_fat", "fat mass": "body_fat", "body fat percentage": "body_fat", "total body fat": "body_fat", "body fat mass": "body_fat",
    "visceral adipose tissue": "vat", "visceral fat": "vat", "vat": "vat", "visceral adiposity": "vat",
    "bone mineral density": "bmd", "bmd": "bmd", "egfr": "egfr", "estimated gfr": "egfr",
    "resting heart rate": "heart_rate", "heart rate": "heart_rate", "pulse rate": "heart_rate",
    "blood pressure": "bp", "systolic blood pressure": "bp", "diastolic blood pressure": "bp", "sbp": "bp", "dbp": "bp", "systolic bp": "bp", "diastolic bp": "bp",
    "nt-probnp": "ntprobnp", "ntprobnp": "ntprobnp", "nt-pro-bnp": "ntprobnp", "mr-proanp": "mrproanp", "epigenetic age": "epigenetic_age",
    # reviewer spellings seen in the first 300 records
    "tnfa": "tnf", "tnf-α (tumor necrosis factor-alpha)": "tnf", "fasting serum insulin": "insulin", "fasting plasma insulin": "insulin",
    "homa2-ir": "homa_ir", "homa2-b": "homa_beta", "homa-%b": "homa_beta", "hff": "liver_fat", "hepatic fat fraction": "liver_fat",
    "liver fat fraction": "liver_fat", "mri-pdff (liver fat)": "liver_fat", "fasting glucose (fpg)": "glucose", "hba1c (glycated hemoglobin)": "hba1c",
}


def canon(name):
    n = name.strip().lower()
    if n in ALIASES:
        return ALIASES[n]
    n2 = re.sub(r"\s*\(.*?\)\s*", "", n).strip()
    return ALIASES.get(n2, "other")


def scan(text):
    return {k: len(p.findall(text)) for k, p in PATTERNS}


def main():
    items = [it for it in fs.load_items() if it["text"]]
    A, B = fs.read_dec(fs.dec_path("A")), fs.read_dec(fs.dec_path("B"))
    keys = [k for k, _ in LEXICON]
    rows = []
    for it in items:
        c = scan(it["text"])
        named = set()
        for d in (A, B):
            if it["key"] in d:
                named |= {canon(x) for x in (d[it["key"]]["biomarkers_reported"] or "").split(";") if x.strip()}
        named.discard("other")
        both = it["key"] in A and it["key"] in B
        unsupported = sorted(n for n in named if c.get(n, 0) == 0) if both else []
        unnamed = sorted(k for k in keys if c[k] >= MENTION_FLOOR and k not in named) if both else []
        rows.append(dict(key=it["key"], source=it["source"], chars=len(it["text"]), screened_by_both="yes" if both else "no",
                         named=";".join(sorted(named)), named_without_mention=";".join(unsupported),
                         mentioned_not_named=";".join(unnamed), **{k: c[k] for k in keys}))
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    sources = fs.SOURCE_ORDER
    md = ["# Biomarker lexicon scan of the full text screen inputs\n",
          f"One regular expression per inventory biomarker (criterion O), case insensitive, run over the exact text each reviewer received "
          f"({len(items)} records with a text). Produced by `src/biomarker_scan.py`; per record counts are in the untracked "
          f"`biomarker_scan_2026-10-16.csv`. A mention shows the marker is discussed, not that a result is reported.\n",
          "| Biomarker | " + " | ".join(sources) + " | Any |\n|---|" + "---|" * (len(sources) + 1)]
    for k in keys:
        per = [sum(1 for r in rows if r["source"] == s and r[k] > 0) for s in sources]
        md.append(f"| {k} | " + " | ".join(str(x) for x in per) + f" | {sum(per)} |")
    both = [r for r in rows if r["screened_by_both"] == "yes"]
    md.append(f"\n## Audit of the reviewers' biomarkers_reported field ({len(both)} records screened by both reviewers so far)\n")
    md.append("Named without a mention: a marker named by either reviewer whose pattern finds nothing in the text given to them (a naming error, "
              "a synonym outside the lexicon, or a marker the lexicon does not cover). Mentioned, not named: a marker with "
              f"{MENTION_FLOOR} or more mentions that neither reviewer named (a possible omission, or a marker discussed without a result).\n")
    unsup, unnm = Counter(), Counter()
    for r in both:
        unsup.update(x for x in r["named_without_mention"].split(";") if x)
        unnm.update(x for x in r["mentioned_not_named"].split(";") if x)
    md.append("| Biomarker | Named without a mention (records) | Mentioned, not named (records) |\n|---|---|---|")
    for k in keys:
        if unsup[k] or unnm[k]:
            md.append(f"| {k} | {unsup[k]} | {unnm[k]} |")
    md.append(f"| records with at least one flag | {sum(1 for r in both if r['named_without_mention'])} | {sum(1 for r in both if r['mentioned_not_named'])} |")
    other = Counter()
    for r in both:
        for d in (A, B):
            if r["key"] in d:
                other.update(x.strip().lower() for x in (d[r["key"]]["biomarkers_reported"] or "").split(";") if x.strip() and canon(x) == "other")
    md.append("\n| Reviewer name outside the lexicon (not an inventory biomarker, or a synonym to add to the alias map) | Records |\n|---|---|")
    for name, cnt in other.most_common(25):
        md.append(f"| {name} | {cnt} |")
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
