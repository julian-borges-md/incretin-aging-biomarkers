#!/usr/bin/env python3
"""
manifest_check.py

Chain gate. Verifies every SHA-256 in analysis/output/MANIFEST.csv against the file on disk.

Why. The manifest's stated purpose is that "a reviewer can verify that the files accompanying the
submission are exactly those this script produced, and a future reader can confirm that a rerun
reproduces identical output". Nothing had ever verified it. A manifest that is not checked is a
list, and this project has already shipped two claims of that kind: a figure set that did not exist
and a reference list that had never been resolved.

What it checks

  1. Every file named in the manifest exists and its content hashes to the recorded digest.
  2. Every file in analysis/output is named in the manifest, except the manifest itself and the
     files the repository deliberately does not track. A result produced after the manifest was
     written is a result the manifest does not describe, and the submission would carry it anyway.

A failure is not necessarily corruption. The ordinary cause is an output regenerated after the run
that wrote the manifest, which is what happens when a gate script is rerun on its own. The remedy is
the same either way and the gate says so: rerun the analysis pipeline, which rewrites the manifest
last, so that the manifest describes the outputs beside it.

Usage
  python3 -I src/manifest_check.py
  python3 -I src/manifest_check.py --self-test
"""
import csv
import hashlib
import os
import sys

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "analysis", "output")
MANIFEST = os.path.join(OUT, "MANIFEST.csv")

# Not results, and deliberately not in the manifest.
IGNORED = {"MANIFEST.csv", ".gitkeep"}
IGNORED_SUFFIXES = (".tmp", ".log")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check(rows, digest_of, present):
    """rows: manifest rows. digest_of: basename -> digest or None if absent.

    present: the basenames actually in the output directory.
    """
    failures = []
    named = set()
    for r in rows:
        name = os.path.basename((r.get("file") or "").strip())
        if not name:
            failures.append("the manifest has a row with no file name")
            continue
        named.add(name)
        recorded = (r.get("sha256") or "").strip()
        if not recorded:
            failures.append("%s is in the manifest with no digest" % name)
            continue
        actual = digest_of(name)
        if actual is None:
            failures.append("%s is in the manifest and not in the output directory" % name)
        elif actual != recorded:
            failures.append("%s does not hash to its recorded digest (recorded %s, on disk %s)"
                            % (name, recorded[:16], actual[:16]))
    for name in sorted(present - named):
        if name in IGNORED or name.endswith(IGNORED_SUFFIXES):
            continue
        failures.append("%s is in the output directory and not in the manifest, so the submission "
                        "would carry a result the manifest does not describe" % name)
    return failures


def self_test():
    rows = [{"file": "analysis/output/a.csv", "sha256": "aaaa"},
            {"file": "analysis/output/b.csv", "sha256": "bbbb"}]
    digests = {"a.csv": "aaaa", "b.csv": "bbbb"}
    present = {"a.csv", "b.csv", "MANIFEST.csv"}

    cases = [
        ("a matching set passes",
         check(rows, digests.get, present) == []),
        ("a changed file is caught",
         any("does not hash to its recorded digest" in f
             for f in check(rows, {"a.csv": "aaaa", "b.csv": "cccc"}.get, present))),
        ("a missing file is caught",
         any("not in the output directory" in f
             for f in check(rows, {"a.csv": "aaaa"}.get, {"a.csv", "MANIFEST.csv"}))),
        ("a file the manifest never saw is caught",
         any("not in the manifest" in f
             for f in check(rows, digests.get, present | {"c.csv"}))),
        ("an ignored file is not required in the manifest",
         check(rows, digests.get, present | {"scratch.log", "partial.tmp", ".gitkeep"}) == []),
        ("a row with no digest is caught",
         any("no digest" in f
             for f in check(rows + [{"file": "c.csv", "sha256": ""}], digests.get,
                            present | {"c.csv"}))),
    ]
    print("SELF TEST")
    ok = True
    for name, passed in cases:
        print("  %-48s %s" % (name, passed))
        ok = ok and passed
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
        if rc != 0:
            return rc
        print()

    if not os.path.exists(MANIFEST):
        print("FAIL: analysis/output/MANIFEST.csv is missing; run the analysis pipeline")
        return 1
    with open(MANIFEST, newline="") as fh:
        rows = list(csv.DictReader(fh))

    present = {f for f in os.listdir(OUT) if os.path.isfile(os.path.join(OUT, f))}
    cache = {}

    def digest_of(name):
        if name not in present:
            return None
        if name not in cache:
            cache[name] = sha256(os.path.join(OUT, name))
        return cache[name]

    failures = check(rows, digest_of, present)

    print("manifest check")
    print("  %d file(s) in the manifest, %d in the output directory" % (len(rows), len(present)))
    if not failures:
        print("  every recorded digest matches the file on disk, and every result is recorded")
        return 0
    print("\nFAIL: %d problem(s)" % len(failures))
    for f in failures:
        print("  " + f)
    print("\nThe usual cause is an output regenerated after the run that wrote the manifest. Rerun "
          "the analysis pipeline, which rewrites the manifest last.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
