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
  python3 src/dedup_embase.py            # Embase export (default)
  python3 src/dedup_embase.py central    # CENTRAL export, same gates and
                                         # linkage, plus overlap with the
                                         # Embase export by DOI and title
Each export has its own count and SHA-256 gate in SOURCES; a file that is
not the logged file stops the run before anything is read from it.
"""
import csv
import hashlib
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis/data/extraction_master.csv")
REFS = os.path.join(ROOT, "docs/REFERENCES.md")
KNOWN = os.path.join(ROOT, "search/known_relevant_trials.csv")

SOURCES = {
    "embase": dict(
        label="Embase",
        ris="search/embase_2026-10-15/embase_659.ris",
        out_md="search/embase_2026-10-15/RECALL_AND_DEDUP.md",
        out_csv="search/embase_2026-10-15/embase_659_dedup.csv",
        expected=659,
        sha256="e8d3a9d4e195375f1d1aaaead76ae0ad0d937206194e152984d71d42405fefb2",
    ),
    "central": dict(
        label="CENTRAL",
        ris="search/central_2026-10-15/central_460.ris",
        out_md="search/central_2026-10-15/RECALL_AND_DEDUP.md",
        out_csv="search/central_2026-10-15/central_460_dedup.csv",
        expected=460,
        sha256="7c12c88115631e45195e82641d2b0a6f9c5bd0835d48f7972c5b08372c0547f3",
        overlap_with=("embase",),
    ),
    "wos": dict(
        label="Web of Science",
        ris="search/wos_2026-10-16/wos_317.ris",
        out_md="search/wos_2026-10-16/RECALL_AND_DEDUP.md",
        out_csv="search/wos_2026-10-16/wos_317_dedup.csv",
        expected=317,
        sha256="844f31118a3495a63892f8562f49ec8d52ab1f93cbade3b9a9051da3b12fa259",
        overlap_with=("embase", "central"),
    ),
}
SOURCE = sys.argv[1] if len(sys.argv) > 1 else "embase"
if SOURCE not in SOURCES:
    print("FAIL: unknown source", SOURCE, "; known:", ", ".join(SOURCES))
    sys.exit(1)
SRC = SOURCES[SOURCE]
LABEL = SRC["label"]
RIS = os.path.join(ROOT, SRC["ris"])
OUT_MD = os.path.join(ROOT, SRC["out_md"])
OUT_CSV = os.path.join(ROOT, SRC["out_csv"])
EXPECTED_RECORDS = SRC["expected"]
EXPECTED_SHA256 = SRC["sha256"]
# Cross database overlap: each later export is compared with the earlier ones
# (CENTRAL with Embase; Web of Science with Embase and CENTRAL). The reference
# exports pass the same count and hash gates when they are read for that purpose.
OVERLAP_REFS = [(k, SOURCES[k]) for k in SRC.get("overlap_with", ())]


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
text = raw.decode("utf-8", errors="replace").lstrip("\ufeff")  # Web of Science writes a byte order mark before the first TY
n_ty = len(re.findall(r"^TY  - ", text, flags=re.M))
n_er = len(re.findall(r"^ER  -", text, flags=re.M))  # Web of Science writes ER without the trailing space
if n_ty != EXPECTED_RECORDS or n_er != EXPECTED_RECORDS:
    fail(f"count gate: TY {n_ty}, ER {n_er}, expected {EXPECTED_RECORDS}")
if sha != EXPECTED_SHA256:
    fail(f"hash gate: SHA-256 {sha} differs from the logged {EXPECTED_SHA256}")
print(f"count gate PASS: {n_ty} TY / {n_er} ER; SHA-256 matches SEARCH_LOG.md")

# ---------------------------------------------------------------------------
# Parse RIS
# ---------------------------------------------------------------------------
def parse_ris(text):
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
    return records


records = parse_ris(text)
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
        first_author=first_author, title=title, journal=first(r, "JO", "JF", "T2", "JA"),
        pubtype=first(r, "TY"),
    ))

# Within export duplicates
doi_counts = Counter(x["doi"] for x in rows if x["doi"])
dup_doi = {d for d, c in doi_counts.items() if c > 1}
title_counts = Counter(norm_title(x["title"]) for x in rows if x["title"])
dup_title = {t for t, c in title_counts.items() if c > 1}

# Overlap with the Embase export (cross database deduplication), DOI first,
# normalised title for the rest. The reference export passes the same gates.
overlaps = []
for ref_key, ref in OVERLAP_REFS:
    ref_path = os.path.join(ROOT, ref["ris"])
    if not os.path.exists(ref_path):
        fail(f"overlap reference not found at {ref_path}")
    with open(ref_path, "rb") as fh:
        ref_raw = fh.read()
    if hashlib.sha256(ref_raw).hexdigest() != ref["sha256"]:
        fail(f"overlap reference {ref_key}: SHA-256 differs from the logged value")
    ref_records = parse_ris(ref_raw.decode("utf-8", errors="replace").lstrip("\ufeff"))
    if len(ref_records) != ref["expected"]:
        fail(f"overlap reference {ref_key}: parsed {len(ref_records)} records")
    ref_dois = {norm_doi(first(r, "DO")) for r in ref_records if first(r, "DO")}
    ref_titles = {norm_title(first(r, "TI", "T1")) for r in ref_records if first(r, "TI", "T1")}
    n_by_doi = n_by_title = 0
    for x in rows:
        how = ""
        if x["doi"] and x["doi"] in ref_dois:
            how = "doi"
            n_by_doi += 1
        elif x["title"] and norm_title(x["title"]) in ref_titles:
            how = "title"
            n_by_title += 1
        x[f"in_{ref_key}_export"] = how or "no"
    overlaps.append(dict(key=ref_key, label=ref["label"], n=ref["expected"], by_doi=n_by_doi, by_title=n_by_title))
if overlaps:
    for x in rows:
        x["in_any_earlier_export"] = "yes" if any(x[f"in_{o['key']}_export"] != "no" for o in overlaps) else "no"

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
md.append(f"# {LABEL} export: recall against the known corpus, and deduplication\n")
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
md.append(f"## Recall of the {LABEL} string against trials known from other routes\n")
md.append(f"| Known set | Items | Retrieved by {LABEL} | Recall |\n|---|---|---|---|")
for src, (n, hit) in by_source.items():
    md.append(f"| {src} | {n} | {hit} | {hit / n:.0%} |")
md.append("\nAn item counts as retrieved when a record shares its DOI, or its first author surname and year. "
          "Author plus year matches are listed with the matched title so a false match can be seen.\n")
md.append("| Set | Item | Matched by | Matched record title |\n|---|---|---|---|")
for src, label, how, titles in recall_lines:
    md.append(f"| {src} | {label} | {how or 'NOT RETRIEVED'} | {titles} |")
for overlap in overlaps:
    n_over = overlap["by_doi"] + overlap["by_title"]
    md.append(f"\n## Overlap with the {overlap['label']} export\n")
    md.append("| Quantity | Value |\n|---|---|")
    md.append(f"| {overlap['label']} records compared | {overlap['n']} |")
    md.append(f"| {LABEL} records also in {overlap['label']}, matched by DOI | {overlap['by_doi']} |")
    md.append(f"| {LABEL} records also in {overlap['label']}, matched by normalised title only | {overlap['by_title']} |")
    md.append(f"| {LABEL} records not in the {overlap['label']} export | {EXPECTED_RECORDS - n_over} |")
    md.append("\nA title match without a DOI match is a candidate duplicate, not a confirmed one; the per record flag names the route.\n")
if len(overlaps) > 1:
    n_any = sum(1 for x in rows if x["in_any_earlier_export"] == "yes")
    md.append(f"\n## Records not in any earlier export\n")
    md.append("| Quantity | Value |\n|---|---|")
    md.append(f"| {LABEL} records in at least one earlier export ({', '.join(o['label'] for o in overlaps)}) | {n_any} |")
    md.append(f"| {LABEL} records in none of them (new to screening from this database) | {EXPECTED_RECORDS - n_any} |")
flag_names = "".join(f", in_{o['key']}_export" for o in overlaps) + (", in_any_earlier_export" if len(overlaps) > 1 else "")
md.append(f"\nPer record flags (matched_known, duplicate DOI, duplicate title{flag_names}) are in `{os.path.basename(OUT_CSV)}`, "
          "which stays untracked beside the export.\n")
# A manual reading appended below the generated tables survives regeneration:
# the generated part is replaced, the hand written part is kept verbatim.
MANUAL_MARKER = "\n## Manual reading"
manual_tail = ""
if os.path.exists(OUT_MD):
    prev = open(OUT_MD).read()
    if MANUAL_MARKER in prev:
        manual_tail = prev[prev.index(MANUAL_MARKER):]
with open(OUT_MD, "w") as fh:
    fh.write("\n".join(md) + "\n" + manual_tail)

print(f"{LABEL}: records {EXPECTED_RECORDS}, with DOI {n_with_doi}, matched known {n_matched}, new to screening {n_new}")
for overlap in overlaps:
    print(f"overlap with {overlap['label']}: {overlap['by_doi']} by DOI, {overlap['by_title']} by title only")
if len(overlaps) > 1:
    print(f"in none of the earlier exports: {sum(1 for x in rows if x['in_any_earlier_export'] == 'no')}")
for src, (n, hit) in by_source.items():
    print(f"recall {src}: {hit}/{n}")
print("wrote", os.path.relpath(OUT_MD, ROOT), "and", os.path.relpath(OUT_CSV, ROOT))
