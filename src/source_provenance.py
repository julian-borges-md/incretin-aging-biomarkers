#!/usr/bin/env python3
"""
source_provenance.py

Classifies every source file the corpus was extracted from, and reports what each provenance
checking gate can therefore be said to establish.

Why this exists. Gates nine, ten and eleven compare a row's numbers against the text retained for
its trial. They were built, and their results reported, as though "the source" were one kind of
thing. It is not. Some retained files are the publisher's own words, arriving as text from an API or
as a dump of a rendered page; others were written during this review by a session reading a page it
could not retrieve as text, and those carry the session's captions, its column labels and its choice
of what to transcribe. Against the first kind a match is independent verification that the extraction
reproduces the source. Against the second a match establishes only that the extraction reproduces the
capture, and a misreading at the capture step is reproduced rather than caught. The distinction was
nowhere recorded, so every gate's count silently mixed the two.

Classification is from signatures in the files themselves, not from their directory alone, because a
directory records the retrieval route that was attempted and not what came back: 61 of the retained
files hold no article text at all, being redirect or interstitial pages saved by a fetch that failed,
and several machine dumps sit in the companion directory beside hand written captures.

Classes, in the order they are tested. The first match wins, and the order runs from the strongest
evidence to the weakest.

  retrieval_failure  The file holds no article text. A saved redirect, consent wall or access
                     interstitial. These must not be counted as sources at all.
  session_capture    The file declares its own making: a session read a rendered page, often through
                     the accessibility tree, and wrote the values out. The capture preamble that this
                     review's own convention requires is what identifies it.
  session_notes      The session's prose notes about candidate sources, with no transcribed values.
  publisher_page     A dump of a rendered publisher page, carrying the retrieval header this
                     repository's fetch script writes (KEY, SOURCE, TITLE). The body is the
                     publisher's text, machine saved rather than retyped.
  publisher_api      Full text retrieved as text, from PubMed Central or an open access source, with
                     the section markers that route produces.
  publisher_pdf      Text extracted from a publisher PDF.
  registry_api       ClinicalTrials.gov field values retrieved by the registry script. The values are
                     the registry's; the field labels and layout are the script's.
  unclassified       No signature matched. Reported, never assumed into a class.

For auditing, the first three are session evidence and the next four are independent evidence, and
the summary reports rows by which kinds they rest on. A row resting on both is independent, because
one publisher source is enough to verify a number; a row resting only on session evidence is the
qualified case the manuscript must describe as such.

Outputs
  analysis/data/source_provenance.csv   one line per retained file: path, class, evidence, bytes
  stdout                                counts by class, and the master's 524 rows by evidence kind

The CSV is tracked. It holds paths and classifications only, never source text, so it does not carry
licensed material into the repository.

Usage
  python3 -I src/source_provenance.py
  python3 -I src/source_provenance.py --unclassified   list the files no signature matched
  exit 1 when any retained file is unclassified, or when a row rests on a retrieval failure alone
"""
import csv
import importlib.util
import os
import re
import sys

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
OUT = os.path.join(ROOT, "analysis", "data", "source_provenance.csv")
ROWS_OUT = os.path.join(ROOT, "analysis", "data", "row_source_provenance.csv")
DOC = os.path.join(ROOT, "docs", "SOURCE_PROVENANCE.md")


def _load(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Head of the file only. Every signature below is a preamble or an early structural marker, so
# reading the first few kilobytes is enough and avoids holding 439 full texts in memory at once.
HEAD = 4000

# An interstitial page saved by a failed fetch. Matched against the head, and only alongside the
# length test below, so an article that happens to discuss access control is not misread as one.
INTERSTITIAL = (
    "redirecting", "just a moment", "verifying you are human", "access denied", "are you a robot",
    "enable javascript", "page not found", "403 forbidden", "subscribe to continue",
    "checking your browser",
)
MIN_BODY = 1200   # characters of body text below which a file cannot hold an article or a table

# This review's capture convention: a capture states when it was read, from where, and by what means.
# That preamble is the signature, and it is also the evidence a reader needs, which is why the
# convention is worth keeping.
CAPTURE_DECL = (
    "with the chrome extension", "accessibility tree", "by reading the table",
    "read 2026-", "transcribed from", "read from the article full text",
)

SESSION = {"session_capture", "session_capture_undeclared", "session_notes"}
# Independent of the session's reading, and split by how much of the paper the source holds, because
# a number verified against a conference abstract is verified against less than one verified against
# a full text, and the manuscript should not claim the stronger thing for the weaker source.
FULLTEXT = {"publisher_api", "publisher_page", "publisher_pdf"}
PARTIAL = {"publisher_page_partial", "indexed_abstract", "registry_api"}
INDEPENDENT = FULLTEXT | PARTIAL

# The retrieval route each packet manifest records for its texts. This is the pipeline's own record
# of where a file came from and is better evidence than any signature read out of the file, so it is
# consulted first. It says what was ATTEMPTED, though, and the file itself says what arrived: a
# manifest claiming a full text whose file holds a redirect page is a real and detectable defect, so
# the failure test below still overrides it.
MANIFEST_CLASS = {
    "epmc_fulltext": "publisher_api",
    "direct_fulltext": "publisher_api",
    "proxy_fulltext": "publisher_page",
    "proxy_partial": "publisher_page_partial",
    "conference_abstract": "indexed_abstract",
    "registry_summary": "registry_api",
    "ctgov_entry": "registry_api",
    "already_extracted": "pointer_not_a_source",
}


def strip_header(head):
    """Drop this repository's fetch header so the body length test measures the body."""
    out = []
    for ln in head.split("\n"):
        if re.match(r"^(KEY|SOURCE|TITLE|FETCHED|STATUS):", ln):
            continue
        out.append(ln)
    return "\n".join(out)


def manifest_sources():
    """Map every packet text file to the retrieval route its packet manifest records for it."""
    import glob
    import json
    out = {}
    for p in glob.glob(os.path.join(ROOT, "work", "extraction", "packets", "*", "packet.json")):
        try:
            d = json.load(open(p))
        except (OSError, ValueError):
            continue
        for t in d.get("texts", []):
            f = t.get("file")
            if f:
                out[os.path.join(ROOT, f)] = t.get("source", "")
    return out


def classify_file(path, manifest=None):
    """Return (class, evidence) for one retained source file."""
    try:
        with open(path, errors="replace") as fh:
            head = fh.read(HEAD)
        size = os.path.getsize(path)
    except OSError as e:
        return "unclassified", f"unreadable: {e}"
    low = head.lower()
    body = strip_header(head)
    has_header = bool(re.search(r"^KEY: ", head, re.M) and re.search(r"^SOURCE: ", head, re.M))

    # 1. Retrieval failure. Both conditions, because a long article may mention any of these phrases
    #    and a short file may still be a legitimate one page registry extract.
    hit = next((p for p in INTERSTITIAL if p in low[:2500]), None)
    if hit and len(body.strip()) < MIN_BODY:
        return "retrieval_failure", f"interstitial phrase '{hit}' and body under {MIN_BODY} chars"
    if size < 200:
        return "retrieval_failure", f"file is {size} bytes"

    # 2. Session written. Tested before the header and the manifest because 7 captures carry a fetch
    #    header from the page they were read beside while their values were written out by hand; the
    #    declaration is the stronger evidence and the stricter reading.
    if re.search(r"^CAPTURED:", head, re.M):
        return "session_capture", "CAPTURED header declares the session read the page"
    decl = next((p for p in CAPTURE_DECL if p in low), None)
    if decl:
        return "session_capture", f"capture preamble declares '{decl}'"
    if os.path.basename(path).startswith("NOTES_"):
        return "session_notes", "file name marks it as the session's own notes"

    # 3. The pipeline's own record of the retrieval route, which covers every packet text.
    route = (manifest or {}).get(path)
    if route:
        k = MANIFEST_CLASS.get(route)
        if k:
            return k, f"packet manifest records the retrieval route '{route}'"
        return "unclassified", f"packet manifest records an unmapped route '{route}'"

    # 4. Signature routes, for files cited in a row's notes rather than carried by a packet.
    if has_header:
        return "publisher_page", "fetch header present, body is the saved page text"
    if re.search(r"^# NCT\d+", head, re.M) and "brief title:" in low:
        return "registry_api", "ClinicalTrials.gov field layout written by the registry script"
    if re.search(r"^## \d+", head, re.M) or "PMC" in os.path.basename(path):
        return "publisher_api", "section markers or PMC identifier from the text retrieval route"
    if os.sep + "repo" + os.sep in path:
        return "publisher_pdf", "text extracted from a publisher PDF"
    # 5. Last resort, and reported as its own class rather than folded into session_capture. A file
    #    in the companion directory with no preamble is a capture by its location only, and location
    #    is the weakest evidence this script uses: the directory records where the session put the
    #    file, not how the file was made. That these exist at all is the finding, because the review's
    #    capture convention requires a preamble and these were written without one.
    if os.sep + "companion" + os.sep in path:
        return "session_capture_undeclared", "in the companion directory with no capture preamble"
    return "unclassified", "no signature matched"


def main(argv):
    show_unclassified = "--unclassified" in argv
    lines_for = _load("extraction_attachment_check").make_source_lines()
    files_for = lines_for.files_for

    rows = list(csv.DictReader(open(MASTER, newline="")))
    per_trial = {}
    for r in rows:
        t = r["trial_id"]
        if t not in per_trial:
            per_trial[t] = files_for(t, r.get("notes", ""))

    manifest = manifest_sources()
    cls, contradicted = {}, []
    for files in per_trial.values():
        for fp in files:
            if fp in cls:
                continue
            cls[fp] = classify_file(fp, manifest)
            # The manifest says what was attempted and the file says what arrived. A packet that
            # records a full text but holds a redirect page is a defect worth naming, not a source.
            route = manifest.get(fp, "")
            if cls[fp][0] == "retrieval_failure" and "fulltext" in route:
                contradicted.append((os.path.relpath(fp, ROOT), route, cls[fp][1]))

    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "provenance_class", "evidence", "bytes"])
        for fp in sorted(cls):
            k, ev = cls[fp]
            rel = os.path.relpath(fp, ROOT)
            w.writerow([rel, k, ev, os.path.getsize(fp) if os.path.exists(fp) else ""])

    counts = {}
    for k, _ in cls.values():
        counts[k] = counts.get(k, 0) + 1
    print(f"source provenance over {len(cls)} retained file(s) cited by the master's "
          f"{len(per_trial)} trial(s)")
    for k in sorted(counts, key=lambda x: -counts[x]):
        print(f"  {k:19} {counts[k]}")

    # Rows by the kind of evidence they rest on. This is the number the manuscript needs.
    # Attribution is by the file whose lines actually carry the row's numbers, not by the best file
    # its trial happens to hold. The first draft of this script did the latter and reported the
    # SURPASS-3 MRI rows as resting on an abstract, because their packet holds conference abstracts
    # alongside the article table the session captured; their numbers are in the capture and nowhere
    # else. Reporting the strongest source retained would have overstated six rows and understated
    # the very thing this registry exists to make visible.
    attach = _load("extraction_attachment_check")
    file_lines = {}

    def lines_of(fp):
        if fp not in file_lines:
            raw = open(fp, errors="replace").read().replace("−", "-").replace("·", ".")
            file_lines[fp] = raw.split("\n")
        return file_lines[fp]

    order = ["publisher full text", "abstract or registry only", "session capture only",
             "mixed, capture and publisher", "numbers not located in any retained source"]
    kinds = dict.fromkeys(order, 0)
    session_only, weak_only = [], []
    row_class = []
    for r in rows:
        nums = attach.ident_numbers(r)
        where = set()
        if nums:
            for fp in per_trial[r["trial_id"]]:
                if fp not in cls or cls[fp][0] == "retrieval_failure":
                    continue
                if attach.matching_lines(nums, lines_of(fp)):
                    where.add(cls[fp][0])
        if not where:
            k = "numbers not located in any retained source"
        elif (where & FULLTEXT) and (where & SESSION):
            k = "mixed, capture and publisher"
        elif where & FULLTEXT:
            k = "publisher full text"
        elif where & PARTIAL and not where & SESSION:
            k = "abstract or registry only"
            weak_only.append((r["trial_id"], r["biomarker"]))
        else:
            k = "session capture only"
            session_only.append((r["trial_id"], r["biomarker"]))
        kinds[k] += 1
        row_class.append((r["trial_id"], r["biomarker"], k))
    print(f"\nmaster rows by the source their numbers were located in, of {len(rows)}")
    for k in order:
        print(f"  {k:42} {kinds[k]}")
    if contradicted:
        print(f"\nPackets recording a full text whose saved file holds none: {len(contradicted)}")
        for p, route, why in contradicted[:12]:
            print(f"  {p}  route '{route}', {why}")
    if session_only:
        print("\nRows resting on session written captures alone. A match for these establishes that "
              "the extraction reproduces the capture, not that it reproduces the publisher.")
        by_trial = {}
        for t, b in session_only:
            by_trial.setdefault(t, []).append(b)
        for t in sorted(by_trial):
            print(f"  {t[:44]:46} {', '.join(sorted(by_trial[t]))[:90]}")

    if weak_only:
        print("\nRows whose trial retained only an abstract or a registry entry. These were "
              "extracted from what the record prints, and no full text is held to check them "
              "against.")
        by_trial = {}
        for t, b in weak_only:
            by_trial.setdefault(t, []).append(b)
        for t in sorted(by_trial):
            print(f"  {t[:44]:46} {', '.join(sorted(by_trial[t]))[:90]}")

    with open(ROWS_OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["trial_id", "biomarker", "located_in"])
        w.writerows(row_class)

    bad = [fp for fp in cls if cls[fp][0] == "unclassified"]
    if bad or show_unclassified:
        print(f"\nUnclassified files: {len(bad)}")
        for fp in sorted(bad)[:40]:
            print(f"  {os.path.relpath(fp, ROOT)}  ({cls[fp][1]})")

    # The capture convention is enforced from here on rather than merely recommended. A capture
    # whose provenance rests on its directory alone is weak evidence, and the two that exist are
    # pre-existing: they are written up in the document below, which doubles as the allowlist, so
    # they do not fail the chain while a NEW capture written without a preamble does.
    allowed = set()
    if os.path.exists(DOC):
        for ln in open(DOC, errors="replace"):
            allowed.update(re.findall(r"work/fulltext/[^\s`|)]+\.txt", ln))
    undeclared = sorted(os.path.relpath(fp, ROOT) for fp in cls
                        if cls[fp][0] == "session_capture_undeclared")
    new_undeclared = [p for p in undeclared if p not in allowed]
    if undeclared:
        print(f"\nCaptures with no provenance preamble: {len(undeclared)}")
        for p in undeclared:
            print(f"  {'written up ' if p in allowed else 'NOT WRITTEN UP'} {p}")
        if new_undeclared:
            print("  A capture must state when it was read, from where and by what means. Add a "
                  "CAPTURED header, or write the file up in docs/SOURCE_PROVENANCE.md if its "
                  "making is no longer recoverable.")
    print(f"\nwritten {os.path.relpath(OUT, ROOT)} and {os.path.relpath(ROWS_OUT, ROOT)}")
    sys.exit(1 if (bad or new_undeclared) else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
