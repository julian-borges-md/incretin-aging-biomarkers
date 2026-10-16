#!/usr/bin/env python3
"""
dedup_embase.py

Links the Embase export to what the review already knows, and measures the
recall of the Embase search string against the trials the review already
holds. Two questions, one pass:

  1. Deduplication. Which of the 659 Embase records are already in the
     corpus (extracted trial analyses, the DOI verified reference list), and
     which are new to screening? Embase delivers no PMID tag, so linkage is
     by DOI first (611 of 659 carry one) and by first author surname plus
     year, with the matched title printed, for the rest.
  2. Recall. Of the trials known to be relevant from another route (the
     extracted set, and the 38 mono agonist trials in the included studies
     table of Alrasheed 2026), how many does the Embase search retrieve?
     A low recall is evidence against the search string, not against the
     trials.

Inputs
  search/embase_2026-10-15/embase_659.ris     gitignored licensed export
  analysis/data/extraction_master.csv         extracted trial analyses
  docs/REFERENCES.md                          DOI verified references
  search/known_relevant_trials.csv            first author and year list

Outputs
  search/embase_2026-10-15/RECALL_AND_DEDUP.md       counts only, committed
  search/embase_2026-10-15/embase_659_dedup.csv      per record, untracked

Standard library only. Run from the repository root:
  python3 src/dedup_embase.py
"""
import csv
import hashlib
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.getcwd()
RIS = os.path.join(ROOT, "search/embase_2026-10-15/embase_659.ris")
MASTER = os.path.join(ROOT, "analysis/data/extraction_master.csv")
REFS = os.path.join(ROOT, "docs/REFERENCES.md")
KNOWN = os.path.join(ROOT, "search/known_relevant_trials.csv")
OUT_MD = os.path.join(ROOT, "search/embase_2026-10-15/RECALL_AND_DEDUP.md")
OUT_CSV = os.path.join(ROOT, "search/embase_2026-10-15/embase_659_dedup.csv")

EXPECTED_RECORDS = 659
EXPECTED_SHA256 = "e8d3a9d4e195375f1d1aaaead76ae0ad0d937206194e152984d71d42405fefb2"


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def norm_doi(d):
    if not d:
        return ""
    d = d.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm_surname(s):
    s = strip_accents(s or "").lower().strip()
    s = re.sub(r"[^a-z ]", "", s)
    return s


def norm_title(t):
    t = strip_accents(t or "").lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# Count gate on the export before anything is read from it
# ---------------------------------------------------------------------------
if not os.path.exists(RIS):
    fail(f"export not found at {RIS} (it is gitignored; place the licensed file there)")
with open(RIS, "rb") as fh:
    raw = fh.read()
sha = hashlib.sha256(raw).hexdigest()
text = raw.decode("utf-8", errors="replace")
n_ty = len(re.findall(r"^TY  - ", text, flags=re.M))
n_er = len(re.findall(r"^ER  - ", text, flags=re.M))
if n_ty != EXPECTED_RECORDS or n_er != EXPECTED_RECORDS:
    fail(f"count gate: TY {n_ty}, ER {n_er}, expected {EXPECTED_RECORDS}")
if sha != EXPECTED_SHA256:
    fail(f"hash gate: SHA-256 {sha} differs from the logged {EXPECTED_SHA256}")
print(f"count gate PASS: {n_ty} TY / {n_er} ER; SHA-256 matches SEARCH_LOG.md")

# ---------------------------------------------------------------------------
# Parse RIS
# ---------------------------------------------------------------------------
records = []
cur = None
for line in text.splitlines():
    m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
    if not m:
        continue
    tag, val = m.group(1), m.group(2).strip()
    if tag == "TY":
        cur = defaultdict(list)
        cur["TY"].append(val)
    elif tag == "ER":
        records.append(cur)
        cur = None
    elif cur is not None:
        cur[tag].append(val)
if len(records) != EXPECTED_RECORDS:
    fail(f"parsed {len(records)} records")


def first(rec, *tags):
    for t in tags:
        if rec.get(t):
            return rec[t][0]
    return ""


rows = []
for i, r in enumerate(records, 1):
    title = first(r, "TI", "T1")
    doi = norm_doi(first(r, "DO"))
    year = re.sub(r"[^0-9]", "", first(r, "PY", "Y1"))[:4]
    authors = r.get("AU", []) or r.get("A1", [])
    first_author = authors[0].split(",")[0] if authors else ""
    rows.append(dict(
        n=i, accession=first(r, "U2", "AN"), doi=doi, year=year,
        first_author=first_author, title=title, journal=first(r, "JO", "JF", "T2"),
        pubtype=first(r, "TY"),
    ))

# Within export duplicates
doi_counts = Counter(x["doi"] for x in rows if x["doi"])
dup_doi = {d for d, c in doi_counts.items() if c > 1}
title_counts = Counter(norm_title(x["title"]) for x in rows if x["title"])
dup_title = {t for t, c in title_counts.items() if c > 1}

# ---------------------------------------------------------------------------
# Known corpus
# ---------------------------------------------------------------------------
known = []  # dicts: label, source, doi, pmid, surname, year
with open(MASTER, newline="") as fh:
    seen = set()
    for r in csv.DictReader(fh):
        key = (r.get("pmid"), r.get("doi"))
        if key in seen:
            continue
        seen.add(key)
        known.append(dict(label=f"{r['first_author']} {r['year']} ({r['trial_id']})",
                          source="extracted", doi=norm_doi(r.get("doi")), pmid=r.get("pmid"),
                          surname=r["first_author"], year=str(r["year"])[:4]))
with open(REFS) as fh:
    for m in re.finditer(r"\|\s*(\d+)\s*\|\s*([^|]+?)\|\s*(10\.\S+?)\s*\|", fh.read()):
        cite = m.group(2).strip()
        am = re.match(r"([A-Za-z\-' ]+?)\s+[A-Z]{1,3}[,.]", cite)
        ym = re.search(r"\b(19|20)\d{2}\b", cite)
        known.append(dict(label=f"REF{m.group(1)} {cite[:60]}", source="references",
                          doi=norm_doi(m.group(3)), pmid="",
                          surname=(am.group(1) if am else ""), year=(ym.group(0) if ym else "")))
DRUGS = ("exenatide", "liraglutide", "dulaglutide", "semaglutide", "lixisenatide",
         "albiglutide", "tirzepatide", "glp-1", "glp 1", "glucagon-like")
# "cells" is deliberately not in this list: Ahmad 2021 reports circulating
# progenitor cells in its title and is a trial.
NOT_A_TRIAL = re.compile(r"\b(mice|mouse|rats?|in vitro|cell line|meta-analysis|"
                         r"systematic review|review|protocol|case report)\b", re.I)
with open(KNOWN, newline="") as fh:
    for r in csv.DictReader(fh):
        known.append(dict(label=f"{r['first_author']} {r['year']}", source=r["source"],
                          doi="", pmid="", surname=r["first_author"], year=r["year"],
                          require_drug=True))

doi_index = defaultdict(list)
for x in rows:
    if x["doi"]:
        doi_index[x["doi"]].append(x)
ay_index = defaultdict(list)
for x in rows:
    ay_index[(norm_surname(x["first_author"]), x["year"])].append(x)

matched_record_ns = set()
recall_lines = []
for k in known:
    hits = []
    how = ""
    if k["doi"] and k["doi"] in doi_index:
        hits = doi_index[k["doi"]]
        how = "doi"
    else:
        key = (norm_surname(k["surname"]), k["year"])
        # tolerate particles: "le Roux" vs "Roux", "von Scholten" vs "Scholten"
        cands = ay_index.get(key, [])
        if not cands and " " in key[0]:
            cands = ay_index.get((key[0].split()[-1], key[1]), [])
        if k.get("require_drug"):
            # A surname and a year are not an identity. For the adopted mono
            # agonist list the matched title must name an incretin drug and
            # must not read as an animal, in vitro or review paper; Derosa
            # 2010 matched two orlistat trials and Zhang 2018 a rat study
            # before this filter existed.
            cands = [c for c in cands
                     if any(d in c["title"].lower() for d in DRUGS)
                     and not NOT_A_TRIAL.search(c["title"])]
        if cands:
            hits = cands
            how = "author+year+drug" if k.get("require_drug") else "author+year"
    for h in hits:
        matched_record_ns.add(h["n"])
    recall_lines.append((k["source"], k["label"], how, "; ".join(h["title"][:90] for h in hits[:2])))

for x in rows:
    x["matched_known"] = "yes" if x["n"] in matched_record_ns else "no"
    x["dup_doi_within_export"] = "yes" if x["doi"] in dup_doi else "no"
    x["dup_title_within_export"] = "yes" if norm_title(x["title"]) in dup_title else "no"

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
with open(OUT_CSV, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

by_source = defaultdict(lambda: [0, 0])
for src, label, how, titles in recall_lines:
    by_source[src][0] += 1
    if how:
        by_source[src][1] += 1

n_with_doi = sum(1 for x in rows if x["doi"])
n_matched = len(matched_record_ns)
n_new = EXPECTED_RECORDS - n_matched

md = []
md.append("# Embase export: recall against the known corpus, and deduplication\n")
md.append("Produced by `src/dedup_embase.py` from the gitignored export. Count gate: "
          f"{n_ty} TY and {n_er} ER records; SHA-256 `{sha[:12]}…` equals the value in SEARCH_LOG.md.\n")
md.append("## Export composition\n")
md.append("| Quantity | Value |\n|---|---|")
md.append(f"| Records | {EXPECTED_RECORDS} |")
md.append(f"| With DOI | {n_with_doi} |")
md.append(f"| Duplicate DOIs within the export | {sum(doi_counts[d] for d in dup_doi)} records in {len(dup_doi)} DOI groups |")
md.append(f"| Duplicate normalised titles within the export | {sum(title_counts[t] for t in dup_title)} records in {len(dup_title)} title groups |")
md.append(f"| Records matching something already in the corpus | {n_matched} |")
md.append(f"| Records new to screening | {n_new} |\n")
md.append("## Recall of the Embase string against trials known from other routes\n")
md.append("| Known set | Items | Retrieved by Embase | Recall |\n|---|---|---|---|")
for src, (n, hit) in by_source.items():
    md.append(f"| {src} | {n} | {hit} | {hit / n:.0%} |")
md.append("\nAn item counts as retrieved when a record shares its DOI, or its first author surname and year. "
          "Author plus year matches are listed with the matched title so a false match can be seen.\n")
md.append("| Set | Item | Matched by | Matched record title |\n|---|---|---|---|")
for src, label, how, titles in recall_lines:
    md.append(f"| {src} | {label} | {how or 'NOT RETRIEVED'} | {titles} |")
md.append("\nPer record flags (matched_known, duplicate DOI, duplicate title) are in `embase_659_dedup.csv`, "
          "which stays untracked beside the export.\n")
with open(OUT_MD, "w") as fh:
    fh.write("\n".join(md) + "\n")

print(f"records {EXPECTED_RECORDS}, with DOI {n_with_doi}, matched known {n_matched}, new to screening {n_new}")
for src, (n, hit) in by_source.items():
    print(f"recall {src}: {hit}/{n}")
print("wrote", os.path.relpath(OUT_MD, ROOT), "and", os.path.relpath(OUT_CSV, ROOT))
