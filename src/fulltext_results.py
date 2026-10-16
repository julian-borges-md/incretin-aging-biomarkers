#!/usr/bin/env python3
"""Study level view of the full text screen.

Joins the pool (search/screening/fulltext_pool_2026-10-16.csv) with the three
decision files of src/fulltext_screen.py and rolls the record level outcome up
to the candidate study groups built by src/build_fulltext_pool.py (DOI, title
and NCT grouping). A study group is included when at least one of its records
is included at full text; excluded when every screened record is excluded;
pending while a record awaits a reviewer or the adjudicator; no_text when none
of its records has a text yet.

Writes search/screening/FULLTEXT_RESULTS_SUMMARY.md (tracked) and the per
group table search/screening/fulltext_results_2026-10-16.csv (untracked, like
the other per record files). Deterministic; no model is called.

Usage, from the repository root: python3 -I src/fulltext_results.py
"""
import csv
import os
import sys
import time
from collections import Counter, defaultdict

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.argv = [sys.argv[0]]
import fulltext_screen as fs  # noqa: E402
import biomarker_scan as bs  # noqa: E402

OUT_MD = os.path.join(fs.OUTDIR, "FULLTEXT_RESULTS_SUMMARY.md")
OUT_CSV = os.path.join(fs.OUTDIR, "fulltext_results_2026-10-16.csv")
SCAN_CSV = os.path.join(fs.OUTDIR, "biomarker_scan_2026-10-16.csv")
TEXT_SOURCES = {"epmc_fulltext", "direct_fulltext", "proxy_fulltext"}


def final_decision(key, A, B, ADJ):
    """Record level outcome: agreed decision, else the adjudicator's, else pending."""
    if key in A and key in B:
        if A[key]["decision"] == B[key]["decision"] and A[key]["decision"] != "error":
            return A[key]["decision"], "agreed"
        if key in ADJ:
            return ADJ[key]["decision"], "adjudicated"
        return "pending", "awaiting adjudication"
    if key in A or key in B:
        return "pending", "one reviewer done"
    return "pending", "not screened"


def names(field):
    return {x.strip().lower() for x in (field or "").split(";") if x.strip()}


def read_scan():
    """Per record lexicon counts from src/biomarker_scan.py, when it has been run."""
    if not os.path.exists(SCAN_CSV):
        return {}
    out = {}
    for r in csv.DictReader(open(SCAN_CSV)):
        counts = {k: int(v) for k, v in r.items() if k not in ("key", "source", "chars", "screened_by_both", "named", "named_without_mention", "mentioned_not_named")}
        out[r["key"]] = dict(mentioned={k for k, v in counts.items() if v > 0}, named={x for x in r["named"].split(";") if x})
    return out


def record_rows():
    items = {it["key"]: it for it in fs.load_items()}
    pool = list(csv.DictReader(open(fs.POOL)))
    A, B, ADJ = fs.read_dec(fs.dec_path("A")), fs.read_dec(fs.dec_path("B")), fs.read_dec(fs.ADJ_PATH)
    scan = read_scan()
    rows = []
    for r in pool:
        key = f"{r['pool']}-{r['n']}"
        it = items[key]
        if it["source"] == "already_extracted":
            dec, how = "already_extracted", "in extraction_master"
        elif it["source"] == "awaiting_fulltext":
            dec, how = "no_text", "no text retrieved"
        else:
            dec, how = final_decision(key, A, B, ADJ)
        votes = [d[key] for d in (A, B, ADJ) if key in d]
        dur = {v["duration_weeks"] for v in votes if v.get("duration_weeks") not in (None, "", "null", "None")}
        comp = {v["comparator"].strip().lower() for v in votes if v.get("comparator") and v["comparator"].strip().lower() not in ("null", "none", "")}
        bio = set()
        for v in votes:
            bio |= {bs.canon(x) for x in names(v.get("biomarkers_reported"))}
        bio.discard("other")
        sc = scan.get(key)
        supported = sorted(sc["named"] & sc["mentioned"]) if sc else []
        rows.append(dict(r, key=key, text_source=it["source"], final=dec, how=how,
                         duration_weeks=";".join(sorted(dur)), comparator=";".join(sorted(comp)), biomarkers=";".join(sorted(bio)),
                         biomarkers_supported=";".join(supported), inventory_mentions=len(sc["mentioned"]) if sc else ""))
    return rows


def group_rows(records):
    groups = defaultdict(list)
    for r in records:
        groups[r["study_group"]].append(r)
    out = []
    for g, recs in groups.items():
        finals = Counter(r["final"] for r in recs)
        # order of precedence: an include settles the group; a pending record keeps it open; an
        # exclusion settles it only when no record of the group is still without a text
        if finals["include"]:
            status = "included"
        elif finals["pending"]:
            status = "pending"
        elif finals["exclude"] and not finals["no_text"]:
            status = "excluded"
        elif finals["exclude"]:
            status = "excluded_but_untexted_record"
        elif finals["already_extracted"]:
            status = "already_extracted"
        else:
            status = "no_text"
        years = sorted({r["year"] for r in recs if r["year"]})
        title = max((r["title"] for r in recs), key=len)
        ids = sorted({r["doi"] for r in recs if r["doi"]}) + sorted({n for r in recs for n in (r["nct_ids"] or "").split(";") if n})
        dur, comp, bio, sup = set(), set(), set(), set()
        for r in recs:
            if r["final"] == "include":
                dur |= set(x for x in r["duration_weeks"].split(";") if x)
                comp |= set(x for x in r["comparator"].split(";") if x)
                bio |= set(x for x in r["biomarkers"].split(";") if x)
                sup |= set(x for x in r["biomarkers_supported"].split(";") if x)
        out.append(dict(study_group=g, records=len(recs), status=status,
                        included=finals["include"], excluded=finals["exclude"], pending=finals["pending"],
                        no_text=finals["no_text"], already_extracted=finals["already_extracted"],
                        has_fulltext="yes" if any(r["text_source"] in TEXT_SOURCES for r in recs) else "no",
                        text_sources=";".join(sorted({r["text_source"] for r in recs})),
                        years=(years[0] if len(years) == 1 else f"{years[0]} to {years[-1]}") if years else "",
                        ids=";".join(ids), matched_known="yes" if any(r["matched_known"] in ("True", "yes", "1") for r in recs) else "no",
                        duration_weeks=";".join(sorted(dur)), comparator=";".join(sorted(comp)), biomarkers=";".join(sorted(bio)),
                        biomarkers_supported=";".join(sorted(sup)),
                        no_inventory_mention="yes" if all(r["inventory_mentions"] == 0 for r in recs if r["final"] == "include" and r["inventory_mentions"] != "") and any(r["final"] == "include" and r["inventory_mentions"] != "" for r in recs) else "no",
                        title=title))
    out.sort(key=lambda d: (d["status"] != "included", d["has_fulltext"] != "yes", d["study_group"]))
    return out


def main():
    records = record_rows()
    groups = group_rows(records)
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(groups[0].keys()))
        w.writeheader()
        w.writerows(groups)
    rc = Counter(r["final"] for r in records)
    gc = Counter(g["status"] for g in groups)
    md = ["# Full text screen, study level view\n",
          "Record outcomes from `fulltext_decisions_A.csv`, `fulltext_decisions_B.csv` and `fulltext_adjudication_002.csv` rolled up to the "
          "candidate study groups of `FULLTEXT_POOL_SUMMARY.md`. Produced by `src/fulltext_results.py`; the per group table is the untracked "
          "`fulltext_results_2026-10-16.csv`. A group is included when any of its records is included at full text; an exclusion settles a "
          "group only when none of its records is still without a text.\n",
          f"Snapshot taken {time.strftime('%Y-%m-%d %H:%M %Z')}; " + ("screening complete." if rc["pending"] == 0 else f"screening in progress, {rc['pending']} records pending.") + "\n",
          "| Record outcome | Records |\n|---|---|"]
    for k in ("include", "exclude", "pending", "no_text", "already_extracted"):
        md.append(f"| {k} | {rc[k]} |")
    md.append(f"| total | {len(records)} |")
    md.append("\n| Study group status | Groups |\n|---|---|")
    for k in ("included", "pending", "excluded", "excluded_but_untexted_record", "no_text", "already_extracted"):
        md.append(f"| {k} | {gc[k]} |")
    md.append(f"| total | {len(groups)} |")
    inc = [g for g in groups if g["status"] == "included"]
    md.append(f"\n| Included groups by best text | Groups |\n|---|---|")
    md.append(f"| with a full text (Europe PMC, publisher page, institutional route) | {sum(1 for g in inc if g['has_fulltext'] == 'yes')} |")
    md.append(f"| abstract, registry entry or partial page only | {sum(1 for g in inc if g['has_fulltext'] != 'yes')} |")
    md.append(f"| known relevant (adopted list) among included groups | {sum(1 for g in inc if g['matched_known'] == 'yes')} |")
    bio, sup = Counter(), Counter()
    for g in inc:
        bio.update(x for x in g["biomarkers"].split(";") if x)
        sup.update(x for x in g["biomarkers_supported"].split(";") if x)
    md.append("\n| Biomarker | Named by a reviewer in an included group | Named and mentioned in the text (lexicon scan) |\n|---|---|---|")
    seen = set()
    for name, cnt in sup.most_common(30):
        md.append(f"| {name} | {bio.get(name, 0)} | {cnt} |"); seen.add(name)
    md.append(f"\nThe second column is the one to use: the reviewers echo the example list of the prompt, so a name without a mention in the text is not evidence "
              f"(audit in `BIOMARKER_SCAN_SUMMARY.md`). Included groups whose included records mention no inventory biomarker at all: "
              f"{sum(1 for g in inc if g['no_inventory_mention'] == 'yes')} (flagged `no_inventory_mention` in the CSV; these rest on the rule that an unjudgeable criterion includes).")
    md.append("\n## Included study groups\n")
    md.append("| Group | Records | Years | Text | Duration (weeks, as read) | Comparator (as read) | Identifiers | Known | Title |\n|---|---|---|---|---|---|---|---|---|")
    for g in inc:
        md.append(f"| {g['study_group']} | {g['records']} ({g['included']} inc) | {g['years']} | {'full text' if g['has_fulltext'] == 'yes' else g['text_sources']} | "
                  f"{g['duration_weeks']} | {g['comparator'][:60]} | {g['ids'][:60]} | {g['matched_known']} | {g['title'][:90]} |")
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md[:40]))
    print(f"... {len(inc)} included groups listed in {OUT_MD}")


if __name__ == "__main__":
    main()
