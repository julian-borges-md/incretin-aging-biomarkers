#!/usr/bin/env python3
"""
table1_inventory.py

Generates Table 1, the biomarker inventory, from analysis/data/biomarker_inventory.csv, and states
alongside it how many trials and contrasts the corpus actually holds for each marker.

Why generated rather than typed. Q1 is phrased against a prespecified inventory of 26 markers, and
amendment R2 of 15 October records that the markers actually pooled had drifted from that list in
both directions while the drift went undocumented. A hand maintained Table 1 is how that happens: the
table says one thing, the master holds another, and nobody compares them. This script joins the two,
so the published table reports the inventory as it was pooled, which R2 requires, and any marker in
the inventory with no rows or any marker with rows but no inventory entry is shown rather than lost.

Output
  analysis/output/table1_biomarker_inventory.csv   the table, version controlled
  analysis/output/table1_biomarker_inventory.md    the same, formatted for the manuscript
  stdout: the reconciliation between the inventory and the master

WRITING AND CHECKING ARE SEPARATE MODES, and the chain uses the second. Until 22 October this script
only wrote, and the chain ran it, so gate seventeen REGENERATED the artefact it was supposed to
verify. A chain that writes to what it verifies cannot fail on it: a Table 1 that disagreed with the
inventory would have been silently replaced on the next run rather than reported. Nothing had gone
wrong, because this table is a deterministic function of two tracked inputs, but the gate was
establishing nothing. It also had a visible consequence: a display name change in the inventory left
the result manifest describing a Table 1 that no longer existed, and the manifest gate failed on a
file this gate had correctly regenerated.

So `--check` compares and never writes, and the chain calls it. Regeneration is a deliberate step,
`make table1`, followed by `make manifest` to rehash the output directory. The comparison is on
bytes, and it reports the first differing line of each file rather than only that they differ,
because a gate that says a file is wrong without saying how is a gate someone has to reimplement by
hand before they can act on it.

Usage
  python3 -I src/table1_inventory.py            regenerate both files
  python3 -I src/table1_inventory.py --check    compare, write nothing
  exit 1 when a marker carries rows but no inventory entry, which would mean the corpus pools
  something the protocol never declared, and under --check also when either file on disk is not what
  the inventory and the harmonised master produce
"""
import csv
import io
import os
import sys
from collections import defaultdict

ROOT = os.getcwd()
INV = os.path.join(ROOT, "analysis", "data", "biomarker_inventory.csv")
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master_harmonised.csv")
OUT_CSV = os.path.join(ROOT, "analysis", "output", "table1_biomarker_inventory.csv")
OUT_MD = os.path.join(ROOT, "analysis", "output", "table1_biomarker_inventory.md")

DOMAIN_ORDER = ["inflammaging", "adipose_senescence", "hepatic_aging", "metabolic_aging",
                "vascular_aging", "cardiac_aging", "renal_aging", "musculoskeletal_aging"]


def build():
    """
    Build Table 1 in memory and return (rows, csv bytes, markdown bytes, report lines, orphans).

    Separated from writing so that --check can compare instead of overwrite. Returning bytes rather
    than text is deliberate: the csv module's excel dialect terminates lines with CRLF and this file
    has always been written that way, while the markdown is LF. A comparison that normalised line
    endings would pass on a file whose endings had changed, and a writer that normalised them would
    rewrite the file on every run for no reason.
    """
    inv = list(csv.DictReader(open(INV, newline="")))
    rows = list(csv.DictReader(open(MASTER, newline="")))

    trials = defaultdict(set)
    contrasts = defaultdict(int)
    convertible = defaultdict(int)
    for r in rows:
        bm = r["biomarker"]
        trials[bm].add(r["trial_id"])
        contrasts[bm] += 1
        if (r.get("yi_pct") or "").strip() not in ("", "NA"):
            convertible[bm] += 1

    out = []
    for e in inv:
        bm = e["biomarker"]
        out.append({
            "number": e["table1_number"],
            "biomarker": e["table1_name"] or bm,
            "key": bm,
            "hallmark_domain": e["hallmark_domain"],
            "direction_of_aging": "higher is older" if e["aging_direction"] == "-1"
                                   else "lower is older",
            "clinical_weight": e["clinical_weight"],
            "weight_status": e["weight_status"],
            "inventory_status": e["inventory_status"],
            "in_composite": e["composite_primary"],
            "trials": len(trials.get(bm, ())),
            "contrasts": contrasts.get(bm, 0),
            "contrasts_on_percent_scale": convertible.get(bm, 0),
        })

    # Order by domain as the protocol groups them, then by the inventory number.
    def key(o):
        d = o["hallmark_domain"]
        return (DOMAIN_ORDER.index(d) if d in DOMAIN_ORDER else len(DOMAIN_ORDER), d,
                int(o["number"]) if o["number"].isdigit() else 999)
    out.sort(key=key)

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
    csv_bytes = buf.getvalue().encode()

    cols = [("biomarker", "Biomarker"), ("hallmark_domain", "Hallmark domain"),
            ("direction_of_aging", "Direction"), ("clinical_weight", "Weight"),
            ("inventory_status", "Inventory"), ("in_composite", "Composite"),
            ("trials", "Trials"), ("contrasts", "Contrasts"),
            ("contrasts_on_percent_scale", "On scale")]
    md = io.StringIO()
    md.write("# Table 1. Biomarker inventory as pooled\n\n")
    md.write("Generated by `src/table1_inventory.py` from `analysis/data/biomarker_inventory.csv`"
             " joined to the harmonised master. Amendment R2 requires that the review report the"
             " inventory as it was pooled rather than as the prespecified list reads; the two"
             " final columns are what makes the difference visible.\n\n")
    md.write("| " + " | ".join(c[1] for c in cols) + " |\n")
    md.write("|" + "|".join("---" for _ in cols) + "|\n")
    for o in out:
        md.write("| " + " | ".join(str(o[c[0]]) for c in cols) + " |\n")
    md_bytes = md.getvalue().encode()

    in_inv = {e["biomarker"] for e in inv}
    pooled = {bm for bm in trials if contrasts[bm] > 0}
    orphan = sorted(pooled - in_inv)
    empty = sorted(bm for bm in in_inv if contrasts.get(bm, 0) == 0)

    report = [
        f"Table 1: {len(out)} inventory entries over "
        f"{len({o['hallmark_domain'] for o in out})} hallmark domains",
        f"  markers with at least one contrast: {len(pooled & in_inv)}",
        f"  inventory markers with no contrast: {len(empty)}"
        + (f" ({', '.join(empty)})" if empty else ""),
    ]
    if orphan:
        report += [
            f"  POOLED BUT NOT IN THE INVENTORY: {', '.join(orphan)}",
            "  A marker pooled without an inventory entry has no declared domain, direction or "
            "weight, so the composite cannot place it and the protocol never admitted it.",
        ]
    return out, csv_bytes, md_bytes, report, orphan


def compare(path, expected):
    """Return a one line verdict, or None when the file on disk is what build() produced."""
    rel = os.path.relpath(path, ROOT)
    if not os.path.exists(path):
        return f"{rel} does not exist"
    got = open(path, "rb").read()
    if got == expected:
        return None
    g, e = got.decode(errors="replace").split("\n"), expected.decode(errors="replace").split("\n")
    if len(g) != len(e):
        return f"{rel} has {len(g)} line(s), the inventory gives {len(e)}"
    for i, (a, b) in enumerate(zip(g, e), start=1):
        if a != b:
            return (f"{rel} line {i} is\n      {a.strip()}\n    the inventory gives\n      "
                    f"{b.strip()}")
    return f"{rel} differs from the inventory in its line endings or trailing bytes"


def main(argv):
    check = "--check" in argv
    out, csv_bytes, md_bytes, report, orphan = build()
    for line in report:
        print(line)

    if check:
        drift = [d for d in (compare(OUT_CSV, csv_bytes), compare(OUT_MD, md_bytes)) if d]
        print("\ntable 1 check")
        if drift:
            for d in drift:
                print("  DRIFT " + d)
            print("  Table 1 on disk is not what the biomarker inventory and the harmonised master "
                  "produce.\n  Regenerate it with `make table1`, then refresh the result manifest "
                  "with `make manifest`.")
        else:
            print("  both files on disk are byte identical to what the inventory produces")
        sys.exit(1 if (orphan or drift) else 0)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "wb") as fh:
        fh.write(csv_bytes)
    with open(OUT_MD, "wb") as fh:
        fh.write(md_bytes)
    print(f"written {os.path.relpath(OUT_CSV, ROOT)} and {os.path.relpath(OUT_MD, ROOT)}")
    sys.exit(1 if orphan else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
