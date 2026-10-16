#!/usr/bin/env python3
"""
epmc_fetch_one.py

Fetches one open access full text from Europe PMC by DOI, PMID or PMCID and writes a plain text
rendering (same rendering as epmc_harvest.py: section titles, paragraphs, table cells tab separated)
under work/fulltext/companion/ (gitignored). Used for companion papers of included abstracts and for
baseline tables that an extracted row needs as a denominator. Nothing is fetched through a proxy
here: a record without an open access full text in Europe PMC is reported and left alone.

Usage
  python3 -I src/epmc_fetch_one.py 10.1186/s12933-015-0279-z [NAME]
  python3 -I src/epmc_fetch_one.py PMC4551517 [NAME]
  python3 -I src/epmc_fetch_one.py 26338040 [NAME]
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.getcwd()
OUTDIR = os.path.join(ROOT, "work", "fulltext", "companion")
API = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def xml_to_text(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []

    def walk(el):
        tag = el.tag.split("}")[-1]
        if tag in ("title", "label"):
            out.append("\n## " + "".join(el.itertext()).strip() + "\n")
            return
        if tag in ("p", "td", "th", "caption", "abstract"):
            out.append("".join(el.itertext()).strip() + ("\t" if tag in ("td", "th") else "\n"))
            return
        if tag == "tr":
            for c in el:
                walk(c)
            out.append("\n")
            return
        for c in el:
            walk(c)

    walk(root)
    return re.sub(r"\n{3,}", "\n\n", "".join(out))


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "incretin-aging-biomarkers/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main(argv):
    if not argv:
        sys.exit(__doc__)
    ident = argv[0].strip()
    if ident.upper().startswith("PMC"):
        q = f"PMCID:{ident.upper()}"
    elif ident.isdigit():
        q = f"EXT_ID:{ident} AND SRC:MED"
    else:
        q = f"DOI:{ident}"
    url = f"{API}/search?query={urllib.parse.quote(q)}&format=json&resultType=lite"
    hits = json.loads(get(url)).get("resultList", {}).get("result", [])
    if not hits:
        sys.exit(f"no Europe PMC record for {ident}")
    h = hits[0]
    pmcid = h.get("pmcid", "")
    print(f"{ident}: pmid {h.get('pmid', '')} pmcid {pmcid or '-'} oa {h.get('isOpenAccess', '')} "
          f"{h.get('authorString', '')[:40]} {h.get('pubYear', '')} {h.get('journalTitle', '')[:40]}")
    if not pmcid:
        sys.exit("no PMCID: no Europe PMC full text")
    xml_bytes = get(f"{API}/{pmcid}/fullTextXML", timeout=40)
    if not xml_bytes.strip():
        sys.exit(f"{pmcid}: empty full text response (not open access in Europe PMC)")
    text = xml_to_text(xml_bytes)
    name = argv[1] if len(argv) > 1 else pmcid
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{name}.txt")
    with open(path, "w") as fh:
        fh.write(text)
    print(f"wrote {os.path.relpath(path, ROOT)} ({len(text)} chars, {len(xml_bytes)} xml bytes)")


if __name__ == "__main__":
    main(sys.argv[1:])
