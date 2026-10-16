#!/usr/bin/env python3
"""
extraction_ledger.py

The extraction ledger: one row per candidate study group that the full text screen included,
with its extraction state, built from files the pipeline already produces and from the staging
directory the extractors write to. Rebuilt on every run, so the ledger is a view, not a hand kept
list; the only hand written inputs are the extractor and reconciler JSON notes in staging.

Inputs
  search/screening/fulltext_results_<date>.csv   study group status from the full text screen
  work/extraction/PACKET_INDEX.csv               packets per included group (src/extraction_packets.py)
  work/extraction/staging/<group>/A.csv, B.csv, A.json, B.json, reconciled.json
  analysis/data/extraction_*.csv                 trials already in the master (by DOI, PMID or NCT)

Status per group (first that applies)
  reconciled: extracted | excluded_at_extraction | molecule_not_admitted | no_usable_contrast
              | held_pending_decision                (from reconciled.json)
  in_extraction        at least one extractor file exists, no reconciliation yet
  already_extracted    an identifier of the group is in an extraction file in analysis/data
  no_usable_contrast_scan  no full text and no dispersion, interval or exact p in any text of the
                       group (work/extraction/abstract_scan.csv, src/abstract_scan.py): closed without a read
  waiting_screen       a full text of the group still awaits its second reviewer or adjudication
  queued               included, packet present, nothing started
  not_included         screening status is not included (pending, excluded, no_text)

Priority of the queue: known relevant first, then groups with a full text, then by the number of
inventory biomarkers the text mentions, then group number.

Outputs
  analysis/data/EXTRACTION_LEDGER.csv   tracked (identifiers, titles and states; no licensed text)
  stdout                                 counts and the head of the queue

Usage
  python3 -I src/extraction_ledger.py [--queue N]
"""
import csv
import glob
import json
import os
import re
import sys

ROOT = os.getcwd()
OUTDIR = os.path.join(ROOT, "search", "screening")
STAGING = os.path.join(ROOT, "work", "extraction", "staging")
PACKET_INDEX = os.path.join(ROOT, "work", "extraction", "PACKET_INDEX.csv")
LEDGER = os.path.join(ROOT, "analysis", "data", "EXTRACTION_LEDGER.csv")
NCT = re.compile(r"NCT\d{8}")

FIELDS = ["study_group", "status", "priority", "records", "has_fulltext", "text_sources", "matched_known",
          "years", "identifiers", "biomarkers_supported", "extractors", "reconciled_file", "rows_written",
          "reason", "molecule", "biomarkers_reported_no_variance", "other_markers", "updated", "title"]


def results_csv():
    files = sorted(glob.glob(os.path.join(OUTDIR, "fulltext_results_*.csv")))
    if not files:
        sys.exit("no fulltext_results CSV: run python3 -I src/fulltext_results.py first")
    return files[-1]


def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d


def known_identifiers():
    """DOIs, PMIDs and NCT ids present in the extraction files of analysis/data."""
    ids = set()
    for f in glob.glob(os.path.join(ROOT, "analysis", "data", "extraction_*.csv")):
        if os.path.basename(f) in ("extraction_schema.csv", "extraction_master.csv",
                                   "extraction_master_harmonised.csv"):
            continue
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("doi"):
                    ids.add(norm_doi(r["doi"]))
                if r.get("pmid"):
                    ids.add(r["pmid"].strip())
                ids.update(NCT.findall(r.get("trial_id", "") or ""))
    return ids


def pending_fulltext(group):
    """True when a full text in the packet has no final screening decision yet."""
    p = os.path.join(ROOT, "work", "extraction", "packets", str(group), "packet.json")
    if not os.path.exists(p):
        return False
    with open(p) as fh:
        d = json.load(fh)
    return any(t.get("final") == "pending" and t.get("source") in ("epmc_fulltext", "direct_fulltext", "proxy_fulltext")
               for t in d.get("texts", []))


def staging_state(group):
    d = os.path.join(STAGING, str(group))
    rec = os.path.join(d, "reconciled.json")
    out = dict(extractors="", reconciled_file="", rows_written="", reason="", molecule="",
               biomarkers_reported_no_variance="", other_markers="")
    if os.path.exists(rec):
        with open(rec) as fh:
            j = json.load(fh)
        out.update(status=j.get("status", "extracted"), reconciled_file=j.get("file", ""),
                   rows_written=str(j.get("rows", "")), reason=j.get("reason", ""),
                   molecule=j.get("molecule", ""),
                   biomarkers_reported_no_variance=";".join(j.get("biomarkers_reported_no_variance", [])),
                   other_markers=";".join(j.get("other_markers", [])))
        return out
    ex = [x for x in ("A", "B", "V", "S") if os.path.exists(os.path.join(d, f"{x}.csv")) or os.path.exists(os.path.join(d, f"{x}.json"))]
    if ex:
        out.update(status="in_extraction", extractors="".join(ex))
        for x in ex:
            jp = os.path.join(d, f"{x}.json")
            if os.path.exists(jp):
                with open(jp) as fh:
                    j = json.load(fh)
                out["molecule"] = out["molecule"] or j.get("molecule", "")
        return out
    out["status"] = None
    return out


def main():
    queue_n = 25
    if "--queue" in sys.argv:
        queue_n = int(sys.argv[sys.argv.index("--queue") + 1])
    packets = {}
    if os.path.exists(PACKET_INDEX):
        with open(PACKET_INDEX, newline="") as fh:
            for r in csv.DictReader(fh):
                packets[r["study_group"]] = r
    known = known_identifiers()
    scan = {}
    scan_path = os.path.join(ROOT, "work", "extraction", "abstract_scan.csv")
    if os.path.exists(scan_path):
        with open(scan_path, newline="") as fh:
            scan = {r["study_group"]: r for r in csv.DictReader(fh)}
    rows = []
    with open(results_csv(), newline="") as fh:
        for r in csv.DictReader(fh):
            g = r["study_group"]
            ids = [i.strip() for i in (r.get("ids") or "").split(";") if i.strip()]
            st = staging_state(g)
            if r["status"] != "included":
                status = "not_included"
            elif st["status"]:
                status = st["status"]
            elif any((norm_doi(i) in known) or (i in known) for i in ids):
                status = "already_extracted"
            elif g in scan and scan[g]["verdict"] == "no_variance_marks":
                status = "no_usable_contrast_scan"
                st["reason"] = (f"deterministic scan (src/abstract_scan.py): no dispersion, interval or exact p in "
                                f"{scan[g]['chars']} characters across {scan[g]['texts']} text(s) ({scan[g]['sources']})")
            elif g in packets and pending_fulltext(g):
                status = "waiting_screen"
                st["reason"] = "a full text of the group is still pending its second reviewer or adjudication"
            elif g in packets:
                status = "queued"
            else:
                status = "queued_no_packet"
            nb = len([b for b in (r.get("biomarkers_supported") or "").split(";") if b])
            priority = (0 if r.get("matched_known") == "yes" else 1, 0 if r.get("has_fulltext") == "yes" else 1, -nb, int(g))
            rows.append(dict(study_group=g, status=status, priority="%d%d%03d" % (priority[0], priority[1], 99 - min(nb, 99)),
                             records=r["records"], has_fulltext=r.get("has_fulltext", ""),
                             text_sources=r.get("text_sources", ""), matched_known=r.get("matched_known", ""),
                             years=r.get("years", ""), identifiers=";".join(ids),
                             biomarkers_supported=r.get("biomarkers_supported", ""),
                             extractors=st["extractors"], reconciled_file=st["reconciled_file"],
                             rows_written=st["rows_written"], reason=st["reason"], molecule=st["molecule"],
                             biomarkers_reported_no_variance=st["biomarkers_reported_no_variance"],
                             other_markers=st["other_markers"], updated="", title=r.get("title", "")[:160],
                             _prio=priority))
    rows.sort(key=lambda x: x["_prio"])
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            if r["status"] != "not_included":
                w.writerow(r)
    from collections import Counter
    c = Counter(r["status"] for r in rows)
    print("ledger:", ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    queue = [r for r in rows if r["status"] in ("queued", "queued_no_packet")]
    print(f"queue head ({min(queue_n, len(queue))} of {len(queue)}): group  known  fulltext  markers  title")
    for r in queue[:queue_n]:
        print(f"  {r['study_group']:>4}  {r['matched_known']:5}  {r['has_fulltext']:8}  "
              f"{len([b for b in r['biomarkers_supported'].split(';') if b]):7}  {r['title'][:80]}")
    print("wrote", os.path.relpath(LEDGER, ROOT))


if __name__ == "__main__":
    main()
