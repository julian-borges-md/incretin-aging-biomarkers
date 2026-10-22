#!/usr/bin/env python3
"""
arm_header_attribution_check.py

The extension docs/ARM_ATTRIBUTION_TRIAGE.md measured and specified, built, and tightened by what
building it found. It reaches the rows the adjacent label gate cannot: table captures, where the arm
names sit in a header line above the values rather than in front of them.

WHAT THE ADJACENT LABEL GATE LEAVES. src/arm_attribution_check.py attributes a derived row's two arm
values by finding the nearest arm name to the LEFT of each value on the line they share. Of 122
derived rows it classifies 3; 80 of the remaining 119 fail for one reason, which this gate takes as
its scope: the line holds `MRI-PDFF  15.4% +/- 5.6%  12.5% +/- 6.4%  -4.0% +/- 4.5%` and the arm
names are in a header above it. No lookback along the value line can reach a header.

THE RULE. These captures separate columns with a delimiter rather than aligning character columns,
so column position cannot be recovered. What survives is ORDER: the order in which the header names
the arms is the order in which their values print below. Per row:

  1. find every line carrying both of the row's arm values as numbers
  2. keep the candidates where the two values are adjacent arm columns, in the sense below
  3. for each, find the nearest header above it, in the same file, naming both arms once
  4. the arm named first in the header owns the value that prints first
  5. require every surviving candidate to agree

FOUR GUARDS, each of which exists because its absence produced a false REVERSED on the first run
over the real corpus. Reporting them is the point: the first version of this gate found five
REVERSED rows and all five were artefacts of the rule, not defects in the extraction.

  Numbers, not substrings. The adjacent label gate matches a value as a string, and falls back to
  the unsigned string when the signed one misses. On this corpus that fallback makes the value -4
  match the printed 4.5, because the digit 4 occurs in it standalone by its own test. This gate
  extracts numeric TOKENS with their positions and compares them as numbers, so 4.5 is the number
  4.5 and nothing else. It is the one place where this gate deliberately does not reuse the adjacent
  gate's definition, and the divergence is recorded in the triage document as a defect of that gate
  rather than fixed here, because its output is already in the record.

  Adjacency. In a three arm table the row's two values are two of nine fields, with another arm's
  values between them, and the order rule cannot say which column either value came from. So every
  numeric token between the two matched values must be ATTACHED to a value rather than standing
  alone: a dispersion after a +/-, a count in parentheses, a p value. A bare number between them is
  another column, and the row is refused. This is what the Light On three arm table is, and the
  first version read it as a swap.

  Prose is not a header. A sentence that names both arms names them in the order the sentence
  needs, not in column order. The GDF15 row's nearest line naming both arms was a figure caption;
  the NCT04844918 rows' was the abstract's randomisation sentence; and the Kelly 2012 triglyceride
  row's was the paper's title, which names exenatide before metformin while the table prints
  metformin first, so a title admitted as a header inverts every verdict it attributes.

  The first version of this guard used length, on the measurement that the real headers here run 32
  to 83 characters and the prose lines exceed 100. That threshold admitted a 78 character sentence,
  `Body fat data were obtained in 35 patients (exenatide N = 17; metformin N = 18)`, and attributed
  the Kelly triglyceride row from it. Length is a proxy for the property that matters, and the
  property itself is available: a header is a line of COLUMN LABELS. So the test is structural. The
  line is accepted when it is columnar, meaning it splits into fields on a tab, a pipe or a run of
  spaces and names the two arms in DIFFERENT fields; or, when it is not, only if the value line
  itself splits into exactly two fields, which is the two arm case where no column can be mistaken
  for another and which is the shape this review's own captures use. A line that names both arms
  and fails both tests stops the search rather than being skipped, because a header further up
  belongs to a different block of the table.

  Unanimity. The first version chose the single line on which the two values sat closest together,
  which is the adjacent gate's rule, and a spuriously tight pair elsewhere in the same paper beats
  the true pair sixty characters apart. Every candidate is now classified and they must agree; a
  disagreement is reported as unclassifiable, which is what an ambiguous attribution is.

WHAT A GREEN RESULT IS WORTH, which is the finding the triage document insists this gate carry.
A header is evidence of attribution only as far as its own provenance goes:

  independent source   the header is the publisher's or the indexer's own text, machine retrieved.
                       Agreement means the extraction matches the source
  session capture      the header is a caption this review wrote while reading a rendered page.
                       Agreement means the extraction matches the capture, and a misreading at the
                       capture step is reproduced rather than caught

Those are different claims and this gate never adds them together. Every count it prints is split by
the provenance of the file the verdict came from, and the classification is imported from
src/source_provenance.py so that this gate and the provenance registry cannot drift apart.

FAILURE. Only REVERSED fails the chain, and only when the row is not written up in
docs/ARM_ATTRIBUTION_TRIAGE.md, which is the allowlist the adjacent label gate already uses. UNCLEAR
is counted and its reasons listed, never folded into a pass.

Usage
  python3 -I src/arm_header_attribution_check.py                  all rows
  python3 -I src/arm_header_attribution_check.py TRIAL_SUBSTRING  one trial
  python3 -I src/arm_header_attribution_check.py --evidence       print each candidate considered
  python3 -I src/arm_header_attribution_check.py --self-test      the synthetic cases, including
                                                                  the four artefacts above, then an
                                                                  injected swap on every real
                                                                  ALIGNED row
  exit 1 when a REVERSED row is not written up, or when the self test fails
"""
import csv
import importlib.util
import os
import re
import sys

ROOT = os.getcwd()


# Loaded by explicit file path, not by name: the chain runs python3 -I, which strips the script's
# own directory from sys.path on purpose. Putting that directory back would restore the shadowing
# risk -I exists to remove, so one named file is loaded instead.
def _load(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_arm = _load("arm_attribution_check")
_prov = _load("source_provenance")

# What a row is, what an arm name reduces to, and which rows are in scope are the adjacent label
# gate's definitions. This gate differs from it in the attribution rule and the value locator only.
st = _arm.st
arm_names = _arm.arm_names
in_scope = _arm.in_scope
# The numeric locator lives in the adjacent label gate and is imported here. It was written in this
# file on 22 October, because that gate located a value as a string and the string locator cannot
# serve this rule; the two were merged the same day, in that gate, where both now use it.
numbers = _arm.numbers
as_float = _arm.as_float
TOL = _arm.TOL
SESSION_CLASSES = _prov.SESSION
INDEPENDENT_CLASSES = _prov.INDEPENDENT

MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
TRIAGE = os.path.join(ROOT, "docs", "ARM_ATTRIBUTION_TRIAGE.md")
PROVENANCE = os.path.join(ROOT, "analysis", "data", "source_provenance.csv")

HEADER_LOOKBACK = 25     # lines above the value line; the reach the triage document measured
CLUSTER_GAP = 12         # matches for one arm further apart than this are separate mentions

# The reason string the adjacent label gate returns for the rows this gate exists to reach. It is
# compared rather than reimplemented, so that a change to that gate's wording shows up here as an
# empty scope rather than as a silently different one.
BLIND_SPOT = "an arm name does not precede its value on the line"


# What makes a number part of another number's cell rather than a column of its own: a dispersion
# after a plus or minus sign, a count or an interval in brackets, a p value, an n, a percentage
# after a comma. A number with none of these in front of it is a column.
ATTACHED = re.compile(
    r"(?:±|\+/-|plus or minus|[(\[]|=|<|>|\bn\s*|\bSD\b|\bSE\b|\bCI\b|,)\s*$", re.I)


def mentions(line, toks):
    """Positions at which any of an arm's tokens appears on a line, in order."""
    low = line.lower()
    out = []
    for t in toks:
        out += [m.start() for m in re.finditer(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low)]
    return sorted(out)


def single_mention(pos):
    """
    True when a side's matches form ONE mention rather than several columns.

    Clustered rather than spanned, because an arm written `insulin glargine` matches twice inside
    one mention while `Exenatide 2 mg, Exenatide 5 mg` matches twice in two columns, and a span test
    wide enough to admit the first admits the second. The gap is measured between the starts of
    consecutive matches, so it is the longest arm word that a single name may carry.
    """
    if not pos:
        return False
    clusters = 1
    for a, b in zip(pos, pos[1:]):
        if b - a > CLUSTER_GAP:
            clusters += 1
    return clusters == 1


def field_spans(line):
    """
    The line's columns as (start, end), split on the delimiter it actually uses.

    Tab first, then pipe, then a run of two or more spaces, which is the order of how reliably each
    marks a column in these captures. Empty fields are dropped: a tab separated header often holds
    several tabs between labels, and a column that holds nothing is not a column.
    """
    if "\t" in line:
        sep = re.compile(r"\t")
    elif "|" in line:
        sep = re.compile(r"\|")
    else:
        sep = re.compile(r" {2,}")
    out, at = [], 0
    for m in sep.finditer(line):
        if line[at:m.start()].strip():
            out.append((at, m.start()))
        at = m.end()
    if line[at:].strip():
        out.append((at, len(line)))
    return out


def field_of(spans, pos):
    for k, (a, b) in enumerate(spans):
        if a <= pos < b:
            return k
    return None


def columnar(line, pd, pc):
    """True when the line is a row of column labels naming the two arms in different columns."""
    spans = field_spans(line)
    if len(spans) < 2:
        return False
    fd, fc = field_of(spans, pd), field_of(spans, pc)
    return fd is not None and fc is not None and fd != fc


def bare(line, at):
    """True when the number at this position is a column value rather than part of another cell."""
    return not ATTACHED.search(line[max(0, at - 20):at])


def adjacent(line, nums, i, j):
    """
    True when the two matched values are adjacent arm columns.

    Both ends must be column values, and every numeric token between them must be attached to a
    value rather than standing alone.

    The ends are tested because a row's value can coincide with a dispersion somewhere else in the
    table. The Light On LDL row records a change of -0.01 against 0.2, and on the HDL line below it
    the number 0.2 is the standard deviation of the liraglutide baseline, printed immediately
    before the HDL change of -0.01. Nothing stands between them, the pair reads as two adjacent
    columns in the wrong order, and the first version of this gate reported the row as a swapped
    arm on that evidence.

    A bare number BETWEEN them is a third column, and no order rule can say which column either of
    the two matched values came from. That is the Light On three arm table.
    """
    lo, hi = (i, j) if i < j else (j, i)
    if not bare(line, nums[lo][0]) or not bare(line, nums[hi][0]):
        return False
    for k in range(lo + 1, hi):
        if bare(line, nums[k][0]):
            return False
    return True


def header_above(lines, idx, tx, ct, drug, comp, two_field_values):
    """
    The nearest header above idx, as (index, line, drug pos, comp pos, why).

    A line carrying either of the two values is another value line, not a header. A line that names
    an arm more than once is a column list, which the order rule cannot read. A line that is not a
    row of column labels is prose, and is admitted only where the value line has exactly two
    fields, the case in which no column can be mistaken for another.
    """
    for k in range(idx - 1, max(-1, idx - 1 - HEADER_LOOKBACK), -1):
        ln = lines[k]
        if not ln.strip():
            continue
        vals = [v for _, v in numbers(ln)]
        if any(abs(v - tx) <= TOL for v in vals) or any(abs(v - ct) <= TOL for v in vals):
            continue
        pd, pc = mentions(ln, drug), mentions(ln, comp)
        if not pd or not pc:
            continue
        if not single_mention(pd) or not single_mention(pc):
            return None, None, None, None, \
                "the nearest line naming both arms names one of them more than once"
        if not columnar(ln, pd[0], pc[0]) and not two_field_values:
            return None, None, None, None, \
                "the nearest line naming both arms is prose, not a row of column labels"
        return k, ln, pd[0], pc[0], ""
    return None, None, None, None, (
        f"no header naming both arms within {HEADER_LOOKBACK} lines above the values")


def candidates(blocks, tx, ct, drug, comp):
    """
    Every attribution the sources support, as a list of (verdict, path, detail).

    One entry per line that carries both values as adjacent columns under a readable header. The
    caller requires them to agree.
    """
    out, refused = [], {}
    for path, lines in blocks:
        for idx, ln in enumerate(lines):
            nums = numbers(ln)
            hit_tx = [k for k, (_, v) in enumerate(nums) if abs(v - tx) <= TOL]
            hit_ct = [k for k, (_, v) in enumerate(nums) if abs(v - ct) <= TOL]
            if not hit_tx or not hit_ct:
                continue
            # Reported in two stages so that the reason a row is out of reach is the real one. A
            # value that coincides with a dispersion elsewhere in the table and a value separated
            # from its pair by a third arm's column are different findings about the source.
            ends = [(i, j) for i in hit_tx for j in hit_ct
                    if bare(ln, nums[i][0]) and bare(ln, nums[j][0])]
            if not ends:
                refused["a matched value is a dispersion or a count, not a column value"] = 1
                continue
            pairs = [(i, j) for i, j in ends if adjacent(ln, nums, i, j)]
            if not pairs:
                refused["the two values are not adjacent columns on any line that carries both"] = 1
                continue
            k, hdr, pd, pc, why = header_above(lines, idx, tx, ct, drug, comp,
                                               len(field_spans(ln)) == 2)
            if k is None:
                refused[why] = 1
                continue
            ev = " ".join(hdr.split())
            detail = f"header -{idx - k} line(s): {ev}"
            for i, j in pairs:
                drug_first = pd < pc
                tx_first = nums[i][0] < nums[j][0]
                out.append(("ALIGNED" if drug_first == tx_first else "REVERSED", path, detail))
    return out, refused


def classify(r, blocks):
    """Return (verdict, detail, path). Verdicts: ALIGNED, REVERSED, UNCLEAR."""
    tx, ct = as_float(st(r, "mean_tx")), as_float(st(r, "mean_ctrl"))
    if tx is None or ct is None:
        return "UNCLEAR", "an arm value is absent or not numeric", ""
    if abs(tx - ct) <= TOL:
        return "UNCLEAR", "the two arms print the same value, so no attribution is possible", ""
    drug, comp, why = arm_names(r)
    if why:
        return "UNCLEAR", why, ""
    found, refused = candidates(blocks, tx, ct, drug, comp)
    if not found:
        if refused:
            return "UNCLEAR", sorted(refused)[0], ""
        return "UNCLEAR", "no line carries both arm values", ""
    verdicts = {v for v, _, _ in found}
    if len(verdicts) > 1:
        return ("UNCLEAR",
                f"{len(found)} candidate attribution(s) disagree, so the attribution is ambiguous",
                found[0][1])
    v, path, detail = found[0]
    return v, detail, path


def provenance():
    """path -> provenance class, from the registry rather than a second classifier here."""
    out = {}
    if not os.path.exists(PROVENANCE):
        return out
    with open(PROVENANCE, newline="") as fh:
        for r in csv.DictReader(fh):
            out[(r.get("path") or "").strip()] = (r.get("provenance_class") or "").strip()
    return out


def evidence_kind(cls):
    if cls in INDEPENDENT_CLASSES:
        return "independent"
    if cls in SESSION_CLASSES:
        return "session"
    return "unclassified"


def self_test(rows, blocks_for):
    """
    The synthetic cases first, then an injected swap on every real ALIGNED row.

    The synthetic cases are the pattern the triage document quotes, Davies 2013, and the four
    artefacts the first run over the real corpus produced. Without them the only demonstration
    would be the swap, and a swap flips the order by construction, so it proves the implementation
    and not the rule.
    """
    bad = []
    hdr = "Outcome measures, exenatide once weekly against insulin detemir, baseline to week 26"
    vals = "-1.32 (0.076), n 95 | -0.91 (0.077), n 96   [mixed models analysis]"
    row = {"drug": "exenatide once weekly", "comparator": "insulin detemir",
           "mean_tx": "-1.32", "mean_ctrl": "-0.91", "yi_reported": "NA",
           "trial_id": "SELF-TEST", "biomarker": "HbA1c", "notes": ""}
    three_arm = ("MRI-PDFF\t15.4% ± 5.6%\t12.5% ± 6.4%\t-4.0% ± 4.5%\t"
                 "15.5% ± 5.6%\t11.7% ± 5.0%\t-3.8% ± 5.0%\t"
                 "14.9% ± 5.5%\t14.1% ± 7.3%\t-0.8% ± 5.3%")
    three_hdr = "Characteristic\tLiraglutide (n = 24)\tSitagliptin (n = 27)\tInsulin glargine (n = 24)"
    lo_row = {"drug": "liraglutide", "comparator": "insulin glargine titrated",
              "mean_tx": "-4", "mean_ctrl": "-0.8", "yi_reported": "NA",
              "trial_id": "SELF-TEST", "biomarker": "liver_fat_pdff", "notes": ""}
    kelly_row = {"drug": "exenatide", "comparator": "metformin",
                 "mean_tx": "-12.0", "mean_ctrl": "-3.0", "yi_reported": "NA",
                 "trial_id": "SELF-TEST", "biomarker": "TG", "notes": ""}

    cases = [
        ("the header's order attributes the values",
         [("t.txt", [hdr, vals])], row, "ALIGNED"),
        ("a swapped pair reads REVERSED",
         [("t.txt", [hdr, vals])], dict(row, mean_tx="-0.91", mean_ctrl="-1.32"), "REVERSED"),
        ("a header naming an arm twice is refused",
         [("t.txt", ["exenatide 2 mg, exenatide 5 mg, and insulin detemir", vals])],
         row, "UNCLEAR"),
        ("a header beyond the measured reach is refused",
         [("t.txt", [hdr] + ["filler"] * (HEADER_LOOKBACK + 1) + [vals])], row, "UNCLEAR"),
        ("a value line is never read as a header",
         [("t.txt", [hdr, vals, "-1.32 (0.076), n 95 | -0.91 (0.077), n 96"])], row, "ALIGNED"),
        # The four artefacts of the first run, in the order the docstring names them.
        # The row's treatment value is -4 and the line prints 4.5 as a dispersion. The adjacent
        # label gate's unsigned fallback matches the 4 inside 4.5 by its own standalone test; a
        # numeric token cannot.
        ("an unsigned digit inside another number is not a match",
         [("t.txt", ["Characteristic\tLiraglutide (n = 24)\tInsulin glargine (n = 24)",
                     "MRI-PDFF\t-4.0 ± 4.5\t-0.8 ± 5.3"])],
         lo_row, "ALIGNED"),
        ("a third arm's values between the two refuse the row",
         [("t.txt", [three_hdr, three_arm])], lo_row, "UNCLEAR"),
        ("a prose sentence naming both arms is not a header",
         [("t.txt", ["75 patients with type 2 diabetes and fatty liver were randomized (1:1:1) "
                     "to add on liraglutide, sitagliptin, or insulin glargine in this 26 week trial",
                     "change -4.0 ± 4.5 against -0.8 ± 5.3"])],
         lo_row, "UNCLEAR"),
        ("a value matching a dispersion is not a column value",
         [("t.txt", ["Characteristic\tLiraglutide (n = 24)\tInsulin glargine (n = 24)",
                     "HDL-C (mmol/L)\t1.1 ± 0.2\t1.1 ± 0.2\t-0.01 ± 0.1"])],
         lo_row, "UNCLEAR"),
        ("a tab delimited header attributes by column, in either order",
         [("t.txt", ["Variable\tΔ Metformin(N = 25)\tΔ Exenatide(N = 25)\tDifference\tP",
                     "TG (mg/dL)\t-3.0\t-12.0\t-9.0\t0.04"])], kelly_row, "ALIGNED"),
        ("a sentence naming both arms above a multi column line is not a header",
         [("t.txt", ["Body fat data were obtained in 35 patients "
                     "(exenatide N = 17; metformin N = 18)",
                     "TG (mg/dL)\t-3.0\t-12.0\t-9.0\t0.04"])], kelly_row, "UNCLEAR"),
        ("two candidate lines that disagree refuse the row",
         [("t.txt", [hdr, vals, "", hdr, "-0.91 (0.077), n 96 | -1.32 (0.076), n 95"])],
         row, "UNCLEAR"),
    ]
    for label, blocks, rr, want in cases:
        got, detail, _ = classify(rr, blocks)
        print(f"  {'ok  ' if got == want else 'FAIL'} {label}: {got}")
        if got != want:
            bad.append(f"{label}: expected {want}, got {got} ({detail})")

    aligned = [r for r in rows if in_scope(r)
               and classify(r, blocks_for(r["trial_id"], st(r, "notes")))[0] == "ALIGNED"]
    flipped, stuck = 0, []
    for r in aligned:
        m = dict(r)
        m["mean_tx"], m["mean_ctrl"] = st(r, "mean_ctrl"), st(r, "mean_tx")
        v = classify(m, blocks_for(r["trial_id"], st(r, "notes")))[0]
        if v == "REVERSED":
            flipped += 1
        else:
            stuck.append(f"{r['trial_id'][:34]} {r['biomarker']} swapped reads {v}, not REVERSED")
    print(f"  {len(aligned)} real ALIGNED row(s); an injected swap is detected on {flipped}")
    for s in stuck:
        bad.append(s)
        print("  FAIL " + s)
    return not bad


def main(argv):
    selftest = "--self-test" in argv
    show = "--evidence" in argv
    argv = [a for a in argv if not a.startswith("--")]
    want = argv[0].lower() if argv else None

    lines_for = _arm.make_source_lines()
    if not hasattr(lines_for, "blocks_for"):
        print("FAIL the source reader does not expose blocks_for, so a header cannot be located "
              "without reading across file boundaries")
        sys.exit(1)
    blocks_for = lines_for.blocks_for

    rows = list(csv.DictReader(open(MASTER, newline="")))
    if want:
        rows = [r for r in rows if want in r["trial_id"].lower()]

    # Scope: the derived rows the adjacent label gate reports as unclassifiable because no arm name
    # precedes the value. Taking that gate's own verdict, rather than re-deriving the condition,
    # is what keeps the two scopes complementary instead of merely similar.
    scope, out_of_scope = [], 0
    for r in rows:
        if not in_scope(r):
            continue
        lines = lines_for(r["trial_id"], st(r, "notes"))
        if not lines:
            continue
        v, detail = _arm.classify(r, lines)
        if v == "UNCLEAR" and detail == BLIND_SPOT:
            scope.append(r)
        else:
            out_of_scope += 1

    prov = provenance()
    counts = {}
    reasons, reversed_rows, aligned_rows = {}, [], []
    for r in scope:
        blocks = blocks_for(r["trial_id"], st(r, "notes"))
        v, detail, path = classify(r, blocks)
        kind = evidence_kind(prov.get(path, "")) if path else "unlocated"
        counts[(v, kind)] = counts.get((v, kind), 0) + 1
        if v == "REVERSED":
            reversed_rows.append((r["trial_id"], r["biomarker"], kind, detail))
        elif v == "ALIGNED":
            aligned_rows.append((r["trial_id"], r["biomarker"], kind, detail))
        else:
            reasons[detail] = reasons.get(detail, 0) + 1

    done = _arm.triaged()
    untriaged = [x for x in reversed_rows if (x[0], x[1]) not in done]

    print(f"header order attribution over {len(rows)} row(s); {len(scope)} in scope (derived, and "
          f"no arm name precedes the value), {out_of_scope} derived row(s) out of scope")
    kinds = ["independent", "session", "unclassified", "unlocated"]
    print(f"  {'verdict':10} " + " ".join(f"{k:>13}" for k in kinds) + f" {'total':>7}")
    for v in ("ALIGNED", "REVERSED", "UNCLEAR"):
        row_counts = [counts.get((v, k), 0) for k in kinds]
        print(f"  {v:10} " + " ".join(f"{n:>13}" for n in row_counts) + f" {sum(row_counts):>7}")
    print("\n  independent: the header is the publisher's or the indexer's own text, so agreement\n"
          "  verifies the extraction against the source. session: the header is a caption this\n"
          "  review wrote, so agreement establishes only that the extraction matches the capture.")

    if reversed_rows:
        print("\nREVERSED rows: the header names the arms in the opposite order to this row's "
              "values")
        for t, b, kind, d in reversed_rows:
            tag = "triaged  " if (t, b) in done else "UNTRIAGED"
            print(f"  {tag} {t[:34]:36} {b:18} {kind:12} {d}")
    if reasons:
        print("\nWhy the rest are unclassifiable, which is where this gate's reach ends")
        for d, n in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {n:4}  {d}")
    if aligned_rows and show:
        print("\nALIGNED rows, with the header that attributes them")
        for t, b, kind, d in aligned_rows:
            print(f"        {t[:34]:36} {b:18} {kind:12} {d}")
    elif aligned_rows:
        print(f"\n{len(aligned_rows)} ALIGNED row(s); --evidence prints the header behind each")

    bad = False
    if selftest:
        print("\nself test")
        bad = not self_test(rows, blocks_for)
    sys.exit(1 if (untriaged or bad) else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
