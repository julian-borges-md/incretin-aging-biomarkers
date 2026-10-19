#!/usr/bin/env python3
"""
citation_record_check.py

Chain gate. Asks whether the committed reference record still describes the committed corpus,
offline.

src/included_studies_references.py builds the reference list and verifies each entry against
Europe PMC and Crossref. That script needs the network, so it cannot sit in the gate chain: a
chain that fails without a connection stops being a test of the repository. This gate checks the
record that script leaves behind, which is the part that must stay true between runs:

  1. analysis/output/included_studies.csv covers every trial in analysis/data/extraction_master.csv
     and no others. A trial added to the corpus without regenerating the reference list is the
     failure this catches, and it is silent otherwise: the manuscript would cite 76 trials while
     pooling 77.
  2. Every verdict is one this project recognises.
  3. No verdict is 'mismatch' or 'identifier_not_found' unless the case is written up in
     docs/CITATION_TRIAGE.md. Those two mean the recorded bibliography disagrees with the registry,
     which is a defect until someone has judged it.
  4. Every 'no_identifier_exists' row is written up as well. It is a terminal state, not a defect,
     but a reference the manuscript cannot resolve to a DOI or PMID must be a decision on the
     record rather than a blank in a table.
  5. Each row's first_author, year and doi match the master's values for that trial, so that a
     correction applied to one and not the other cannot survive a run.
  6. The anchor reference record, analysis/output/anchor_references_check.csv, covers the references
     in docs/REFERENCES.md and every one of them verifies. That list carries the Introduction and the
     Discussion, and the first run of its check found seven references whose recorded issue or pages
     pointed at the wrong article in the right journal. Like the included studies list it is built
     with the network and checked here without it.

Usage
  python3 -I src/citation_record_check.py
  python3 -I src/citation_record_check.py --self-test
"""
import csv
import os
import re
import sys

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
RECORD = os.path.join(ROOT, "analysis", "output", "included_studies.csv")
TRIAGE = os.path.join(ROOT, "docs", "CITATION_TRIAGE.md")
ANCHOR_DOC = os.path.join(ROOT, "docs", "REFERENCES.md")
ANCHOR_RECORD = os.path.join(ROOT, "analysis", "output", "anchor_references_check.csv")

VERDICTS = {
    "verified",
    "mismatch",
    "author_absent_in_master",
    "no_identifier_exists",
    "identifier_not_found",
}
NEEDS_TRIAGE = {"mismatch", "identifier_not_found", "no_identifier_exists"}


def absent(v):
    """Normalise the two spellings of a missing bibliographic field to one.

    Three trials in this corpus are conference abstracts or a local journal with no DOI and no
    PMID. The master carries the literal string "NA" in those fields, which is what the captures
    printed; the reference list writes an empty string. Both mean absent, and a gate whose job is
    to check that two files agree in meaning must not fail on the spelling. The string "NA" in a
    DOI column remains an upstream smell and is recorded as an amendment candidate in
    docs/CITATION_TRIAGE.md rather than fixed here, because correcting it means rewriting three
    extractions for a field that is empty either way.
    """
    s = (v or "").strip()
    return "" if s.upper() in ("NA", "NAN", "NONE", "NULL") else s


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def triaged_trials():
    """Trial identifiers named in the triage document.

    The document is prose with tables, so the rule is deliberately loose: a trial counts as
    written up if its identifier appears anywhere in the file. A stricter parse would make the
    gate depend on the document's layout, and a gate that breaks when a table gains a column
    teaches people to delete the gate.
    """
    if not os.path.exists(TRIAGE):
        return ""
    with open(TRIAGE) as fh:
        return fh.read()


def check(master_rows, record_rows, triage_text):
    failures = []

    master_trials = {}
    for r in master_rows:
        master_trials.setdefault(r["trial_id"], r)
    record_trials = {r["trial_id"]: r for r in record_rows}

    missing = sorted(set(master_trials) - set(record_trials))
    extra = sorted(set(record_trials) - set(master_trials))
    for t in missing:
        failures.append("trial %r is in the master and not in the reference record; regenerate "
                        "with src/included_studies_references.py" % t)
    for t in extra:
        failures.append("trial %r is in the reference record and not in the master" % t)

    if len(record_rows) != len(record_trials):
        failures.append("the reference record has %d rows for %d trials; one row per trial"
                        % (len(record_rows), len(record_trials)))

    for t, rec in sorted(record_trials.items()):
        verdict = (rec.get("verdict") or "").strip()
        if verdict not in VERDICTS:
            failures.append("trial %r carries an unrecognised verdict %r" % (t, verdict))
        elif verdict in NEEDS_TRIAGE and t not in triage_text:
            failures.append("trial %r is %r and is not written up in docs/CITATION_TRIAGE.md"
                            % (t, verdict))

        m = master_trials.get(t)
        if m is None:
            continue
        for field in ("first_author", "year", "doi"):
            a = absent(m.get(field))
            b = absent(rec.get(field))
            if a != b:
                failures.append("trial %r %s is %r in the master and %r in the reference record"
                                % (t, field, a, b))
    return failures


def self_test():
    master = [
        {"trial_id": "T1", "first_author": "Wang", "year": "2019", "doi": "10.1/a"},
        {"trial_id": "T2", "first_author": "Li", "year": "2019", "doi": "10.1/b"},
    ]
    cases = [
        ("a trial absent from the record",
         [{"trial_id": "T1", "first_author": "Wang", "year": "2019", "doi": "10.1/a",
           "verdict": "verified"}],
         "", "is in the master and not in the reference record"),
        ("an untriaged mismatch",
         [{"trial_id": "T1", "first_author": "Wang", "year": "2019", "doi": "10.1/a",
           "verdict": "mismatch"},
          {"trial_id": "T2", "first_author": "Li", "year": "2019", "doi": "10.1/b",
           "verdict": "verified"}],
         "", "not written up in docs/CITATION_TRIAGE.md"),
        ("a correction applied to the record only",
         [{"trial_id": "T1", "first_author": "Zhang", "year": "2019", "doi": "10.1/a",
           "verdict": "verified"},
          {"trial_id": "T2", "first_author": "Li", "year": "2019", "doi": "10.1/b",
           "verdict": "verified"}],
         "", "in the master and 'Zhang' in the reference record"),
        ("an unrecognised verdict",
         [{"trial_id": "T1", "first_author": "Wang", "year": "2019", "doi": "10.1/a",
           "verdict": "probably fine"},
          {"trial_id": "T2", "first_author": "Li", "year": "2019", "doi": "10.1/b",
           "verdict": "verified"}],
         "", "unrecognised verdict"),
    ]
    print("SELF TEST")
    ok = True
    for name, record, triage, expect in cases:
        found = any(expect in f for f in check(master, record, triage))
        print("  %-42s %s" % (name, found))
        ok = ok and found

    clean = [{"trial_id": "T1", "first_author": "Wang", "year": "2019", "doi": "10.1/a",
              "verdict": "verified"},
             {"trial_id": "T2", "first_author": "Li", "year": "2019", "doi": "10.1/b",
              "verdict": "mismatch"}]
    quiet = not check(master, clean, "T2 is the Nanjing trial, judged on 19 October")
    print("  %-42s %s" % ("a triaged mismatch passes", quiet))
    ok = ok and quiet
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def check_anchor(doc_text, record_rows):
    """The anchor reference list against its own committed check result."""
    failures = []
    doc_dois = set(re.findall(r"\|\s*(10\.\S+?)\s*\|", doc_text))
    rec_dois = {(r.get("doi") or "").strip() for r in record_rows}
    for d in sorted(doc_dois - rec_dois):
        failures.append("anchor reference %s is in docs/REFERENCES.md and not in the check record; "
                        "rerun src/anchor_references_check.py" % d)
    for d in sorted(rec_dois - doc_dois):
        failures.append("the anchor check record holds %s, which docs/REFERENCES.md no longer "
                        "cites" % d)
    for r in record_rows:
        v = (r.get("verdict") or "").strip()
        if v != "verified":
            failures.append("anchor reference %s is %r: %s"
                            % (r.get("n", "?"), v, (r.get("note") or "")[:120]))
    return failures


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
        if rc != 0:
            return rc
        print()

    for p in (MASTER, RECORD):
        if not os.path.exists(p):
            print("FAIL: %s is missing" % os.path.relpath(p, ROOT))
            return 1

    master_rows = read_csv(MASTER)
    record_rows = read_csv(RECORD)
    failures = check(master_rows, record_rows, triaged_trials())

    anchor_rows = []
    if not os.path.exists(ANCHOR_RECORD):
        failures.append("analysis/output/anchor_references_check.csv is missing; the anchor "
                        "reference list has not been checked. Run src/anchor_references_check.py")
    elif os.path.exists(ANCHOR_DOC):
        anchor_rows = read_csv(ANCHOR_RECORD)
        with open(ANCHOR_DOC) as fh:
            failures += check_anchor(fh.read(), anchor_rows)

    verdicts = {}
    for r in record_rows:
        v = (r.get("verdict") or "").strip()
        verdicts[v] = verdicts.get(v, 0) + 1

    print("citation record check")
    print("  %d trial(s) in the master, %d row(s) in the reference record"
          % (len({r["trial_id"] for r in master_rows}), len(record_rows)))
    print("  %d anchor reference(s) checked" % len(anchor_rows))
    for v in sorted(verdicts):
        print("  %-24s %d" % (v, verdicts[v]))
    if not failures:
        print("  the reference record covers the corpus and every non verified case is written up")
        return 0
    print("\nFAIL: %d problem(s)" % len(failures))
    for f in failures:
        print("  " + f)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
