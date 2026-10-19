#!/usr/bin/env python3
"""
anchor_references_check.py

Verifies the 29 anchor references in docs/REFERENCES.md the way
src/included_studies_references.py verifies the 76 included studies: resolve each DOI at Europe PMC,
fall back to Crossref, and compare the returned first author surname and publication year against
what the document records.

Why. docs/REFERENCES.md asserted that all 29 were verified against PubMed with a resolvable DOI. The
same assertion was made about the included studies and, when the check was finally written, eight of
those 76 named the wrong first author and one the wrong year. An assertion of verification is not
verification, and the anchor references carry the Introduction and the Discussion, where a wrong
citation is a wrong attribution of a claim to a research group.

The document is prose with tables, so the parse is deliberately narrow: a reference row is a table
row with three cells whose first cell is an integer and whose third is a DOI. Rows that do not match
are reported as unparsed rather than skipped silently, because a reference this script cannot see is
a reference it cannot check.

Surnames are folded for diacritics before comparison, as in the included studies check: the registry
prints Meyhofer with an umlaut and Simo with an acute accent, and a comparison that fails on those
reports a defect where there is none.

Usage
  python3 -I src/anchor_references_check.py              # network
  python3 -I src/anchor_references_check.py --offline    # parse and report only, no lookups
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = os.getcwd()
DOC = os.path.join(ROOT, "docs", "REFERENCES.md")
OUT = os.path.join(ROOT, "analysis", "output", "anchor_references_check.csv")
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF = "https://api.crossref.org/works/"

ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(10\.\S+?)\s*\|\s*$")


def fold(s):
    """Strip diacritics and lower case, so Petkovic and Petkovic with accents compare equal."""
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def parse_year(ref):
    """The publication year, which in this citation style follows the journal and precedes the
    volume: `Journal. 2024;30(7):2037-2048`.

    Taking the last four digit number in the row instead returns the last page: reference 15 came
    out as 2048 and reference 17 as 2065, and both would then have been reported as a year mismatch
    against the registry, which is a check manufacturing its own defects. The year is read from its
    position in the style, and only if that fails is any year in the string accepted.
    """
    m = re.search(r"\.\s*((?:19|20)\d\d)\s*[;:]", ref)
    if m:
        return m.group(1)
    m = re.search(r"\.\s*((?:19|20)\d\d)\s*$", ref.strip())
    if m:
        return m.group(1)
    m = re.search(r"\b((?:19|20)\d\d)\b", ref)
    return m.group(1) if m else ""


def parse_locus(ref):
    """Volume, issue and pages from `Journal. YYYY;vol(iss):pages`.

    Any of the three may be absent, in which case it is not compared rather than guessed.
    """
    m = re.search(r";\s*(\d+)\s*(?:\((\d+[^)]*)\))?\s*(?::\s*([0-9eE]+[-\u2013]?[0-9]*))?", ref)
    if not m:
        return "", "", ""
    vol = m.group(1) or ""
    iss = m.group(2) or ""
    pages = (m.group(3) or "").replace("\u2013", "-")
    return vol, iss, pages


def parse(text):
    refs, unparsed = [], []
    for line in text.splitlines():
        line = line.rstrip()
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*#\s*\|", line) or re.match(r"^\|[-\s|]+\|$", line):
            continue
        m = ROW.match(line)
        if not m:
            unparsed.append(line)
            continue
        num, ref, doi = m.group(1), m.group(2), m.group(3)
        surname = re.split(r"[ ,]", ref.strip())[0]
        year = parse_year(ref)
        vol, iss, pages = parse_locus(ref)
        refs.append({"n": int(num), "reference": ref, "doi": doi,
                     "first_author": surname, "year": year,
                     "volume": vol, "issue": iss, "pages": pages})
    return refs, unparsed


def epmc(doi):
    q = urllib.parse.urlencode({"query": 'DOI:"%s"' % doi, "format": "json",
                                "resultType": "core", "pageSize": "1"})
    with urllib.request.urlopen(EPMC + "?" + q, timeout=45) as fh:
        d = json.load(fh)
    hits = d.get("resultList", {}).get("result", [])
    if not hits:
        return None
    r = hits[0]
    ji = r.get("journalInfo", {}) or {}
    return {"authors": r.get("authorString", ""), "year": str(r.get("pubYear", "")),
            "title": r.get("title", ""), "registry": "Europe PMC", "pmid": r.get("pmid", ""),
            "journal": (ji.get("journal", {}) or {}).get("medlineAbbreviation", ""),
            "volume": str(ji.get("volume") or ""), "issue": str(ji.get("issue") or ""),
            "pages": r.get("pageInfo", "") or "",
            "first_publication": r.get("firstPublicationDate", "") or ""}


def crossref(doi):
    req = urllib.request.Request(CROSSREF + urllib.parse.quote(doi),
                                 headers={"User-Agent": "M5-AGE reference check"})
    with urllib.request.urlopen(req, timeout=45) as fh:
        d = json.load(fh).get("message", {})
    auths = d.get("author", []) or []
    names = ", ".join(("%s %s" % (a.get("family", ""), (a.get("given", "") or "")[:1])).strip()
                      for a in auths)
    parts = (d.get("issued", {}) or {}).get("date-parts", [[None]])
    year = str(parts[0][0]) if parts and parts[0] and parts[0][0] else ""
    title = (d.get("title") or [""])[0]
    return {"authors": names, "year": year, "title": title, "registry": "Crossref", "pmid": "",
            "journal": (d.get("short-container-title") or d.get("container-title") or [""])[0],
            "volume": str(d.get("volume") or ""), "issue": str(d.get("issue") or ""),
            "pages": d.get("page", "") or "", "first_publication": ""}


def verdict(ref, rec):
    if rec is None:
        return "identifier_not_found", "the DOI resolved at neither registry"
    notes = []
    if ref["first_author"] and fold(ref["first_author"]) not in fold(rec["authors"]):
        notes.append("first author %r not in %r" % (ref["first_author"], rec["authors"][:70]))
    if ref["year"] and rec["year"] and ref["year"] != rec["year"]:
        notes.append("year %s against %s (registry first publication %s)"
                     % (ref["year"], rec["year"], rec.get("first_publication") or "unknown"))
    # Volume, issue and pages are compared only where the document records them. A reference that
    # cites a volume the registry does not hold sends a reader to the wrong page of the right
    # journal, which a DOI check cannot see: both rows that failed the first pass of this check had
    # a wrong volume and wrong pages as well as a wrong year, and neither would have been noticed
    # by comparing identifiers.
    for field, label in (("volume", "volume"), ("issue", "issue"), ("pages", "pages")):
        a, b = (ref.get(field) or "").strip(), (rec.get(field) or "").strip()
        if not a or not b:
            continue
        if field == "pages":
            # Two registry spellings are not defects. Cell Press prints an electronic article
            # suffix, `1234-1247.e9` for the document's `1234-1247`; and some journals hold the
            # article identifier in the page field, `dci210034`, where the document records the
            # print pages. Neither disagrees with the document about where the article is.
            if re.fullmatch(re.escape(a) + r"\.e\d+", b):
                continue
            if not re.search(r"\d+\s*[-\u2013]\s*\d+", b):
                continue
        if a != b:
            notes.append("%s %s against %s" % (label, a, b))
    if notes:
        return "mismatch", "; ".join(notes)
    return "verified", ""


def main(argv):
    if not os.path.exists(DOC):
        print("FAIL: %s is missing" % os.path.relpath(DOC, ROOT))
        return 1
    with open(DOC) as fh:
        refs, unparsed = parse(fh.read())

    print("anchor reference check")
    print("  %d reference row(s) parsed from %s" % (len(refs), os.path.relpath(DOC, ROOT)))
    if unparsed:
        print("  %d table row(s) could not be parsed as a reference:" % len(unparsed))
        for u in unparsed[:10]:
            print("    " + u[:110])

    if "--offline" in argv:
        for r in refs:
            print("  %2d  %-16s %-5s %s" % (r["n"], r["first_author"], r["year"], r["doi"]))
        return 0

    rows, counts = [], {}
    for i, r in enumerate(refs, 1):
        rec = None
        try:
            rec = epmc(r["doi"])
        except Exception as e:
            print("  %s: Europe PMC error %s" % (r["doi"], e))
        if rec is None:
            try:
                rec = crossref(r["doi"])
            except Exception:
                rec = None
        v, note = verdict(r, rec)
        counts[v] = counts.get(v, 0) + 1
        rows.append(dict(r, verdict=v, note=note,
                         registry=(rec or {}).get("registry", ""),
                         pmid=(rec or {}).get("pmid", ""),
                         title_from_registry=(rec or {}).get("title", ""),
                         authors_from_registry=(rec or {}).get("authors", ""),
                         journal_from_registry=(rec or {}).get("journal", ""),
                         year_from_registry=(rec or {}).get("year", ""),
                         volume_from_registry=(rec or {}).get("volume", ""),
                         issue_from_registry=(rec or {}).get("issue", ""),
                         pages_from_registry=(rec or {}).get("pages", ""),
                         first_publication=(rec or {}).get("first_publication", "")))
        if i % 10 == 0:
            print("  looked up %d of %d" % (i, len(refs)))
        time.sleep(0.2)

    import csv
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print()
    for v in sorted(counts):
        print("  %-22s %d" % (v, counts[v]))
    print("written %s" % os.path.relpath(OUT, ROOT))
    bad = [r for r in rows if r["verdict"] != "verified"]
    for r in bad:
        print("\n  reference %d: %s" % (r["n"], r["verdict"]))
        print("    recorded : %s %s, doi %s" % (r["first_author"], r["year"], r["doi"]))
        print("    registry : %s" % (r["authors_from_registry"][:100] or "(none)"))
        print("    title    : %s" % r["title_from_registry"][:100])
        print("    note     : %s" % r["note"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
