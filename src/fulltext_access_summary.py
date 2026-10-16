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
DIRECT = "work/fulltext/direct/MANIFEST_direct_2026-10-16.csv"
if os.path.exists(DIRECT):
    dm = list(csv.DictReader(open(DIRECT)))
    dc = Counter(r["status"] for r in dm)
    md.append("## Direct fetch of the records still needing a text (no proxy, no credentials)\n")
    md.append("Produced by `src/direct_fetch.py`: DOI resolved and the publisher page saved as text, classified by section headings, length and paywall marks; "
              "preprints fetched as JATS XML from the bioRxiv or medRxiv API; records without a DOI looked up in PubMed by title.\n")
    md.append("| Outcome | Records |\n|---|---|")
    for k, v in dc.most_common():
        md.append(f"| {k} | {v} |")
    md.append(f"\nFull texts obtained this way: {sum(v for k, v in dc.items() if k.startswith('fulltext'))} (publisher open access pages and preprints), "
              "screened as the `direct_fulltext` source. Everything else on this list needs the institutional route (BU EZproxy), which requires a live sign in.\n")
PROXY = "work/fulltext/proxy/MANIFEST_proxy_2026-10-16.csv"
if os.path.exists(PROXY):
    pm = list(csv.DictReader(open(PROXY)))
    pc = Counter(r["status"] for r in pm)
    hosts = Counter(r["host"] for r in pm if r["status"] == "fulltext")
    md.append("## Institutional route (BU EZproxy, browser capture)\n")
    md.append("Each remaining DOI was opened in the browser through `https://ezproxy.bu.edu/login?url=https://doi.org/<doi>` (publisher hosts where the DOI route fails: "
              "NEJM `www-nejm-org.ezproxy.bu.edu/doi/full/`, Springer `link-springer-com.ezproxy.bu.edu/article/`, ClinicalKey titles through the ScienceDirect PII page, Thieme `products/ejournals/html/`); "
              "the page's visible text was saved from the browser as a local file with a KEY header, then moved and classified by `src/proxy_harvest.py` (manifest beside the files, gitignored). "
              "The sign in was done by the Director; the agent never entered credentials. Classification: `fulltext` = three of the four section marks (Methods, Results, Discussion, References; English or Russian) "
              "and more than 12,000 characters; `partial` otherwise (abstract pages, but also complete short documents such as letters, comments and reviews without methods sections).\n")
    md.append("| Outcome | Records |\n|---|---|")
    for k, v in pc.most_common():
        md.append(f"| {k} | {v} |")
    small = sum(1 for r in pm if r["status"] == "partial" and int(r["chars"] or 0) < 2000)
    md.append(f"\nCaptures of at least 2,000 characters are screened: `fulltext` as the `proxy_fulltext` source, `partial` as the `proxy_partial` source with a label that says the page may be complete or abstract only "
              f"({pc['partial'] - small} records; the other {small} partial captures are resolver or error pages under 2,000 characters and count as not retrieved).\n")
    md.append("| Host of the full text captures | Records |\n|---|---|")
    for k, v in hosts.most_common():
        md.append(f"| {k} | {v} |")
    md.append("\n### Records still without a text (recorded by hand from the capture attempts)\n")
    md.append("| Record | Identifier | What was found |\n|---|---|---|")
    for row in (
        ("1-48", "10.13429/j.cnki.cjcr.2026.06.008", "chndoi.org resolver page only (423 characters); Chinese journal, full text not on a reachable site"),
        ("1-90", "10.25258/ijddt.16.44s.15", "DOI does not resolve (impactfactor.org placeholder, 105 characters)"),
        ("1-160", "10.31838/ijprt/15.02.374", "DOI not found at doi.org"),
        ("1-183", "10.3760/cma.j.cn115791-20240318-00120", "yiigle.com page did not render (131 characters)"),
        ("1-443", "no DOI; Int J Clin Exp Med 2020;13(2):1219", "publisher site answered 509 Bandwidth Limit Exceeded; not in PubMed"),
        ("1-595", "no DOI; Dokkyo J Med Sci 2014;41(3):211", "not located online; not in PubMed"),
        ("2-223", "no DOI; Drug Invention Today 2019;12(11):2549", "not located online; not in PubMed"),
    ):
        md.append(f"| {row[0]} | {row[1]} | {row[2]} |")
    md.append("")
open(OUT, "w").write("\n".join(md) + "\n")
print("\n".join(md))
