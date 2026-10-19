#!/usr/bin/env python3
"""
prisma_diagram.py

Draws the PRISMA 2020 flow diagram as a self contained SVG from docs/prisma_counts.json.

Design constraints, each from a source rather than from taste.

  1. docs/PRISMA_FLOW.md requires that Stream B, the mono agonist trials adopted from two published
     reviews, is shown as a SEPARATE inflow and never merged into our own screening stages: "A
     single merged diagram implying one unified search would misrepresent the process." It is drawn
     as a dashed box joining at the synthesis, with its status in the box text.
  2. Every number is computed here from the declared counts and asserted before anything is drawn.
     A PRISMA diagram is a chain of subtractions, so a box holding a number that does not follow
     from the box above it is a published error. src/prisma_check.py asserts the identities among
     the recorded counts; this script asserts the ones the diagram itself creates, which are the
     exclusion counts shown on the right.
  3. No data is encoded in colour. A flow diagram has no series, so there is no categorical palette
     to validate; the adopted inflow is distinguished by a dashed stroke AND its label, never by
     colour alone, and all text sits in one ink rather than in a mark colour. The figure is legible
     in greyscale print, which is what journals reproduce.

Output
  analysis/output/figure0_prisma_flow.svg   version controlled

Usage
  python3 -I src/prisma_diagram.py
  exit 1 if any count on the diagram fails to follow from the counts above it
"""
import json
import os
import sys

ROOT = os.getcwd()
COUNTS = os.path.join(ROOT, "docs", "prisma_counts.json")
OUT = os.path.join(ROOT, "analysis", "output", "figure0_prisma_flow.svg")

INK = "#1a1a1a"
MUTED = "#5c5c5c"
RULE = "#8a8a8a"
SURFACE = "#ffffff"
W, PAD = 1040, 24
BOX_W, EX_W = 430, 420
LX, RX = 40, 560


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self):
        self.parts = []
        self.y = 0

    def box(self, x, w, title, lines, dashed=False, bold_title=True):
        body = []
        for ln in lines:
            body.extend(wrap(ln, 62))
        h = 26 + 15 * len(body) + 14
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.parts.append(
            f'<rect x="{x}" y="{self.y}" width="{w}" height="{h}" rx="3" fill="{SURFACE}" '
            f'stroke="{RULE}" stroke-width="1.2"{dash}/>')
        ty = self.y + 20
        weight = "600" if bold_title else "400"
        self.parts.append(
            f'<text x="{x + 14}" y="{ty}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="13" font-weight="{weight}" fill="{INK}">{esc(title)}</text>')
        for i, ln in enumerate(body):
            self.parts.append(
                f'<text x="{x + 14}" y="{ty + 17 + 15 * i}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="11.5" '
                f'fill="{MUTED}">{esc(ln)}</text>')
        return h

    def arrow(self, x1, y1, x2, y2, dashed=False):
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RULE}" '
            f'stroke-width="1.2" marker-end="url(#a)"{dash}/>')

    def route(self, points, dashed=False):
        """An orthogonal path along given points. Used to take the adopted inflow down the right
        margin: drawn as a straight line it passed through three exclusion boxes, which reads as a
        flow into them and is exactly the merged diagram PRISMA_FLOW.md forbids."""
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{RULE}" stroke-width="1.2" '
            f'marker-end="url(#a)"{dash}/>')

    def stage(self, label, y):
        self.parts.append(
            f'<text x="18" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="10.5" '
            f'font-weight="600" fill="{MUTED}" letter-spacing="1.1" '
            f'transform="rotate(-90 18 {y})">{esc(label.upper())}</text>')


def main():
    d = json.load(open(COUNTS))
    a, b = d["stream_a_identification"], d["title_abstract_screening"]
    f, g, inc = d["full_text_stage"], d["grouping_and_extraction"], d["included_in_synthesis"]
    sb = d["stream_b_adopted"]

    # Counts the diagram itself creates, asserted before use.
    ex_screen = (b["pool1_v2_remain_excluded"] + b["pool2_exclude"] + b["pool3_exclude"])
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

    c = Canvas()
    c.y = 54

    c.stage("Identification", 150)
    h = c.box(LX, BOX_W, f"Records identified from our own searching (n = {b['records_screened_all_pools']})", [
        f"Embase, 15 Oct 2026: {a['embase_hits']} hits, {a['embase_article_records_exported']} "
        f"article records and {a['embase_registry_records_exported']} registry records exported",
        f"CENTRAL, 15 Oct 2026: {a['central_records_exported']} exported, "
        f"{a['central_unique']} not already in Embase",
        f"Web of Science, 16 Oct 2026: {a['wos_records_exported']} exported, "
        f"{a['wos_in_neither']} in neither other database",
        f"PubMed anchor searches for the dual and triple agonists: "
        f"{a['pubmed_anchor_body_composition']}, {a['pubmed_anchor_hepatic']} and "
        f"{a['pubmed_anchor_gdf15']} PMIDs",
    ])
    hr = c.box(RX, EX_W, "Separate inflow, not from our searching", [
        f"Mono agonist comparator trials adopted from two published systematic reviews: "
        f"Alrasheed 2026, {sb['alrasheed_2026_rcts']} RCTs; Ren 2025, {sb['ren_2025_rcts']} RCTs.",
        "Their screening was performed by other groups and is inherited, so these records do not "
        "pass through the stages below. Re-screened against this review's criteria at extraction.",
    ], dashed=True)
    y_streamb = c.y + hr
    c.y += max(h, hr) + 30

    c.arrow(LX + BOX_W / 2, c.y - 30, LX + BOX_W / 2, c.y - 4)
    c.stage("Screening", c.y + 70)
    h = c.box(LX, BOX_W, f"Records screened, title and abstract (n = {b['records_screened_all_pools']})", [
        f"Three pools screened on different days by two independent reviewers with a third "
        f"adjudicating: pool 1, the {a['embase_article_records_exported']} Embase articles; "
        f"pool 2, {b['pool2_records']} registry and CENTRAL only records; pool 3, "
        f"{b['pool3_records']} Web of Science records.",
        f"Cohen kappa {b['kappa_pool1_v1']} (pool 1) and {b['kappa_pool2_v2']} (pool 2).",
    ])
    c.arrow(LX + BOX_W, c.y + h / 2, RX - 4, c.y + h / 2)
    hr = c.box(RX, EX_W, f"Records excluded (n = {ex_screen})", [
        f"Pool 1 after the criteria v2 rescreen of its v1 exclusions: "
        f"{b['pool1_v2_remain_excluded']} "
        f"({b['pool1_v2_rescued_from_exclusions']} of {b['pool1_v1_exclude']} rescued).",
        f"Pool 2: {b['pool2_exclude']}.   Pool 3: {b['pool3_exclude']}.",
    ])
    c.y += max(h, hr) + 30

    c.arrow(LX + BOX_W / 2, c.y - 30, LX + BOX_W / 2, c.y - 4)
    h = c.box(LX, BOX_W, f"Records sought for full text (n = {b['records_to_full_text']})", [
        f"Pool 1: {b['pool1_to_full_text']}.   Pool 2: {b['pool2_include']}.   "
        f"Pool 3: {b['pool3_include']}.",
    ])
    c.arrow(LX + BOX_W, c.y + h / 2, RX - 4, c.y + h / 2)
    hr = c.box(RX, EX_W, f"Not assessed (n = {f['without_any_text'] + f['already_in_master']})", [
        f"No text obtainable: {f['without_any_text']}, listed with reasons.",
        f"Already held in the master under another record: {f['already_in_master']}.",
    ])
    c.y += max(h, hr) + 30

    c.arrow(LX + BOX_W / 2, c.y - 30, LX + BOX_W / 2, c.y - 4)
    c.stage("Eligibility", c.y + 60)
    h = c.box(LX, BOX_W, f"Records assessed at full text (n = {f['needing_a_screen']})", [
        f"Raw agreement {f['raw_agreement_numerator']} of {f['raw_agreement_denominator']}, "
        f"Cohen kappa {f['kappa']}, low because the marginals are extremely unbalanced and "
        f"reported as such. All {f['disagreements_adjudicated']} disagreements adjudicated, "
        f"{f['adjudicated_to_include']} to include and {f['adjudicated_to_exclude']} to exclude.",
    ])
    c.arrow(LX + BOX_W, c.y + h / 2, RX - 4, c.y + h / 2)
    hr = c.box(RX, EX_W, f"Records excluded (n = {ex_fulltext})", [
        "Design, population, intervention, outcome or timing criterion not met.",
    ])
    c.y += max(h, hr) + 30

    c.arrow(LX + BOX_W / 2, c.y - 30, LX + BOX_W / 2, c.y - 4)
    h = c.box(LX, BOX_W, f"Records included, grouped into studies (n = {g['ledger_groups_final']})", [
        f"{f['included_records']} included records grouped by DOI, title and registry identifier, "
        f"so one study with a conference abstract, a register entry and a full text is one group.",
    ])
    c.y += h + 30

    c.arrow(LX + BOX_W / 2, c.y - 30, LX + BOX_W / 2, c.y - 4)
    c.stage("Included", c.y + 70)
    h = c.box(LX, BOX_W, f"Studies contributing to the synthesis (n = {contributing} groups)", [
        f"{inc['rows']} contrasts over {inc['trials_or_trial_analyses']} trials or trial analyses; "
        f"groups can share a trial. {inc['rows_convertible_to_percent_scale']} convertible to the "
        f"percent change scale, {inc['rows_not_convertible']} not, for want of a printed baseline "
        f"denominator. Risk of bias assessed for {inc['risk_of_bias_records']} records.",
    ])
    c.arrow(LX + BOX_W, c.y + h / 2, RX - 4, c.y + h / 2)
    hr_last = c.box(RX, EX_W, f"Studies closed without contributing (n = {closed})", [
        f"No recoverable variance, closed by the deterministic scan: "
        f"{g['no_usable_contrast_scan']}.",
        f"No recoverable variance on reading: {g['no_usable_contrast']}.",
        f"Eligibility failure visible only at extraction, including three data integrity "
        f"refusals: {g['excluded_at_extraction']}.",
        f"Molecule outside the admitted classes: {g['molecule_not_admitted']}.   "
        f"Registered without posted results: {g['ongoing_no_results']}.",
        f"Held for a Director decision on population or co formulation: "
        f"{g['held_pending_decision']}.",
    ])
    # The adopted inflow joins the synthesis and nowhere above, routed down the right margin so it
    # does not cross the exclusion boxes it has nothing to do with.
    margin_x = RX + EX_W + 28
    below_y = c.y + max(h, hr_last) + 22
    c.route([(RX + EX_W, y_streamb), (margin_x, y_streamb),
             (margin_x, below_y), (LX + BOX_W / 2, below_y),
             (LX + BOX_W / 2, c.y + h + 6)], dashed=True)
    c.parts.append(
        f'<text x="{LX + BOX_W / 2 + 12}" y="{below_y - 7}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="10.5" fill="{MUTED}">'
        f'adopted comparator trials, re-screened at extraction</text>')
    c.y = below_y + PAD

    height = c.y
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" '
        f'aria-label="PRISMA 2020 flow diagram for the incretin aging biomarker review">',
        '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{RULE}"/></marker></defs>',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{LX}" y="30" font-family="Helvetica,Arial,sans-serif" font-size="15" '
        f'font-weight="600" fill="{INK}">PRISMA 2020 flow of records through the review</text>',
    ]
    svg.extend(c.parts)
    svg.append('</svg>')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("\n".join(svg))
        fh.flush()

    print(f"screening balances: {ex_screen} excluded + {b['records_to_full_text']} sought "
          f"= {b['records_screened_all_pools']} screened")
    print(f"full text: {f['needing_a_screen']} assessed - {ex_fulltext} excluded "
          f"= {f['included_records']} included records")
    print(f"ledger balances: {closed} closed + {contributing} contributing "
          f"= {g['ledger_groups_final']} groups")
    print(f"written {os.path.relpath(OUT, ROOT)} ({height} px tall)")


if __name__ == "__main__":
    main()
