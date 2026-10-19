#!/usr/bin/env python3
"""
prisma_check.py

Checks that the PRISMA counts add up, before any diagram is drawn from them.

Why. docs/PRISMA_FLOW.md narrates the selection process and had accumulated three strata written on
different days. Its headline Included section still read "6 trials, 7 trial-analyses, 43 poolable
rows" while its own later sections recorded 440 included records and a 524 row master, and its
Screening section still said the second blinded reviewer "has not yet been implemented" and Web of
Science "has not been run" while the outstanding table recorded both as done. A diagram drawn from
the top of that file would have reported 6 trials for a 76 trial review.

Numbers therefore live once, in docs/prisma_counts.json, and this script states the arithmetic that
must hold between them. A PRISMA diagram is a set of subtractions, so every step either reconciles or
there is something the review does not understand about its own selection process. Where a step does
not reconcile the script says so and exits non zero rather than drawing a diagram that implies it
does.

Usage
  python3 -I src/prisma_check.py
  exit 1 on any identity that fails, or on any unexplained residual
"""
import json
import os
import sys

ROOT = os.getcwd()
COUNTS = os.path.join(ROOT, "docs", "prisma_counts.json")


def main():
    d = json.load(open(COUNTS))
    a, b = d["stream_a_identification"], d["title_abstract_screening"]
    f, g, inc = d["full_text_stage"], d["grouping_and_extraction"], d["included_in_synthesis"]

    checks = []

    def check(name, lhs, rhs, note=""):
        checks.append((name, lhs, rhs, lhs == rhs, note))

    # Identification. The screened set is the Embase articles plus the registry records plus the
    # CENTRAL records that Embase did not already hold.
    check("pools 1 and 2 screened = Embase articles + Embase registry + CENTRAL unique",
          b["records_screened_pools_1_and_2"],
          a["embase_article_records_exported"] + a["embase_registry_records_exported"]
          + a["central_unique"])

    check("pool 3 = Web of Science records in neither other database",
          b["pool3_records"], a["wos_in_neither"])

    check("pool 3 include + exclude = pool 3 records",
          b["pool3_include"] + b["pool3_exclude"], b["pool3_records"])

    check("all records screened = pools 1 and 2 + pool 3",
          b["records_screened_all_pools"],
          b["records_screened_pools_1_and_2"] + b["pool3_records"])

    check("pool 2 = Embase registry + CENTRAL unique",
          b["pool2_records"],
          a["embase_registry_records_exported"] + a["central_unique"])

    check("CENTRAL exported = overlapping + unique",
          a["central_records_exported"], a["central_overlapping_embase"] + a["central_unique"])

    # Web of Science records are either already held by one of the other two databases or unique.
    # They can overlap both, so this is an inequality rather than a sum.
    wos_accounted = a["wos_also_in_embase"] + a["wos_in_neither"]
    checks.append(("Web of Science: unique + also in Embase does not exceed exported",
                   wos_accounted, a["wos_records_exported"],
                   wos_accounted <= a["wos_records_exported"],
                   "inequality, because a record can sit in both other databases"))

    # Title and abstract screening.
    check("pool 1 v1 include + exclude = Embase articles",
          b["pool1_v1_include"] + b["pool1_v1_exclude"],
          a["embase_article_records_exported"])

    check("pool 1 v2 rescued + remaining excluded = v1 excluded",
          b["pool1_v2_rescued_from_exclusions"] + b["pool1_v2_remain_excluded"],
          b["pool1_v1_exclude"])

    check("pool 1 to full text = v1 include + v2 rescued",
          b["pool1_to_full_text"],
          b["pool1_v1_include"] + b["pool1_v2_rescued_from_exclusions"])

    check("pool 2 include + exclude = pool 2 records",
          b["pool2_include"] + b["pool2_exclude"], b["pool2_records"])

    check("pools 1 and 2 to full text = pool 1 + pool 2 includes",
          b["records_to_full_text_pools_1_and_2"],
          b["pool1_to_full_text"] + b["pool2_include"])

    # The identity that was missing until 19 October, and whose absence left 29 records entering the
    # full text stage from nowhere. A PRISMA diagram asserts that every record at a stage came from
    # the one above it, so this is the identity that makes the diagram drawable.
    check("full text pool = pool 1 + pool 2 + pool 3 includes",
          b["records_to_full_text"],
          b["pool1_to_full_text"] + b["pool2_include"] + b["pool3_include"])

    check("full text pool as recorded = full text pool as screened",
          f["pool_records"], b["records_to_full_text"])

    # Full text stage.
    check("needing a screen = pool - without text - already in master",
          f["needing_a_screen"],
          f["pool_records"] - f["without_any_text"] - f["already_in_master"])

    check("adjudicated to include + to exclude = disagreements",
          f["adjudicated_to_include"] + f["adjudicated_to_exclude"], f["disagreements"])

    check("every disagreement adjudicated",
          f["disagreements_adjudicated"], f["disagreements"])

    check("reviewer 2 include + exclude + model error = screened by both",
          f["reviewer2_include"] + f["reviewer2_exclude"] + f["reviewer2_model_error"],
          f["screened_by_both_reviewers"])

    # Extraction ledger.
    terminal = sum(g[k] for k in ("no_usable_contrast_scan", "no_usable_contrast", "extracted",
                                  "excluded_at_extraction", "already_extracted",
                                  "held_pending_decision", "ongoing_no_results",
                                  "molecule_not_admitted", "queued"))
    check("ledger statuses sum to the group total", terminal, g["ledger_groups_final"])
    check("extraction queue is empty", g["queued"], 0)

    check("convertible + unconvertible rows = master rows",
          inc["rows_convertible_to_percent_scale"] + inc["rows_not_convertible"], inc["rows"])

    failed = [c for c in checks if not c[3]]
    print(f"PRISMA arithmetic: {len(checks)} identities checked, {len(checks) - len(failed)} hold")
    for name, lhs, rhs, ok, note in checks:
        tag = "ok  " if ok else "FAIL"
        extra = f"   [{note}]" if note else ""
        print(f"  {tag} {name}: {lhs} vs {rhs}{extra}")

    if not failed:
        print("\nEvery stage reconciles, so the diagram can be drawn: each record at a stage is "
              "accounted for by the stage above it.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
