#!/usr/bin/env python3
"""
extraction_attachment_check.py

Second provenance layer over the whole corpus. src/extraction_numbers_check.py asks whether every
number an extractor wrote occurs somewhere in the source text; it cannot ask whether the number was
attached to the right BIOMARKER. A value lifted from the neighbouring row of a table passes that
first check and corrupts the pool, and two errors of exactly that family were made and corrected by
hand on 16 October (a weight read from the wrong row, and an author name that was not in the text).

What this does, per row of the master
  1. collect the row's identifying numbers (reported effect, interval bounds, arm means, dispersions)
  2. find the lines of the row's source texts that carry those numbers
  3. check whether a synonym of the row's biomarker appears on such a line or within a small window
     of lines around it, which is where a table keeps its row label
  4. classify the row
       OK      a line carries the numbers and the marker name is on it or beside it
       WEAK    lines carry the numbers but no marker name is anywhere near them
       NOLINE  no line of the source carries the numbers (a derived or companion sourced row)
       NOTEXT  the source text is not on disk (registry or proxy capture not retained)

Nothing is corrected here. WEAK and NOLINE are the verifier's reading list, in the order a verifier
should work through them, and the counts are the audit record.

Usage
  python3 -I src/extraction_attachment_check.py                  all rows, summary plus the list
  python3 -I src/extraction_attachment_check.py GROUP_OR_TRIAL   one group number or trial substring
  exit 1 when any row is WEAK
"""
import csv
import json
import os
import re
import sys

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
# Rows whose attachment has been read and judged by a human or by the session, written up as the
# audit record and used here as the allowlist: a WEAK row listed there does not fail the gate, and
# a WEAK row that is not listed does, which is what a new extraction with a misattached number
# would produce. The file also records the one row whose source capture is not retained.
TRIAGE = os.path.join(ROOT, "docs", "ATTACHMENT_TRIAGE.md")
LEDGER = os.path.join(ROOT, "analysis", "data", "EXTRACTION_LEDGER.csv")
PACKETS = os.path.join(ROOT, "work", "extraction", "packets")
WINDOW = 8  # lines either side; a table row label sits on the line or just above the values

NUMERIC_COLS = ("yi_reported", "ci_lb_reported", "ci_ub_reported", "mean_tx", "mean_ctrl",
                "sd_tx", "sd_ctrl", "sem_tx", "sem_ctrl", "final_mean_tx", "final_mean_ctrl",
                "base_mean_tx", "base_mean_ctrl", "events_tx", "events_ctrl")

SYNONYMS = {
    "hsCRP": ["crp", "c-reactive", "c reactive", "c‐reactive"],
    "IL6": ["il-6", "il6", "il‐6", "interleukin"],
    "TNF_alpha": ["tnf", "necrosis factor"],
    "adiponectin": ["adiponectin", "adipo"],
    "leptin": ["leptin"],
    "ALT": ["alt", "alanine"],
    "AST": ["ast", "aspartate"],
    "GGT": ["ggt", "glutamyl", "γ-gt", "gamma-gt", "gamma- gt", "γ -gt", "g-gt"],
    "fatty_liver_index": ["fatty liver index", "fli"],
    "SBP": ["systolic", "sbp"],
    "DBP": ["diastolic", "dbp", "blood pressure"],
    "TC": ["cholesterol", "tch", "thc", "total-c", "tc,", "tc "],
    "LDL": ["ldl", "low-density", "low density"],
    "TG": ["triglyceride", "triacylglycerol", "tg,", "tg ", "tg("],
    "fasting_glucose": ["glucose", "fpg", "fbg", "fsg", "glycaemia", "glycemia"],
    "fasting_insulin": ["insulin", "fpi", "fins", "insulinaemia", "insulinemia"],
    "resting_heart_rate": ["heart rate", "pulse", "bpm", "b.p.m"],
    "HOMA_IR": ["homa"],
    "HOMA_beta": ["homa"],
    "C_peptide": ["peptide"],
    "eGFR": ["egfr", "glomerular"],
    "VAT": ["visceral", "vat"],
    "lean_mass": ["lean"],
    "body_fat_pct": ["body fat", "fat mass", "fat percentage", "fat, %"],
    "liver_fat_pdff": ["liver fat", "pdff", "lfc", "intrahepatic", "hepatic fat", "steatosis", "ihl"],
    "NTproBNP": ["probnp", "natriuretic"],
    "MR_proANP": ["proanp", "natriuretic"],
    "glucagon": ["glucagon"],
    "GDF15": ["gdf"],
    "HbA1c": ["hba1c", "hba1", "a1c", "a1 c", "glycated", "glycosylated", "hb a1c", "haemoglobin"],
    "BMD": ["bone mineral", "bmd"],
    "ICAM1": ["icam"],
    "YKL40": ["ykl"],
    "MASH_resolution": ["mash", "nash", "resolution"],
    "fibrosis_improvement": ["fibrosis"],
}


def ident_numbers(row):
    out = []
    for c in NUMERIC_COLS:
        v = (row.get(c) or "").strip().replace("−", "-").lstrip("+-")
        if not v or v in ("NA", "TRUE", "FALSE"):
            continue
        try:
            f = abs(float(v))
        except ValueError:
            continue
        if "." not in v and f < 10:
            continue  # too common to identify a line
        out.append(v)
    # Sorted by length descending and then lexically. The second key is not cosmetic: sorting a set
    # by length alone leaves ties in set iteration order, which varies with the interpreter's string
    # hash seed, so two runs of this gate on identical data printed different numbers as the
    # evidence for the same verdict. The verdicts themselves never depended on the order, because
    # the line search counts matches over every number and every line rather than stopping at the
    # first, but an audit record that changes between runs is not an audit record.
    return sorted(set(out), key=lambda v: (-len(v), v))


def line_has(num, line):
    return re.search(r"(?<![\d.])" + re.escape(num) + r"(?![\d])", line) is not None


def matching_lines(nums, lines):
    """
    Indices of the lines that carry enough of a row's identifying numbers to be its source line.

    Two of them where the row has more than one, because a single number coincides too easily. Kept
    at module level so the provenance registry applies the same rule: if the registry counted a row
    as located in a file that this gate would not accept as its source line, its split of this
    gate's own counts would describe something else.
    """
    need = 2 if len(nums) > 1 else 1
    return [i for i, ln in enumerate(lines)
            if sum(1 for n in nums if line_has(n, ln)) >= need]


def make_source_lines():
    """
    Build and return the trial to source lines lookup used by this gate.

    Exposed at module level rather than nested inside main() because gate fifteen needs exactly the
    same lookup, and a second copy of it is the defect that has already bitten this chain twice: the
    middle dot normalisation and the trial notes union both had to be applied in two places, and the
    second place was found only after rows had read as unverifiable for a day. One definition, two
    callers.
    """
    gm = {}
    with open(LEDGER, newline="") as fh:
        for r in csv.DictReader(fh):
            f = (r.get("reconciled_file") or "").strip()
            if f:
                gm.setdefault(f, []).append(r["study_group"])
    file_of = {}
    for name in sorted(os.listdir(os.path.join(ROOT, "analysis", "data"))):
        if not (name.startswith("extraction_") and name.endswith(".csv")) or "master" in name:
            continue
        p = os.path.join("analysis", "data", name)
        with open(os.path.join(ROOT, p), newline="") as fh:
            rd = csv.DictReader(fh)
            if "trial_id" not in (rd.fieldnames or []):
                continue
            for r in rd:
                if r.get("trial_id"):
                    file_of.setdefault(r["trial_id"], p)
    cache = {}
    # A companion capture is cited in the notes of the row that needed it, not of every row of the
    # trial, so a trial's sources are the UNION over its rows. Without this, a row whose own notes
    # name no capture is checked against the packet alone and reads as unattached: the SCALE 3 year
    # pressure rows did exactly that, and the first version of this check reported them as WEAK
    # while their numbers sat in the le Roux companion capture cited by the heart rate row.
    trial_notes = {}
    for r in csv.DictReader(open(MASTER, newline="")):
        trial_notes.setdefault(r["trial_id"], []).append(r.get("notes", ""))

    def files_for(trial, notes):
        """
        The source files a trial's rows were read from: its packet texts plus every companion
        capture cited anywhere in the trial's notes.

        Separated from the text loading below because the provenance registry needs the file list
        without the text, and because a gate and the registry disagreeing about what counts as a
        row's source would make the registry's counts meaningless for that gate.
        """
        notes = " ".join(trial_notes.get(trial, [notes]))
        files = []
        for g in gm.get(file_of.get(trial, ""), []):
            pj = os.path.join(PACKETS, str(g), "packet.json")
            if os.path.exists(pj):
                for t in json.load(open(pj))["texts"]:
                    fp = os.path.join(ROOT, t["file"])
                    if os.path.exists(fp):
                        files.append(fp)
        for m in re.findall(r"work/fulltext/[^\s,;)]+\.txt", notes or ""):
            fp = os.path.join(ROOT, m)
            if os.path.exists(fp):
                files.append(fp)
        return sorted(set(files))

    def lines_for(trial, notes):
        key = trial
        if key in cache:
            return cache[key]
        txt = []
        for fp in files_for(trial, notes):
            # Lancet style captures print 79·4 for 79.4, so the middle dot is normalised
            # here; without it every number of such a source misses and the row reads as
            # unattached, which is what the SCALE pressure rows did.
            raw = open(fp, errors="replace").read().replace("−", "-").replace("\u00b7", ".")
            txt += raw.split("\n")
        cache[key] = txt
        return txt

    lines_for.files_for = files_for
    return lines_for


def self_test():
    """Exercise the three decisions this gate rests on.

    The gate reports a verdict for every row on every run, so it is not silent; what had never been
    shown is that its three decisions are the ones it describes. Each case below is a way the gate
    could pass a row it should question, or question a row it should pass.
    """
    cases = []

    # A number must match as a number, not as a substring of a longer one. Without the boundary
    # guard, a row whose value is 5.7 would be located in any line that happens to print 15.73, and
    # the gate would report an extraction as attached to a line it has nothing to do with.
    cases.append(("5.7 does not match inside 15.73", line_has("5.7", "baseline 15.73 mg/dL") is False))
    cases.append(("5.7 matches 5.7 in a table row", line_has("5.7", "HbA1c 5.7 (0.4)") is True))
    cases.append(("5.7 does not match inside 5.78", line_has("5.7", "value 5.78") is False))
    cases.append(("a negative value matches its printed form",
                  line_has("4.72", "change -4.72 (1.1)") is True))

    # Two numbers on ONE line is the rule. Numbers spread over several lines are not a source line,
    # which is the whole reason the unlocated rows in this corpus are unlocated.
    one_line = ["week 24: 2.31 vs 4.72 (p 0.03)", "unrelated 9.99"]
    spread = ["treatment arm 2.31", "control arm 4.72"]
    cases.append(("two numbers on one line locate the row",
                  matching_lines(["2.31", "4.72"], one_line) == [0]))
    cases.append(("the same two numbers on separate lines do not",
                  matching_lines(["2.31", "4.72"], spread) == []))
    cases.append(("a single number row needs only that number",
                  matching_lines(["2.31"], spread) == [0]))

    # Values too common to identify a line are dropped before the search, or every row would locate
    # itself in any table that prints a small integer.
    r = {c: "" for c in NUMERIC_COLS}
    r[NUMERIC_COLS[0]] = "7"
    cases.append(("a bare integer below ten identifies nothing", ident_numbers(r) == []))
    r[NUMERIC_COLS[0]] = "7.0"
    cases.append(("the same value with a decimal point is kept", ident_numbers(r) == ["7.0"]))
    r[NUMERIC_COLS[0]] = "42"
    cases.append(("an integer of ten or more is kept", ident_numbers(r) == ["42"]))

    # The printed order of the evidence must not depend on the interpreter's hash seed.
    r2 = {c: "" for c in NUMERIC_COLS}
    for col, v in zip(NUMERIC_COLS[:4], ["1.23", "4.56", "7.89", "0.12"]):
        r2[col] = v
    cases.append(("the evidence order is deterministic",
                  ident_numbers(r2) == sorted(set(["1.23", "4.56", "7.89", "0.12"]),
                                              key=lambda v: (-len(v), v))))

    print("SELF TEST")
    ok = True
    for name, passed in cases:
        print("  %-52s %s" % (name, passed))
        ok = ok and passed
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
        if rc != 0:
            return rc
        print()
        argv = [a for a in argv if a != "--self-test"]
    want = argv[0] if argv else None
    lines_for = make_source_lines()
    rows = list(csv.DictReader(open(MASTER, newline="")))
    if want:
        rows = [r for r in rows if want.lower() in r["trial_id"].lower()]
    verdict = {"OK": 0, "WEAK": 0, "NOLINE": 0, "NOTEXT": 0}
    weak, noline = [], []
    for r in rows:
        lines = lines_for(r["trial_id"], r.get("notes", ""))
        if not lines:
            verdict["NOTEXT"] += 1
            continue
        nums = ident_numbers(r)
        if not nums:
            verdict["NOLINE"] += 1
            noline.append((r["trial_id"], r["biomarker"], "no identifying number on the row"))
            continue
        hit_idx = matching_lines(nums, lines)
        if not hit_idx:
            verdict["NOLINE"] += 1
            noline.append((r["trial_id"], r["biomarker"], f"numbers {','.join(nums[:3])} on no single line"))
            continue
        syns = SYNONYMS.get(r["biomarker"], [r["biomarker"].lower()])
        near = False
        for i in hit_idx:
            lo, hi = max(0, i - WINDOW), min(len(lines), i + WINDOW + 1)
            blob = " ".join(lines[lo:hi]).lower()
            if any(s in blob for s in syns):
                near = True
                break
        if near:
            verdict["OK"] += 1
        else:
            verdict["WEAK"] += 1
            weak.append((r["trial_id"], r["biomarker"], f"numbers {','.join(nums[:3])} found, "
                                                        f"marker name not within {WINDOW} lines"))
    done = set()
    if os.path.exists(TRIAGE):
        for ln in open(TRIAGE, errors="replace"):
            m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z0-9_]+)\s*\|", ln)
            if m and m.group(2) not in ("Marker", "marker"):
                done.add((m.group(1).strip(), m.group(2).strip()))
    untriaged = [w for w in weak if (w[0], w[1]) not in done]
    print("attachment check over", len(rows), "row(s)")
    for k in ("OK", "WEAK", "NOLINE", "NOTEXT"):
        print(f"  {k:7} {verdict[k]}")
    if weak:
        print(f"\nWEAK rows ({len(weak) - len(untriaged)} already triaged in "
              f"{os.path.relpath(TRIAGE, ROOT)}, {len(untriaged)} not)")
        for t, b, why in weak:
            tag = "triaged  " if (t, b) in done else "UNTRIAGED"
            print(f"  {tag} {t[:40]:42} {b:18} {why}")
    if noline:
        print("\nNOLINE rows (derived, companion sourced, or computed by the session)")
        for t, b, why in noline[:40]:
            print(f"  {t[:44]:46} {b:18} {why}")
        if len(noline) > 40:
            print(f"  ... and {len(noline) - 40} more")
    sys.exit(1 if untriaged else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
