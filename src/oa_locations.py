#!/usr/bin/env python3
"""Open access locations for the records whose best text is still a partial page or nothing.

Reads the pool, the full text screen's source assignment and the Europe PMC lookup, then asks
OpenAlex (no key, no email, no personal data; one GET per DOI) for an open access location of each
record in proxy_partial or awaiting_fulltext. Writes work/fulltext/oa_locations_2026-10-16.csv
(untracked) and prints a table. The capture of any location found is a separate, browser step.

Usage, from the repository root: python3 -I src/oa_locations.py
"""
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.argv = [sys.argv[0]]
import fulltext_screen as fs  # noqa: E402

ACCESS = os.path.join(fs.OUTDIR, "fulltext_access_2026-10-16.csv")
OUT = os.path.join(ROOT, "work/fulltext/oa_locations_2026-10-16.csv")
FIELDS = ["key", "source", "doi", "pmid", "pmcid_epmc", "openalex_id", "is_oa", "oa_status", "oa_url", "pdf_url", "pmcid_openalex", "note"]


def openalex(doi):
    url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/:()")
    req = urllib.request.Request(url, headers={"User-Agent": "incretin-aging-biomarkers review tooling"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r), ""
    except urllib.error.HTTPError as e:
        return None, f"http {e.code}"
    except Exception as e:  # network errors are recorded, not raised
        return None, type(e).__name__


def main():
    items = {it["key"]: it for it in fs.load_items()}
    pool = {f"{r['pool']}-{r['n']}": r for r in csv.DictReader(open(fs.POOL))}
    access = {}
    if os.path.exists(ACCESS):
        for r in csv.DictReader(open(ACCESS)):
            access[f"{r['pool']}-{r['n']}"] = r
    targets = [k for k, it in items.items() if it["source"] in ("proxy_partial", "awaiting_fulltext")]
    rows = []
    for key in sorted(targets, key=lambda k: (k.split("-")[0], int(k.split("-")[1]))):
        p = pool[key]
        row = dict(key=key, source=items[key]["source"], doi=p["doi"], pmid=p["pmid"],
                   pmcid_epmc=(access.get(key) or {}).get("pmcid", ""), openalex_id="", is_oa="", oa_status="",
                   oa_url="", pdf_url="", pmcid_openalex="", note="")
        if not p["doi"]:
            row["note"] = "no DOI; OpenAlex not queried"
        else:
            w, err = openalex(p["doi"])
            if w is None:
                row["note"] = err
            else:
                oa = w.get("open_access") or {}
                best = w.get("best_oa_location") or {}
                row.update(openalex_id=w.get("id", "").rsplit("/", 1)[-1], is_oa=str(oa.get("is_oa", "")), oa_status=oa.get("oa_status", "") or "",
                           oa_url=oa.get("oa_url", "") or "", pdf_url=best.get("pdf_url", "") or "", pmcid_openalex=(w.get("ids") or {}).get("pmcid", "") or "")
            time.sleep(0.2)
        rows.append(row)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{'key':7s} {'source':18s} {'is_oa':5s} {'status':8s} {'pmcid':12s} location")
    for r in rows:
        print(f"{r['key']:7s} {r['source']:18s} {r['is_oa']:5s} {r['oa_status']:8s} {(r['pmcid_openalex'] or r['pmcid_epmc']):12s} {r['oa_url'] or r['pdf_url'] or r['note']}")


if __name__ == "__main__":
    main()
