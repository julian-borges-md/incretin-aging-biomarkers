#!/usr/bin/env python3
"""
screen_titles.py

Title and abstract screening of the Embase export by two independent,
blinded, deterministic reviewer agents, with a third agent adjudicating
disagreements. Implements the three agent review design approved on
2026-10-15 (reviewers 013A and 013B, different models, blinded to each other
and to any prior decision; adjudicator 002; kappa per stage logged).

The models run locally. Their names live in search/screening/
screener_config.json, which is gitignored, so this repository names no
product. Every call is made with temperature 0 and a fixed seed, so a rerun
with the same configuration reproduces the same decisions.

Stages
  screen      each reviewer sees title, abstract, year and record type only,
              and returns include or exclude with the failed criteria and a
              one sentence reason, as JSON
  adjudicate  for every disagreement the adjudicator sees the record and
              both reasons and decides, with its own reason
  summarise   counts, per stage agreement, Cohen's kappa, recall of the
              screening against records already known to be relevant,
              written to search/screening/SCREENING_SUMMARY.md

Resumable: decisions already on disk are not recomputed.

Pools. The default pool is the Embase article export (659 records, files
without a suffix). The pool "batch2" is the 51 Embase clinical trial registry
records plus the 200 CENTRAL records that are not in the Embase article
export (selected by the in_embase_export flag that src/dedup_embase.py
central writes); its decision, adjudication and summary files carry the
suffix _batch2 so the first pool is never touched. Both pools pass the same
count and SHA-256 gates on their exports before a record is read.

Criteria versions. v1 is the prompt used for the first full run on the
Embase pool. An audit of that run found the criteria misapplied in two
recurring ways (a DPP-4 inhibitor comparator read as an exclusion; 12 weeks
and 6 months read as shorter than 12 weeks). v2 appends clarifications that
restate the criteria without changing them. v1 decisions are never rewritten:
v2 files carry the suffix _v2. The stage rescreen-excluded runs both reviewers
under v2 on the records a pool's v1 run finally excluded, so that the set
going to full text is the v1 includes plus every record either reviewer
includes under v2. Includes are not revisited: an inclusion error is caught at
full text, an exclusion error is not.

Usage, from the repository root:
  python3 -I src/screen_titles.py screen [--limit N] [--reviewer A|B] [--pool embase|batch2] [--criteria v1|v2]
  python3 -I src/screen_titles.py rescreen-excluded --criteria v2 [--pool embase|batch2]
  python3 -I src/screen_titles.py adjudicate [--pool embase|batch2] [--criteria v1|v2]
  python3 -I src/screen_titles.py summarise [--pool embase|batch2] [--criteria v1|v2]
"""
import hashlib
import csv
import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict

ROOT = os.getcwd()
CFG = os.path.join(ROOT, "search/screening/screener_config.json")
OUTDIR = os.path.join(ROOT, "search/screening")

EXPORTS = {
    "embase": dict(ris="search/embase_2026-10-15/embase_659.ris", expected=659,
                   sha256="e8d3a9d4e195375f1d1aaaead76ae0ad0d937206194e152984d71d42405fefb2",
                   dedup="search/embase_2026-10-15/embase_659_dedup.csv"),
    "embase_registry": dict(ris="search/embase_2026-10-15/embase_registry_51.ris", expected=51,
                            sha256="d740d349bf45d00d5311d6cb72cf4c7fc92e64d21ee6bb9744940be6c407665a",
                            dedup=None),
    "central": dict(ris="search/central_2026-10-15/central_460.ris", expected=460,
                    sha256="7c12c88115631e45195e82641d2b0a6f9c5bd0835d48f7972c5b08372c0547f3",
                    dedup="search/central_2026-10-15/central_460_dedup.csv"),
}
POOLS = {
    "embase": dict(suffix="", title="the Embase export",
                   members=[("embase", "all")]),
    "batch2": dict(suffix="_batch2",
                   title="the Embase clinical trial registry records and the CENTRAL records not in the Embase export",
                   members=[("embase_registry", "all"), ("central", "not_in_embase")]),
}
POOL = "embase"  # set by main() from --pool
CRITERIA_VERSION = "v1"  # set by main() from --criteria
ABSTRACT_CAP = 10000  # characters; above the longest Embase abstract (9,551), below the context window


def pool():
    return POOLS[POOL]


def file_suffix():
    return pool()["suffix"] + ("" if CRITERIA_VERSION == "v1" else f"_{CRITERIA_VERSION}")


def summary_path():
    return os.path.join(OUTDIR, f"SCREENING_SUMMARY{file_suffix()}.md")

CRITERIA = """You are screening titles and abstracts for a systematic review of randomised
trials of incretin and glucagon receptor agonists and aging related biomarkers.
Apply these pre specified eligibility criteria. At this stage a record is
EXCLUDED only when the title or abstract shows that it clearly fails at least
one criterion; when a criterion cannot be judged from the text, treat it as
met and INCLUDE, because full text screening follows.

D  Design: a randomised controlled trial in humans, parallel or crossover,
   including secondary or post hoc analyses of a randomised trial. Exclude
   observational studies, single arm studies, animal or in vitro work,
   reviews, meta analyses, editorials, protocols, case reports, modelling.
P  Population: adults with overweight, obesity, type 2 diabetes, MASH or
   MASLD. Exclude children or adolescents, type 1 diabetes, post bariatric
   surgery populations.
I  Intervention: at least one arm receives semaglutide, liraglutide,
   exenatide, dulaglutide, tirzepatide, survodutide, mazdutide, pemvidutide,
   cotadutide, retatrutide, amycretin, cagrilintide or CagriSema. Any
   comparator is acceptable. Exclude trials whose only incretin agent is
   lixisenatide, albiglutide or a DPP-4 inhibitor.
O  Outcome: at least one of these biomarkers is reported: C reactive
   protein or hsCRP, interleukin 6, TNF alpha, GDF-15, YKL-40, ICAM-1,
   leptin, adiponectin, fasting insulin, HOMA-IR, HOMA-beta, C-peptide,
   glucagon, fasting glucose, HbA1c, liver fat by imaging, ALT, AST, GGT,
   MASH resolution or fibrosis, triglycerides, LDL or total cholesterol,
   lean mass, body fat, visceral adipose tissue, bone mineral density, eGFR,
   resting heart rate, blood pressure, NT-proBNP, MR-proANP, epigenetic
   age. Exclude only if the abstract shows none of these could have been
   measured (for example a pure pharmacokinetic or device study).
T  Duration: treatment for 12 weeks or longer. Exclude if the stated
   treatment period is clearly shorter.

Answer with JSON only, exactly this shape:
{"decision": "include" or "exclude",
 "failed_criteria": [list of letters among D P I O T that clearly fail, empty if none],
 "reason": one sentence of at most 40 words}
"""


CRITERIA_V2_ADDENDUM = """
Clarifications (criteria version 2, added 2026-10-15 after an audit of the
first run; they restate the criteria above and do not change them):
- I: the comparator never excludes a trial. A trial is eligible when at least
  one arm receives an eligible agent, whatever the other arms receive
  (placebo, insulin, metformin, a sulfonylurea, lifestyle, or a DPP-4
  inhibitor such as sitagliptin or vildagliptin). The DPP-4 inhibitor
  exclusion applies only when no arm receives an eligible agent.
- T: 12 weeks exactly is eligible. Convert before comparing: 12 weeks,
  3 months, 84 days, 6 months (26 weeks), 1 year all meet the criterion.
  Exclude on T only when the stated treatment period is clearly shorter
  than 12 weeks.
- P: adults with type 2 diabetes are eligible whether or not overweight or
  obesity is mentioned.
- D: a secondary or post hoc analysis of a randomised trial is eligible.
  Exclude on D only when the text states a non randomised design, a single
  arm, animals, cells, or a review.
"""


def criteria_text():
    return CRITERIA + (CRITERIA_V2_ADDENDUM if CRITERIA_VERSION == "v2" else "")


def load_cfg():
    with open(CFG) as fh:
        return json.load(fh)


def parse_ris_file(name):
    """Parse one export after its count and hash gate; returns records in file order."""
    ex = EXPORTS[name]
    path = os.path.join(ROOT, ex["ris"])
    if not os.path.exists(path):
        print(f"FAIL: export not found at {path} (gitignored; place the licensed file there)")
        sys.exit(1)
    with open(path, "rb") as fh:
        raw = fh.read()
    if hashlib.sha256(raw).hexdigest() != ex["sha256"]:
        print(f"FAIL: {name}: SHA-256 differs from the logged value")
        sys.exit(1)
    text = raw.decode("utf-8", errors="replace")
    recs, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            cur = defaultdict(list)
            cur["TY"].append(val)
        elif tag == "ER":
            recs.append(cur)
            cur = None
        elif cur is not None:
            cur[tag].append(val)
    if len(recs) != ex["expected"]:
        print(f"FAIL: {name}: parsed {len(recs)} records, expected {ex['expected']}")
        sys.exit(1)
    out = []
    for i, r in enumerate(recs, 1):
        def first(*tags):
            for t in tags:
                if r.get(t):
                    return r[t][0]
            return ""
        out.append(dict(n=i, source=name, accession=first("U2", "AN"), title=first("T1", "TI"),
                        abstract=first("AB", "N2")[:ABSTRACT_CAP], year=re.sub(r"[^0-9]", "", first("Y1", "PY"))[:4],
                        rtype=first("M3", "TY"), doi=first("DO").lower()))
    return out


def read_dedup(name):
    """Per record flags written by src/dedup_embase.py, keyed by position in that export."""
    ex = EXPORTS[name]
    if not ex["dedup"]:
        return {}
    path = os.path.join(ROOT, ex["dedup"])
    if not os.path.exists(path):
        print(f"FAIL: {path} not found; run src/dedup_embase.py {'central' if name == 'central' else ''} first")
        sys.exit(1)
    with open(path, newline="") as fh:
        return {int(r["n"]): r for r in csv.DictReader(fh)}


def parse_ris():
    """The records of the selected pool, numbered 1..N in pool order, with the
    known relevant flag carried over from the dedup files where one exists."""
    out = []
    for name, rule in pool()["members"]:
        recs = parse_ris_file(name)
        flags = read_dedup(name)
        if rule == "not_in_embase":
            if not flags or "in_embase_export" not in next(iter(flags.values())):
                print(f"FAIL: {name}: in_embase_export flag missing; run src/dedup_embase.py central")
                sys.exit(1)
            recs = [r for r in recs if flags[r["n"]]["in_embase_export"] == "no"]
        for r in recs:
            r["matched_known"] = flags.get(r["n"], {}).get("matched_known") == "yes"
            r["source_n"] = r["n"]
        out.extend(recs)
    for i, r in enumerate(out, 1):
        r["n"] = i
    if POOL == "batch2" and len(out) != 251:
        print(f"FAIL: batch2 pool has {len(out)} records, expected 251 (51 registry plus 200 CENTRAL only)")
        sys.exit(1)
    return out


def ollama_chat(cfg, model, system, user, max_retries=3):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "format": "json",
        "options": {"temperature": cfg["temperature"], "seed": cfg["seed"],
                    "num_ctx": cfg["num_ctx"], "num_predict": cfg["num_predict"]},
    }).encode()
    last = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(cfg["ollama_url"] + "/api/chat", data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as resp:
                return json.loads(resp.read().decode())["message"]["content"]
        except Exception as e:  # network or model error: retry, then give up loudly
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"ollama call failed after {max_retries} attempts: {last}")


def parse_decision(raw):
    try:
        d = json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, flags=re.S)
        try:
            d = json.loads(m.group(0)) if m else {}
        except Exception:
            d = {}  # truncated or malformed JSON: handled below as unparseable, never as a crash
    if not isinstance(d, dict):
        d = {}
    dec = str(d.get("decision", "")).strip().lower()
    if dec not in ("include", "exclude"):
        dec = "include"  # an unparseable answer is never a silent exclusion
        d["reason"] = "UNPARSEABLE: " + raw[:200].replace("\n", " ")
    failed = d.get("failed_criteria", [])
    if isinstance(failed, str):
        failed = [x for x in re.findall(r"[DPIOT]", failed.upper())]
    failed = "".join(sorted({str(x).strip().upper()[:1] for x in failed if str(x).strip()}))
    return dec, failed, str(d.get("reason", ""))[:400].replace("\n", " ")


def record_text(rec):
    return (f"Record type: {rec['rtype']}\nYear: {rec['year']}\n"
            f"Title: {rec['title']}\nAbstract: {rec['abstract'] or '(no abstract in the record)'}")


def decisions_path(rev, version=None):
    sfx = file_suffix() if version is None else pool()["suffix"] + ("" if version == "v1" else f"_{version}")
    return os.path.join(OUTDIR, f"decisions_{rev}{sfx}.csv")


def adjudication_path(version=None):
    sfx = file_suffix() if version is None else pool()["suffix"] + ("" if version == "v1" else f"_{version}")
    return os.path.join(OUTDIR, f"adjudication_002{sfx}.csv")


def final_decisions(version):
    """Final decision per record for a pool under one criteria version: agreement, else adjudication."""
    A, B = read_decisions(decisions_path("A", version)), read_decisions(decisions_path("B", version))
    ADJ = read_decisions(adjudication_path(version))
    final = {}
    for n in set(A) & set(B):
        if A[n]["decision"] == B[n]["decision"]:
            final[n] = A[n]["decision"]
        elif n in ADJ:
            final[n] = ADJ[n]["decision"]
    return final


def read_decisions(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="") as fh:
        return {int(r["n"]): r for r in csv.DictReader(fh)}


def screen(cfg, recs, reviewer, limit=None, subset=None):
    model = cfg["screeners"][reviewer]
    path = decisions_path(reviewer)
    done = read_decisions(path)
    todo = [r for r in recs if r["n"] not in done and (subset is None or r["n"] in subset)]
    if limit:
        todo = todo[:limit]
    print(f"reviewer {reviewer}: {len(done)} done, {len(todo)} to screen")
    new_file = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["n", "accession", "decision", "failed", "reason", "seconds"])
        if new_file:
            w.writeheader()
        t_all = time.time()
        for i, rec in enumerate(todo, 1):
            t0 = time.time()
            raw = ollama_chat(cfg, model, criteria_text(), record_text(rec))
            dec, failed, reason = parse_decision(raw)
            w.writerow(dict(n=rec["n"], accession=rec["accession"], decision=dec, failed=failed,
                            reason=reason, seconds=f"{time.time() - t0:.1f}"))
            fh.flush()
            if i % 10 == 0 or i == len(todo):
                print(f"  {reviewer}: {i}/{len(todo)} ({(time.time() - t_all) / i:.1f} s per record)", flush=True)


def adjudicate(cfg, recs):
    A, B = read_decisions(decisions_path("A")), read_decisions(decisions_path("B"))
    path = adjudication_path()
    done = read_decisions(path)
    disagreements = [r for r in recs if r["n"] in A and r["n"] in B
                     and A[r["n"]]["decision"] != B[r["n"]]["decision"] and r["n"] not in done]
    print(f"adjudicator: {len(done)} done, {len(disagreements)} disagreements to adjudicate")
    new_file = not os.path.exists(path)
    system = criteria_text() + ("\nTwo independent reviewers disagreed on this record. Their decisions and "
                         "reasons follow the record. Decide independently against the criteria; do not "
                         "defer to either reviewer by default. Use the same JSON shape.")
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["n", "accession", "decision_A", "decision_B", "decision",
                                           "failed", "reason", "seconds"])
        if new_file:
            w.writeheader()
        for i, rec in enumerate(disagreements, 1):
            a, b = A[rec["n"]], B[rec["n"]]
            user = (record_text(rec) + f"\n\nReviewer 1: {a['decision']} ({a['failed'] or 'none'}): {a['reason']}"
                    f"\nReviewer 2: {b['decision']} ({b['failed'] or 'none'}): {b['reason']}")
            t0 = time.time()
            raw = ollama_chat(cfg, cfg["adjudicator"], system, user)
            dec, failed, reason = parse_decision(raw)
            w.writerow(dict(n=rec["n"], accession=rec["accession"], decision_A=a["decision"],
                            decision_B=b["decision"], decision=dec, failed=failed, reason=reason,
                            seconds=f"{time.time() - t0:.1f}"))
            fh.flush()
            if i % 10 == 0 or i == len(disagreements):
                print(f"  adjudicated {i}/{len(disagreements)}", flush=True)


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(1 for a, b in pairs if a == b) / n
    pa_inc = sum(1 for a, _ in pairs if a == "include") / n
    pb_inc = sum(1 for _, b in pairs if b == "include") / n
    pe = pa_inc * pb_inc + (1 - pa_inc) * (1 - pb_inc)
    k = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    se = ((po * (1 - po)) / (n * (1 - pe) ** 2)) ** 0.5 if pe < 1 else float("nan")
    return k, se


def summarise(cfg, recs):
    A, B = read_decisions(decisions_path("A")), read_decisions(decisions_path("B"))
    ADJ = read_decisions(adjudication_path())
    both = [r["n"] for r in recs if r["n"] in A and r["n"] in B]
    pairs = [(A[n]["decision"], B[n]["decision"]) for n in both]
    k, se = kappa(pairs)
    agree = sum(1 for a, b in pairs if a == b)
    final = {}
    for n in both:
        if A[n]["decision"] == B[n]["decision"]:
            final[n] = A[n]["decision"]
        elif n in ADJ:
            final[n] = ADJ[n]["decision"]
    known = {r["n"]: r["matched_known"] for r in recs}
    known_ns = [n for n in final if known.get(n)]
    known_inc = sum(1 for n in known_ns if final[n] == "include")
    failA = Counter(c for n in both for c in (A[n]["failed"] or ""))
    failB = Counter(c for n in both for c in (B[n]["failed"] or ""))
    lines = []
    lines.append(f"# Title and abstract screening of {pool()['title']}\n")
    lines.append("Two independent reviewer agents (different local models, temperature 0, fixed seed, blinded to each other), "
                 "a third agent adjudicating disagreements. Models are named only in the untracked configuration file. "
                 f"Criteria version {CRITERIA_VERSION}. Produced by `src/screen_titles.py summarise`.\n")
    v1_final = final_decisions("v1") if CRITERIA_VERSION != "v1" else {}
    if v1_final and all(n in v1_final for n in both):
        # Rescreen of the v1 excluded set: report the rescue, not a second kappa over a biased subset.
        v1_exc = sorted(n for n, d in v1_final.items() if d == "exclude")
        rescued = [n for n in both if "include" in (A[n]["decision"], B[n]["decision"])]
        still = [n for n in both if n not in rescued]
        v1_inc = sum(1 for d in v1_final.values() if d == "include")
        lines.append(f"## Rescreen of the records excluded under criteria v1\n")
        lines.append("| Quantity | Value |\n|---|---|")
        lines.append(f"| Records finally excluded under v1 | {len(v1_exc)} |")
        lines.append(f"| Rescreened by both reviewers under {CRITERIA_VERSION} | {len(both)} |")
        lines.append(f"| Included by either reviewer under {CRITERIA_VERSION} (rescued, to full text) | {len(rescued)} |")
        lines.append(f"| Excluded by both reviewers under {CRITERIA_VERSION} | {len(still)} |")
        lines.append(f"| Agreement on the rescreened set | {agree} of {len(pairs)} ({(agree / len(pairs) if pairs else 0):.1%}) |")
        lines.append(f"| Set going to full text: v1 includes plus rescued | {v1_inc} + {len(rescued)} = {v1_inc + len(rescued)} |")
        known_resc = [n for n in rescued if known.get(n)]
        known_still = [n for n in still if known.get(n)]
        lines.append(f"| Known relevant records among the rescreened | {len(known_resc) + len(known_still)}: rescued {len(known_resc)}, still excluded {len(known_still)} |\n")
        lines.append("| Criterion failed in the rescreen | Reviewer 1 | Reviewer 2 |\n|---|---|---|")
        for c in "DPIOT":
            lines.append(f"| {c} | {failA.get(c, 0)} | {failB.get(c, 0)} |")
        if known_still:
            lines.append("\n| n | Title | Reviewer 1 | Reviewer 2 |\n|---|---|---|---|")
            for n in known_still:
                rec = next(r for r in recs if r["n"] == n)
                lines.append(f"| {n} | {rec['title'][:90]} | {A[n]['decision']} {A[n]['failed']} | {B[n]['decision']} {B[n]['failed']} |")
        sfx = file_suffix()
        lines.append(f"\nPer record decisions stay untracked beside the export (decisions_A{sfx}.csv, decisions_B{sfx}.csv).")
        with open(summary_path(), "w") as fh:
            fh.write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return
    lines.append("| Quantity | Value |\n|---|---|")
    lines.append(f"| Records in pool | {len(recs)} |")
    if len(pool()["members"]) > 1:
        by_src = Counter(r["source"] for r in recs)
        lines.append("| Pool composition | " + "; ".join(f"{k} {v}" for k, v in by_src.items()) + " |")
    lines.append(f"| Screened by both reviewers | {len(both)} |")
    lines.append(f"| Reviewer 1 include / exclude | {sum(1 for a, _ in pairs if a == 'include')} / {sum(1 for a, _ in pairs if a == 'exclude')} |")
    lines.append(f"| Reviewer 2 include / exclude | {sum(1 for _, b in pairs if b == 'include')} / {sum(1 for _, b in pairs if b == 'exclude')} |")
    lines.append(f"| Agreement | {agree} of {len(pairs)} ({(agree / len(pairs) if pairs else 0):.1%}) |")
    lines.append(f"| Cohen's kappa | {k:.3f} (SE {se:.3f}) |")
    lines.append(f"| Disagreements adjudicated | {len(ADJ)} of {len(pairs) - agree} |")
    lines.append(f"| Final include / exclude / pending | {sum(1 for v in final.values() if v == 'include')} / "
                 f"{sum(1 for v in final.values() if v == 'exclude')} / {len(both) - len(final)} |")
    lines.append(f"| Records already known relevant, included by screening | {known_inc} of {len(known_ns)} |\n")
    lines.append("| Criterion failed | Reviewer 1 | Reviewer 2 |\n|---|---|---|")
    for c in "DPIOT":
        lines.append(f"| {c} | {failA.get(c, 0)} | {failB.get(c, 0)} |")
    sfx = file_suffix()
    lines.append(f"\nPer record decisions and reasons stay untracked beside the export (decisions_A{sfx}.csv, decisions_B{sfx}.csv, "
                 f"adjudication_002{sfx}.csv). A known relevant record excluded by screening is listed below for audit.\n")
    missed = [n for n in known_ns if final[n] == "exclude"]
    if missed:
        lines.append("| n | Title | Reviewer 1 | Reviewer 2 | Adjudicator |\n|---|---|---|---|---|")
        for n in missed:
            rec = next(r for r in recs if r["n"] == n)
            lines.append(f"| {n} | {rec['title'][:90]} | {A[n]['decision']} | {B[n]['decision']} | "
                         f"{ADJ[n]['decision'] if n in ADJ else ''} |")
    else:
        lines.append("No known relevant record was excluded.")
    with open(summary_path(), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("screen", "rescreen-excluded", "adjudicate", "summarise"):
        print(__doc__)
        sys.exit(2)
    global POOL, CRITERIA_VERSION
    args = sys.argv[2:]
    if "--pool" in args:
        POOL = args[args.index("--pool") + 1]
        if POOL not in POOLS:
            print("unknown pool", POOL, "; known:", ", ".join(POOLS))
            sys.exit(2)
    if "--criteria" in args:
        CRITERIA_VERSION = args[args.index("--criteria") + 1]
        if CRITERIA_VERSION not in ("v1", "v2"):
            print("unknown criteria version", CRITERIA_VERSION)
            sys.exit(2)
    cfg = load_cfg()
    recs = parse_ris()
    os.makedirs(OUTDIR, exist_ok=True)
    stage = sys.argv[1]
    if stage == "screen":
        limit = None
        reviewers = ["A", "B"]
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        if "--reviewer" in args:
            reviewers = [args[args.index("--reviewer") + 1]]
        for rev in reviewers:
            screen(cfg, recs, rev, limit)
    elif stage == "rescreen-excluded":
        if CRITERIA_VERSION == "v1":
            print("rescreen-excluded needs --criteria v2: it rescreens the v1 exclusions under the clarified criteria")
            sys.exit(2)
        v1_final = final_decisions("v1")
        if not v1_final:
            print("no v1 decisions for this pool; nothing to rescreen")
            sys.exit(1)
        subset = {n for n, d in v1_final.items() if d == "exclude"}
        print(f"rescreen: {len(subset)} records finally excluded under v1")
        for rev in ["A", "B"]:
            screen(cfg, recs, rev, None, subset)
    elif stage == "adjudicate":
        adjudicate(cfg, recs)
    else:
        summarise(cfg, recs)


if __name__ == "__main__":
    main()
