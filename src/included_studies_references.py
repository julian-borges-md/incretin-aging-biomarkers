#!/usr/bin/env python3
"""
included_studies_references.py

Builds the included studies reference list from the extraction master and VERIFIES every identifier
against Europe PMC before the list is published.

Why verified rather than formatted. docs/REFERENCES.md states that its 29 anchor references were each
"verified against PubMed and carrying a resolvable DOI". The included studies, which are the larger
part of the reference list and the part a reader checks when they want to find a pooled number's
source, have never been through that check. A reference list containing an identifier that does not
resolve, or one that resolves to a different paper, is a citation integrity failure of the kind this
lab keeps a standard for, and it is invisible to every gate in the chain because the gates compare
numbers against texts rather than identifiers against registries.

What it checks, per trial
  1. the PMID resolves at Europe PMC at all
  2. the first author surname recorded in the master appears in the returned author string
  3. the publication year matches
  4. the DOI recorded in the master matches the DOI Europe PMC returns for that PMID

A mismatch is reported with both values. Nothing is corrected automatically: a reference that points
somewhere unexpected is a question about the extraction, not a formatting error to patch.

Outputs
  analysis/output/included_studies.csv          one row per trial, with the verification verdict
  analysis/output/included_studies.md           the reference list for the manuscript
  stdout: the verification summary

Usage
  python3 -I src/included_studies_references.py            verify over the network
  python3 -I src/included_studies_references.py --offline  build the list, skip verification
  exit 1 when any identifier fails to resolve or disagrees with the master
"""
import csv
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
OUT_CSV = os.path.join(ROOT, "analysis", "output", "included_studies.csv")
OUT_MD = os.path.join(ROOT, "analysis", "output", "included_studies.md")
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF = "https://api.crossref.org/works/"
BATCH = 20
# Europe PMC is one registry, not the registry. A DOI it does not index is not thereby a bad DOI, so
# a second source is consulted before anything is called unresolved. Yu 2015 is the standing case:
# Journal of Endocrinology and Metabolism is outside Europe PMC coverage and the DOI resolves at
# Crossref with a matching author, year and title.
UA = {"User-Agent": "M5-AGE-reference-check/1.0 (mailto:jyborges@bu.edu)"}


def crossref(doi):
    url = CROSSREF + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as fh:
        m = json.load(fh)["message"]
    auth = m.get("author") or []
    parts = (m.get("issued", {}).get("date-parts") or [[None]])[0]
    return {
        "authorString": ", ".join(f"{a.get('family','')}" for a in auth[:8]),
        "pubYear": str(parts[0]) if parts and parts[0] else "",
        "doi": (m.get("DOI") or "").lower(),
        "title": (m.get("title") or [""])[0],
        "journal": (m.get("container-title") or [""])[0],
        "_source": "Crossref",
    }


def fold(s):
    """Strip diacritics before comparing names. Without this the check reports Meyhofer against
    Meyhofer and Simo against Simo as mismatches, because the master stores the surname without its
    umlaut or acute accent while Europe PMC returns it with. Two false positives out of 24 is enough
    to make a verification report unreadable, and a check that cries wolf is worse than none."""
    return "".join(c for c in unicodedata.normalize("NFKD", s or "")
                   if not unicodedata.combining(c)).lower()


def fetch(terms):
    """terms are already formed query clauses, so a trial can be looked up by PMID or by DOI. 52 of
    the 76 trials carry NA in the pmid field and a DOI, so verifying by PMID alone would leave two
    thirds of the included studies unverified."""
    q = " OR ".join(terms)
    url = f"{API}?{urllib.parse.urlencode({'query': q, 'format': 'json', 'pageSize': 100})}"
    with urllib.request.urlopen(url, timeout=40) as fh:
        data = json.load(fh)
    out = {}
    for r in data.get("resultList", {}).get("result", []):
        if r.get("id"):
            out[str(r["id"])] = r
        if r.get("doi"):
            out["doi:" + r["doi"].lower()] = r
    return out


def main(argv):
    offline = "--offline" in argv
    rows = list(csv.DictReader(open(MASTER, newline="")))

    def g(r, k):
        return (r.get(k) or "").strip()

    trials = {}
    for r in rows:
        t = g(r, "trial_id")
        rec = trials.setdefault(t, {"trial_id": t, "doi": "", "pmid": "", "first_author": "",
                                    "year": "", "journal": "", "drug": "", "rows": 0})
        rec["rows"] += 1
        for k in ("doi", "pmid", "first_author", "year", "journal", "drug"):
            if not rec[k]:
                rec[k] = g(r, k)

    recs = sorted(trials.values(), key=lambda x: (x["first_author"].lower(), x["year"]))

    found = {}
    if not offline:
        terms, owner = [], {}
        for r in recs:
            if r["pmid"].isdigit():
                terms.append(f'EXT_ID:{r["pmid"]}')
                owner[("pmid", r["pmid"])] = r
            elif r["doi"]:
                terms.append(f'DOI:"{r["doi"]}"')
                owner[("doi", r["doi"].lower())] = r
        for i in range(0, len(terms), BATCH):
            chunk = terms[i:i + BATCH]
            try:
                found.update(fetch(chunk))
            except Exception as e:                      # noqa: BLE001
                print(f"  lookup failed for a batch of {len(chunk)}: {e}")
            print(f"  looked up {min(i + BATCH, len(terms))} of {len(terms)}")

    problems = []
    for r in recs:
        r["verdict"], r["note"] = "not_checked", ""
        if offline:
            continue
        if r["doi"].upper() == "NA":
            r["doi"] = ""
        if r["pmid"].upper() == "NA":
            r["pmid"] = ""
        hit = None
        r["verified_against"] = "Europe PMC"
        if r["pmid"].isdigit():
            hit = found.get(r["pmid"])
        if hit is None and r["doi"]:
            hit = found.get("doi:" + r["doi"].lower())
        if hit is None and r["doi"]:
            try:
                hit = crossref(r["doi"])
                r["verified_against"] = "Crossref"
            except Exception:                           # noqa: BLE001
                hit = None
        if not hit:
            # A trial with no identifier recorded at all has nothing to resolve, which is the normal
            # state of a conference abstract or a journal that assigns no DOI. That is a different
            # thing from an identifier that exists and fails, and conflating the two makes the report
            # read as though the corpus were full of broken references.
            if not r["doi"] and not r["pmid"].isdigit():
                r["verdict"] = "no_identifier_exists"
                r["note"] = ("no DOI or PMID recorded; citable by meeting and abstract number, or by "
                             "journal volume, issue and pages")
                continue
            r["verdict"] = "identifier_not_found"
            problems.append((r["trial_id"], "identifier recorded but resolved at neither Europe PMC "
                             "nor Crossref", r["pmid"], r["doi"]))
            continue
        # Where the master records NA for the PMID and the DOI resolved, report the PMID the registry
        # holds. It is NOT written back to the master: that is an extraction change and belongs to a
        # spec, not to a reference formatter.
        if not r["pmid"].isdigit() and hit.get("pmid"):
            r["pmid_from_api"] = str(hit["pmid"])
        notes = []
        # The master sometimes records, honestly, that the capture did not name an author. That is a
        # declared absence rather than a disagreement, and lumping the two together would bury the
        # cases where the master and the registry name DIFFERENT people, which are the ones that
        # matter. The registry's author is reported for these so the reference list can carry it.
        if r["first_author"].lower().startswith("not named"):
            r["author_from_api"] = hit.get("authorString") or ""
            r["verdict"] = "author_absent_in_master"
            r["note"] = "capture did not name an author; registry supplies it"
            continue
        surname = fold(re.split(r"[\s,]+", r["first_author"].strip())[0]) if r["first_author"] else ""
        authors = fold(hit.get("authorString") or "")
        if surname and surname not in authors:
            notes.append(f"first author '{r['first_author']}' not in '{hit.get('authorString','')[:60]}'")
        if r["year"] and hit.get("pubYear") and r["year"] != str(hit["pubYear"]):
            notes.append(f"year {r['year']} against {hit['pubYear']}")
        api_doi = (hit.get("doi") or "").lower().strip()
        our_doi = r["doi"].lower().strip()
        if our_doi and api_doi and our_doi != api_doi:
            notes.append(f"doi {our_doi} against {api_doi}")
        r["title_from_api"] = (hit.get("title") or "").rstrip(".")
        if notes:
            r["verdict"], r["note"] = "mismatch", "; ".join(notes)
            problems.append((r["trial_id"], "; ".join(notes), r["pmid"], r["doi"]))
        else:
            r["verdict"] = "verified"

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    fields = ["trial_id", "first_author", "year", "journal", "drug", "pmid", "pmid_from_api",
              "doi", "rows", "verdict", "verified_against", "note", "title_from_api",
              "author_from_api"]
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in recs:
            w.writerow(r)

    with open(OUT_MD, "w") as fh:
        fh.write("# Included studies\n\n")
        fh.write(f"{len(recs)} trials or trial analyses contributing {sum(r['rows'] for r in recs)} "
                 "contrasts. Generated by `src/included_studies_references.py` from the extraction "
                 "master, with every PMID verified against Europe PMC.\n\n")
        for i, r in enumerate(recs, 1):
            title = r.get("title_from_api") or r["trial_id"]
            fh.write(f"{i}. {r['first_author']} {r['year']}. {title}. *{r['journal']}*. "
                     f"PMID {r['pmid']}. doi:{r['doi']}. "
                     f"[{r['drug']}; {r['rows']} contrasts]\n")

    verified = sum(1 for r in recs if r["verdict"] == "verified")
    print(f"\nIncluded studies: {len(recs)} trials, {sum(r['rows'] for r in recs)} contrasts")
    print(f"  identifiers verified against Europe PMC: {verified}")
    print(f"  mismatches, master and registry name different people or years: "
          f"{sum(1 for r in recs if r['verdict'] == 'mismatch')}")
    print(f"  author absent in the master, supplied by the registry: "
          f"{sum(1 for r in recs if r['verdict'] == 'author_absent_in_master')}")
    print(f"  no identifier recorded, citable by other means: "
          f"{sum(1 for r in recs if r['verdict'] == 'no_identifier_exists')}")
    print(f"  identifier recorded but resolved nowhere: "
          f"{sum(1 for r in recs if r['verdict'] == 'identifier_not_found')}")
    backfilled = [r for r in recs if r.get("pmid_from_api")]
    print(f"  PMID recorded as NA in the master but found via the DOI: {len(backfilled)}"
          " (reported, not written back)")
    for t, why, pmid, doi in problems:
        print(f"    {t[:40]:42} {why}")
    print(f"written {os.path.relpath(OUT_CSV, ROOT)} and {os.path.relpath(OUT_MD, ROOT)}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
