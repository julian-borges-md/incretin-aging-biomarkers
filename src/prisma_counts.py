#!/usr/bin/env python3
"""
prisma_counts.py

Computes, from docs/prisma_counts.json, the count printed in every box of the PRISMA 2020 flow
diagram, with the arithmetic that produces each, and asserts the identities the diagram creates.

The diagram itself is drawn by src/prisma_figure.R, in figure style 2 like every other figure of
the submission, and writes the counts it prints as its data twin, analysis/output/
figure0_prisma_flow.csv. This module is the second, independent implementation of the same
arithmetic from the same file: src/figure_check.py imports it and requires the twin to equal its
rows, so a declared count changed without the diagram being redrawn, a box whose count the R script
computes differently, or a twin edited by hand stops the gate chain.

Until 24 October 2026 this file was src/prisma_diagram.py and drew the diagram itself, as an SVG;
the gate then regenerated the SVG and compared it byte for byte. The SVG was set in whatever
Helvetica or Arial the viewer had, at no journal size, which figure style 2 replaced. What carried
over is the arithmetic and its assertions, unchanged: a PRISMA diagram is a chain of subtractions, so
a box holding a number that does not follow from the box above it is a published error.
src/prisma_check.py asserts the identities among the recorded counts; this module asserts the ones
the diagram creates, which are the exclusion counts shown on the right.

Usage
  python3 -I src/prisma_counts.py
  prints every box count with its derivation and the balance of each stage; exit 1 if any count on
  the diagram fails to follow from the counts above it
"""
import json
import os
import sys

ROOT = os.getcwd()
COUNTS = os.path.join(ROOT, "docs", "prisma_counts.json")
TWIN_HEADER = ("stage", "box", "n")


def rows(d):
    """The box counts of the diagram, in drawing order, from the declared counts d.

    Returns (stage, box, n, derivation) tuples and the balance report. Every count is asserted
    before it is returned, so an AssertionError here is a diagram that would not follow from its
    own inputs."""
    a, b = d["stream_a_identification"], d["title_abstract_screening"]
    f, g = d["full_text_stage"], d["grouping_and_extraction"]
    sb = d["stream_b_adopted"]

    ex_screen = b["pool1_v2_remain_excluded"] + b["pool2_exclude"] + b["pool3_exclude"]
    assert ex_screen + b["records_to_full_text"] == b["records_screened_all_pools"], (
        f"screening does not balance: {ex_screen} + {b['records_to_full_text']} "
        f"!= {b['records_screened_all_pools']}")

    ex_fulltext = f["needing_a_screen"] - f["included_records"]
    assert ex_fulltext >= 0, "negative full text exclusions"

    closed = (g["no_usable_contrast_scan"] + g["no_usable_contrast"] + g["excluded_at_extraction"]
              + g["molecule_not_admitted"] + g["ongoing_no_results"] + g["held_pending_decision"])
    contributing = g["extracted"] + g["already_extracted"]
    assert closed + contributing == g["ledger_groups_final"], (
        f"ledger does not balance: {closed} + {contributing} != {g['ledger_groups_final']}")

    drawn = [
        ("identification", "Records identified from our own searching",
         b["records_screened_all_pools"], "title_abstract_screening.records_screened_all_pools"),
        ("identification", "Separate inflow, Alrasheed 2026 RCTs",
         sb["alrasheed_2026_rcts"], "stream_b_adopted.alrasheed_2026_rcts"),
        ("identification", "Separate inflow, Ren 2025 RCTs",
         sb["ren_2025_rcts"], "stream_b_adopted.ren_2025_rcts"),
        ("screening", "Records screened, title and abstract",
         b["records_screened_all_pools"], "title_abstract_screening.records_screened_all_pools"),
        ("screening", "Records excluded at title and abstract", ex_screen,
         "title_abstract_screening: pool1_v2_remain_excluded + pool2_exclude + pool3_exclude"),
        ("screening", "Records sought for full text",
         b["records_to_full_text"], "title_abstract_screening.records_to_full_text"),
        ("screening", "Not assessed", f["without_any_text"] + f["already_in_master"],
         "full_text_stage: without_any_text + already_in_master"),
        ("eligibility", "Records assessed at full text",
         f["needing_a_screen"], "full_text_stage.needing_a_screen"),
        ("eligibility", "Records excluded at full text", ex_fulltext,
         "full_text_stage: needing_a_screen minus included_records"),
        ("eligibility", "Records included, grouped into studies",
         g["ledger_groups_final"], "grouping_and_extraction.ledger_groups_final"),
        ("included", "Studies contributing to the synthesis", contributing,
         "grouping_and_extraction: extracted + already_extracted"),
        ("included", "Studies closed without contributing", closed,
         "grouping_and_extraction: no_usable_contrast_scan + no_usable_contrast + "
         "excluded_at_extraction + molecule_not_admitted + ongoing_no_results + "
         "held_pending_decision"),
    ]
    report = [
        f"screening balances: {ex_screen} excluded + {b['records_to_full_text']} sought "
        f"= {b['records_screened_all_pools']} screened",
        f"full text: {f['needing_a_screen']} assessed - {ex_fulltext} excluded "
        f"= {f['included_records']} included records",
        f"ledger balances: {closed} closed + {contributing} contributing "
        f"= {g['ledger_groups_final']} groups",
    ]
    return drawn, report


def main():
    with open(COUNTS) as fh:
        d = json.load(fh)
    try:
        drawn, report = rows(d)
    except AssertionError as e:
        print("FAIL: %s" % e)
        return 1
    for line in report:
        print(line)
    for stage, box, n, derivation in drawn:
        print("  %-15s %-44s %5d  %s" % (stage, box, n, derivation))
    print("%d box counts; the diagram is drawn by src/prisma_figure.R" % len(drawn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
