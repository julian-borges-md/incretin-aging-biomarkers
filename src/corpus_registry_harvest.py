#!/usr/bin/env python3
"""
corpus_registry_harvest.py

Retrieves the ClinicalTrials.gov record of every INCLUDED trial that has a registry identifier, into
work/fulltext/registry_corpus/<NCT>.json (gitignored), with a manifest beside it.

WHY A SECOND HARVESTER. src/ctgov_harvest.py is driven by the screening pool and fetches the records
of pool entries whose retrieval route was the registry. Those are candidate records, and the 38 files
it left under work/fulltext/registry cover screening candidates rather than the corpus: of the 44
included trials that carry an NCT identifier, exactly one has a record there. Measuring the reach of
a timepoint check against that directory gives 5 rows of 524 and would have been read as a property
of the data, when it is a property of what had been retrieved.

HOW A TRIAL IS RESOLVED TO AN NCT, in order of directness, with the source recorded per trial in the
manifest so that a reader can see which identifier a comparison rests on:

  trial_id   the identifier is in the trial's own label, for 27 of the 76 trials
  notes      an NCT appears in the extraction notes of one of the trial's rows, for 14 more
  ledger     the extraction ledger's identifiers column for the group whose reconciled file holds
             the trial's rows, for 3 more
  none       32 trials carry no registry identifier anywhere in the repository. Most are older
             single centre studies; one records a EudraCT number instead

WHAT THIS DOES NOT DO. It retrieves metadata and writes it to the gitignored work tree. It changes no
tracked file, computes no statistic and is not a gate. The gate that would use it is measured first,
in docs/TIMEPOINT_REACH.md, under the chain's rule that reach is measured before a gate is built.

Usage
  python3 -I src/corpus_registry_harvest.py            fetch what is missing
  python3 -I src/corpus_registry_harvest.py --resolve  print the trial to NCT mapping, fetch nothing
  exit 1 when a fetch fails for a reason other than the record not existing
"""
import collections
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
LEDGER = os.path.join(ROOT, "analysis", "data", "EXTRACTION_LEDGER.csv")
OUTDIR = os.path.join(ROOT, "work", "fulltext", "registry_corpus")
MANIFEST = os.path.join(OUTDIR, "MANIFEST.csv")
API = "https://clinicaltrials.gov/api/v2/studies/{}"
NCT = re.compile(r"NCT\d{8}")
PAUSE = 0.34       # three requests a second, well inside the public API's rate


def resolve():
    """trial_id -> (source, sorted NCT ids). One entry per trial in the master."""
    rows = list(csv.DictReader(open(MASTER, newline="")))

    notes = collections.defaultdict(set)
    for r in rows:
        notes[r["trial_id"]] |= set(NCT.findall(r.get("notes") or ""))

    # The ledger names an extraction file per group; that file names the trials.
    file_trials = collections.defaultdict(set)
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
                    file_trials[p].add(r["trial_id"])
    ledger = collections.defaultdict(set)
    for r in csv.DictReader(open(LEDGER, newline="")):
        f = (r.get("reconciled_file") or "").strip()
        ids = set(NCT.findall(r.get("identifiers") or ""))
        if f and ids:
            for t in file_trials.get(f, ()):
                ledger[t] |= ids

    out = {}
    for r in rows:
        t = r["trial_id"]
        if t in out:
            continue
        if NCT.findall(t):
            out[t] = ("trial_id", sorted(set(NCT.findall(t))))
        elif notes[t]:
            out[t] = ("notes", sorted(notes[t]))
        elif ledger.get(t):
            out[t] = ("ledger", sorted(ledger[t]))
        else:
            out[t] = ("none", [])
    return out


def fetch(nct):
    req = urllib.request.Request(API.format(nct), headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as fh:
        return json.loads(fh.read().decode())


def main(argv):
    res = resolve()
    by_src = collections.Counter(s for s, _ in res.values())
    print(f"trials in the master: {len(res)}")
    for s in ("trial_id", "notes", "ledger", "none"):
        print(f"  {by_src.get(s, 0):3}  resolved from {s}")

    if "--resolve" in argv:
        for t, (s, ids) in sorted(res.items()):
            print(f"  {s:8} {','.join(ids) or '-':14} {t}")
        return 0

    os.makedirs(OUTDIR, exist_ok=True)
    wanted = sorted({(ids[0], t, s) for t, (s, ids) in res.items() if ids})
    print(f"\nregistry records to hold: {len(wanted)}")
    manifest, failed, fetched, cached = [], [], 0, 0
    for nct, trial, src in wanted:
        path = os.path.join(OUTDIR, nct + ".json")
        if os.path.exists(path) and os.path.getsize(path) > 500:
            cached += 1
        else:
            try:
                d = fetch(nct)
                with open(path, "w") as fh:
                    json.dump(d, fh)
                fetched += 1
                time.sleep(PAUSE)
            except urllib.error.HTTPError as e:
                print(f"  {nct} HTTP {e.code}")
                failed.append((nct, trial, f"HTTP {e.code}"))
                continue
            except Exception as e:  # noqa: BLE001 - the reason is recorded, not swallowed
                print(f"  {nct} {type(e).__name__}: {e}")
                failed.append((nct, trial, f"{type(e).__name__}: {e}"))
                continue
        d = json.load(open(path))
        po = (d.get("protocolSection", {}).get("outcomesModule", {}) or {}).get(
            "primaryOutcomes", [])
        manifest.append({
            "nct": nct, "trial_id": trial, "id_source": src,
            "bytes": os.path.getsize(path),
            "primary_outcomes": len(po),
            "time_frames": " | ".join((o.get("timeFrame") or "").replace("\n", " ")
                                      for o in po)[:400],
        })
    with open(MANIFEST, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0]) if manifest else
                           ["nct", "trial_id", "id_source", "bytes", "primary_outcomes",
                            "time_frames"])
        w.writeheader()
        w.writerows(manifest)
    print(f"  fetched {fetched}, already held {cached}, failed {len(failed)}")
    print(f"  records stating at least one primary outcome: "
          f"{sum(1 for m in manifest if m['primary_outcomes'])}")
    print(f"  manifest: {os.path.relpath(MANIFEST, ROOT)}")
    # A record that does not exist is a fact about the registry; anything else is a retrieval
    # problem and must not be mistaken for one.
    hard = [f for f in failed if "HTTP 404" not in f[2]]
    for nct, trial, why in hard:
        print(f"  FAILED {nct} ({trial}): {why}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
