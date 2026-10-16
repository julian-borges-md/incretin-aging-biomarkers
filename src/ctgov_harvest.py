#!/usr/bin/env python3
"""Fetch ClinicalTrials.gov records (API v2, public, no key) for every pool
record that is a registry record with an NCT identifier, or that names one,
and render each as plain text under work/fulltext/registry/ (gitignored):
design, arms, interventions, eligibility, outcomes, status, results summary
and linked publications. Writes a manifest beside the files."""
import csv, json, os, re, time, urllib.request
POOL = "search/screening/fulltext_pool_2026-10-16.csv"
OUTDIR = "work/fulltext/registry"
MANIFEST = f"{OUTDIR}/MANIFEST_ctgov_2026-10-16.csv"
os.makedirs(OUTDIR, exist_ok=True)
rows = list(csv.DictReader(open(POOL)))
targets = []
for r in rows:
    if r["route"] != "registry_record":
        continue
    ncts = [x for x in r["nct_ids"].split(";") if x]
    if r["accession"].startswith("NCT"):
        ncts = [r["accession"]] + [x for x in ncts if x != r["accession"]]
    if ncts:
        targets.append((r, ncts[0]))
print("registry records:", sum(r["route"] == "registry_record" for r in rows), "with an NCT id:", len(targets), flush=True)

def g(d, *keys, default=""):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d if d is not None else default

def render(study):
    p = study.get("protocolSection", {})
    out = []
    idm = p.get("identificationModule", {}); st = p.get("statusModule", {}); dm = p.get("designModule", {})
    out.append(f"# {idm.get('nctId','')}: {idm.get('officialTitle') or idm.get('briefTitle','')}")
    out.append(f"Brief title: {idm.get('briefTitle','')}")
    out.append(f"Status: {st.get('overallStatus','')}; start {g(st,'startDateStruct','date')}; primary completion {g(st,'primaryCompletionDateStruct','date')}; completion {g(st,'completionDateStruct','date')}; results first posted {g(st,'resultsFirstPostDateStruct','date')}")
    out.append(f"Study type: {dm.get('studyType','')}; phases: {', '.join(dm.get('phases', []) or [])}; allocation: {g(dm,'designInfo','allocation')}; model: {g(dm,'designInfo','interventionModel')}; masking: {g(dm,'designInfo','maskingInfo','masking')}; enrollment: {g(dm,'enrollmentInfo','count')} ({g(dm,'enrollmentInfo','type')})")
    cm = p.get("conditionsModule", {})
    out.append(f"Conditions: {'; '.join(cm.get('conditions', []) or [])}")
    out.append("\n## Summary\n" + g(p, "descriptionModule", "briefSummary"))
    dd = g(p, "descriptionModule", "detailedDescription")
    if dd:
        out.append("\n## Detailed description\n" + dd)
    am = p.get("armsInterventionsModule", {})
    out.append("\n## Arms")
    for a in am.get("armGroups", []) or []:
        out.append(f"- {a.get('label','')} ({a.get('type','')}): {a.get('description','')} | interventions: {', '.join(a.get('interventionNames', []) or [])}")
    out.append("\n## Interventions")
    for i in am.get("interventions", []) or []:
        out.append(f"- {i.get('type','')}: {i.get('name','')} — {i.get('description','')}")
    om = p.get("outcomesModule", {})
    for kind in ("primaryOutcomes", "secondaryOutcomes", "otherOutcomes"):
        if om.get(kind):
            out.append(f"\n## {kind}")
            for o in om[kind]:
                out.append(f"- {o.get('measure','')} | {o.get('description','')} | time frame: {o.get('timeFrame','')}")
    em = p.get("eligibilityModule", {})
    out.append("\n## Eligibility\n" + f"Sex: {em.get('sex','')}; ages {em.get('minimumAge','')} to {em.get('maximumAge','')}; healthy volunteers: {em.get('healthyVolunteers','')}\n" + (em.get("eligibilityCriteria", "") or ""))
    refs = g(p, "referencesModule", "references", default=[]) or []
    if refs:
        out.append("\n## References")
        for ref in refs:
            out.append(f"- PMID {ref.get('pmid','')} [{ref.get('type','')}]: {ref.get('citation','')}")
    res = study.get("resultsSection")
    if res:
        out.append("\n## Results section present (posted results)")
        for om2 in g(res, "outcomeMeasuresModule", "outcomeMeasures", default=[]) or []:
            out.append(f"- {om2.get('type','')}: {om2.get('title','')} | {om2.get('timeFrame','')} | unit {om2.get('unitOfMeasure','')}")
            for cls in om2.get("classes", []) or []:
                for cat in cls.get("categories", []) or []:
                    vals = "; ".join(f"{m.get('groupId','')}={m.get('value','')}{'±'+m.get('spread','') if m.get('spread') else ''}" for m in cat.get("measurements", []) or [])
                    if vals:
                        out.append(f"    {cls.get('title','')} {cat.get('title','')}: {vals}")
    return "\n".join(out)

with open(MANIFEST, "w", newline="") as mf:
    w = csv.DictWriter(mf, fieldnames=["pool", "n", "nct", "status", "has_results", "chars", "file"])
    w.writeheader()
    ok = 0
    for r, nct in targets:
        path = f"{OUTDIR}/pool{r['pool']}_n{r['n']}_{nct}.txt"
        status, has_res, chars = "", "", 0
        if os.path.exists(path) and os.path.getsize(path) > 300:
            status = "exists"; chars = os.path.getsize(path)
        else:
            url = f"https://clinicaltrials.gov/api/v2/studies/{nct}"
            req = urllib.request.Request(url, headers={"User-Agent": "incretin-aging-biomarkers-review/1.0", "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=40) as resp:
                    study = json.load(resp)
                txt = render(study)
                open(path, "w").write(txt)
                status, chars = "ok", len(txt)
                has_res = "yes" if study.get("resultsSection") else "no"
                open(path.replace(".txt", ".json"), "w").write(json.dumps(study))
            except Exception as e:
                status = f"error: {str(e)[:80]}"
            time.sleep(0.3)
        ok += status in ("ok", "exists")
        w.writerow(dict(pool=r["pool"], n=r["n"], nct=nct, status=status, has_results=has_res, chars=chars, file=path)); mf.flush()
print(f"done: {ok} of {len(targets)} registry records saved under {OUTDIR}", flush=True)
