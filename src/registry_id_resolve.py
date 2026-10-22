#!/usr/bin/env python3
"""
registry_id_resolve.py

Resolves a registry identifier for the included trials that carry none, from the publisher's own
record of it rather than from a search, and verifies each candidate before accepting it. Writes
analysis/data/trial_registry_ids.csv, which is tracked and which src/corpus_registry_harvest.py
reads as its fourth lookup.

WHY. Gate twenty five compares a row's timepoint with the timepoint its trial registered as its
primary endpoint. Its measured ceiling is the 32 trials, 143 rows, for which no registry identifier
exists anywhere in the repository: 27 trials carry one in their label, 14 in the extraction notes of
one of their rows, 3 in the extraction ledger, and the rest in none of the three. Decision D2 of the
Director register records that arithmetic and recommended deferring the work to a session with
nothing else blocked.

TWO ROUTES, both of which make the paper the source of its own identifier.

  annotation  Europe PMC's annotation of the article, which records the accession number it found
              with the sentence it was found in and the section it was in. For Kelly 2012 that reads
              `Abstract: This study is registered on [NCT00546728]`. This is the publisher's text,
              machine extracted, and it is the stronger route
  capture     a scan of the source text retained for the trial, accepting an NCT only where the
              surrounding 120 characters say that this is a registration. Without that condition the
              route would attribute to a trial any identifier its discussion happens to cite, which
              in this literature means the large cardiovascular outcome trials

THREE CHECKS, in the order of how much they establish. The first version of this script had only the
third, and it assigned ONE registration to both STEP 2 and STEP 3, and the same one to the two
survodutide trials 1404-0002 and 1404-0036. Two trials cannot share a registration. The drug check
could not see the error, because STEP 2 and STEP 3 are both semaglutide against placebo, so a check
that passes for every candidate separates nothing.

  identifier   the registry's own `orgStudyIdInfo.id`, or one of its secondary ids, EQUALS the
               trial's label once punctuation is removed. This resolves the survodutide pair:
               NCT04153929 is registered as 1404-0002 and NCT04667377 as 1404-0036. An identifier
               match is the strongest evidence available and verifies on its own
  label        the trial's label appears inside one of those ids, the acronym or a title, with the
               match not followed by another digit so that `STEP 2` does not match `STEP 25`. This
               separates candidates rather than verifying one, and it is what tells the STEP trials
               apart: NCT03552757 and NCT03611582 carry their numbers in their titles
  drug         the registration's interventions or arm labels name the trial's drug, or a
               development code the registry itself declares to be that drug

The comparator is checked the same way and reported, but it is not required: a registration often
names the comparator only as placebo or standard of care. Enrollment is reported as a ratio against
the row's arm sizes and never decides a verdict, because a row may come from a substudy of a much
larger trial, which is the Drum Tower case gate twenty five found.

THE SYNONYM TABLE IS DERIVED, NOT ASSERTED. A registration may predate the international
nonproprietary name: NCT04153929 names its intervention `BI 456906` and nothing else, so a check for
`survodutide` fails against the correct record. The equivalences are read out of the registry records
themselves, from the `otherNames` the registry states beside each intervention, over every record
this repository holds and every record this run fetches. On this corpus that yields survodutide and
BI 456906 from the sibling trial NCT04667377, which names both, and also dulaglutide and LY2189265,
tirzepatide and LY3298176, cotadutide and MEDI0382. Nothing is written down here that a registry
record does not state.

WHAT THIS DOES NOT DO. It does not search the registry by title or population. A search would find a
plausible record for almost every trial, and plausible is the failure mode this file exists to avoid.
A trial whose registration cannot be found from its own text stays unresolved and is reported as
such, which is itself a finding: its prespecification cannot be verified at all.

Usage
  python3 -I src/registry_id_resolve.py            resolve, verify, write the table
  python3 -I src/registry_id_resolve.py --dry-run  resolve and verify, write nothing
  exit 1 when a candidate is found but cannot be verified, which needs a human reading
"""
import collections
import csv
import glob
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "analysis", "data", "extraction_master.csv")
OUT = os.path.join(ROOT, "analysis", "data", "trial_registry_ids.csv")
HELD = os.path.join(ROOT, "work", "fulltext", "registry_corpus")
NCT = re.compile(r"NCT\d{8}")
PAUSE = 0.34

EPMC_SEARCH = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
               "?query={}&resultType=core&format=json&pageSize=1")
EPMC_ANNOT = ("https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds"
              "?articleIds={}&type=Accession%20Numbers&format=JSON")
CTG = "https://clinicaltrials.gov/api/v2/studies/{}"

# A registration sentence, not a citation. These are the phrasings this corpus uses.
REGISTERED = re.compile(
    r"(registered|registration|registry|clinicaltrials\.gov|trial identifier|"
    r"identifier[:s ]|number[:s ]|ctri|isrctn)", re.I)
# A development code: a short letter prefix and a run of digits, long enough not to be a dose.
CODE = re.compile(r"^[a-z]{1,4}\d{4,8}$")


def _load(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_harvest = _load("corpus_registry_harvest")
_arm = _load("arm_attribution_check")
_attach = _load("extraction_attachment_check")
tokens = _arm.tokens


def collapse(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def get_json(url, timeout=45):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.loads(fh.read().decode())


def epmc_ids(doi, pmid):
    """(source, extId) for the Europe PMC record of this article, or (None, None)."""
    if pmid:
        return "MED", pmid
    if not doi:
        return None, None
    try:
        d = get_json(EPMC_SEARCH.format(urllib.parse.quote(f'DOI:"{doi}"')))
    except Exception:  # noqa: BLE001 - a lookup failure is reported, never fatal
        return None, None
    hits = (d.get("resultList") or {}).get("result") or []
    if not hits:
        return None, None
    return hits[0].get("source"), hits[0].get("id")


def annotation_candidates(source, ext_id):
    """[(nct, evidence)] from Europe PMC's accession annotations of the article."""
    if not source or not ext_id:
        return []
    try:
        d = get_json(EPMC_ANNOT.format(f"{source}:{ext_id}"))
    except Exception:  # noqa: BLE001
        return []
    out = []
    for rec in d or []:
        for a in rec.get("annotations") or []:
            exact = (a.get("exact") or "").strip()
            if not NCT.fullmatch(exact):
                continue
            ev = (f"{a.get('section', '?')}: {(a.get('prefix') or '').strip()} "
                  f"[{exact}] {(a.get('postfix') or '').strip()}")
            out.append((exact, " ".join(ev.split())[:220]))
    return out


def capture_candidates(lines_for, trial, notes):
    """[(nct, evidence)] from the retained source text, registration context required."""
    out = []
    for ln in lines_for(trial, notes):
        for m in NCT.finditer(ln):
            lo, hi = max(0, m.start() - 120), m.end() + 60
            ctx = " ".join(ln[lo:hi].split())
            if REGISTERED.search(ctx):
                out.append((m.group(0), ctx[:220]))
    return out


def registry_record(nct):
    try:
        return get_json(CTG.format(nct))
    except urllib.error.HTTPError as e:
        return {"__error__": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"__error__": f"{type(e).__name__}: {e}"}


def ident_fields(rec):
    """(identifiers, titles) the registry gives this trial."""
    idm = (rec.get("protocolSection", {}) or {}).get("identificationModule", {}) or {}
    ids = [idm.get("orgStudyIdInfo", {}).get("id", "")]
    ids += [s.get("id", "") for s in idm.get("secondaryIdInfos", []) or []]
    titles = [idm.get("acronym", ""), idm.get("briefTitle", ""), idm.get("officialTitle", "")]
    return [i for i in ids if i], [t for t in titles if t]


def identifier_match(trial, rec):
    """The registry registers this trial under exactly the label the review uses for it."""
    lab = collapse(trial)
    if len(lab) < 6:
        return False
    return any(collapse(i) == lab for i in ident_fields(rec)[0])


def label_match(trial, rec):
    """The label appears in the record's identifiers or titles. Separates, does not verify."""
    lab = collapse(trial)
    if len(lab) < 4:
        return False
    ids, titles = ident_fields(rec)
    for f in ids + titles:
        hay = collapse(f)
        for m in re.finditer(re.escape(lab), hay):
            if not hay[m.end():m.end() + 1].isdigit():
                return True
    return False


def intervention_strings(rec):
    """Every name the registration gives its interventions and arms."""
    arms = (rec.get("protocolSection", {}) or {}).get("armsInterventionsModule", {}) or {}
    out = []
    for i in arms.get("interventions", []) or []:
        out += [i.get("name", ""), i.get("description", "")]
        out += i.get("otherNames", []) or []
    for g in arms.get("armGroups", []) or []:
        out += [g.get("label", ""), g.get("description", "")]
    return [s for s in out if s]


def synonyms(records, keep=None):
    """
    drug token -> development codes the REGISTRY itself declares to be that drug.

    Read from the otherNames a record states beside an intervention: where one side carries a drug
    word and the other a development code, the registry has declared them the same thing. Nothing
    is asserted here that a record does not state.

    `keep` restricts the keys to the drug words this corpus actually studies, taken from the
    master's own drug column. Without it the derivation pairs every word in an intervention group
    with every code in it, and a record whose otherNames carry a marketing authorisation block
    yields entries such as `holder` and `number`. Those are harmless to the drug check, which only
    ever asks about a trial's own drug, but a derived table that states things nobody means is a
    table the next reader has to disbelieve in parts.
    """
    out = collections.defaultdict(set)
    for rec in records:
        arms = (rec.get("protocolSection", {}) or {}).get("armsInterventionsModule", {}) or {}
        for i in arms.get("interventions", []) or []:
            group = [i.get("name", "")] + (i.get("otherNames", []) or [])
            words, codes = set(), set()
            for g in group:
                words |= tokens(g)
                for part in re.split(r"[^A-Za-z0-9]+", g or ""):
                    if CODE.fullmatch(part.lower()):
                        codes.add(part.lower())
                if CODE.fullmatch(collapse(g)):
                    codes.add(collapse(g))
            for w in words:
                if keep is None or w in keep:
                    out[w] |= codes
    return {k: v for k, v in out.items() if v}


def held_records():
    out = []
    for p in sorted(glob.glob(os.path.join(HELD, "*.json"))):
        try:
            out.append(json.load(open(p)))
        except Exception:  # noqa: BLE001
            continue
    return out


def verify(rec, trial, drug, comp, n_total, syn):
    """Return (verdict, detail). Identifier equality verifies; otherwise the drug must be named."""
    if "__error__" in rec:
        return "unverified", f"the registry record could not be retrieved: {rec['__error__']}"
    p = rec.get("protocolSection", {})
    blob = collapse(" ".join(intervention_strings(rec)))
    enrol = ((p.get("designModule", {}) or {}).get("enrollmentInfo", {}) or {}).get("count")
    ratio = f"{enrol}/{n_total}" if enrol and n_total else "n/a"

    d_tok = tokens(drug)
    c_tok = tokens(comp) - d_tok
    d_hit = sorted(t for t in d_tok if any(f in blob for f in {t} | syn.get(t, set())))
    c_hit = sorted(t for t in c_tok if any(f in blob for f in {t} | syn.get(t, set())))
    comp_note = (f" and comparator {c_hit}" if c_hit else
                 "; the comparator is not named, which is usual")

    if identifier_match(trial, rec):
        ids = ident_fields(rec)[0]
        return "verified", (f"the registration's own identifier is this review's label for the "
                            f"trial ({ids[0]})"
                            + (f"; it also names {d_hit}" if d_hit else
                               f"; it names the drug by development code only, with "
                               f"{sorted(d_tok)} absent from the intervention names")
                            + f"; enrollment {ratio}")
    if not d_tok:
        return "unverified", "the trial's drug name has no word long enough to match on"
    if not d_hit:
        return "unverified", (f"the registration names none of {sorted(d_tok)} nor a declared "
                              f"code for them; enrollment {ratio}")
    return "verified", f"the registration names {d_hit}{comp_note}; enrollment {ratio}"


def trial_meta(rows):
    meta = {}
    for r in rows:
        m = meta.setdefault(r["trial_id"], {"doi": "", "pmid": "", "drug": "", "comp": "",
                                            "n": 0, "rows": 0, "notes": []})
        m["rows"] += 1
        m["notes"].append(r.get("notes") or "")
        for k, c in (("doi", "doi"), ("pmid", "pmid")):
            v = (r.get(c) or "").strip()
            if v and v.upper() != "NA" and not m[k]:
                m[k] = v
        if not m["drug"]:
            m["drug"] = r.get("drug") or ""
        if not m["comp"]:
            m["comp"] = r.get("comparator") or ""
        try:
            m["n"] = max(m["n"], int(float(r.get("n_tx") or 0)) + int(float(r.get("n_ctrl") or 0)))
        except ValueError:
            pass
    return meta


def main(argv):
    dry = "--dry-run" in argv
    res = _harvest.resolve()
    unresolved = sorted(t for t, (s, ids) in res.items() if s == "none")
    meta = trial_meta(list(csv.DictReader(open(MASTER, newline=""))))
    lines_for = _attach.make_source_lines()

    # How many of the unresolved trials each article accounts for. An article reporting two of them
    # cannot supply one registration to both.
    sharing = collections.Counter()
    for t in unresolved:
        key = meta[t]["pmid"] or meta[t]["doi"]
        if key:
            sharing[key] += 1

    print(f"trials with no registry identifier: {len(unresolved)}")

    # PASS ONE: gather candidates and fetch every distinct record. Separated from the decision so
    # that the synonym table is built from everything this run has seen, whatever order the trials
    # come in: 1404-0002 is decided before 1404-0036, and it is 1404-0036's record that states
    # survodutide and BI 456906 to be the same drug.
    found, cache = {}, {}
    for t in unresolved:
        m = meta[t]
        src, ext = epmc_ids(m["doi"], m["pmid"])
        cands = [(n, "annotation", e) for n, e in annotation_candidates(src, ext)]
        if not cands:
            cands = [(n, "capture", e)
                     for n, e in capture_candidates(lines_for, t, " ".join(m["notes"]))]
        time.sleep(PAUSE)
        uniq = []
        for nct, route, ev in cands:
            if nct not in [u[0] for u in uniq]:
                uniq.append((nct, route, ev))
            if nct not in cache:
                cache[nct] = registry_record(nct)
                time.sleep(PAUSE)
        found[t] = uniq
    print(f"  candidate records fetched: {len(cache)}")

    corpus_drugs = set()
    for r in csv.DictReader(open(MASTER, newline="")):
        corpus_drugs |= tokens(r.get("drug") or "")
    syn = synonyms(held_records() + list(cache.values()), keep=corpus_drugs)
    print(f"  drug codes the registry declares, over the {len(corpus_drugs)} drug words this "
          f"corpus studies: { {k: sorted(v) for k, v in sorted(syn.items())} }")

    # PASS TWO: decide.
    out, counts = [], collections.Counter()
    for t in unresolved:
        m, uniq = meta[t], found[t]
        if not uniq:
            counts["none_found"] += 1
            out.append({"trial_id": t, "nct": "", "route": "", "verdict": "none_found",
                        "rows": m["rows"],
                        "detail": "no registration identifier in the article's annotations or in "
                                  "the retained source text", "evidence": ""})
            print(f"  none_found {t[:44]:46} rows {m['rows']}")
            continue

        shared = sharing.get(m["pmid"] or m["doi"], 1)
        ident = [n for n, _, _ in uniq if identifier_match(t, cache[n])]
        labelled = [n for n, _, _ in uniq if label_match(t, cache[n])]
        if len(ident) == 1:
            nct, how = ident[0], "identifier"
        elif len(labelled) == 1:
            nct, how = labelled[0], "label"
        elif len(uniq) == 1 and shared == 1:
            nct, how = uniq[0][0], "sole candidate"
        else:
            why = (f"the article states {len(uniq)} registrations and the trial's label matches "
                   f"{len(labelled)} of them" if len(uniq) > 1 else
                   f"{shared} unresolved trials share this article and its single registration")
            counts["ambiguous"] += 1
            out.append({"trial_id": t, "nct": "", "route": "", "verdict": "ambiguous",
                        "rows": m["rows"],
                        "detail": f"{why}; candidates {[n for n, _, _ in uniq]}",
                        "evidence": uniq[0][2]})
            print(f"  ambiguous  {t[:44]:46} {','.join(n for n, _, _ in uniq)}")
            continue

        route, ev = next((r, e) for n, r, e in uniq if n == nct)
        verdict, detail = verify(cache[nct], t, m["drug"], m["comp"], m["n"], syn)
        others = sorted({n for n, _, _ in uniq} - {nct})
        counts[verdict] += 1
        out.append({"trial_id": t, "nct": nct, "route": route, "verdict": verdict,
                    "rows": m["rows"],
                    "detail": f"separated by {how}; " + detail
                              + (f"; other registrations in the article: {others}"
                                 if others else ""),
                    "evidence": ev})
        print(f"  {verdict:10} {t[:44]:46} {nct}  {route:10} by {how:14} {detail[:56]}")

    print("\nsummary")
    for k, v in counts.most_common():
        print(f"  {v:3}  {k}")
    gained = sum(r["rows"] for r in out if r["verdict"] == "verified")
    print(f"  rows brought into gate twenty five's reach: {gained}")

    if not dry:
        with open(OUT, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["trial_id", "nct", "route", "verdict", "rows",
                                               "detail", "evidence"])
            w.writeheader()
            for r in sorted(out, key=lambda x: (x["verdict"], x["trial_id"])):
                w.writerow({k: r[k] for k in w.fieldnames})
        print(f"  written {os.path.relpath(OUT, ROOT)}")
    return 1 if counts["unverified"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
