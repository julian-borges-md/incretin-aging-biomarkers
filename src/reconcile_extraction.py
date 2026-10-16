#!/usr/bin/env python3
"""
reconcile_extraction.py

Reconciliation of two independent extractions of one study group (docs/EXTRACTION_BRIEF.md,
Section 6). Extractor files live in work/extraction/staging/<group>/A.csv and B.csv with their
notes A.json and B.json. Nothing here edits an extractor's file: a disagreement is settled by a
third read, the settled value is written into the chosen file by hand with the resolution in the
row's notes, and only then is the group written to analysis/data.

Commands
  compare GROUP [--pair A,V]
      align the rows of the pair (default A,B; A,V for an extraction and its verification) on (biomarker, dose_mg, comparator, timepoint) and report every
      field that differs: numbers beyond 0.5 percent relative or 0.05 absolute, categoricals
      exactly (case and spaces ignored). Exit 1 while any disagreement or unmatched row remains.
  write GROUP --from A|B --out NAME [--single] [--note TEXT] [--resolve TEXT]
      copy the chosen file to analysis/data/extraction_NAME.csv once compare passes, or with
      --resolve stating how each remaining disagreement was settled in the chosen file (the
      compare output and the resolution are stored in reconciled.json), or with --single when
      only one extractor read the study (the ledger then shows it); writes reconciled.json
      {status extracted, file, rows, extractors, note, resolution, disagreements_at_write}.
  close GROUP --status STATUS --reason TEXT [--molecule M]
      no rows for this group: STATUS is excluded_at_extraction, molecule_not_admitted,
      no_usable_contrast or held_pending_decision; the extractor JSON notes are folded in.

Usage
  python3 -I src/reconcile_extraction.py compare 18
  python3 -I src/reconcile_extraction.py write 18 --from A --out sandsdal2023_liraglutide
  python3 -I src/reconcile_extraction.py close 77 --status molecule_not_admitted --reason "lixisenatide" --molecule lixisenatide
"""
import csv
import json
import os
import shutil
import sys
import time

ROOT = os.getcwd()
STAGING = os.path.join(ROOT, "work", "extraction", "staging")
DATA = os.path.join(ROOT, "analysis", "data")
KEY = ("biomarker", "dose_mg", "comparator", "assessment_timepoint_weeks", "duration_weeks")
CATEGORICAL = ("trial_id", "first_author", "year", "drug", "receptor_class", "comparator_type", "population",
               "measure", "se_source", "outcome_type", "prespecified_endpoint", "industry_funded", "rob_overall",
               "hallmark_domain", "aging_direction", "clinical_weight", "p_is_bound")
IGNORED = ("notes", "source_file", "journal", "pmid", "doi", "phase")


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def norm(v):
    return (v or "").strip().lower()


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def key_of(r):
    return tuple(norm(r.get(k)) for k in KEY)


def compare(group, pair=("A", "B")):
    d = os.path.join(STAGING, str(group))
    x, y = pair
    pa, pb = os.path.join(d, f"{x}.csv"), os.path.join(d, f"{y}.csv")
    if not (os.path.exists(pa) and os.path.exists(pb)):
        print(f"group {group}: both {x}.csv and {y}.csv are needed to compare (have {x}={os.path.exists(pa)}, {y}={os.path.exists(pb)})")
        return 1
    A, B = read(pa), read(pb)
    ka = {key_of(r): r for r in A}
    kb = {key_of(r): r for r in B}
    problems = 0
    for k in sorted(set(ka) - set(kb)):
        print(f"  only in {x}: {k}")
        problems += 1
    for k in sorted(set(kb) - set(ka)):
        print(f"  only in {y}: {k}")
        problems += 1
    for k in sorted(set(ka) & set(kb)):
        ra, rb = ka[k], kb[k]
        cols = sorted((set(ra) | set(rb)) - set(IGNORED))
        for c in cols:
            va, vb = ra.get(c), rb.get(c)
            if norm(va) == norm(vb):
                continue
            na, nb = num(va), num(vb)
            if na is not None and nb is not None:
                tol = max(0.05, 0.005 * max(abs(na), abs(nb)))
                if abs(na - nb) <= tol:
                    continue
            print(f"  {k[0]:18} dose {k[1]:>5} vs {k[2][:18]:18} wk {k[3] or k[4]:>4}  {c:22} {x}={va!r}  {y}={vb!r}")
            problems += 1
    print(f"group {group}: {len(A)} rows in {x}, {len(B)} rows in {y}, {problems} disagreement(s)")
    return 1 if problems else 0


ROB_FILE = os.path.join(DATA, "risk_of_bias.csv")
ROB_DOMAINS = ("d1_randomisation", "d2_deviations", "d3_missing", "d4_measurement", "d5_selection", "overall")


def append_rob(group, rows, notes, pair, resolve):
    """Append the trial's RoB-2 row from the extractor JSON rob objects when the two reads agree on
    every domain (or a resolution is recorded); build_master requires one row per trial."""
    robs = {x: notes[x].get("rob") for x in pair if x in notes and notes[x].get("rob")}
    if not robs:
        print(f"  no rob object in the JSON notes of {pair}: add the RoB-2 row to {os.path.relpath(ROB_FILE, ROOT)} by hand")
        return
    trial_id = rows[0]["trial_id"] if rows else notes[pair[0]].get("trial_id", "")
    with open(ROB_FILE, newline="") as fh:
        existing = list(csv.DictReader(fh))
        hdr = list(existing[0].keys())
    if any(r["trial_id"] == trial_id for r in existing):
        print(f"  RoB-2 row for {trial_id} already present")
        return
    vals = list(robs.values())
    diff = [dom for dom in ROB_DOMAINS if len({norm(v.get(dom)) for v in vals}) > 1]
    if diff and not resolve:
        print(f"  RoB-2 domains differ between {list(robs)}: {diff}; settle in the JSON of {pair[0]} and write with --resolve")
        sys.exit(1)
    src = robs[pair[0]] if pair[0] in robs else vals[0]
    just = " | ".join(f"{x}: {v.get('justification', '')}" for x, v in robs.items())
    row = dict(trial_id=trial_id, first_author=rows[0]["first_author"] if rows else "", year=rows[0]["year"] if rows else "",
               pmid=rows[0]["pmid"] if rows else "", design=notes[pair[0]].get("design", "")[:200],
               justification=just + (f" | resolution: {resolve}" if diff else ""))
    for dom in ROB_DOMAINS:
        row[dom] = src.get(dom, "")
    with open(ROB_FILE, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr, extrasaction="ignore")
        w.writerow(row)
    print(f"  RoB-2 row appended for {trial_id}: {row['overall']}")


def write(group, src, name, single=False, note="", resolve="", pair=("A", "B")):
    d = os.path.join(STAGING, str(group))
    p = os.path.join(d, f"{src}.csv")
    if not os.path.exists(p):
        sys.exit(f"{p} does not exist")
    disagreements = ""
    if not single:
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = compare(group, pair)
        disagreements = buf.getvalue()
        print(disagreements, end="")
        if rc != 0 and not resolve:
            sys.exit("compare has not passed: settle the disagreements in the chosen file, then write with "
                     "--resolve \"what was settled and how\" (recorded), or --single for a single extraction")
    out = os.path.join(DATA, f"extraction_{name}.csv")
    if os.path.exists(out):
        sys.exit(f"{out} exists: choose another name or remove it deliberately")
    rows = read(p)
    notes = {}
    for x in ("A", "B", "V"):
        jp = os.path.join(d, f"{x}.json")
        if os.path.exists(jp):
            with open(jp) as fh:
                notes[x] = json.load(fh)
    if rows:
        append_rob(group, rows, notes, pair if not single else (src,), resolve)
    shutil.copyfile(p, out)
    rec = dict(status="extracted", file=os.path.relpath(out, ROOT), rows=len(rows), source=src,
               extractors="single " + src if single else "+".join(pair) + " reconciled",
               molecule=next((n.get("molecule", "") for n in notes.values() if n.get("molecule")), ""),
               biomarkers_reported_no_variance=sorted({b for n in notes.values() for b in n.get("biomarkers_reported_no_variance", [])}),
               other_markers=sorted({b for n in notes.values() for b in n.get("other_markers", [])}),
               note=note, resolution=resolve, disagreements_at_write=disagreements.strip(),
               written=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(os.path.join(d, "reconciled.json"), "w") as fh:
        json.dump(rec, fh, indent=1)
    print(f"group {group}: {len(rows)} rows -> {rec['file']} ({rec['extractors']})")


def close(group, status, reason, molecule=""):
    d = os.path.join(STAGING, str(group))
    os.makedirs(d, exist_ok=True)
    notes = {}
    for x in ("A", "B"):
        jp = os.path.join(d, f"{x}.json")
        if os.path.exists(jp):
            with open(jp) as fh:
                notes[x] = json.load(fh)
    rec = dict(status=status, reason=reason, rows=0, file="",
               molecule=molecule or next((n.get("molecule", "") for n in notes.values() if n.get("molecule")), ""),
               biomarkers_reported_no_variance=sorted({b for n in notes.values() for b in n.get("biomarkers_reported_no_variance", [])}),
               other_markers=sorted({b for n in notes.values() for b in n.get("other_markers", [])}),
               written=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(os.path.join(d, "reconciled.json"), "w") as fh:
        json.dump(rec, fh, indent=1)
    print(f"group {group}: closed as {status} ({reason})")


def main(argv):
    if len(argv) < 2 or argv[0] not in ("compare", "write", "close"):
        print(__doc__)
        sys.exit(2)
    cmd, group = argv[0], argv[1]
    opts = {}
    i = 2
    flags = set()
    while i < len(argv):
        if argv[i] == "--single":
            flags.add("single")
            i += 1
        elif argv[i].startswith("--") and i + 1 < len(argv):
            opts[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            sys.exit(f"unexpected argument {argv[i]}")
    pair = tuple(opts.get("pair", "A,B").split(","))
    if cmd == "compare":
        sys.exit(compare(group, pair))
    if cmd == "write":
        if "from" not in opts or "out" not in opts:
            sys.exit("write needs --from A|B and --out NAME")
        write(group, opts["from"], opts["out"], single="single" in flags, note=opts.get("note", ""),
              resolve=opts.get("resolve", ""), pair=pair)
    elif cmd == "close":
        if "status" not in opts or "reason" not in opts:
            sys.exit("close needs --status and --reason")
        if opts["status"] not in ("excluded_at_extraction", "molecule_not_admitted", "no_usable_contrast", "held_pending_decision"):
            sys.exit("unknown status")
        close(group, opts["status"], opts["reason"], opts.get("molecule", ""))


if __name__ == "__main__":
    main(sys.argv[1:])
