#!/usr/bin/env python3
"""
timepoint_check.py

Twenty fifth gate. Asks, for every row the review records as the trial's prespecified endpoint,
whether the timepoint it was read at is the timepoint the trial REGISTERED as its primary endpoint.

WHY THIS MATTERS AND WHAT IT IS NOT. A biomarker read at week 24 in a trial whose primary endpoint is
week 48 is not an error: most of this corpus's markers are secondary outcomes reported at whatever
visit the paper chose. So an unflagged row carries no expectation and this gate returns no verdict on
it. The rows that do carry one are the 161 the extraction marks `prespecified_endpoint`. A reader of
the manuscript who sees that label will take it to mean the endpoint the trial was designed around,
and where the registry says otherwise the difference belongs in the record rather than in a reader's
assumption.

SCOPE AND WHY IT IS AS LARGE AS IT IS. Version 1.1 of the chain document listed this candidate as
"stands, unmeasured" and warned it was the more fragile of the two remaining, because it needs
registry retrieval. The reach was then measured, and the measurement is recorded in
docs/TIMEPOINT_TRIAGE.md. The first measurement gave 5 rows of 524 and was wrong in the way this
chain has learned to distrust: 38 registry records were on disk, retrieved during screening, and
exactly one of them was for an included trial. Retrieving the records of the corpus itself, which is
src/corpus_registry_harvest.py, took the comparable set to 291 rows of 524, of which 161 carry the
prespecified flag. A reach measured against what happened to have been retrieved is not a reach.

HOW A TIME FRAME IS READ, and the distinction the measurement forced. ClinicalTrials.gov states a
primary outcome's time frame as free text. Two shapes occur here and they mean different things:

  a point     "48 weeks", "Week 26", "6 months". The row's timepoint should equal it
  a window    "Baseline to end of Period II (up to 4.5 years)", "through week 72". The row's
              timepoint should fall inside it

Treating a window as a point produced six of the first ten findings: the six EUREXA rows were read at
36 months inside a window stated as up to 4.5 years, and were reported as disagreeing with it. A rule
that cannot tell a deadline from a visit is not reading the registry, it is reading numbers out of
it.

VERDICTS

  MATCHES         the row's timepoint equals a registered primary time point, within TOL weeks, or
                  falls inside a registered window
  OUTSIDE         the row is flagged as the trial's prespecified endpoint and its timepoint is
                  neither. Fails the chain unless written up in docs/TIMEPOINT_TRIAGE.md
  CONTEXT         the row is not flagged, so no expectation applies. Counted, never a verdict
  UNREACHABLE     no timepoint on the row, no registry identifier for the trial, no retained record,
                  or no time frame that parses. Counted with the reason

WHAT A GREEN RESULT IS WORTH. The comparison is against the registry, which is independent of both
the paper and this review, so an agreement is evidence that the row was read at the endpoint the
trial declared. It says nothing about whether the VALUE at that timepoint was read correctly, which
is what gates nine to twenty four are for.

Usage
  python3 -I src/timepoint_check.py                  all rows
  python3 -I src/timepoint_check.py TRIAL_SUBSTRING  one trial
  python3 -I src/timepoint_check.py --self-test      shift the timepoint of every MATCHES row and
                                                     require the verdict to change
  exit 1 when an OUTSIDE row is not written up, or when the self test fails
"""
import collections
import csv
import importlib.util
import json
import os
import re
import sys

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
TRIAGE = os.path.join(ROOT, "docs", "TIMEPOINT_TRIAGE.md")
REG = os.path.join(ROOT, "work", "fulltext", "registry_corpus")

TOL = 1.0          # weeks. A registry stating 6 months and a paper stating 26 weeks agree
WINDOW_SLACK = 1.0  # weeks past a window's end still counts as inside it


def _load(name):
    """Load a sibling script by explicit path: the chain runs python3 -I."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The trial to registry identifier mapping is the harvester's, not a second copy of it.
_harvest = _load("corpus_registry_harvest")
resolve = _harvest.resolve

MONTH = 365.25 / 12 / 7
YEAR = 365.25 / 7
UNIT = {"week": 1.0, "weeks": 1.0, "wk": 1.0, "wks": 1.0,
        "month": MONTH, "months": MONTH, "mo": MONTH,
        "year": YEAR, "years": YEAR, "day": 1 / 7, "days": 1 / 7}
# A time frame using one of these says when something ENDS, not when it was measured.
WINDOW = re.compile(r"\b(up to|through|until|over|during|within|by week|by month|end of)\b", re.I)


def quantities(text):
    """Every duration a time frame states, in weeks."""
    out, t = [], (text or "").lower()
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(weeks?|wks?|months?|mo|years?|days?)\b", t):
        out.append(float(m.group(1)) * UNIT[m.group(2)])
    for m in re.finditer(r"\b(weeks?|months?|years?|days?)\s*(\d+(?:\.\d+)?)\b", t):
        out.append(float(m.group(2)) * UNIT[m.group(1)])
    return sorted(set(round(v, 2) for v in out))


def read_time_frame(text):
    """
    Return (points, windows) in weeks: visits the row should match, and ends it should fall within.

    A phrase marking a deadline makes every quantity in the same time frame a window end. Mixing
    the two inside one string is not worth guessing at, and the conservative reading is the window,
    which accepts more and therefore reports less.
    """
    q = quantities(text)
    if not q:
        return [], []
    if WINDOW.search(text or ""):
        return [], [max(q)]
    return q, []


def frames_for(path):
    """(points, windows, raw strings) over every primary outcome of a registry record."""
    d = json.load(open(path))
    po = (d.get("protocolSection", {}).get("outcomesModule", {}) or {}).get("primaryOutcomes", [])
    points, windows, raw = [], [], []
    for o in po:
        tf = o.get("timeFrame") or ""
        raw.append(tf.replace("\n", " ").strip())
        p, w = read_time_frame(tf)
        points += p
        windows += w
    return sorted(set(points)), sorted(set(windows)), raw


def records():
    out = {}
    if not os.path.isdir(REG):
        return out
    for name in sorted(os.listdir(REG)):
        m = re.fullmatch(r"(NCT\d{8})\.json", name)
        if m:
            out[m.group(1)] = os.path.join(REG, name)
    return out


def classify(weeks, flagged, points, windows):
    """Return (verdict, detail)."""
    if any(abs(weeks - p) <= TOL for p in points):
        return "MATCHES", f"registered primary endpoint at {points}"
    if any(weeks <= w + WINDOW_SLACK for w in windows):
        return "MATCHES", f"inside a registered window ending at {windows}"
    if not flagged:
        return "CONTEXT", f"not flagged as the prespecified endpoint; registered {points or windows}"
    return "OUTSIDE", f"row at {weeks} weeks against registered {points or windows}"


def triaged():
    """(trial, marker) pairs written up in the triage document."""
    out = set()
    if not os.path.exists(TRIAGE):
        return out
    for ln in open(TRIAGE, errors="replace"):
        m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z0-9_]+)\s*\|", ln)
        if m and m.group(2).lower() not in ("marker", "rows"):
            out.add((m.group(1).strip(), m.group(2).strip()))
    return out


def rows_in_scope(rows, source, reg):
    """Yield (row, verdict, detail) for every row, with UNREACHABLE reasons included."""
    for r in rows:
        tp = (r.get("assessment_timepoint_weeks") or "").strip()
        flagged = (r.get("prespecified_endpoint") or "").strip().upper() == "TRUE"
        if tp in ("", "NA"):
            yield r, "UNREACHABLE", "no timepoint recorded on the row"
            continue
        try:
            weeks = float(tp)
        except ValueError:
            yield r, "UNREACHABLE", f"the row's timepoint {tp!r} is not a number of weeks"
            continue
        ids = [i for i in source.get(r["trial_id"], ("none", []))[1] if i in reg]
        if not source.get(r["trial_id"], ("none", []))[1]:
            yield r, "UNREACHABLE", "no registry identifier for the trial"
            continue
        if not ids:
            yield r, "UNREACHABLE", "registry identifier known, no record retained"
            continue
        points, windows, raw = frames_for(reg[ids[0]])
        if not raw:
            yield r, "UNREACHABLE", "the registry record states no primary outcome"
            continue
        if not points and not windows:
            yield r, "UNREACHABLE", f"no primary time frame parses to weeks: {raw[:1]}"
            continue
        v, d = classify(weeks, flagged, points, windows)
        yield r, v, d


def self_test(rows, source, reg):
    """
    Shift the timepoint of every MATCHES row and require the verdict to stop being MATCHES.

    Two synthetic cases first, because the window rule is the part a reader will doubt and the part
    that produced six false findings before it existed.
    """
    bad = []
    cases = [
        ("a point time frame accepts its own visit", 48.0, True, ["48 weeks"], "MATCHES"),
        ("a point time frame rejects another visit", 24.0, True, ["48 weeks"], "OUTSIDE"),
        ("a window accepts a visit inside it", 156.0, True,
         ["Baseline to end of Period II (up to 4.5 years)"], "MATCHES"),
        ("a window rejects a visit beyond it", 300.0, True,
         ["Baseline to end of Period II (up to 4.5 years)"], "OUTSIDE"),
        ("months and weeks are the same scale", 26.0, True, ["6 months"], "MATCHES"),
        ("an unflagged row gets no verdict", 24.0, False, ["48 weeks"], "CONTEXT"),
    ]
    for label, weeks, flagged, raw, want in cases:
        points, windows = [], []
        for tf in raw:
            p, w = read_time_frame(tf)
            points += p
            windows += w
        got, detail = classify(weeks, flagged, sorted(set(points)), sorted(set(windows)))
        print(f"  {'ok  ' if got == want else 'FAIL'} {label}: {got}")
        if got != want:
            bad.append(f"{label}: expected {want}, got {got} ({detail})")

    shifted = 0
    stuck = []
    for r, v, _ in rows_in_scope(rows, source, reg):
        if v != "MATCHES":
            continue
        m = dict(r)
        m["assessment_timepoint_weeks"] = str(float(r["assessment_timepoint_weeks"]) + 500)
        for _, v2, _d in rows_in_scope([m], source, reg):
            if v2 == "MATCHES":
                stuck.append(f"{r['trial_id'][:34]} {r['biomarker']} still MATCHES 500 weeks later")
            else:
                shifted += 1
    print(f"  {shifted} MATCHES row(s) stop matching when shifted 500 weeks; {len(stuck)} do not")
    for s in stuck[:10]:
        bad.append(s)
        print("  FAIL " + s)
    # Without the registry records every row is UNREACHABLE, there is no MATCHES row to shift, and
    # the demonstration above passes by having nothing to do. That is the vacuous green this chain's
    # design rule exists to prevent, so the absence of the records is a failure of the self test
    # rather than a quiet success, and it names the command that fixes it.
    if shifted == 0:
        bad.append("no row reached a verdict, so nothing was demonstrated")
        print("  FAIL no MATCHES row to shift. The registry records this gate reads are retrieved "
              "into\n       work/fulltext/registry_corpus/, which is gitignored. Run\n"
              "       python3 -I src/corpus_registry_harvest.py")
    return not bad


def main(argv):
    selftest = "--self-test" in argv
    argv = [a for a in argv if not a.startswith("--")]
    want = argv[0].lower() if argv else None

    rows = list(csv.DictReader(open(MASTER, newline="")))
    if want:
        rows = [r for r in rows if want in r["trial_id"].lower()]
    source = resolve()
    reg = records()

    counts = collections.Counter()
    reasons = collections.Counter()
    outside, context_miss = [], collections.Counter()
    for r, v, d in rows_in_scope(rows, source, reg):
        counts[v] += 1
        if v == "UNREACHABLE":
            reasons[d.split(":")[0]] += 1
        elif v == "OUTSIDE":
            outside.append((r["trial_id"], r["biomarker"], d))
        elif v == "CONTEXT":
            context_miss["registered elsewhere" if "registered" in d else "other"] += 1

    done = triaged()
    untriaged = [x for x in outside if (x[0], x[1]) not in done]

    print(f"timepoint check over {len(rows)} row(s); {len(reg)} registry record(s) retained")
    for v in ("MATCHES", "OUTSIDE", "CONTEXT", "UNREACHABLE"):
        print(f"  {v:12} {counts[v]}")
    print("\n  MATCHES and OUTSIDE are the rows the review marks as the trial's prespecified\n"
          "  endpoint, plus the unflagged rows that happen to sit at the registered one. CONTEXT\n"
          "  rows are unflagged and carry no expectation, so no verdict is returned on them.")

    if outside:
        print("\nOUTSIDE rows: flagged as the prespecified endpoint, read at another timepoint")
        for t, b, d in outside:
            tag = "triaged  " if (t, b) in done else "UNTRIAGED"
            print(f"  {tag} {t[:34]:36} {b:18} {d}")
    if reasons:
        print("\nWhy a row is unreachable, which is where this gate's reach ends")
        for d, n in reasons.most_common():
            print(f"  {n:4}  {d}")

    bad = False
    if selftest:
        print("\nself test")
        bad = not self_test(rows, source, reg)
    sys.exit(1 if (untriaged or bad) else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
