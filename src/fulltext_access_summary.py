#!/usr/bin/env python3
"""Counts only summary of full text access for the pool: Europe PMC lookup and
the open access harvest manifest. Writes search/screening/FULLTEXT_ACCESS_SUMMARY.md."""
import csv, os
from collections import Counter
ACCESS = "search/screening/fulltext_access_2026-10-16.csv"
MANIFEST = "work/fulltext/pool/MANIFEST_epmc_2026-10-16.csv"
OUT = "search/screening/FULLTEXT_ACCESS_SUMMARY.md"
rows = list(csv.DictReader(open(ACCESS)))
man = list(csv.DictReader(open(MANIFEST))) if os.path.exists(MANIFEST) else []
def block(route):
    sub = [r for r in rows if r["route"] == route]
    return (len(sub), sum(r["epmc_found"] == "yes" for r in sub), sum(bool(r["epmc_pmcid"]) for r in sub),
            sum(r["is_open_access"] == "Y" for r in sub))
md = ["# Full text access for the screening pool, 16 October 2026\n",
      "Lookup: Europe PMC REST search by DOI (batches of 20) and by PMID for records without a DOI; no key, no email, no personal data sent. "
      "Harvest: Europe PMC full text XML for every record with a PMCID and `isOpenAccess` = Y, saved as XML and a plain text rendering under "
      "`work/fulltext/pool/` (gitignored). Per record rows are in the untracked `fulltext_access_2026-10-16.csv`; the harvest manifest is beside the files.\n",
      "| Route | Records looked up | Found in Europe PMC | With PMCID | Open access |\n|---|---|---|---|---|"]
for route, label in (("doi", "doi (journal articles)"), ("already_extracted", "already_extracted"), ("abstract_only", "abstract_only with a DOI"), ("title_search", "title_search")):
    n, f, p, o = block(route)
    md.append(f"| {label} | {n} | {f} | {p} | {o} |")
doi = [r for r in rows if r["route"] == "doi"]
closed = sum(r["epmc_found"] == "yes" and r["is_open_access"] != "Y" for r in doi)
missing = sum(r["epmc_found"] == "no" for r in doi)
md.append(f"\nOf the {len(doi)} journal articles to retrieve by DOI: {sum(r['is_open_access']=='Y' for r in doi)} are open access, "
          f"{closed} are closed access and need the institutional route (BU EZproxy), {missing} are not in Europe PMC at all "
          f"(articles in press, preprints and journals outside its coverage; locate by DOI resolver).\n")
if man:
    st = Counter(r["status"] for r in man)
    big = sum(1 for r in man if r["status"] in ("ok", "exists") and int(r["txt_chars"] or 0) >= 2000)
    stub = sum(1 for r in man if r["status"] in ("ok", "exists") and int(r["txt_chars"] or 0) < 2000)
    md.append("| Harvest | Value |\n|---|---|")
    md.append(f"| Open access records with PMCID attempted | {len(man)} |")
    md.append(f"| Fetched | {st.get('ok', 0) + st.get('exists', 0)} |")
    md.append(f"| Substantive full text (2,000 characters or more) | {big} |")
    md.append(f"| Stub (front matter, news or calendar items that share a supplement DOI with a conference abstract) | {stub} |")
    md.append(f"| Errors | {sum(v for k, v in st.items() if k.startswith('error'))} |")
    md.append("\nA stub is not a failure of the review record: the conference abstract itself is the full text for that record, and the DOI it carries belongs to the supplement issue.\n")
open(OUT, "w").write("\n".join(md) + "\n")
print("\n".join(md))
