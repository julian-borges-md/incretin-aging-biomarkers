#!/usr/bin/env python3
"""
figure_check.py

Chain gate. Asks whether every figure the manuscript will submit exists on disk, is hashed in
the manifest, and is named in the mapping document.

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

Usage
  python3 -I src/figure_check.py
  python3 -I src/figure_check.py --self-test
"""
import csv
import os
import re
import sys

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "analysis", "output")
INDEX = os.path.join(OUT, "figure_index.csv")
MANIFEST = os.path.join(OUT, "MANIFEST.csv")
MAPPING = os.path.join(ROOT, "docs", "FIGURES.md")

# Figures written by a script other than the analysis pipeline: stem -> producing script.
EXTERNAL = {
    "figure0_prisma_flow": "src/prisma_diagram.py",
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

    for stem, script in sorted(EXTERNAL.items()):
        found = [f for f in file_sizes
                 if f.rsplit(".", 1)[0] == stem and (file_sizes[f] or 0) >= MIN_BYTES]
        if not found:
            failures.append("figure %r, produced by %s, has no file of at least %d bytes"
                            % (stem, script, MIN_BYTES))
        else:
            stems.add(stem)
            for f in found:
                if f not in manifest_names:
                    failures.append("figure file %s is not in MANIFEST.csv" % f)

    mapped = mapped_stems(mapping_text)
    for stem in sorted(stems - mapped):
        failures.append("figure %r exists and is not mapped to a submission number in "
                        "docs/FIGURES.md" % stem)
    for stem in sorted(mapped - stems):
        failures.append("docs/FIGURES.md maps figure %r, which no run has produced" % stem)
    return failures


def self_test():
    index = [{"name": "figure9_thing", "caption": "a caption",
              "files": "figure9_thing.pdf; figure9_thing.png"}]
    manifest = {"figure9_thing.pdf", "figure9_thing.png", "figure0_prisma_flow.svg"}
    sizes = {"figure9_thing.pdf": 40000, "figure9_thing.png": 90000,
             "figure0_prisma_flow.svg": 12000}
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
    s = dict(sizes); s.pop("figure0_prisma_flow.svg")
    cases.append(("the external PRISMA figure missing",
                  check(index, manifest, mapping, s), "produced by src/prisma_diagram.py"))

    print("SELF TEST")
    ok = True
    for name, failures, expect in cases:
        found = any(expect in f for f in failures)
        print("  %-40s %s" % (name, found))
        ok = ok and found
    quiet = not check(index, manifest, mapping, sizes)
    print("  %-40s %s" % ("a complete set passes", quiet))
    print("  %-40s %s" % ("prose naming the gate is not a figure", quiet_prose))
    ok = ok and quiet and quiet_prose
    print("  %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        rc = self_test()
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

    print("figure check")
    print("  %d figure(s) in the index, %d external, %d file(s) in the output directory"
          % (len(index_rows), len(EXTERNAL), len(file_sizes)))
    for r in index_rows:
        print("  %-34s %s" % (r.get("name", ""), r.get("files", "")))
    if not failures:
        print("  every figure exists, is hashed, and is mapped to a submission number")
        return 0
    print("\nFAIL: %d problem(s)" % len(failures))
    for f in failures:
        print("  " + f)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
