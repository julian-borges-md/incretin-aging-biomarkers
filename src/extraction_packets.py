#!/usr/bin/env python3
"""Extraction packets: the queue for the extraction stage, one directory per included study group.

For every study group the full text screen includes (src/fulltext_results.py), writes under the
gitignored work/extraction/packets/<group>/:
  packet.json            group identifiers, records, text sources, the reviewers' reads (duration,
                         comparator, biomarkers) labelled as candidates to verify, the lexicon
                         mentions, and the extraction schema columns
  text_<key>.txt         the complete rendered text of each record (untrimmed, uncapped), for the
                         extractor; the trimmed and capped screening text is not reused here
  extraction_template.csv the schema header with identifiers prefilled from the pool only; no value
                         read by a model is written into it

Tracked output: search/screening/EXTRACTION_QUEUE.md (counts and the ordered queue). Order: groups
with a full text first, then by the number of inventory biomarkers that a reviewer named and the
text mentions, then year. Deterministic; no model is called.

Usage, from the repository root: python3 -I src/extraction_packets.py
"""
import csv
import json
import os
import sys

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.argv = [sys.argv[0]]
import fulltext_screen as fs  # noqa: E402
import fulltext_results as fr  # noqa: E402

PACKETS = os.path.join(ROOT, "work/extraction/packets")
INDEX = os.path.join(ROOT, "work/extraction/PACKET_INDEX.csv")
QUEUE_MD = os.path.join(fs.OUTDIR, "EXTRACTION_QUEUE.md")
SCHEMA = os.path.join(ROOT, "analysis/data/extraction_schema.csv")


def full_text_path(key, source):
    """The complete rendered text for a record, by source; None when the record is its own text."""
    pool, n = key.split("-")
    k = (pool, int(n))
    if source == "epmc_fulltext":
        m = fs.read_manifest(fs.EPMC_MANIFEST, None).get(k)
        return m["file"] if m else None
    if source == "direct_fulltext":
        m = fs.read_manifest(fs.DIRECT_MANIFEST, None).get(k)
        return m["file"] if m else None
    if source in ("proxy_fulltext", "proxy_partial"):
        m = fs.read_proxy_manifest().get(k)
        return m["file"] if m else None
    if source == "ctgov_entry":
        m = fs.read_manifest(fs.CTGOV_MANIFEST, None).get(k)
        return m["file"] if m else None
    return None


def main():
    records = fr.record_rows()
    groups = {g["study_group"]: g for g in fr.group_rows(records)}
    by_group = {}
    for r in records:
        by_group.setdefault(r["study_group"], []).append(r)
    schema = [r["column"] for r in csv.DictReader(open(SCHEMA))]
    items = {it["key"]: it for it in fs.load_items()}
    queue = [g for g in groups.values() if g["status"] == "included"]
    queue.sort(key=lambda g: (g["has_fulltext"] != "yes", -len([x for x in g["biomarkers_supported"].split(";") if x]), g["years"], g["study_group"]))
    os.makedirs(PACKETS, exist_ok=True)
    index = []
    for g in queue:
        gdir = os.path.join(PACKETS, g["study_group"])
        os.makedirs(gdir, exist_ok=True)
        recs = by_group[g["study_group"]]
        texts = []
        for r in recs:
            src = r["text_source"]
            path = full_text_path(r["key"], src)
            if path and os.path.exists(path):
                raw = open(path, encoding="utf-8", errors="replace").read()
                if src in ("proxy_fulltext", "proxy_partial") and "\n\n" in raw:
                    raw = raw.split("\n\n", 1)[1]  # drop the capture header (KEY, SOURCE, TITLE)
            else:
                raw = items[r["key"]]["text"]  # conference abstract or register summary: the record is the text
            out = os.path.join(gdir, f"text_{r['key']}.txt")
            with open(out, "w") as fh:
                fh.write(raw)
            texts.append(dict(key=r["key"], source=src, chars=len(raw), file=os.path.relpath(out, ROOT), final=r["final"]))
        nct = sorted({n for r in recs for n in (r["nct_ids"] or "").split(";") if n})
        packet = dict(study_group=g["study_group"], status=g["status"], title=g["title"], years=g["years"], identifiers=g["ids"],
                      nct=nct, matched_known=g["matched_known"], has_fulltext=g["has_fulltext"], texts=texts,
                      reviewer_reads_to_verify=dict(duration_weeks=g["duration_weeks"], comparator=g["comparator"],
                                                    biomarkers_named=g["biomarkers"], biomarkers_named_and_mentioned=g["biomarkers_supported"]),
                      extraction_schema_columns=schema)
        with open(os.path.join(gdir, "packet.json"), "w") as fh:
            json.dump(packet, fh, indent=1, ensure_ascii=False)
        with open(os.path.join(gdir, "extraction_template.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=schema)
            w.writeheader()
            w.writerow({c: "" for c in schema} | dict(trial_id=nct[0] if nct else "", year=g["years"][:4]))
        index.append(dict(study_group=g["study_group"], records=g["records"], has_fulltext=g["has_fulltext"], years=g["years"],
                          biomarkers_supported=g["biomarkers_supported"], duration_weeks=g["duration_weeks"], comparator=g["comparator"],
                          identifiers=g["ids"], matched_known=g["matched_known"], title=g["title"], packet=os.path.relpath(gdir, ROOT)))
    with open(INDEX, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(index[0].keys()) if index else ["study_group"])
        w.writeheader()
        w.writerows(index)
    md = ["# Extraction queue\n",
          f"Produced by `src/extraction_packets.py` from the study level view (`FULLTEXT_RESULTS_SUMMARY.md`). Packets live in the gitignored "
          f"`work/extraction/packets/<group>/` (packet.json, the complete texts, an extraction template with identifiers only). "
          f"Snapshot: {fr.time.strftime('%Y-%m-%d %H:%M %Z')}.\n",
          "| Queue | Groups |\n|---|---|",
          f"| included groups, packet written | {len(index)} |",
          f"| with a full text | {sum(1 for g in index if g['has_fulltext'] == 'yes')} |",
          f"| abstract, register entry or partial page only | {sum(1 for g in index if g['has_fulltext'] != 'yes')} |",
          f"| known relevant (adopted list) | {sum(1 for g in index if g['matched_known'] == 'yes')} |",
          "\n| # | Group | Text | Years | Biomarkers named and mentioned | Duration as read | Comparator as read | Identifiers | Title |\n|---|---|---|---|---|---|---|---|---|"]
    for i, g in enumerate(index, 1):
        md.append(f"| {i} | {g['study_group']} | {'full text' if g['has_fulltext'] == 'yes' else 'partial'} | {g['years']} | {g['biomarkers_supported']} | "
                  f"{g['duration_weeks']} | {g['comparator'][:50]} | {g['identifiers'][:50]} | {g['title'][:80]} |")
    with open(QUEUE_MD, "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md[:9]))
    print(f"... {len(index)} packets under {PACKETS}")


if __name__ == "__main__":
    main()
