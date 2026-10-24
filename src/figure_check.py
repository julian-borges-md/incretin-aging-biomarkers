#!/usr/bin/env python3
"""
figure_check.py

Chain gate. Asks whether every figure the manuscript will submit exists on disk, is hashed in
the manifest, is named in the mapping document, and plots the values of the tables it is drawn
from.

Why this gate exists. Every figure in the analysis pipeline was written with device = cairo_pdf.
The cairo device cannot load on the analysis machine, cairo_pdf warns instead of failing, ggsave
returns normally, and no file is produced. The pipeline then listed the output directory and
printed "Pipeline complete. 35 output files written", which was true of the directory and false of
the figures: there were none, and had never been any, through five days of runs that each reported
success. The run's own count was computed from the directory rather than from the work it had just
claimed to do, so it could not notice.

The lesson generalises past cairo. A figure is an artefact of a device, a font stack and a
filesystem, none of which the script controls, so the only acceptable evidence that a figure exists
is the file. This gate requires that evidence for each figure separately, and requires the three
records that describe the figures to agree:

  1. analysis/output/figure_index.csv, written by the pipeline as it saves each figure, names a
     file for every figure, and every one of those files exists and exceeds 1 KiB. A PDF from an
     empty device is a few hundred bytes, so the size floor distinguishes "written" from "opened".
  2. Every figure file is present in analysis/output/MANIFEST.csv with a SHA-256, so a reviewer can
     verify the figure that accompanies the submission is the figure the run produced.
  3. docs/FIGURES.md names exactly the figures that exist, and assigns each a submission number.
     A figure produced and never mapped does not reach the manuscript; a figure mapped and never
     produced is a hole in the submission. Either way the two must agree.

Figures produced outside the pipeline, the PRISMA flow diagram among them, are declared in
EXTERNAL below with the script that writes them, and are held to the same three requirements.

What a figure shows, added 23 October 2026. The three requirements establish that a figure exists,
is the file the run produced, and is the one the manuscript will number; none of them looks at what
the figure shows. A figure is a second rendering of numbers a table already reports, and the two
can disagree with every file present: until 19 October Figure 4 drew one least squares line per
receptor class beside a table reporting a random effects meta-regression, and nothing here could
have noticed, because a PDF does not record which number a mark stands for. Hence a fourth
requirement:

  4. Every figure writes the values it plots beside it as analysis/output/<stem>.csv, its data
     twin, hashed in the manifest like the figure itself. RULES below holds one rule per figure,
     which recomputes the twin from the result tables and the data the figure is drawn from,
     without the pipeline, and the twin must agree to the ten significant digits it is written at.
     The PRISMA diagram is drawn by src/prisma_figure.R from docs/prisma_counts.json, and its rule
     recomputes every box count with src/prisma_counts.py, a second implementation of the same
     arithmetic, and requires the twin to equal it. The mapping document names, in each figure's
     row, its twin and every file its rule reads, so the record of what a figure is drawn from is
     checked rather than asserted. A produced figure with no rule fails, so a new figure enters the
     manuscript together with the check that covers it.

What a figure is, added 24 October 2026 with figure style 2 (analysis/figure_style.R). A figure is
drawn at its final journal width and written as a vector PDF and a 600 dpi PNG, so a fifth
requirement reads the files themselves rather than the record of them:

  5. Every figure has both files. The PNG records 600 dpi in its pHYs chunk and is 89, 120 or
     183 mm wide and at most 170 mm high, or 247 mm, the full page depth, for a supplementary
     figure; the figure index states the same size. The PDF's page is that size, carries no
     creation or modification date, so an unchanged figure is the same file on every run, and
     declares no font, because figure style 2 draws every glyph as an outline and a font resource
     in the file is text that was set in a face other than the vendored one.

The rules are independent statements of what each figure must show, and two of them do more than
look values up. Figure 4's line and band are refitted from the plotted points: weighted least
squares at the between trial variance Table 4a reports reproduces that table's slope and standard
error only if the points are the model's points, and reproduces the drawn prediction and confidence
band only if the line is the model's line; each point must also be one of its trial's liver fat arms
in the harmonised master, with that trial's receptor class. Figure 5's rule compares the drawn
interval with the table's percentile interval and requires the table to label it so, because the
table carries the BCa interval beside it: a figure drawing that one, or a table whose primary
interval became BCa, would contradict the caption.

Usage
  python3 -I src/figure_check.py
  python3 -I src/figure_check.py --self-test
"""
import csv
import importlib.util
import json
import math
import os
import re
import struct
import sys
import zlib

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "analysis", "output")
INDEX = os.path.join(OUT, "figure_index.csv")
MANIFEST = os.path.join(OUT, "MANIFEST.csv")
MAPPING = os.path.join(ROOT, "docs", "FIGURES.md")
PIPELINE = os.path.join(ROOT, "analysis", "M5_AGE_analysis_pipeline.R")

# Figures written by a script other than the analysis pipeline: stem -> producing script.
EXTERNAL = {
    "figure0_prisma_flow": "src/prisma_figure.R",
}

MIN_BYTES = 1024


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def mapped_stems(text):
    """File stems named in the mapping document.

    The document is a table whose file column holds the stem, optionally with an extension. Any
    token that looks like a figure stem is taken, so the gate does not depend on the column order.

    A stem carries a submission position immediately after the word figure: a digit, or S and a
    digit for a supplementary figure. Requiring it is what keeps the prose out of the parse. The
    first version matched any `figure*_*` token and therefore read this script's own name,
    `figure_check`, and `figure_index.csv` out of the document's prose and reported them as mapped
    figures that no run had produced. A gate that fails on a sentence about itself is a gate people
    switch off.
    """
    return set(re.findall(r"\b(figure(?:\d+|S\d+)_[A-Za-z0-9_]+)\b", text))


def check_twin_file(stem, twin, manifest_names, file_sizes):
    size = file_sizes.get(twin)
    if size is None:
        return ["figure %r has no data twin %s, so what it plots is not on record" % (stem, twin)]
    problems = []
    if size == 0:
        problems.append("data twin %s of figure %r is empty" % (twin, stem))
    if twin not in manifest_names:
        problems.append("data twin %s is not in MANIFEST.csv, so its hash is not on record" % twin)
    return problems


def check(index_rows, manifest_names, mapping_text, file_sizes):
    """file_sizes maps a basename to its size in bytes, or to None if it does not exist."""
    failures = []
    stems = set()

    for r in index_rows:
        stem = (r.get("name") or "").strip()
        if not stem:
            failures.append("figure_index.csv has a row with no name")
            continue
        stems.add(stem)
        files = [f.strip() for f in (r.get("files") or "").split(";") if f.strip()]
        if not files:
            failures.append("figure %r is indexed with no file" % stem)
        if not (r.get("caption") or "").strip():
            failures.append("figure %r is indexed with no caption" % stem)
        for f in files:
            size = file_sizes.get(f)
            if size is None:
                failures.append("figure %r names %s, which does not exist" % (stem, f))
            elif size < MIN_BYTES:
                failures.append("figure %r file %s is %d bytes, below the %d byte floor: a device "
                                "that opened and wrote nothing leaves a file this size"
                                % (stem, f, size, MIN_BYTES))
            if f not in manifest_names:
                failures.append("figure file %s is not in MANIFEST.csv, so its hash is not on "
                                "record" % f)
        twin = (r.get("twin") or "").strip()
        if not twin:
            failures.append("figure %r is indexed with no plotted values; the run writes a data "
                            "twin beside every figure" % stem)
        elif twin != stem + ".csv":
            failures.append("figure %r is indexed with the twin %s, and a twin carries its "
                            "figure's stem" % (stem, twin))
        else:
            failures.extend(check_twin_file(stem, twin, manifest_names, file_sizes))

    for stem, script in sorted(EXTERNAL.items()):
        found = [f for f in file_sizes
                 if f.rsplit(".", 1)[0] == stem and f != stem + ".csv"
                 and (file_sizes[f] or 0) >= MIN_BYTES]
        if not found:
            failures.append("figure %r, produced by %s, has no file of at least %d bytes"
                            % (stem, script, MIN_BYTES))
        else:
            stems.add(stem)
            for f in found:
                if f not in manifest_names:
                    failures.append("figure file %s is not in MANIFEST.csv" % f)
            failures.extend(check_twin_file(stem, stem + ".csv", manifest_names, file_sizes))

    mapped = mapped_stems(mapping_text)
    for stem in sorted(stems - mapped):
        failures.append("figure %r exists and is not mapped to a submission number in "
                        "docs/FIGURES.md" % stem)
    for stem in sorted(mapped - stems):
        failures.append("docs/FIGURES.md maps figure %r, which no run has produced" % stem)
    return failures


def produced_stems(index_rows, file_sizes):
    stems = {(r.get("name") or "").strip() for r in index_rows} - {""}
    for stem in EXTERNAL:
        if any(f.rsplit(".", 1)[0] == stem and f != stem + ".csv" for f in file_sizes):
            stems.add(stem)
    return stems


# ---------------------------------------------------------------------------------------------
# What each figure shows: one rule per figure, each recomputing the figure's twin from its sources
# ---------------------------------------------------------------------------------------------

TABLE2 = "analysis/output/table2_pipeline.csv"
TABLE3 = "analysis/output/table3_primary_results.csv"
TABLE4A = "analysis/output/table4a_hepatic_metaregression.csv"
TABLE5 = "analysis/output/table5_nbais.csv"
INVENTORY = "analysis/data/biomarker_inventory.csv"
MASTER = "analysis/data/extraction_master_harmonised.csv"
ROB = "analysis/data/risk_of_bias.csv"
PRISMA_COUNTS = "docs/prisma_counts.json"
PRISMA_SCRIPT = "src/prisma_counts.py"

# A twin is written at ten significant digits, which moves a value by at most half a unit in the
# tenth digit, 5e-10 of it; twice that is the tolerance for a value read from a twin.
REL = 1e-9
# A quantity this gate derives from several twin values, a refitted slope or a point of a fitted
# band, carries the rounding of all of them.
REL_DERIVED = 1e-6
# The normal quantile metafor uses for a 95 per cent interval under its default z test.
Z975 = 1.959963984540054

ROB_DOMAINS = (("D1", "d1_randomisation"), ("D2", "d2_deviations"), ("D3", "d3_missing"),
               ("D4", "d4_measurement"), ("D5", "d5_selection"), ("Overall", "overall"))
ROB_LEVELS = ("low", "some_concerns", "high")

RULES = {}


def rule(stem, *sources):
    """Registers a rule for a figure with the files it reads, which the mapping document must
    name in that figure's row."""
    def register(fn):
        RULES[stem] = (fn, sources)
        return fn
    return register


def num(s):
    """A number from a CSV cell: None for an empty or NA cell, NaN for one that is not a number."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = s.strip()
    if s in ("", "NA", "NaN"):
        return None
    try:
        return float(s)
    except ValueError:
        return float("nan")


def close(a, b, rel=REL, floor=1e-12):
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), floor)


def agree(got, want):
    """got is a twin cell as written; want is what the source implies, None for an empty cell."""
    if want is None:
        return (got or "").strip() in ("", "NA")
    if isinstance(want, str):
        return (got or "").strip() == want
    g = num(got)
    if g is None or math.isnan(g):
        return False
    if isinstance(want, int):
        return g == want
    return close(g, want)


def shown(v):
    if v is None or v == "":
        return "empty"
    if isinstance(v, float):
        return "%.10g" % v
    return str(v)


def keyed(stem, rows, expected, key, fields):
    """Compares a twin with the rows its source implies, matched on the key columns."""
    failures = []
    seen = {}
    for r in rows:
        k = tuple((r.get(f) or "").strip() for f in key)
        if k in seen:
            failures.append("%s draws %s twice" % (stem, describe(key, k)))
        seen[k] = r
    for k in sorted(set(expected) - set(seen)):
        failures.append("%s does not draw %s, which its source holds" % (stem, describe(key, k)))
    for k in sorted(set(seen) - set(expected)):
        failures.append("%s draws %s, which its source does not hold" % (stem, describe(key, k)))
    for k in sorted(set(seen) & set(expected)):
        for f in fields:
            got, want = seen[k].get(f), expected[k][f]
            if not agree(got, want):
                failures.append("%s, %s: %s is %s in the figure and %s in its source"
                                % (stem, describe(key, k), f, shown(got), shown(want)))
    return failures


def describe(key, k):
    return ", ".join("%s %s" % (f, v) for f, v in zip(key, k))


def inventory(data):
    return {r["biomarker"]: r for r in data[INVENTORY]}


def display_name(entry, biomarker):
    """The name a figure prints, from the inventory's table1_name, as the pipeline labels it."""
    name = (entry.get("table1_name") or "").strip()
    return name if name and name != "NA" else biomarker


@rule("figure0_prisma_flow", PRISMA_COUNTS)
def prisma_rule(stem, rows, data, ctx):
    # The box counts in drawing order, as src/prisma_counts.py computes them from the declared
    # counts; the diagram is drawn by src/prisma_figure.R, so the two implementations must agree.
    prisma = ctx["prisma"]
    try:
        drawn, _ = prisma.rows(json.loads(json.dumps(data[PRISMA_COUNTS])))
    except AssertionError as e:
        return ["%s cannot be drawn from docs/prisma_counts.json: %s" % (stem, e)]
    want = [[str(v) for v in d[:len(prisma.TWIN_HEADER)]] for d in drawn]
    got = [[(r.get(h) or "").strip() for h in prisma.TWIN_HEADER] for r in rows]
    if got != want:
        diff = [i for i in range(max(len(got), len(want)))
                if i >= len(got) or i >= len(want) or got[i] != want[i]]
        return ["%s.csv is not the box counts src/prisma_counts.py computes from "
                "docs/prisma_counts.json, first at row %d of %d; redraw the diagram with "
                "src/prisma_figure.R" % (stem, diff[0] + 1, len(want))]
    return []


@rule("figure1_signature_heatmap", TABLE3, INVENTORY)
def heatmap_rule(stem, rows, data, ctx):
    # Every biomarker that pools in at least one class, against every declared class: a cell with
    # no pooled estimate is drawn empty rather than omitted. The value is the pooled estimate times
    # the biomarker's declared aging direction, so a positive cell is a shift toward younger.
    inv = inventory(data)
    estimate = {(r["biomarker"], r["receptor_class"]): num(r["estimate"]) for r in data[TABLE3]}
    failures, expected = [], {}
    for b in sorted({b for b, _ in estimate}):
        entry = inv.get(b)
        if entry is None:
            failures.append("%s: %s pools in table3_primary_results.csv and has no inventory "
                            "entry, so its direction and domain are not declared" % (stem, b))
            continue
        for c in ctx["receptor_classes"]:
            e = estimate.get((b, c))
            expected[(b, c)] = {
                "hallmark_domain": entry["hallmark_domain"],
                "biomarker_label": display_name(entry, b),
                "signed_effect": None if e is None else num(entry["aging_direction"]) * e,
            }
    return failures + keyed(stem, rows, expected, ("biomarker", "receptor_class"),
                            ("hallmark_domain", "biomarker_label", "signed_effect"))


@rule("figure2_forest_overall", TABLE2, INVENTORY)
def forest_rule(stem, rows, data, ctx):
    # One row per biomarker of Table 2, with the name and favourable direction the inventory
    # declares and its k, in order of effect from the top, which is what the caption states.
    inv = inventory(data)
    failures, expected = [], {}
    for r in data[TABLE2]:
        b = r["biomarker"]
        entry = inv.get(b)
        if entry is None:
            failures.append("%s: %s is in table2_pipeline.csv and has no inventory entry"
                            % (stem, b))
            continue
        expected[(b,)] = {
            "biomarker_label": display_name(entry, b),
            "favourable": "lower" if num(entry["aging_direction"]) < 0 else "higher",
            "k": int(num(r["k"])), "estimate": num(r["estimate"]), "ci_lb": num(r["ci_lb"]),
            "ci_ub": num(r["ci_ub"]), "I2": num(r["I2"]),
        }
    failures += keyed(stem, rows, expected, ("biomarker",),
                      ("biomarker_label", "favourable", "k", "estimate", "ci_lb", "ci_ub", "I2"))
    drawn = [num(r.get("estimate")) for r in rows]
    if all(v is not None and not math.isnan(v) for v in drawn) and drawn != sorted(drawn):
        failures.append("%s: the rows are not in order of effect, which the caption states" % stem)
    return failures


def wls(xs, ys, vs, tau2):
    """Weighted least squares of y on x at weights 1 / (v + tau2), which is the random effects
    meta-regression at a given between trial variance. Returns the intercept, the slope and the
    three entries of their covariance matrix (X'WX)^-1: var(b0), cov(b0, b1), var(b1)."""
    s0 = s1 = s2 = t0 = t1 = 0.0
    for x, y, v in zip(xs, ys, vs):
        w = 1.0 / (v + tau2)
        s0 += w
        s1 += w * x
        s2 += w * x * x
        t0 += w * y
        t1 += w * x * y
    det = s0 * s2 - s1 * s1
    return ((s2 * t0 - s1 * t1) / det, (s0 * t1 - s1 * t0) / det,
            s2 / det, -s1 / det, s0 / det)


def is_arm(arm, x, y, v):
    vals = [num(arm.get(c)) for c in ("pct_weight_change", "yi_pct", "vi_pct")]
    if any(a is None or math.isnan(a) for a in vals):
        return False
    return close(vals[0], x) and close(vals[1], y) and close(vals[2], v)


@rule("figure4_weight_adjusted_liverfat", TABLE4A, TABLE2, MASTER)
def liverfat_rule(stem, rows, data, ctx):
    bm = "liver_fat_pdff"
    t4 = [r for r in data[TABLE4A] if r["biomarker"] == bm]
    t2 = [r for r in data[TABLE2] if r["biomarker"] == bm]
    if len(t4) != 1 or t4[0]["status"] != "fitted" or len(t2) != 1:
        return ["%s: Table 4a and Table 2 do not each carry one fitted liver fat row to check the "
                "figure against" % stem]
    t4, t2 = t4[0], t2[0]
    failures = []
    layers = sorted({(r.get("layer") or "").strip() for r in rows})
    if layers != ["line", "points"]:
        failures.append("%s has the layers %s; it draws points and the fitted line"
                        % (stem, ", ".join(layers) or "none"))
    points = [r for r in rows if (r.get("layer") or "").strip() == "points"]
    line = [r for r in rows if (r.get("layer") or "").strip() == "line"]

    k, set_aside, pooled = (int(num(t4["k"])), int(num(t4["n_dropped_no_covariate"])),
                            int(num(t2["k"])))
    if len(points) != k:
        failures.append("%s draws %d arms; the weight model of Table 4a rests on k = %d"
                        % (stem, len(points), k))
    if len(points) + set_aside != pooled:
        failures.append("%s draws %d arms and Table 4a sets aside %d without the covariate, which "
                        "is not the %d liver fat arms Table 2 pools"
                        % (stem, len(points), set_aside, pooled))

    arms = {}
    for r in data[MASTER]:
        if r["biomarker"] == bm:
            arms.setdefault(r["trial_id"], []).append(r)
    xs, ys, vs = [], [], []
    for p in points:
        trial = (p.get("trial_id") or "").strip()
        x, y, v = num(p.get("pct_weight_change")), num(p.get("yi")), num(p.get("vi"))
        if any(a is None or math.isnan(a) for a in (x, y, v)) or v <= 0:
            failures.append("%s draws a point for %s without a covariate, an effect or a positive "
                            "variance" % (stem, trial or "an unnamed trial"))
            continue
        candidates = arms.get(trial, [])
        if not candidates:
            failures.append("%s draws %s, which has no liver fat row in the harmonised master"
                            % (stem, trial))
            continue
        if not any(is_arm(a, x, y, v) for a in candidates):
            failures.append("%s draws a point for %s that is none of that trial's liver fat arms "
                            "in the harmonised master" % (stem, trial))
        classes = sorted({a["receptor_class"] for a in candidates})
        if classes != [(p.get("receptor_class") or "").strip()]:
            failures.append("%s draws %s as %s, and the harmonised master classes it as %s"
                            % (stem, trial, p.get("receptor_class"), ", ".join(classes)))
        xs.append(x)
        ys.append(y)
        vs.append(v)
    if failures:
        return failures
    if len(xs) < 3:
        return ["%s draws %d arms, too few to refit its line" % (stem, len(xs))]

    # The line is the weight only model, refitted here at Table 4a's between trial variance.
    b0, b1, v00, v01, v11 = wls(xs, ys, vs, num(t4["tau2_weight_only"]))
    slope, se = num(t4["beta_weight_unadjusted"]), num(t4["se_weight_unadjusted"])
    if not close(b1, slope, REL_DERIVED):
        failures.append("%s: the drawn points refit to a slope of %.10g at Table 4a's between "
                        "trial variance, and Table 4a reports %.10g, so the points are not the "
                        "model's points" % (stem, b1, slope))
    if not close(math.sqrt(v11), se, REL_DERIVED):
        failures.append("%s: the drawn points refit to a slope standard error of %.10g, and "
                        "Table 4a reports %.10g" % (stem, math.sqrt(v11), se))
    if len(line) != 100:
        failures.append("%s draws its line at %d points; the pipeline predicts at 100"
                        % (stem, len(line)))
    lo, hi = min(xs), max(xs)
    for j, r in enumerate(line):
        x = lo + (hi - lo) * j / (len(line) - 1) if len(line) > 1 else lo
        pred = b0 + b1 * x
        half = Z975 * math.sqrt(v00 + 2.0 * x * v01 + x * x * v11)
        want = (("pct_weight_change", x), ("yi", pred), ("lo", pred - half), ("hi", pred + half))
        bad = [(f, w) for f, w in want
               if num(r.get(f)) is None or math.isnan(num(r.get(f)))
               or not close(num(r.get(f)), w, REL_DERIVED, 1e-6)]
        if bad:
            f, w = bad[0]
            failures.append("%s, line point %d: %s is %s in the figure and %.10g in the weight "
                            "model of Table 4a, so the line and band are not that model's"
                            % (stem, j + 1, f, shown(r.get(f)), w))
            break
    return failures


@rule("figure5_nbais", TABLE5)
def nbais_rule(stem, rows, data, ctx):
    # The computed composites only; the interval drawn is the percentile interval of the two level
    # bootstrap, which is what the caption names.
    failures, expected = [], {}
    for r in data[TABLE5]:
        if r["status"] != "computed":
            continue
        if r["ci_type"] != "percentile_two_level":
            failures.append("%s: the interval of %s under %s weighting is %s in table5_nbais.csv; "
                            "the figure draws, and its caption names, the percentile interval of "
                            "the two level bootstrap"
                            % (stem, r["receptor_class"], r["weighting"], r["ci_type"]))
        expected[(r["weighting"], r["receptor_class"])] = {
            "nbais": num(r["nbais"]), "ci_lb": num(r["ci_lb"]), "ci_ub": num(r["ci_ub"]),
            "n_markers": int(num(r["n_markers"])),
        }
    return failures + keyed(stem, rows, expected, ("weighting", "receptor_class"),
                            ("nbais", "ci_lb", "ci_ub", "n_markers"))


def rob_cells(stem, data):
    failures, cells, seen = [], {}, set()
    for r in data[ROB]:
        trial = r["trial_id"]
        if trial in seen:
            failures.append("%s: risk_of_bias.csv holds %s twice" % (stem, trial))
        seen.add(trial)
        for domain, column in ROB_DOMAINS:
            judgement = (r.get(column) or "").strip()
            if judgement not in ROB_LEVELS:
                failures.append("%s: %s carries %r in %s, which is not a RoB-2 level"
                                % (stem, trial, judgement, column))
            cells[(trial, domain)] = judgement
    return failures, cells


@rule("figure6_rob_summary", ROB)
def rob_summary_rule(stem, rows, data, ctx):
    # Per domain, the number of trials at each judgement that occurs and its share of the domain.
    failures, cells = rob_cells(stem, data)
    counts, totals = {}, {}
    for (_, domain), judgement in cells.items():
        counts[(domain, judgement)] = counts.get((domain, judgement), 0) + 1
        totals[domain] = totals.get(domain, 0) + 1
    expected = {k: {"n": n, "share": n / totals[k[0]]} for k, n in counts.items()}
    return failures + keyed(stem, rows, expected, ("domain", "judgement"), ("n", "share"))


@rule("figureS1_rob_traffic_light", ROB)
def rob_traffic_rule(stem, rows, data, ctx):
    failures, cells = rob_cells(stem, data)
    expected = {k: {"judgement": j} for k, j in cells.items()}
    return failures + keyed(stem, rows, expected, ("trial_id", "domain"), ("judgement",))


def check_registry(mapping_text, stems):
    """Each figure's row in the figure set table of docs/FIGURES.md names its twin and every file
    its rule reads."""
    failures = []
    rows = [ln for ln in mapping_text.splitlines() if ln.startswith("| Figure")]
    for stem in sorted(stems):
        mine = [ln for ln in rows if "`%s`" % stem in ln]
        if len(mine) != 1:
            failures.append("docs/FIGURES.md has %d rows for %r in its figure set table, and needs "
                            "one naming the figure's plotted values and their sources"
                            % (len(mine), stem))
            continue
        for name in [stem + ".csv"] + [os.path.basename(s) for s in RULES[stem][1]]:
            if name not in mine[0]:
                failures.append("docs/FIGURES.md does not name %s in the row of %r, so the record "
                                "of what that figure is drawn from is incomplete" % (name, stem))
    return failures


def check_content(stems, twins, data, ctx, mapping_text):
    failures = []
    for stem in sorted(stems - set(RULES)):
        failures.append("figure %r has no rule in src/figure_check.py recomputing what it plots; "
                        "a figure enters the manuscript with the rule that checks it" % stem)
    for stem in sorted(set(RULES) - stems):
        failures.append("src/figure_check.py holds a rule for figure %r, which no run has produced"
                        % stem)
    for stem in sorted(stems & set(RULES)):
        if stem in twins:   # a missing twin is reported by check()
            failures.extend(RULES[stem][0](stem, twins[stem], data, ctx))
    failures.extend(check_registry(mapping_text, stems & set(RULES)))
    return failures


# ---------------------------------------------------------------------------------------------
# What a figure is: the files of figure style 2, read from the files themselves
# ---------------------------------------------------------------------------------------------

JOURNAL_WIDTHS_MM = (89.0, 120.0, 183.0)
MAX_HEIGHT_MM = 170.0
PAGE_DEPTH_MM = 247.0
DPI = 600
PX_PER_METRE = round(DPI / 0.0254)
# A device writes whole pixels and R's PDF device whole points, so a size read back from a file is
# short of the size drawn by up to one pixel or one point.
PNG_TOL_MM = 0.1
PDF_TOL_MM = 0.4
MM_PER_PT = 25.4 / 72


def png_geometry(data):
    """Width and height in pixels and the pHYs chunk (x and y pixels per unit, unit) or None, read
    from the chunks a PNG carries before its image data."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    pos, size, phys = 8, None, None
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            size = struct.unpack(">II", body[:8])
        elif kind == b"pHYs":
            phys = struct.unpack(">IIB", body[:9])
        elif kind == b"IDAT":
            break
        pos += 12 + length
    if size is None:
        raise ValueError("no IHDR chunk")
    return size[0], size[1], phys


def pdf_geometry(data):
    """The page width and height in points, whether the file carries a date, and the fonts its
    resources name."""
    m = re.search(rb"/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]", data)
    if not m:
        raise ValueError("no page size")
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    dated = b"/CreationDate" in data or b"/ModDate" in data
    fonts = sorted({f.decode("latin-1") for f in re.findall(rb"/BaseFont\s*/([^\s/<>\[\]()]+)",
                                                           data)})
    return x1 - x0, y1 - y0, dated, fonts


def supplementary(stem):
    return re.match(r"figureS\d+_", stem) is not None


def check_format(stem, png, pdf, index_row=None):
    """png and pdf are the bytes of the figure's files, or None where a file does not exist; the
    PNG may be only its first few kilobytes."""
    failures = []
    if png is None or pdf is None:
        missing = " and ".join(e for e, b in (("PDF", pdf), ("PNG", png)) if b is None)
        failures.append("figure %r has no %s; every figure is written as a vector PDF and a %d dpi "
                        "PNG" % (stem, missing, DPI))
    width_mm = height_mm = None
    if png is not None:
        try:
            w, h, phys = png_geometry(png)
        except (ValueError, struct.error) as e:
            return failures + ["%s.png cannot be read: %s" % (stem, e)]
        if phys is None or phys[2] != 1:
            failures.append("%s.png does not record its resolution, so it is %d by %d pixels at no "
                            "stated size" % (stem, w, h))
        elif abs(phys[0] - PX_PER_METRE) > 1 or abs(phys[1] - PX_PER_METRE) > 1:
            failures.append("%s.png is %.0f dpi, and a figure is written at %d dpi"
                            % (stem, phys[0] * 0.0254, DPI))
        else:
            width_mm, height_mm = w / phys[0] * 1000.0, h / phys[1] * 1000.0
            if min(abs(width_mm - j) for j in JOURNAL_WIDTHS_MM) > PNG_TOL_MM:
                failures.append("%s.png is %.1f mm wide, and a figure is drawn at a journal width, "
                                "%s mm" % (stem, width_mm,
                                           ", ".join("%g" % j for j in JOURNAL_WIDTHS_MM)))
            limit = PAGE_DEPTH_MM if supplementary(stem) else MAX_HEIGHT_MM
            if height_mm > limit + PNG_TOL_MM:
                failures.append("%s.png is %.1f mm high, above the %g mm a %s figure may take"
                                % (stem, height_mm, limit,
                                   "supplementary" if supplementary(stem) else "main text"))
            if index_row is not None:
                for field, got in (("width_mm", width_mm), ("height_mm", height_mm)):
                    stated = num(index_row.get(field))
                    if stated is None or math.isnan(stated) or abs(stated - got) > PNG_TOL_MM:
                        failures.append("figure_index.csv states %s %s for %r, and its PNG is "
                                        "%.1f mm" % (field, shown(index_row.get(field)), stem, got))
    if pdf is not None:
        try:
            pw, ph, dated, fonts = pdf_geometry(pdf)
        except ValueError as e:
            return failures + ["%s.pdf cannot be read: %s" % (stem, e)]
        if dated:
            failures.append("%s.pdf carries a creation or modification date, so the same figure "
                            "is a different file on every run" % stem)
        if fonts:
            failures.append("%s.pdf declares the font(s) %s: text set in a face other than the "
                            "vendored one, which figure style 2 draws as outlines"
                            % (stem, ", ".join(fonts)))
        if width_mm is not None and (abs(pw * MM_PER_PT - width_mm) > PDF_TOL_MM
                                     or abs(ph * MM_PER_PT - height_mm) > PDF_TOL_MM):
            failures.append("%s.pdf is %.1f by %.1f mm and its PNG %.1f by %.1f mm, so the two are "
                            "not the same figure" % (stem, pw * MM_PER_PT, ph * MM_PER_PT,
                                                     width_mm, height_mm))
    return failures


def read_head(path, n=None):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return fh.read() if n is None else fh.read(n)


def check_formats(stems, index_rows):
    index = {(r.get("name") or "").strip(): r for r in index_rows}
    failures = []
    for stem in sorted(stems):
        failures.extend(check_format(stem, read_head(os.path.join(OUT, stem + ".png"), 65536),
                                     read_head(os.path.join(OUT, stem + ".pdf")),
                                     index.get(stem)))
    return failures


def declared_classes():
    with open(PIPELINE) as fh:
        text = fh.read()
    m = re.search(r"^RECEPTOR_CLASSES\s*<-\s*c\(([^)]*)\)", text, flags=re.M)
    if not m:
        raise RuntimeError("the pipeline no longer declares RECEPTOR_CLASSES, which the rule for "
                           "figure 1 reads")
    return re.findall(r'"([^"]+)"', m.group(1))


def load_prisma():
    spec = importlib.util.spec_from_file_location("prisma_counts",
                                                  os.path.join(ROOT, PRISMA_SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_content(stems):
    """The twins of the produced figures, every file a rule reads, and the rules' context."""
    twins = {}
    for stem in stems:
        path = os.path.join(OUT, stem + ".csv")
        if os.path.exists(path):
            twins[stem] = read_csv(path)
    data = {}
    for _, sources in RULES.values():
        for s in sources:
            if s not in data:
                full = os.path.join(ROOT, s)
                if s.endswith(".json"):
                    with open(full) as fh:
                        data[s] = json.load(fh)
                else:
                    data[s] = read_csv(full)
    ctx = {"receptor_classes": declared_classes(), "prisma": load_prisma()}
    return twins, data, ctx


def fake_png(width_mm, height_mm, dpi=DPI):
    """The signature and the chunks before the image data of a PNG of that size, as ragg writes
    it: whole pixels, truncated, and the resolution in pixels per metre."""
    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff))
    px = int(width_mm / 25.4 * (dpi or 72))
    py = int(height_mm / 25.4 * (dpi or 72))
    out = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", px, py, 8, 6, 0, 0, 0))
    if dpi is not None:
        ppm = round(dpi / 0.0254)
        out += chunk(b"pHYs", struct.pack(">IIB", ppm, ppm, 1))
    return out + chunk(b"IDAT", b"")


def fake_pdf(width_mm, height_mm, dated=False, font=None):
    """The objects of a PDF that the checks read, as R's PDF device writes them: the page size in
    whole points, truncated, an information dictionary and the page resources."""
    out = b"%PDF-1.4\n1 0 obj\n<<\n/Title (R Graphics Output)\n/Producer (R 4.5.2)\n"
    if dated:
        out += b"/CreationDate (D:20261024120000)\n/ModDate (D:20261024120000)\n"
    out += b">>\nendobj\n"
    out += b"4 0 obj\n<<\n/ProcSet [/PDF /Text]\n/Font <<"
    if font:
        out += b" /F1 5 0 R >>\n>>\nendobj\n5 0 obj\n<< /Type /Font /BaseFont /" + font.encode()
    out += b">>\nendobj\n"
    out += b"3 0 obj\n<< /Type /Pages /MediaBox [0 0 %d %d] >>\nendobj\n" % (
        int(width_mm / 25.4 * 72), int(height_mm / 25.4 * 72))
    return out


def self_test():
    index = [{"name": "figure9_thing", "caption": "a caption",
              "files": "figure9_thing.pdf; figure9_thing.png", "twin": "figure9_thing.csv"}]
    manifest = {"figure9_thing.pdf", "figure9_thing.png", "figure9_thing.csv",
                "figure0_prisma_flow.pdf", "figure0_prisma_flow.png", "figure0_prisma_flow.csv"}
    sizes = {"figure9_thing.pdf": 40000, "figure9_thing.png": 90000, "figure9_thing.csv": 400,
             "figure0_prisma_flow.pdf": 1400000, "figure0_prisma_flow.png": 650000,
             "figure0_prisma_flow.csv": 600}
    mapping = "| Figure 1 | figure0_prisma_flow | x |\n| Figure 2 | figure9_thing | y |"

    cases = []

    # The cairo failure itself: ggsave returned, nothing was written.
    s = dict(sizes); s.pop("figure9_thing.pdf")
    cases.append(("a figure file that does not exist",
                  check(index, manifest, mapping, s), "does not exist"))

    # A device that opened the file and wrote an empty page.
    s = dict(sizes); s["figure9_thing.pdf"] = 300
    cases.append(("a figure file below the size floor",
                  check(index, manifest, mapping, s), "below the"))

    # The figure exists but its hash is not on record.
    m = set(manifest); m.discard("figure9_thing.png")
    cases.append(("a figure missing from the manifest",
                  check(index, m, mapping, sizes), "not in MANIFEST.csv"))

    # Produced and never mapped, and mapped and never produced.
    cases.append(("a figure absent from the mapping",
                  check(index, manifest, "| Figure 1 | figure0_prisma_flow | x |", sizes),
                  "not mapped to a submission number"))
    cases.append(("a mapping entry with no figure",
                  check(index, manifest, mapping + "\n| Figure 3 | figure7_ghost | z |", sizes),
                  "which no run has produced"))

    # The gate's own first run failed on prose: a sentence naming src/figure_check.py and
    # analysis/output/figure_index.csv was parsed as two mapped figures.
    prose = (mapping + "\nThe gate is `src/figure_check.py` and the run writes "
             "`analysis/output/figure_index.csv` beside the figures.")
    quiet_prose = not check(index, manifest, prose, sizes)

    # The externally produced PRISMA figure.
    s = dict(sizes); s.pop("figure0_prisma_flow.pdf"); s.pop("figure0_prisma_flow.png")
    cases.append(("the external PRISMA figure missing",
                  check(index, manifest, mapping, s), "produced by src/prisma_figure.R"))

    # What a figure is, 24 October: the files of figure style 2, read from synthetic files built
    # here to the formats the devices write, one defect at a time.
    row = {"width_mm": "89", "height_mm": "60"}
    good = (fake_png(89, 60), fake_pdf(89, 60))
    quiet_format = not check_format("figure9_thing", *good, index_row=row)
    quiet_supplement = not check_format("figureS9_thing", fake_png(120, 240), fake_pdf(120, 240))
    cases.append(("a PNG at 300 dpi",
                  check_format("figure9_thing", fake_png(89, 60, dpi=300), good[1], row),
                  "is 300 dpi"))
    cases.append(("a PNG that records no resolution",
                  check_format("figure9_thing", fake_png(89, 60, dpi=None), good[1], row),
                  "does not record its resolution"))
    cases.append(("a figure at no journal width",
                  check_format("figure9_thing", fake_png(150, 60), fake_pdf(150, 60)),
                  "journal width"))
    cases.append(("a main text figure above 170 mm",
                  check_format("figure9_thing", fake_png(183, 190), fake_pdf(183, 190)),
                  "above the 170 mm"))
    cases.append(("a supplementary figure above the page depth",
                  check_format("figureS9_thing", fake_png(120, 255), fake_pdf(120, 255)),
                  "above the 247 mm"))
    cases.append(("an index size the PNG does not have",
                  check_format("figure9_thing", *good, index_row={"width_mm": "89",
                                                                 "height_mm": "70"}),
                  "states height_mm"))
    cases.append(("a PDF with a creation date",
                  check_format("figure9_thing", good[0], fake_pdf(89, 60, dated=True), row),
                  "creation or modification date"))
    cases.append(("a PDF that declares a font",
                  check_format("figure9_thing", good[0], fake_pdf(89, 60, font="Helvetica"), row),
                  "declares the font"))
    cases.append(("a PDF of another size than its PNG",
                  check_format("figure9_thing", good[0], fake_pdf(89, 70), row),
                  "not the same figure"))
    cases.append(("a figure with no PNG",
                  check_format("figure9_thing", None, good[1], row), "has no PNG"))

    # The plotted values, 23 October: a figure indexed without them, a twin that was not written,
    # one whose hash is not on record, and the external figure's twin missing.
    i = [dict(index[0], twin="")]
    cases.append(("a figure indexed with no plotted values",
                  check(i, manifest, mapping, sizes), "no plotted values"))
    s = dict(sizes); s.pop("figure9_thing.csv")
    cases.append(("a data twin that does not exist",
                  check(index, manifest, mapping, s), "has no data twin"))
    m = set(manifest); m.discard("figure9_thing.csv")
    cases.append(("a data twin missing from the manifest",
                  check(index, m, mapping, sizes), "data twin figure9_thing.csv is not in"))
    s = dict(sizes); s.pop("figure0_prisma_flow.csv")
    cases.append(("the external figure's twin missing",
                  check(index, manifest, mapping, s), "has no data twin"))

    print("SELF TEST")
    ok = True
    for name, failures, expect in cases:
        found = any(expect in f for f in failures)
        print("  %-48s %s" % (name, found))
        ok = ok and found
    quiet = not check(index, manifest, mapping, sizes)
    print("  %-48s %s" % ("a complete set passes", quiet))
    print("  %-48s %s" % ("prose naming the gate is not a figure", quiet_prose))
    print("  %-48s %s" % ("a figure in figure style 2 passes", quiet_format))
    print("  %-48s %s" % ("a full page supplementary figure passes", quiet_supplement))
    ok = ok and quiet and quiet_prose and quiet_format and quiet_supplement
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


# The plotted field that the generic perturbations of the content self test move, per figure.
MOVE = {
    "figure0_prisma_flow": "n",
    "figure1_signature_heatmap": "signed_effect",
    "figure2_forest_overall": "estimate",
    "figure4_weight_adjusted_liverfat": "yi",
    "figure5_nbais": "nbais",
    "figure6_rob_summary": "n",
    "figureS1_rob_traffic_light": "judgement",
}


def moved(value):
    """A wrong value of the same kind: another RoB-2 level, one more count, or a one per cent
    shift."""
    v = (value or "").strip()
    if v in ROB_LEVELS:
        return "low" if v != "low" else "high"
    if re.fullmatch(r"-?\d+", v):
        return str(int(v) + 1)
    x = float(v)
    return repr(x * 1.01 if x != 0 else 1.0)


def content_self_test():
    """Injects into the tracked twins and tables the defects the content rules exist for, and
    requires each to be caught and the tracked set to pass. It runs on this repository's own
    figures and tables, because a rule shown to work on a toy table has not been shown to work on
    these, and it fails rather than passes when the twins are absent, naming the command."""
    print("CONTENT SELF TEST, on the tracked figures and tables")
    try:
        index_rows = read_csv(INDEX)
        sizes = {f: os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)
                 if os.path.isfile(os.path.join(OUT, f))}
        stems = produced_stems(index_rows, sizes)
        twins, data, ctx = load_content(stems)
        with open(MAPPING) as fh:
            mapping = fh.read()
    except (OSError, RuntimeError) as e:
        print("  cannot run: %s" % e)
        print("  FAIL")
        return 1
    absent = sorted(set(RULES) - set(twins))
    if absent:
        print("  no data twin for %s; run make prisma and make analysis" % ", ".join(absent))
        print("  FAIL")
        return 1

    def run(t=None, d=None, c=None, m=None, s=None):
        return check_content(s or stems, t or twins, d or data, c or ctx,
                             mapping if m is None else m)

    def with_twin(stem, rows):
        t = dict(twins)
        t[stem] = rows
        return t

    def with_data(path, value):
        d = dict(data)
        d[path] = value
        return d

    cases = []
    for stem in sorted(RULES):
        rows, field = twins[stem], MOVE[stem]
        i = next(n for n, r in enumerate(rows) if (r.get(field) or "").strip()
                 and (r.get("layer") or "points") == "points")
        edited = [dict(r) for r in rows]
        edited[i][field] = moved(rows[i][field])
        cases.append(("%s, a plotted value moved" % stem, run(t=with_twin(stem, edited)), stem))
        cases.append(("%s, a plotted row dropped" % stem, run(t=with_twin(stem, rows[:-1])), stem))
        cases.append(("%s, a row drawn twice" % stem,
                      run(t=with_twin(stem, rows + [dict(rows[0])])), stem))

    # Figure 1 drawn without the aging direction: the raw estimate where the direction is minus one.
    stem = "figure1_signature_heatmap"
    direction = {r["biomarker"]: num(r["aging_direction"]) for r in data[INVENTORY]}
    raw = {(r["biomarker"], r["receptor_class"]): r["estimate"] for r in data[TABLE3]}
    edited = [dict(r) for r in twins[stem]]
    j = next(n for n, r in enumerate(edited) if (r["biomarker"], r["receptor_class"]) in raw
             and direction.get(r["biomarker"]) == -1)
    edited[j]["signed_effect"] = raw[(edited[j]["biomarker"], edited[j]["receptor_class"])]
    cases.append(("figure 1 drawn without the aging direction",
                  run(t=with_twin(stem, edited)), "signed_effect"))

    # Figure 2 left as drawn while Table 2 moved, and drawn out of order.
    stem = "figure2_forest_overall"
    t2 = [dict(r) for r in data[TABLE2]]
    t2[0]["estimate"] = repr(float(t2[0]["estimate"]) * 1.01)
    cases.append(("figure 2 stale against a regenerated Table 2",
                  run(d=with_data(TABLE2, t2)), "in its source"))
    cases.append(("figure 2 out of order of effect",
                  run(t=with_twin(stem, list(reversed(twins[stem])))), "order of effect"))

    # Figure 4: another dose arm of the same trial plotted, the line refitted without weights as
    # geom_smooth drew it until 19 October, and a band widened.
    stem = "figure4_weight_adjusted_liverfat"
    rows = twins[stem]
    arms = {}
    for r in data[MASTER]:
        if r["biomarker"] == "liver_fat_pdff" and num(r["pct_weight_change"]) is not None:
            arms.setdefault(r["trial_id"], []).append(r)
    edited = [dict(r) for r in rows]
    for p in edited:
        others = [a for a in arms.get(p["trial_id"], [])
                  if not is_arm(a, num(p["pct_weight_change"]), num(p["yi"]), num(p["vi"]))]
        if p.get("layer") == "points" and others:
            p.update(pct_weight_change="%.10g" % num(others[0]["pct_weight_change"]),
                     yi="%.10g" % num(others[0]["yi_pct"]), vi="%.10g" % num(others[0]["vi_pct"]))
            break
    cases.append(("figure 4 plotting another dose arm of a trial",
                  run(t=with_twin(stem, edited)), "slope"))
    pts = [(num(r["pct_weight_change"]), num(r["yi"])) for r in rows if r["layer"] == "points"]
    mx = sum(x for x, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    b = (sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts))
    edited = [dict(r) for r in rows]
    for r in edited:
        if r["layer"] == "line":
            r["yi"] = "%.10g" % (my + b * (num(r["pct_weight_change"]) - mx))
    cases.append(("figure 4 line fitted by unweighted least squares",
                  run(t=with_twin(stem, edited)), "line and band"))
    edited = [dict(r) for r in rows]
    k = next(n for n, r in enumerate(edited) if r["layer"] == "line")
    edited[k]["hi"] = repr(num(edited[k]["hi"]) + 0.01 * abs(num(edited[k]["hi"])) + 0.01)
    cases.append(("figure 4 band widened", run(t=with_twin(stem, edited)), "line and band"))

    # Figure 5 drawing the BCa interval, and Table 5 relabelling its primary interval.
    stem = "figure5_nbais"
    bca = {(r["weighting"], r["receptor_class"]): r for r in data[TABLE5]
           if r["status"] == "computed"}
    edited = [dict(r) for r in twins[stem]]
    src = bca[(edited[0]["weighting"], edited[0]["receptor_class"])]
    edited[0].update(ci_lb=src["bca_lb"], ci_ub=src["bca_ub"])
    cases.append(("figure 5 drawing the BCa interval", run(t=with_twin(stem, edited)), "ci_lb"))
    t5 = [dict(r) for r in data[TABLE5]]
    next(r for r in t5 if r["status"] == "computed")["ci_type"] = "bca"
    cases.append(("table 5's primary interval relabelled",
                  run(d=with_data(TABLE5, t5)), "percentile interval"))

    # A judgement recoded in the risk of bias data without the figures being redrawn.
    rob = [dict(r) for r in data[ROB]]
    rob[0]["d1_randomisation"] = moved(rob[0]["d1_randomisation"])
    failures = run(d=with_data(ROB, rob))
    cases.append(("a RoB-2 judgement recoded, both RoB figures",
                  failures, "figure6_rob_summary"))
    cases.append(("a RoB-2 judgement recoded, the traffic light",
                  failures, "figureS1_rob_traffic_light"))

    # The PRISMA counts changed without the diagram being redrawn, and a box count computed by the
    # drawing script with a term left out of its sum.
    counts = json.loads(json.dumps(data[PRISMA_COUNTS]))
    counts["stream_b_adopted"]["ren_2025_rcts"] += 1
    cases.append(("PRISMA counts changed, diagram not redrawn",
                  run(d=with_data(PRISMA_COUNTS, counts)), "is not the box counts"))
    stem = "figure0_prisma_flow"
    held = data[PRISMA_COUNTS]["grouping_and_extraction"]["held_pending_decision"]
    edited = [dict(r) for r in twins[stem]]
    last = next(r for r in edited if r["box"] == "Studies closed without contributing")
    last["n"] = str(int(last["n"]) - held)
    cases.append(("PRISMA closed studies summed without the held ones",
                  run(t=with_twin(stem, edited)), "is not the box counts"))

    # Figure 2 labelling a marker with the wrong favourable direction.
    stem = "figure2_forest_overall"
    edited = [dict(r) for r in twins[stem]]
    edited[0]["favourable"] = "higher" if edited[0]["favourable"] == "lower" else "lower"
    cases.append(("figure 2 with a favourable direction flipped",
                  run(t=with_twin(stem, edited)), "favourable"))

    # The record of what a figure is drawn from, and a figure with no rule.
    row = next(ln for ln in mapping.splitlines() if "`figure5_nbais`" in ln)
    cases.append(("a source missing from the mapping row",
                  run(m=mapping.replace(row, row.replace("table5_nbais.csv", "the table"))),
                  "does not name table5_nbais.csv"))
    cases.append(("a produced figure with no rule",
                  run(s=stems | {"figure8_unruled"}), "has no rule"))

    ok = True
    for name, failures, expect in cases:
        found = any(expect in f for f in failures)
        print("  %-56s %s" % (name, found))
        ok = ok and found
    base = run()
    print("  %-56s %s" % ("the tracked figures agree with their sources", not base))
    for f in base:
        print("    " + f)
    ok = ok and not base
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
        print()
        rc = rc or content_self_test()
        if rc != 0:
            return rc
        print()

    for p in (INDEX, MANIFEST, MAPPING):
        if not os.path.exists(p):
            print("FAIL: %s is missing" % os.path.relpath(p, ROOT))
            return 1

    index_rows = read_csv(INDEX)
    manifest_names = {os.path.basename(r["file"]) for r in read_csv(MANIFEST)}
    with open(MAPPING) as fh:
        mapping_text = fh.read()
    file_sizes = {}
    for f in os.listdir(OUT):
        full = os.path.join(OUT, f)
        if os.path.isfile(full):
            file_sizes[f] = os.path.getsize(full)

    failures = check(index_rows, manifest_names, mapping_text, file_sizes)
    stems = produced_stems(index_rows, file_sizes)
    format_failures = check_formats(stems, index_rows)
    failures.extend(format_failures)
    twins = {}
    try:
        twins, data, ctx = load_content(stems)
        failures.extend(check_content(stems, twins, data, ctx, mapping_text))
    except (OSError, RuntimeError) as e:
        failures.append("the plotted values could not be checked: %s" % e)

    print("figure check")
    print("  %d figure(s) in the index, %d external, %d file(s) in the output directory"
          % (len(index_rows), len(EXTERNAL), len(file_sizes)))
    for r in index_rows:
        print("  %-34s %s" % (r.get("name", ""), r.get("files", "")))
    if not format_failures:
        print("  %d figure(s) as a PDF with no date and no font and a %d dpi PNG at a journal "
              "width" % (len(stems), DPI))
    print("  plotted values, recomputed from")
    for stem in sorted(twins):
        sources = ", ".join(os.path.basename(s) for s in RULES.get(stem, (None, ()))[1])
        print("  %-34s %4d row(s)  %s" % (stem, len(twins[stem]), sources))
    if not failures:
        print("  every figure exists, is hashed, is mapped to a submission number, is written in "
              "figure style 2, and plots the values of its sources")
        return 0
    print("\nFAIL: %d problem(s)" % len(failures))
    for f in failures:
        print("  " + f)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
