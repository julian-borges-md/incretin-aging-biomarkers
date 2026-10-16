#!/usr/bin/env python3
"""
arm_attribution_check.py

Fifth provenance gate, and the one that reaches the hole gate fourteen cannot. Gate fourteen checks
a row's arms against its reported effect, which works only where the paper printed both. On the 122
rows whose effect was DERIVED from the arm values there is nothing to check it against: a swapped arm
flips the derived effect too, so the two agree by construction.

The gate chain document named a different candidate for this hole, a sign check between a row's
direction and the direction its source states in words. That candidate is struck, for a structural
reason found by probing the sources rather than by argument: a derived row exists precisely because
the paper never computed the between group contrast, so its text cannot state that contrast's sign.
What the text does state, abundantly, is the direction of each ARM's own change, and a direction word
about one arm says nothing about the sign of a difference between two arms. Of eight derived rows
probed, seven had a sentence pairing the marker with a direction word and not one of those sentences
was about the contrast; the closest, "HbA1c was significantly reduced to a similar extent among three
groups", is a statement about magnitude.

What this does instead. Narrative sources name each arm immediately before its value, as in
"exenatide delta = -62 +/- 19 %, P = 0.012; insulin delta = -60 +/- 17 %". That is direct evidence of
which arm a number belongs to, and it is present on one line for 100 of the 122 derived rows. So, per
row:
  1. find the source lines that carry both of the row's arm values as standalone numbers
  2. keep the line on which the two sit closest together, and only if they sit closer than MAX_SPAN
     characters, because two numbers far apart in a long abstract paragraph co-occur by accident
  3. for each of the two values, find the nearest arm name to its LEFT within LOOKBACK characters,
     which is the arm the source attributes that value to
  4. classify
       ALIGNED    the treatment value is preceded by the drug's name and the control value by the
                  comparator's
       REVERSED   the opposite, which is a swapped arm in the extraction
       UNCLEAR    one or both values have no arm name in front of them, the two arms cannot be told
                  apart by name, or the two values never share a line

Only REVERSED fails the chain, and only when it is not written up in docs/ARM_ATTRIBUTION_TRIAGE.md.
UNCLEAR is counted and listed, never silently folded into a pass; it is the honest majority verdict
on table captures, where the column header rather than an adjacent label carries the attribution.

Name handling. The drug and comparator strings are tokenised to alphabetic tokens of four or more
characters, lowercased, with parentheticals and dose and schedule words removed. Any token the two
arms share disqualifies the row, because a trial of insulin degludec with liraglutide against insulin
degludec cannot be told apart by the word "insulin". Guarding this is the difference between a gate
and a coin toss.

The source locator is imported from the attachment check rather than copied. A second copy of it is
the defect that has bitten this chain twice already.

Usage
  python3 -I src/arm_attribution_check.py                  all rows
  python3 -I src/arm_attribution_check.py TRIAL_SUBSTRING  one trial
  python3 -I src/arm_attribution_check.py --self-test      swap the arms, prove the verdict flips
  exit 1 when a REVERSED row is not written up, or when the self test fails
"""
import csv
import os
import re
import sys

import importlib.util

ROOT = os.getcwd()

# The attachment check is loaded by explicit file path rather than by name. The whole chain runs
# python3 -I, which strips the script's own directory from sys.path on purpose, so a plain import
# fails; putting that directory back would restore exactly the shadowing risk -I exists to remove.
# Loading one named file is narrower than widening the path: it resolves to this file and no other.
def _load(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_attach = _load("extraction_attachment_check")
make_source_lines = _attach.make_source_lines
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
TRIAGE = os.path.join(ROOT, "docs", "ARM_ATTRIBUTION_TRIAGE.md")

MAX_SPAN = 200     # characters between the two arm values on the chosen line
LOOKBACK = 70      # characters to the left of a value in which its arm name must appear
MIN_TOKEN = 4      # shorter tokens match too much ("mix", "ins", "mg")

# Dose, schedule and boilerplate words that name no arm. A token here can never attribute a value.
STOP = {
    "once", "twice", "weekly", "daily", "titrated", "third", "entered", "arm", "arms", "dose",
    "doses", "versus", "plus", "with", "without", "standard", "usual", "care", "treatment",
    "control", "group", "groups", "oral", "subcutaneous", "injection", "high", "low",
    "comparator", "conventional", "therapy", "added", "background", "titration", "study", "trial",
    "mean", "change", "baseline", "week", "weeks", "month", "months", "year", "years", "both",
}


def st(r, k):
    return (r.get(k) or "").strip()


def tokens(name):
    """Arm name reduced to the words that can attribute a value to it."""
    name = re.sub(r"\([^)]*\)", " ", name or "").lower()
    return {t for t in re.findall(r"[a-z]+", name) if len(t) >= MIN_TOKEN and t not in STOP}


def arm_names(r):
    """
    Return (drug tokens, comparator tokens, reason) with the shared tokens removed.

    A trial of insulin degludec with liraglutide against insulin degludec alone shares the word
    insulin, and a gate that attributed a value to whichever arm the word insulin happened to
    precede would be guessing. Shared tokens are therefore dropped from both sides, and if that
    empties either side the row is unclassifiable rather than classified.
    """
    d, c = tokens(st(r, "drug")), tokens(st(r, "comparator"))
    shared = d & c
    d, c = d - shared, c - shared
    if not d:
        return d, c, "the drug name has no word the comparator does not also use"
    if not c:
        return d, c, "the comparator name has no word the drug does not also use"
    return d, c, ""


def positions(line, num):
    """Every standalone occurrence of a printed number on a line."""
    return [m.start() for m in re.finditer(r"(?<![\d.])" + re.escape(num) + r"(?![\d])", line)]


def owner(line, at, drug, comp):
    """
    Which arm the source attributes the value at this position to.

    The nearest arm name to the LEFT within LOOKBACK characters, because that is how these sentences
    are built: the arm is named and its number follows. Searching both directions would let the next
    clause's arm name claim this clause's value.
    """
    seg = line[max(0, at - LOOKBACK):at].lower()
    best, who = -1, None
    for name, tag in [(n, "tx") for n in drug] + [(n, "ctrl") for n in comp]:
        i = seg.rfind(name)
        if i > best:
            best, who = i, tag
    return who


def classify(r, lines):
    """Return (verdict, detail). Verdicts: ALIGNED, REVERSED, UNCLEAR."""
    tx, ct = st(r, "mean_tx").replace("−", "-"), st(r, "mean_ctrl").replace("−", "-")
    if tx in ("", "NA") or ct in ("", "NA"):
        return "UNCLEAR", "an arm value is absent"
    if tx.lstrip("+-") == ct.lstrip("+-"):
        return "UNCLEAR", "the two arms print the same value, so no attribution is possible"
    drug, comp, why = arm_names(r)
    if why:
        return "UNCLEAR", why
    best = None
    for ln in lines:
        p_tx = positions(ln, tx) or positions(ln, tx.lstrip("+-"))
        p_ct = positions(ln, ct) or positions(ln, ct.lstrip("+-"))
        if not p_tx or not p_ct:
            continue
        for a in p_tx:
            for b in p_ct:
                span = abs(a - b)
                if span <= MAX_SPAN and (best is None or span < best[0]):
                    best = (span, ln, a, b)
    if best is None:
        return "UNCLEAR", f"the two values never share a line within {MAX_SPAN} characters"
    _, ln, a, b = best
    who_tx, who_ct = owner(ln, a, drug, comp), owner(ln, b, drug, comp)
    if who_tx is None or who_ct is None:
        return "UNCLEAR", "an arm name does not precede its value on the line"
    # The evidence shown is the region around the two matches, not the head of the line. Captures
    # often hold an entire abstract as one line of 1800 characters, and printing its first 160
    # characters shows background prose next to a verdict drawn from text far to the right: reading
    # that display, the Dutour liver fat row looked like a false ALIGNED and was nearly discarded,
    # when the attribution was correct and only the audit line was wrong.
    lo, hi = max(0, min(a, b) - LOOKBACK), max(a, b) + 14
    ev = ("..." if lo else "") + " ".join(ln[lo:hi].split()) + ("..." if hi < len(ln) else "")
    if who_tx == "tx" and who_ct == "ctrl":
        return "ALIGNED", ev
    if who_tx == "ctrl" and who_ct == "tx":
        return "REVERSED", ev
    return "UNCLEAR", "both values are preceded by the same arm's name"


def triaged():
    if not os.path.exists(TRIAGE):
        return set()
    out = set()
    for ln in open(TRIAGE, errors="replace"):
        m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z0-9_]+)\s*\|", ln)
        if m and m.group(2).lower() != "marker":
            out.add((m.group(1).strip(), m.group(2).strip()))
    return out


def in_scope(r):
    """Derived rows: no reported effect, both arm values present. The hole gate fourteen leaves."""
    return st(r, "yi_reported") in ("", "NA") and st(r, "mean_tx") not in ("", "NA") \
        and st(r, "mean_ctrl") not in ("", "NA")


def self_test(rows, lines_for):
    """
    Swap the arms of every ALIGNED row and require the verdict to flip to REVERSED.

    This is the whole of the gate's claim: that it can tell the two arms apart on the evidence of the
    source. A gate that reports no REVERSED row has not shown that, and on a clean corpus silence is
    the expected result, so the demonstration has to be built in.
    """
    aligned = [r for r in rows if in_scope(r)
               and classify(r, lines_for(r["trial_id"], st(r, "notes")))[0] == "ALIGNED"]
    flipped, stuck = 0, []
    for r in aligned:
        m = dict(r)
        m["mean_tx"], m["mean_ctrl"] = st(r, "mean_ctrl"), st(r, "mean_tx")
        v = classify(m, lines_for(r["trial_id"], st(r, "notes")))[0]
        if v == "REVERSED":
            flipped += 1
        else:
            stuck.append(f"{r['trial_id'][:34]} {r['biomarker']} swapped reads {v}, not REVERSED")
    print(f"self test: {len(aligned)} ALIGNED row(s); an injected swap is detected on {flipped}")
    for s in stuck:
        print("  FAIL " + s)
    return not stuck and bool(aligned)


def main(argv):
    selftest = "--self-test" in argv
    argv = [a for a in argv if not a.startswith("--")]
    want = argv[0].lower() if argv else None
    lines_for = make_source_lines()
    rows = list(csv.DictReader(open(MASTER, newline="")))
    if want:
        rows = [r for r in rows if want in r["trial_id"].lower()]
    scope = [r for r in rows if in_scope(r)]
    counts = {"ALIGNED": 0, "REVERSED": 0, "UNCLEAR": 0}
    reasons, reversed_rows, aligned_rows = {}, [], []
    for r in scope:
        lines = lines_for(r["trial_id"], st(r, "notes"))
        v, detail = ("UNCLEAR", "no source text retained for this trial") if not lines \
            else classify(r, lines)
        counts[v] += 1
        if v == "REVERSED":
            reversed_rows.append((r["trial_id"], r["biomarker"], detail))
        elif v == "ALIGNED":
            aligned_rows.append((r["trial_id"], r["biomarker"], detail))
        else:
            reasons[detail] = reasons.get(detail, 0) + 1
    done = triaged()
    untriaged = [x for x in reversed_rows if (x[0], x[1]) not in done]
    print(f"arm attribution over {len(rows)} row(s), {len(scope)} in scope "
          f"(effect derived from the arm values)")
    for k in ("ALIGNED", "REVERSED", "UNCLEAR"):
        print(f"  {k:9} {counts[k]}")
    if reversed_rows:
        print("\nREVERSED rows: the source names the comparator in front of the value this row "
              "records as treatment")
        for t, b, d in reversed_rows:
            tag = "triaged  " if (t, b) in done else "UNTRIAGED"
            print(f"  {tag} {t[:34]:36} {b:18} {d}")
    if reasons:
        print("\nWhy the rest are unclassifiable, which is where this gate's reach ends")
        for d, n in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {n:4}  {d}")
    if aligned_rows:
        print("\nALIGNED rows, with the line that attributes them")
        for t, b, d in aligned_rows:
            print(f"        {t[:34]:36} {b:18} {d}")
    bad = False
    if selftest:
        print()
        bad = not self_test(rows, lines_for)
    sys.exit(1 if (untriaged or bad) else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
