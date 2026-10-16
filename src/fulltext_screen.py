#!/usr/bin/env python3
"""
fulltext_screen.py

Full text screening of the pool assembled by src/build_fulltext_pool.py, by
the same three agent design as title and abstract screening (two blinded
reviewer agents, different local models, temperature 0, fixed seed; a third
adjudicating), under criteria version 2 plus a full text addendum. Each
reviewer sees the best available text for the record:

  epmc_fulltext        open access full text harvested from Europe PMC
                       (work/fulltext/pool/, 2,000 characters or more)
  direct_fulltext      full text fetched without authentication from the
                       publisher page or a preprint server
                       (work/fulltext/direct/, status fulltext or
                       fulltext_preprint in its manifest)
  ctgov_entry          ClinicalTrials.gov entry rendered to text
                       (work/fulltext/registry/)
  conference_abstract  the record itself: a conference abstract is its own
                       full text
  registry_summary     the record itself: a registry entry from a register
                       without a public API (via ICTRP)
  awaiting_fulltext    no text available yet (closed access, not in Europe
                       PMC, title search): not screened in this stage
  already_extracted    trial already in the extraction master: skipped

The reviewers return, in addition to the decision, the treatment duration in
weeks, the comparator, and the inventory biomarkers with numerical results in
the document, so that the extraction stage inherits a map of what each text
holds. Context window is sized to the text (8k up to 20,000 characters, 16k
above; text capped at 48,000 characters, registry entries at 30,000).

Resumable: decisions already on disk are not recomputed. Per record files
stay untracked beside the exports (fulltext_decisions_A.csv, _B.csv,
fulltext_adjudication_002.csv); FULLTEXT_SCREENING_SUMMARY.md is committed.

Usage, from the repository root:
  python3 -I src/fulltext_screen.py screen [--reviewer A|B] [--source NAME] [--limit N]
  python3 -I src/fulltext_screen.py adjudicate
  python3 -I src/fulltext_screen.py summarise
  python3 -I src/fulltext_screen.py check        state of every chain (built in control, read only)
"""
import csv
import json
import os
import re
import sys
import time
from collections import Counter

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))
import screen_titles as st  # noqa: E402

POOL = os.path.join(ROOT, "search/screening/fulltext_pool_2026-10-16.csv")
EPMC_MANIFEST = os.path.join(ROOT, "work/fulltext/pool/MANIFEST_epmc_2026-10-16.csv")
CTGOV_MANIFEST = os.path.join(ROOT, "work/fulltext/registry/MANIFEST_ctgov_2026-10-16.csv")
DIRECT_MANIFEST = os.path.join(ROOT, "work/fulltext/direct/MANIFEST_direct_2026-10-16.csv")
PROXY_MANIFEST = os.path.join(ROOT, "work/fulltext/proxy/MANIFEST_proxy_2026-10-16.csv")
OUTDIR = os.path.join(ROOT, "search/screening")
SUMMARY = os.path.join(OUTDIR, "FULLTEXT_SCREENING_SUMMARY.md")
CAP_FULLTEXT = 48000
CAP_REGISTRY = 30000
SOURCE_ORDER = ["conference_abstract", "registry_summary", "ctgov_entry", "epmc_fulltext", "direct_fulltext",
                "proxy_fulltext", "proxy_partial"]
# proxy_fulltext: publisher page text captured in the browser through the institutional
# route (src/proxy_harvest.py manifest, status fulltext: three section marks and more than
# 12,000 characters). proxy_partial: a capture of at least 2,000 characters that did not meet
# that rule (abstract pages, but also complete short documents such as letters, comments and
# reviews without methods sections); the label tells the reviewers so. The capture is the
# page's visible text, so the site navigation before the abstract heading, the reference list
# and publisher boilerplate lines are removed before the text is capped (patterns below).
PROXY_KEY = re.compile(r"^pool([12])_n(\d+)$")
PROXY_ABSTRACT = re.compile(r"^\s*(Abstract|Summary|ABSTRACT)\s*$", re.M)
PROXY_REFERENCES = re.compile(r"^\s*(References|REFERENCES|Bibliography)\s*$", re.M)
PROXY_NOISE = re.compile(r"^(Download: Download (full-size|high-res) image.*|Opens in a new window|Show more|Share|Cite"
                         r"|View PDF|Google Scholar|.*View in ScopusGoogle Scholar.*)$")

FULLTEXT_ADDENDUM = """
Full text stage. You now have the complete document (a journal article, a
registry entry, or a conference abstract, as labelled). Judge every criterion
from the whole document, not from the abstract alone. Exclude only when the
document shows that a criterion fails; if a criterion still cannot be judged
(for example a registry entry without results, or a conference abstract),
include and say so in the reason. Report, from the document:
  duration_weeks        the treatment duration in weeks as a number (convert
                        months and years; null if not stated)
  comparator            the comparator arm(s) in a few words
  biomarkers_reported   the inventory biomarkers for which the document gives
                        numerical results (a list of short names such as
                        hsCRP, IL-6, TNF-alpha, HOMA-IR, ALT, liver fat,
                        body fat, lean mass, NT-proBNP; empty list if none)
Answer with JSON only, exactly this shape:
{"decision": "include" or "exclude",
 "failed_criteria": [letters among D P I O T that clearly fail, empty if none],
 "reason": one sentence of at most 40 words,
 "duration_weeks": number or null,
 "comparator": short text,
 "biomarkers_reported": [short names]}
"""


def system_prompt():
    st.CRITERIA_VERSION = "v2"
    return st.criteria_text() + FULLTEXT_ADDENDUM


def read_manifest(path, key):
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            out[(r["pool"], int(r["n"]))] = r
    return out


def read_proxy_manifest():
    """Captures made through the institutional route, keyed like the other manifests."""
    if not os.path.exists(PROXY_MANIFEST):
        return {}
    out = {}
    with open(PROXY_MANIFEST, newline="") as fh:
        for r in csv.DictReader(fh):
            m = PROXY_KEY.match(r["key"])
            if m:
                out[(m.group(1), int(m.group(2)))] = r
    return out


def proxy_text(path):
    """Page text without the capture header (KEY, SOURCE, TITLE), the navigation before
    the abstract heading (only when that heading sits in the first quarter of the page),
    the reference list (first References heading after 40 percent of the page) and the
    boilerplate lines in PROXY_NOISE. Deterministic; the chars kept are logged per record."""
    raw = open(path).read()
    body = raw.split("\n\n", 1)[1] if "\n\n" in raw else raw
    m = PROXY_ABSTRACT.search(body)
    start = m.start() if m and m.start() < len(body) * 0.25 else 0
    m = PROXY_REFERENCES.search(body, int(len(body) * 0.4))
    end = m.start() if m else len(body)
    lines = [ln for ln in body[start:end].split("\n") if not PROXY_NOISE.match(ln.strip())]
    return "\n".join(lines)


def load_items():
    """Pool records with their text source and text."""
    if not os.path.exists(POOL):
        print("FAIL: pool file missing; run src/build_fulltext_pool.py"); sys.exit(1)
    pool = list(csv.DictReader(open(POOL)))
    if len(pool) != 547:
        print(f"FAIL: pool has {len(pool)} rows, expected 547"); sys.exit(1)
    epmc = read_manifest(EPMC_MANIFEST, None)
    ctgov = read_manifest(CTGOV_MANIFEST, None)
    direct = read_manifest(DIRECT_MANIFEST, None)
    proxy = read_proxy_manifest()
    # abstracts come from the gated exports through the screening parser
    abstracts = {}
    for pool_name in ("embase", "batch2"):
        st.POOL = pool_name
        for r in st.parse_ris():
            abstracts[("1" if pool_name == "embase" else "2", r["n"])] = r
    st.POOL = "embase"
    items = []
    for r in pool:
        key = (r["pool"], int(r["n"]))
        rec = abstracts.get(key, {})
        label = f"{r['title']}"
        source, text = "awaiting_fulltext", ""
        if r["already_extracted"] == "yes":
            source = "already_extracted"
        elif r["route"] == "abstract_only":
            source = "conference_abstract"
            text = f"Document type: conference abstract (this is the complete record)\nYear: {r['year']}\nTitle: {r['title']}\nAbstract: {rec.get('abstract', '')}"
        elif r["route"] == "registry_record":
            m = ctgov.get(key)
            if m and m["status"] in ("ok", "exists") and os.path.exists(m["file"]):
                source = "ctgov_entry"
                text = "Document type: ClinicalTrials.gov registry entry\n" + open(m["file"]).read()[:CAP_REGISTRY]
            else:
                source = "registry_summary"
                text = f"Document type: trial registry entry as indexed (register {r['registry_id'] or 'unknown'}; no further text available)\nYear: {r['year']}\nTitle: {r['title']}\nSummary: {rec.get('abstract', '')}"
        else:
            m = epmc.get(key)
            d = direct.get(key)
            if m and m["status"] in ("ok", "exists") and int(m.get("txt_chars") or 0) >= 2000 and os.path.exists(m["file"]):
                source = "epmc_fulltext"
                text = f"Document type: journal article, full text\nTitle: {r['title']}\n\n" + open(m["file"]).read()[:CAP_FULLTEXT]
            elif d and d["status"].startswith("fulltext") and d["file"] and os.path.exists(d["file"]):
                source = "direct_fulltext"
                kind = "preprint, full text" if d["status"].endswith("_preprint") else "journal article, full text as published on the publisher site"
                text = f"Document type: {kind}\nTitle: {r['title']}\n\n" + open(d["file"]).read()[:CAP_FULLTEXT]
            else:
                px = proxy.get(key)
                if px and px["status"] == "fulltext" and os.path.exists(px["file"]):
                    source = "proxy_fulltext"
                    text = (f"Document type: journal article, full text as published on the publisher site "
                            f"through the institutional route\nTitle: {r['title']}\n\n" + proxy_text(px["file"])[:CAP_FULLTEXT])
                elif px and px["status"] == "partial" and int(px["chars"] or 0) >= 2000 and os.path.exists(px["file"]):
                    source = "proxy_partial"
                    text = (f"Document type: publisher or index page as captured in the browser. This may be the complete "
                            f"document (a letter, editorial, comment or review without methods sections) or only the abstract "
                            f"of a longer article whose full text was not captured; judge from what is present\n"
                            f"Title: {r['title']}\n\n" + proxy_text(px["file"])[:CAP_FULLTEXT])
        items.append(dict(pool=r["pool"], n=int(r["n"]), key=f"{r['pool']}-{r['n']}", source=source, text=text,
                          title=r["title"], matched_known=r["matched_known"] in ("True", "yes", "1"),
                          study_group=r["study_group"], route=r["route"]))
    return items


def ctx_for(text):
    return 8192 if len(text) <= 20000 else 16384


def parse(raw):
    dec, failed, reason = st.parse_decision(raw)
    try:
        d = json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, flags=re.S)
        try:
            d = json.loads(m.group(0)) if m else {}
        except Exception:
            d = {}
    if not isinstance(d, dict):
        d = {}
    dur = d.get("duration_weeks")
    dur = "" if dur in (None, "", "null") else str(dur)[:12]
    bio = d.get("biomarkers_reported", [])
    if isinstance(bio, str):
        bio = [bio]
    bio = ";".join(str(b).strip()[:30] for b in bio if str(b).strip())[:300]
    comp = str(d.get("comparator", ""))[:120].replace("\n", " ")
    return dec, failed, reason, dur, comp, bio


def dec_path(rev):
    return os.path.join(OUTDIR, f"fulltext_decisions_{rev}.csv")


ADJ_PATH = os.path.join(OUTDIR, "fulltext_adjudication_002.csv")
# When this file exists, the adjudication of disagreements is delegated to the reviewer it names
# (the session's cloud model, on the Director's instruction) and the local adjudicator is not called;
# the delegated reviewer writes the same adjudication file through src/session_adjudicate.py.
ADJUDICATOR_FILE = os.path.join(OUTDIR, "ADJUDICATOR.txt")
FIELDS = ["key", "pool", "n", "source", "decision", "failed", "reason", "duration_weeks", "comparator", "biomarkers_reported", "chars", "seconds"]


def read_dec(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="") as fh:
        return {r["key"]: r for r in csv.DictReader(fh)}


def screen(cfg, items, reviewer, sources, limit=None):
    model = cfg["screeners"][reviewer]
    path = dec_path(reviewer)
    done = read_dec(path)
    todo = [it for it in items if it["source"] in sources and it["key"] not in done]
    if limit:
        todo = todo[:limit]
    print(f"reviewer {reviewer}: {len(done)} done, {len(todo)} to screen in {sources}", flush=True)
    new_file = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        t_all = time.time()
        for i, it in enumerate(todo, 1):
            c = dict(cfg, num_ctx=ctx_for(it["text"]), num_predict=400)
            t0 = time.time()
            try:
                raw = st.ollama_chat(c, model, system_prompt(), it["text"])
                dec, failed, reason, dur, comp, bio = parse(raw)
            except RuntimeError as e:
                # The server refused every attempt for this record (seen 2026-10-16: Ollama's
                # "prediction aborted, token repeat limit reached", deterministic at temperature 0).
                # The record keeps a row with decision "error" so the run goes on; an "error" row is a
                # disagreement for the adjudicator, never an include or an exclude.
                dec, failed, reason, dur, comp, bio = "error", "", f"model error: {str(e)[:160]}", "", "", ""
                print(f"  {reviewer}: {it['key']} recorded as error after repeated server failures", flush=True)
            w.writerow(dict(key=it["key"], pool=it["pool"], n=it["n"], source=it["source"], decision=dec, failed=failed,
                            reason=reason, duration_weeks=dur, comparator=comp, biomarkers_reported=bio,
                            chars=len(it["text"]), seconds=f"{time.time() - t0:.1f}"))
            fh.flush()
            if i % 5 == 0 or i == len(todo):
                print(f"  {reviewer}: {i}/{len(todo)} ({(time.time() - t_all) / i:.1f} s per record)", flush=True)


def adjudicate(cfg, items):
    if os.path.exists(ADJUDICATOR_FILE):
        print("adjudication delegated:", open(ADJUDICATOR_FILE).read().strip().splitlines()[0], flush=True)
        print("nothing done here; pending disagreements: python3 -I src/session_adjudicate.py list", flush=True)
        return
    A, B = read_dec(dec_path("A")), read_dec(dec_path("B"))
    done = read_dec(ADJ_PATH)
    dis = [it for it in items if it["key"] in A and it["key"] in B and A[it["key"]]["decision"] != B[it["key"]]["decision"]
           and it["key"] not in done]
    print(f"adjudicator: {len(done)} done, {len(dis)} disagreements", flush=True)
    new_file = not os.path.exists(ADJ_PATH)
    system = system_prompt() + ("\nTwo independent reviewers disagreed on this document. Their decisions and reasons follow "
                                "the document. Decide independently against the criteria; do not defer to either reviewer by default.")
    with open(ADJ_PATH, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["key", "pool", "n", "source", "decision_A", "decision_B", "decision", "failed", "reason",
                                           "duration_weeks", "comparator", "biomarkers_reported", "seconds"])
        if new_file:
            w.writeheader()
        for i, it in enumerate(dis, 1):
            a, b = A[it["key"]], B[it["key"]]
            user = it["text"] + f"\n\nReviewer 1: {a['decision']} ({a['failed'] or 'none'}): {a['reason']}\nReviewer 2: {b['decision']} ({b['failed'] or 'none'}): {b['reason']}"
            c = dict(cfg, num_ctx=ctx_for(user), num_predict=400)
            t0 = time.time()
            raw = st.ollama_chat(c, cfg["adjudicator"], system, user)
            dec, failed, reason, dur, comp, bio = parse(raw)
            w.writerow(dict(key=it["key"], pool=it["pool"], n=it["n"], source=it["source"], decision_A=a["decision"], decision_B=b["decision"],
                            decision=dec, failed=failed, reason=reason, duration_weeks=dur, comparator=comp, biomarkers_reported=bio,
                            seconds=f"{time.time() - t0:.1f}"))
            fh.flush()
            if i % 5 == 0 or i == len(dis):
                print(f"  adjudicated {i}/{len(dis)}", flush=True)


def summarise(cfg, items):
    A, B, ADJ = read_dec(dec_path("A")), read_dec(dec_path("B")), read_dec(ADJ_PATH)
    by_source = Counter(it["source"] for it in items)
    both = [it for it in items if it["key"] in A and it["key"] in B]
    errors = [it for it in both if "error" in (A[it["key"]]["decision"], B[it["key"]]["decision"])]
    pairs = [(A[it["key"]]["decision"], B[it["key"]]["decision"]) for it in both if it not in errors]
    k, se = st.kappa(pairs)
    agree = sum(1 for a, b in pairs if a == b)
    final = {}
    for it in both:
        key = it["key"]
        if A[key]["decision"] == B[key]["decision"] and A[key]["decision"] != "error":
            final[key] = A[key]["decision"]
        elif key in ADJ:
            final[key] = ADJ[key]["decision"]
    adjudicator = ("a third agent adjudicating disagreements (local model named in the untracked configuration file)"
                   if not os.path.exists(ADJUDICATOR_FILE) else
                   "disagreements adjudicated by " + open(ADJUDICATOR_FILE).read().strip().splitlines()[0])
    lines = ["# Full text screening of the pool\n",
             "Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), "
             + adjudicator + ", criteria v2 plus the full text addendum. "
             "Produced by `src/fulltext_screen.py summarise`.\n",
             "| Text source | Records | Screened by both | Final include | Final exclude | Pending |\n|---|---|---|---|---|---|"]
    for src in SOURCE_ORDER + ["awaiting_fulltext", "already_extracted"]:
        sub = [it for it in items if it["source"] == src]
        sb = [it for it in sub if it["key"] in A and it["key"] in B]
        inc = sum(1 for it in sb if final.get(it["key"]) == "include")
        exc = sum(1 for it in sb if final.get(it["key"]) == "exclude")
        lines.append(f"| {src} | {len(sub)} | {len(sb)} | {inc} | {exc} | {len(sb) - inc - exc} |")
    lines.append(f"\n| Quantity | Value |\n|---|---|")
    lines.append(f"| Screened by both reviewers | {len(both)} of {sum(by_source[s] for s in SOURCE_ORDER)} with a text |")
    lines.append(f"| Reviewer 1 include / exclude | {sum(1 for a, _ in pairs if a == 'include')} / {sum(1 for a, _ in pairs if a == 'exclude')} |")
    lines.append(f"| Reviewer 2 include / exclude | {sum(1 for _, b in pairs if b == 'include')} / {sum(1 for _, b in pairs if b == 'exclude')} |")
    lines.append(f"| Agreement | {agree} of {len(pairs)} ({(agree / len(pairs) if pairs else 0):.1%}) |")
    if errors:
        lines.append(f"| Records with a reviewer row recorded as model error (outside the agreement statistic, adjudicated) | {len(errors)} |")
    lines.append(f"| Cohen's kappa | {k:.3f} (SE {se:.3f}) |")
    lines.append(f"| Disagreements adjudicated | {len([1 for it in both if it['key'] in ADJ])} of {len(pairs) - agree + len(errors)} |")
    lines.append(f"| Final include / exclude / pending | {sum(1 for v in final.values() if v == 'include')} / {sum(1 for v in final.values() if v == 'exclude')} / {len(both) - len(final)} |")
    known = [it for it in both if it["matched_known"]]
    lines.append(f"| Known relevant records with a text, included | {sum(1 for it in known if final.get(it['key']) == 'include')} of {len(known)} |")
    failA = Counter(c for it in both for c in (A[it["key"]]["failed"] or ""))
    failB = Counter(c for it in both for c in (B[it["key"]]["failed"] or ""))
    lines.append("\n| Criterion failed | Reviewer 1 | Reviewer 2 |\n|---|---|---|")
    for c in "DPIOT":
        lines.append(f"| {c} | {failA.get(c, 0)} | {failB.get(c, 0)} |")
    bio = Counter()
    for it in both:
        if final.get(it["key"]) == "include":
            names = set()
            for r in (A[it["key"]], B[it["key"]]):
                names |= {x.strip().lower() for x in (r["biomarkers_reported"] or "").split(";") if x.strip()}
            bio.update(names)
    lines.append("\n| Biomarker named as reported (either reviewer), included records | Records |\n|---|---|")
    for name, cnt in bio.most_common(25):
        lines.append(f"| {name} | {cnt} |")
    missed = [it for it in known if final.get(it["key"]) == "exclude"]
    lines.append("\nPer record decisions, durations, comparators and biomarker maps stay untracked beside the exports "
                 "(fulltext_decisions_A.csv, fulltext_decisions_B.csv, fulltext_adjudication_002.csv). "
                 "A known relevant record excluded at full text is listed below for audit.\n")
    if missed:
        lines.append("| key | Title | Reviewer 1 | Reviewer 2 | Adjudicator |\n|---|---|---|---|---|")
        for it in missed:
            key = it["key"]
            lines.append(f"| {key} | {it['title'][:90]} | {A[key]['decision']} {A[key]['failed']} | {B[key]['decision']} {B[key]['failed']} | "
                         f"{ADJ[key]['decision'] + ' ' + ADJ[key]['failed'] if key in ADJ else ''} |")
    else:
        lines.append("No known relevant record with a text was excluded.")
    with open(SUMMARY, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


STALE_MINUTES = 12  # a running step with no new decision row for this long is reported as stale


def check():
    """Built in control, read only: the state of every chain (work/screen_chain*.sh) from its log
    and the process table, with progress measured on the decision and adjudication files (one row
    per screened record), never on a process being alive. Exit status 1 when a chain is stale,
    stopped or dead. A chain in that state is relaunched by hand (it resumes where it stopped):
        nohup zsh work/screen_<name>.sh >> search/screening/<name>.log 2>&1 &"""
    import glob
    import subprocess
    rows = [ln.split(None, 3) for ln in subprocess.run(
        ["ps", "-axwwo", "pid=,ppid=,etime=,command="], capture_output=True, text=True).stdout.splitlines()]
    rows = [r for r in rows if len(r) == 4]
    files = [p for p in glob.glob(os.path.join(OUTDIR, "*.csv")) if "decisions" in p or "adjudication" in p]
    newest = max((os.path.getmtime(p) for p in files), default=0.0)
    age = (time.time() - newest) / 60 if newest else float("inf")
    runners = sum(1 for r in rows if os.path.basename(r[3].split()[0]) in ("llama-server", "ollama_llama_server"))
    print(f"check {time.strftime('%Y-%m-%d %H:%M:%S')}: newest decision row {age:.1f} min ago "
          f"(stale at {STALE_MINUTES}); ollama runners alive: {runners}")
    print(f"{'chain':9} {'state':9} {'shell':>6} {'running for':>11}  {'step':56} last log line")
    attention = []
    for script in sorted(glob.glob(os.path.join(ROOT, "work", "screen_chain*.sh"))):
        name = os.path.basename(script)[len("screen_"):-3]
        logp = os.path.join(OUTDIR, f"{name}.log")
        if not os.path.exists(logp):
            continue
        lines = [ln.rstrip("\n") for ln in open(logp, errors="replace") if ln.strip()]
        marker = "empty"
        for ln in lines:
            if ln.startswith(f"{name} complete "):
                marker = "complete"
            elif ln.startswith(f"{name} retired"):  # written by hand, with the reason, when a chain's work moved elsewhere
                marker = "retired"
            elif ln.startswith("CHAIN STOPPED"):
                marker = "stopped"
            elif ln.startswith(f"{name} start ") or ln.startswith("== "):
                marker = "started"
        shell = next((r for r in rows if len(r[3].split()) >= 2
                      and os.path.basename(r[3].split()[0]) in ("zsh", "bash", "sh")
                      and r[3].split()[1].endswith(f"work/screen_{name}.sh")), None)
        step = next((r for r in rows if shell and r[1] == shell[0] and "src/" in r[3]
                     and "ython" in r[3].split()[0]), None)
        if step:
            state = "stale" if age >= STALE_MINUTES else "running"
            stepname, since = step[3].split(" -I ", 1)[-1], step[2]
        elif shell:
            state, stepname, since = ("between" if marker == "started" else "waiting"), "-", shell[2]
        else:
            state, stepname, since = (marker if marker in ("complete", "retired", "stopped") else "dead"), "-", "-"
        if state in ("stale", "stopped", "dead"):
            attention.append(f"{name} {state}")
        print(f"{name:9} {state:9} {shell[0] if shell else '-':>6} {since:>11}  {stepname[:56]:56} "
              f"{(lines[-1] if lines else '')[:70]}")
    print("attention: " + ", ".join(attention) if attention else "attention: none")
    sys.exit(1 if attention else 0)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("screen", "adjudicate", "summarise", "inventory", "check"):
        print(__doc__); sys.exit(2)
    if sys.argv[1] == "check":
        check()
    args = sys.argv[2:]
    cfg = st.load_cfg()
    items = load_items()
    stage = sys.argv[1]
    if stage == "inventory":
        c = Counter(it["source"] for it in items)
        for s in SOURCE_ORDER + ["awaiting_fulltext", "already_extracted"]:
            print(f"{s:22s} {c[s]:4d}  chars total {sum(len(it['text']) for it in items if it['source'] == s):,}")
        return
    if stage == "screen":
        reviewers = ["A", "B"]
        sources = SOURCE_ORDER
        limit = None
        if "--reviewer" in args:
            reviewers = [args[args.index("--reviewer") + 1]]
        if "--source" in args:
            sources = [args[args.index("--source") + 1]]
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        for rev in reviewers:
            screen(cfg, items, rev, sources, limit)
    elif stage == "adjudicate":
        adjudicate(cfg, items)
    else:
        summarise(cfg, items)


if __name__ == "__main__":
    main()
