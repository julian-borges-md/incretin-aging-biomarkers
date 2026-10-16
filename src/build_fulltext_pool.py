#!/usr/bin/env python3
"""
build_fulltext_pool.py

Assembles the set of records that passed title and abstract screening into
one full text screening pool, with the grouping and routing that full text
retrieval needs. Reads the screening decision files through the same pool
construction as src/screen_titles.py, so a record's number here is the number
it had at screening, and every export passes its count and SHA-256 gate
before a record is read.

A record enters the pool by one of three routes
  v1_include     pool 1 (Embase articles), final include under criteria v1
  v2_rescued     pool 1, finally excluded under v1, included by either
                 reviewer under criteria v2
  pool3_include  pool 3 (Web of Science records in neither earlier export),
                 final include under criteria v2; joined once chain4's summary exists
  pool2_include  pool 2 (Embase registry records and CENTRAL records not in
                 the Embase export), final include under criteria v2

For each record: bibliographic identifiers (DOI, PMID where the export
carries one, ClinicalTrials.gov identifiers found in the record), the
publication type, whether the trial is already extracted, and a retrieval
route. Records are then grouped into candidate studies: a shared DOI, a
shared normalised title, or a shared NCT identifier joins two records.

Outputs
  search/screening/fulltext_pool_2026-10-16.csv    per record, untracked
                                                   (carries export titles)
  search/screening/FULLTEXT_POOL_SUMMARY.md        counts only, committed

Standard library only. Run from the repository root:
  python3 -I src/build_fulltext_pool.py
"""
import csv
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
import screen_titles as st  # noqa: E402  (gates, pools, decision readers)

MASTER = os.path.join(ROOT, "analysis/data/extraction_master.csv")
OUT_CSV = os.path.join(ROOT, "search/screening/fulltext_pool_2026-10-16.csv")
OUT_MD = os.path.join(ROOT, "search/screening/FULLTEXT_POOL_SUMMARY.md")

NCT = re.compile(r"\bNCT\d{8}\b")


def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return re.sub(r"^doi:\s*", "", d)


def norm_title(t):
    t = "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def raw_fields(name, tags):
    """Tag values per record (by position) straight from an export, for tags
    the screening parser does not keep (CENTRAL C3 carries PUBMED and EMBASE ids)."""
    path = os.path.join(ROOT, st.EXPORTS[name]["ris"])
    with open(path, "rb") as fh:
        text = fh.read().decode("utf-8", errors="replace")
    out, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            cur = defaultdict(list)
        elif tag == "ER":
            out.append(cur)
            cur = None
        elif cur is not None and tag in tags:
            cur[tag].append(val)
    return out


def load_pool(pool_name):
    st.POOL = pool_name
    return st.parse_ris()


def pmid_from_c3(vals):
    for v in vals:
        m = re.search(r"PUBMED\s+(\d+)", v)
        if m:
            return m.group(1)
    return ""


# ---------------------------------------------------------------------------
# Records that passed screening, by route
# ---------------------------------------------------------------------------
rows = []

st.POOL = "embase"
p1 = load_pool("embase")
st.CRITERIA_VERSION = "v1"
v1_final = st.final_decisions("v1")
st.CRITERIA_VERSION = "v2"
A2, B2 = st.read_decisions(st.decisions_path("A")), st.read_decisions(st.decisions_path("B"))
st.CRITERIA_VERSION = "v1"
if len(v1_final) != len(p1):
    print(f"FAIL: pool 1 has {len(p1)} records but {len(v1_final)} final v1 decisions")
    sys.exit(1)
n_v1_inc = n_v2_resc = 0
for r in p1:
    n = r["n"]
    if v1_final[n] == "include":
        rows.append(dict(r, pool="1", stage="v1_include"))
        n_v1_inc += 1
    elif n in A2 and n in B2 and "include" in (A2[n]["decision"], B2[n]["decision"]):
        rows.append(dict(r, pool="1", stage="v2_rescued"))
        n_v2_resc += 1

st.POOL = "batch2"
st.CRITERIA_VERSION = "v2"
p2 = load_pool("batch2")
p2_final = st.final_decisions("v2")
if len(p2_final) != len(p2):
    print(f"FAIL: pool 2 has {len(p2)} records but {len(p2_final)} final decisions")
    sys.exit(1)
n_p2_inc = 0
for r in p2:
    if p2_final[r["n"]] == "include":
        rows.append(dict(r, pool="2", stage="pool2_include"))
        n_p2_inc += 1
# Pool 3: the Web of Science records in neither earlier export (batch3), screened under v2 by chain4.
# The pool is built without it until chain4's summary exists, so the script runs at every stage.
n_p3_inc = 0
st.POOL, st.CRITERIA_VERSION = "batch3", "v2"
P3_SUMMARY = os.path.join(ROOT, "search/screening/SCREENING_SUMMARY_batch3_v2.md")
if os.path.exists(P3_SUMMARY):
    p3 = load_pool("batch3")
    p3_final = st.final_decisions("v2")
    if len(p3_final) != len(p3):
        print(f"FAIL: pool 3 has {len(p3)} records but {len(p3_final)} final decisions")
        sys.exit(1)
    for r in p3:
        if p3_final[r["n"]] == "include":
            rows.append(dict(r, pool="3", stage="pool3_include"))
            n_p3_inc += 1
else:
    print("pool 3 (batch3) has no screening summary yet: pool built from pools 1 and 2 only")
st.POOL, st.CRITERIA_VERSION = "embase", "v1"

EXPECTED = dict(v1_include=338, v2_rescued=24, pool2_include=185)
EXPECTED_POOL3 = None  # set from SCREENING_SUMMARY_batch3_v2.md once chain4 has run, then gated like the others
got = dict(v1_include=n_v1_inc, v2_rescued=n_v2_resc, pool2_include=n_p2_inc)
if got != EXPECTED:
    print(f"FAIL: stage counts {got} differ from the committed summaries {EXPECTED}")
    sys.exit(1)
if os.path.exists(P3_SUMMARY) and EXPECTED_POOL3 is not None and n_p3_inc != EXPECTED_POOL3:
    print(f"FAIL: pool 3 includes {n_p3_inc} differ from the committed summary {EXPECTED_POOL3}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Identifiers the screening parser does not carry: PMID (CENTRAL C3), raw abstracts for NCT scan
# ---------------------------------------------------------------------------
c3, ja = {}, {}
for i, rec in enumerate(raw_fields("central", {"C3", "JA"}), 1):
    c3[i] = pmid_from_c3(rec.get("C3", []))
    ja[i] = " ".join(rec.get("JA", []))  # registry derived records carry the registry URL here
known = []
with open(MASTER, newline="") as fh:
    for r in csv.DictReader(fh):
        known.append(dict(doi=norm_doi(r.get("doi")), pmid=(r.get("pmid") or "").strip(),
                          trial_id=r.get("trial_id", ""), label=f"{r['first_author']} {r['year']}"))
known_dois = {k["doi"] for k in known if k["doi"]}
known_pmids = {k["pmid"] for k in known if k["pmid"]}
known_ncts = {m for k in known for m in NCT.findall(k["trial_id"] or "")}

for r in rows:
    r["doi"] = norm_doi(r.get("doi"))
    r["pmid"] = c3.get(r["source_n"], "") if r["source"] == "central" else ""
    text = f"{r['accession']} {r['title']} {r.get('abstract', '')} {ja.get(r['source_n'], '') if r['source'] == 'central' else ''}"
    r["nct_ids"] = ";".join(sorted(set(NCT.findall(text))))
    m = re.search(r"TrialID=([A-Za-z0-9\-]+)", ja.get(r["source_n"], "")) if r["source"] == "central" else None
    r["registry_id"] = (r["accession"] if r["accession"].startswith("NCT") else (r["nct_ids"].split(";")[0] if r["nct_ids"] and "registry" in (r.get("rtype") or "").lower() else (m.group(1) if m else "")))
    r["already_extracted"] = "yes" if (r["doi"] and r["doi"] in known_dois) or (r["pmid"] and r["pmid"] in known_pmids) \
        or (set(r["nct_ids"].split(";")) & known_ncts) else "no"
    rt = (r.get("rtype") or "").lower()
    if r["source"] == "embase_registry" or "registry" in rt:
        route = "registry_record"
    elif "conference" in rt:
        route = "abstract_only"
    elif r["already_extracted"] == "yes":
        route = "already_extracted"
    elif r["doi"]:
        route = "doi"
    elif r["pmid"]:
        route = "pmid"
    else:
        route = "title_search"
    r["route"] = route
    r["publication_type"] = r.get("rtype", "")

# ---------------------------------------------------------------------------
# Candidate study grouping: shared DOI, shared normalised title, shared NCT id
# ---------------------------------------------------------------------------
parent = list(range(len(rows)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def union(i, j):
    parent[find(i)] = find(j)


by_key = defaultdict(list)
for i, r in enumerate(rows):
    if r["doi"]:
        by_key[("doi", r["doi"])].append(i)
    t = norm_title(r["title"])
    if t:
        by_key[("title", t)].append(i)
    for nct in filter(None, r["nct_ids"].split(";")):
        by_key[("nct", nct)].append(i)
for key, idx in by_key.items():
    for j in idx[1:]:
        union(idx[0], j)
groups = defaultdict(list)
for i in range(len(rows)):
    groups[find(i)].append(i)
for gid, (root, idx) in enumerate(sorted(groups.items(), key=lambda kv: min(kv[1])), 1):
    for i in idx:
        rows[i]["study_group"] = gid
        rows[i]["group_size"] = len(idx)

fields = ["pool", "stage", "n", "source", "source_n", "accession", "year", "publication_type", "doi", "pmid",
          "nct_ids", "registry_id", "matched_known", "already_extracted", "route", "study_group", "group_size", "title"]
with open(OUT_CSV, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
n = len(rows)
by_stage = Counter(r["stage"] for r in rows)
by_source = Counter(r["source"] for r in rows)
by_route = Counter(r["route"] for r in rows)
by_type = Counter(r["publication_type"] for r in rows)
n_groups = len(groups)
multi = [idx for idx in groups.values() if len(idx) > 1]
reg_linked = sum(1 for r in rows if r["route"] == "registry_record" and r["group_size"] > 1)
reg_nct = sum(1 for r in rows if r["route"] == "registry_record" and r["registry_id"].startswith("NCT"))
reg_other = sum(1 for r in rows if r["route"] == "registry_record" and r["registry_id"] and not r["registry_id"].startswith("NCT"))
with_doi = sum(1 for r in rows if r["doi"])
with_pmid = sum(1 for r in rows if r["pmid"])
with_nct = sum(1 for r in rows if r["nct_ids"])
n_known = sum(1 for r in rows if r["matched_known"])
n_extracted = sum(1 for r in rows if r["already_extracted"] == "yes")
year_c = Counter((r["year"] or "")[:4] for r in rows)

md = ["# Full text screening pool, assembled 16 October 2026\n",
      "Produced by `src/build_fulltext_pool.py` from the screening decision files and the gated exports. "
      "Per record rows (with titles) are in the untracked `fulltext_pool_2026-10-16.csv` beside the decision files.\n",
      "| Quantity | Value |\n|---|---|",
      f"| Records in the pool | {n} |",
      f"| By stage | v1 include {by_stage['v1_include']}; v2 rescued {by_stage['v2_rescued']}; pool 2 include {by_stage['pool2_include']}; pool 3 include {by_stage['pool3_include']}" + ("" if os.path.exists(P3_SUMMARY) else " (pool 3 not screened yet)") + " |",
      f"| By source | " + "; ".join(f"{k} {v}" for k, v in by_source.most_common()) + " |",
      f"| With DOI / with PMID / with an NCT identifier in the record | {with_doi} / {with_pmid} / {with_nct} |",
      f"| Linked to a known relevant trial at screening | {n_known} |",
      f"| Already extracted (DOI, PMID or NCT in the extraction master) | {n_extracted} |",
      f"| Candidate studies after grouping (shared DOI, title or NCT) | {n_groups} |",
      f"| Groups with more than one record | {len(multi)} (records in them {sum(len(g) for g in multi)}) |",
      f"| Registry records grouped with another record in the pool | {reg_linked} of {by_route['registry_record']} |",
      f"| Registry records by register | ClinicalTrials.gov {reg_nct}; other registers via ICTRP {reg_other}; no identifier {by_route['registry_record'] - reg_nct - reg_other} |\n",
      "| Retrieval route | Records | What retrieval means |\n|---|---|---|",
      f"| doi | {by_route['doi']} | journal article, fetch by DOI through the institutional route |",
      f"| pmid | {by_route['pmid']} | journal article without DOI in the record, fetch by PMID |",
      f"| title_search | {by_route['title_search']} | no DOI or PMID in the record, locate by title |",
      f"| abstract_only | {by_route['abstract_only']} | conference abstract; the record is the full text, judged as such |",
      f"| registry_record | {by_route['registry_record']} | ClinicalTrials.gov or ICTRP entry; read the registry page and its results and publications |",
      f"| already_extracted | {by_route['already_extracted']} | trial already in the extraction master; no retrieval |\n",
      "| Publication type (as exported) | Records |\n|---|---|"]
for k, v in by_type.most_common():
    md.append(f"| {k or '(blank)'} | {v} |")
md.append("\n| Year | Records |\n|---|---|")
for k, v in sorted(year_c.items(), reverse=True)[:12]:
    md.append(f"| {k or '(blank)'} | {v} |")
md.append("\nGrouping joins records, not trials: two records in one group are the same study only if full text confirms it, "
          "and a registry record grouped with an article is the natural pair to read together. Reviews and meta analyses that "
          "survived screening (the criteria say include when in doubt) are carried with their publication type so they can be "
          "excluded at the first page of full text.\n")
with open(OUT_MD, "w") as fh:
    fh.write("\n".join(md) + "\n")
print("\n".join(md))
print("wrote", os.path.relpath(OUT_CSV, ROOT), "and", os.path.relpath(OUT_MD, ROOT))
