#!/usr/bin/env python3
"""
duplicate_numbers_check.py

Fourth provenance gate: does the same contrast appear under two different trial identifiers? Two
papers reporting the same patients under different names is duplicate publication, and pooling both
counts those patients twice while shrinking the interval as though the evidence had doubled. This
corpus already holds one such case, found by reading: the post treatment ALT means of 39.82 and
51.48 U/L in a 2018 report are, to two decimals, the values an earlier paper reports for a different
drug in the same population, and whether the earlier trial's rows stay in the analysis is an open
Director decision. That case was found by eye. This gate looks for the rest.

Method
  For every row, build a numeric fingerprint from the values a paper would have to repeat for the
  duplication to be real: the effect and its interval, and the four arm values where they exist.
  Fingerprints are compared only BETWEEN different trial_id values, because the same trial legitimately
  repeats numbers across its own rows (a pooled arm, a second timepoint, a companion paper under the
  same trial id). A pair is reported when
     the two rows share the same biomarker, and
     at least two of their identifying numbers agree exactly as printed
  Exact agreement is the point: two trials of the same drug in the same population plausibly produce
  a mean of 5.6, and implausibly produce 39.82 and 51.48 together.

Severity
  HARD  three or more numbers agree, or two agree and both rows carry the same n per arm
  SOFT  two numbers agree

Nothing is corrected here, and a flagged pair is not by itself duplicate publication: a trial
reported under two identifiers in this corpus (a substudy with its own name, a registry entry and a
publication) will flag, and the triage document records which is which.

Usage
  python3 -I src/duplicate_numbers_check.py
  exit 1 when a HARD pair is not written up in docs/DUPLICATE_TRIAGE.md
"""
import collections
import csv
import itertools
import os
import re
import sys

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
TRIAGE = os.path.join(ROOT, "docs", "DUPLICATE_TRIAGE.md")
FINGERPRINT_COLS = ("yi_reported", "ci_lb_reported", "ci_ub_reported", "mean_tx", "mean_ctrl",
                    "sd_tx", "sd_ctrl", "base_mean_tx", "base_mean_ctrl",
                    "final_mean_tx", "final_mean_ctrl")


def tokens(row):
    """The row's identifying numbers, as printed, excluding values too common to identify."""
    out = set()
    for c in FINGERPRINT_COLS:
        v = (row.get(c) or "").strip().replace("−", "-").lstrip("+-")
        if v in ("", "NA"):
            continue
        if "." not in v:
            continue          # an integer repeats across unrelated trials
        if len(v.replace(".", "").lstrip("0")) < 2:
            continue          # one significant digit identifies nothing
        out.add(v)
    return out


def triaged_pairs():
    if not os.path.exists(TRIAGE):
        return set()
    out = set()
    for ln in open(TRIAGE, errors="replace"):
        m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z0-9_]+)\s*\|", ln)
        if m and m.group(3).lower() != "marker":
            a, b, mk = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            out.add((a, b, mk))
            out.add((b, a, mk))
    return out


def find_pairs(rows):
    """Return (hard, soft), each a list of (trial_a, trial_b, marker, shared values, same n).

    Extracted from main on 2026-10-19 so that the detection can be run on injected rows. A gate that
    has reported nothing on every run has not thereby shown that it works, and this one has reported
    no HARD pair since it was written; the self test below puts the defect in front of it, including
    the real case that was found by reading rather than by this gate.
    """
    by_marker = collections.defaultdict(list)
    for r in rows:
        by_marker[r["biomarker"]].append(r)
    hard, soft = [], []
    for marker, rs in by_marker.items():
        for a, b in itertools.combinations(rs, 2):
            if a["trial_id"] == b["trial_id"]:
                continue
            shared = tokens(a) & tokens(b)
            if len(shared) < 2:
                continue
            same_n = ((a.get("n_tx"), a.get("n_ctrl")) == (b.get("n_tx"), b.get("n_ctrl"))
                      and (a.get("n_tx") or "").strip() not in ("", "NA"))
            rec = (a["trial_id"], b["trial_id"], marker, sorted(shared), same_n)
            (hard if (len(shared) >= 3 or same_n) else soft).append(rec)

    seen = set()

    def dedupe(recs):
        out = []
        for t1, t2, mk, sh, sn in recs:
            key = (t1, t2, mk)
            if key in seen:
                continue
            seen.add(key)
            out.append((t1, t2, mk, sh, sn))
        return out

    return dedupe(hard), dedupe(soft), by_marker


def row(trial, marker, **vals):
    """A master row carrying only what this gate reads."""
    r = {c: "" for c in FINGERPRINT_COLS}
    r.update({"trial_id": trial, "biomarker": marker, "n_tx": "", "n_ctrl": ""})
    r.update({k: str(v) for k, v in vals.items()})
    return r


def self_test():
    cases = []

    # The real case this gate was written for, found by reading and not by the gate: post treatment
    # ALT means repeated to two decimals under two trial identifiers.
    real = [row("TRIAL-2018", "ALT", final_mean_tx="39.82", final_mean_ctrl="51.48",
                yi_reported="-11.66"),
            row("TRIAL-2014", "ALT", final_mean_tx="39.82", final_mean_ctrl="51.48",
                yi_reported="-11.66")]
    h, s, _ = find_pairs(real)
    cases.append(("three repeated values across two trials", len(h) == 1 and not s))

    # Two values and the same n per arm is the other HARD route.
    two_same_n = [row("A", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", n_tx="40", n_ctrl="40"),
                  row("B", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", n_tx="40", n_ctrl="40")]
    h, s, _ = find_pairs(two_same_n)
    cases.append(("two repeated values with the same n per arm", len(h) == 1 and not s))

    # Two values and a different n is SOFT, not HARD.
    two_diff_n = [row("A", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", n_tx="40", n_ctrl="40"),
                  row("B", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", n_tx="55", n_ctrl="52")]
    h, s, _ = find_pairs(two_diff_n)
    cases.append(("two repeated values with a different n is soft", not h and len(s) == 1))

    # One trial legitimately repeats its own numbers across rows.
    same_trial = [row("A", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", yi_reported="-51.06"),
                  row("A", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", yi_reported="-51.06")]
    h, s, _ = find_pairs(same_trial)
    cases.append(("one trial repeating its own numbers is not a pair", not h and not s))

    # Values too common to identify: integers and single significant digits are not fingerprints.
    common = [row("A", "hsCRP", mean_tx="3", mean_ctrl="5", yi_reported="0.2"),
              row("B", "hsCRP", mean_tx="3", mean_ctrl="5", yi_reported="0.2")]
    h, s, _ = find_pairs(common)
    cases.append(("integers and one digit values identify nothing", not h and not s))

    # A different marker is a different group, however the numbers fall.
    other_marker = [row("A", "hsCRP", mean_tx="2.31", mean_ctrl="4.72", yi_reported="-51.06"),
                    row("B", "ALT", mean_tx="2.31", mean_ctrl="4.72", yi_reported="-51.06")]
    h, s, _ = find_pairs(other_marker)
    cases.append(("the same numbers under different markers do not pair", not h and not s))

    print("SELF TEST")
    ok = True
    for name, passed in cases:
        print("  %-52s %s" % (name, passed))
        ok = ok and passed
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv[1:]:
        rc = self_test()
        if rc != 0:
            sys.exit(rc)
        print()
    rows = list(csv.DictReader(open(MASTER, newline="")))
    hard, soft, by_marker = find_pairs(rows)
    done = triaged_pairs()
    untriaged = [h for h in hard if (h[0], h[1], h[2]) not in done]
    print(f"duplicate number check over {len(rows)} row(s) in {len(by_marker)} marker group(s)")
    print(f"  HARD pairs {len(hard)} ({len(hard) - len(untriaged)} triaged, {len(untriaged)} not)")
    print(f"  SOFT pairs {len(soft)}")
    for title, recs in (("HARD pairs", hard), ("SOFT pairs", soft)):
        if not recs:
            continue
        print(f"\n{title}")
        for t1, t2, mk, sh, sn in sorted(recs, key=lambda x: -len(x[3])):
            tag = ("triaged  " if (t1, t2, mk) in done else "UNTRIAGED") if recs is hard else "        "
            print(f"  {tag} {mk:16} {t1[:32]:34} {t2[:32]:34} shared {','.join(sh[:5])}"
                  f"{' | same n per arm' if sn else ''}")
    sys.exit(1 if untriaged else 0)


if __name__ == "__main__":
    main()
