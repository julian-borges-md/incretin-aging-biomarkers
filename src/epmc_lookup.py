#!/usr/bin/env python3
"""Europe PMC lookup for the full text pool: PMID, PMCID, open access flag and
full text availability per DOI or PMID. Writes search/screening/fulltext_access_2026-10-16.csv
(untracked). No email or key is sent; the public REST endpoint only."""
import csv, json, time, urllib.parse, urllib.request, sys, os
POOL = "search/screening/fulltext_pool_2026-10-16.csv"
OUT = "search/screening/fulltext_access_2026-10-16.csv"
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
rows = list(csv.DictReader(open(POOL)))
targets = [r for r in rows if r["route"] in ("doi", "pmid", "already_extracted", "title_search") or (r["route"] == "abstract_only" and r["doi"])]
print("pool rows", len(rows), "lookup targets", len(targets), flush=True)

def query(q):
    url = BASE + "?" + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "lite", "pageSize": 100})
    req = urllib.request.Request(url, headers={"User-Agent": "incretin-aging-biomarkers-review/1.0 (systematic review full text pool)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                return json.load(resp)
        except Exception as e:
            print("retry", attempt, e, flush=True); time.sleep(3)
    return {}

results = {}
dois = sorted({r["doi"] for r in targets if r["doi"]})
for i in range(0, len(dois), 20):
    batch = dois[i:i + 20]
    q = " OR ".join(f'DOI:"{d}"' for d in batch)
    data = query(q)
    for hit in data.get("resultList", {}).get("result", []):
        d = (hit.get("doi") or "").lower()
        if d:
            results[("doi", d)] = hit
    print(f"doi batch {i // 20 + 1}: {len(batch)} queried, {len(data.get('resultList', {}).get('result', []))} hits", flush=True)
    time.sleep(0.5)
pmids = sorted({r["pmid"] for r in targets if r["pmid"] and not r["doi"]})
for i in range(0, len(pmids), 20):
    batch = pmids[i:i + 20]
    q = " OR ".join(f"EXT_ID:{p} AND SRC:MED" for p in batch)
    data = query(q)
    for hit in data.get("resultList", {}).get("result", []):
        results[("pmid", hit.get("pmid", ""))] = hit
    time.sleep(0.5)

fields = ["pool", "n", "source", "accession", "route", "doi", "pmid", "epmc_found", "epmc_pmid", "epmc_pmcid", "is_open_access", "in_epmc", "has_pdf", "pub_type", "title"]
n_found = n_oa = n_pmc = 0
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in targets:
        hit = results.get(("doi", r["doi"])) if r["doi"] else results.get(("pmid", r["pmid"]))
        found = bool(hit)
        n_found += found
        oa = (hit or {}).get("isOpenAccess", "")
        pmcid = (hit or {}).get("pmcid", "")
        n_oa += oa == "Y"; n_pmc += bool(pmcid)
        w.writerow(dict(pool=r["pool"], n=r["n"], source=r["source"], accession=r["accession"], route=r["route"], doi=r["doi"], pmid=r["pmid"],
                        epmc_found="yes" if found else "no", epmc_pmid=(hit or {}).get("pmid", ""), epmc_pmcid=pmcid,
                        is_open_access=oa, in_epmc=(hit or {}).get("inEPMC", ""), has_pdf=(hit or {}).get("hasPDF", ""),
                        pub_type=";".join((hit or {}).get("pubTypeList", {}).get("pubType", [])) if hit else "", title=r["title"][:120]))
print(f"targets {len(targets)}: found in Europe PMC {n_found}, with PMCID {n_pmc}, open access {n_oa}", flush=True)
print("wrote", OUT)
