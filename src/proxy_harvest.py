#!/usr/bin/env python3
"""Move captured page texts from ~/Downloads into work/fulltext/proxy, classify, and update the manifest.
Run from the repository root: python3 -I src/proxy_harvest.py (inputs under work/ are untracked; captures are licensed content and stay gitignored)."""
import csv, glob, json, os, re, shutil
loop = json.load(open("work/proxy_loop.json")) + [dict(key="pool1_n22", doi="10.1016/j.jacc.2026.04.044"),
    # records outside the first loop: two with a DOI not in closed_access_todo at loop time, one PubMed abstract page (no DOI, PMID 38940809)
    dict(key="pool1_n294", doi="10.1016/j.jacc.2023.09.811"), dict(key="pool1_n625", doi="10.1111/j.1472-8206.2010.00888.x"), dict(key="pool1_n255", doi="")]
dl = os.path.expanduser("~/Downloads"); keep = os.path.join(dl, "fulltext_captures"); os.makedirs(keep, exist_ok=True)
M = "work/fulltext/proxy/MANIFEST_proxy_2026-10-16.csv"
rows = {r["key"]: r for r in csv.DictReader(open(M))} if os.path.exists(M) else {}
def classify(t):
    # section marks in English or Russian (one capture, pool1_n447, is a Russian language article)
    marks = sum(bool(re.search(r"\b(" + m + r")\b", t, re.I)) for m in ("Methods|Методы", "Results|Результаты", "Discussion|Обсуждение", "References|Список литературы|Литература"))
    wall = bool(re.search(r"Purchase PDF|Get access|Buy article|Access this article|Institutional subscription|Rent this article|Sign in to access|Purchase access", t))
    if marks >= 3 and len(t) > 12000: return "fulltext", marks
    if wall: return "paywalled_page", marks
    return "partial", marks
for key, r in rows.items():
    if os.path.exists(r["file"]):
        st, mk = classify(open(r["file"], "rb").read().decode("utf-8", errors="replace")); r["status"], r["marks"] = st, mk
new = 0
for it in loop:
    key = it["key"]
    cands = sorted(glob.glob(os.path.join(dl, key + "*.txt")) + glob.glob(os.path.join(dl, ".com.google.Chrome.*")), key=os.path.getmtime)
    src = None
    for c in cands:
        try: head = open(c, "rb").read(300).decode("utf-8", errors="replace")
        except Exception: continue
        if head.startswith(f"KEY: {key}\n") or (key == "pool1_n22" and os.path.basename(c).startswith("pool1_n22")): src = c
    if not src: continue
    data = open(src, "rb").read(); t = data.decode("utf-8", errors="replace")
    out = f"work/fulltext/proxy/{key}.txt"; open(out, "wb").write(data)
    status, marks = classify(t)
    m = re.search(r"^SOURCE: (\S+)", t, re.M)
    rows[key] = dict(key=key, doi=it["doi"], status=status, chars=len(t), marks=marks, host=(m.group(1).split("/")[2] if m else ""), file=out)
    if not os.path.basename(src).startswith("."):
        shutil.move(src, os.path.join(keep, os.path.basename(src)))
    new += 1
with open(M, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["key", "doi", "status", "chars", "marks", "host", "file"]); w.writeheader(); w.writerows(rows.values())
from collections import Counter
print(json.dumps({"harvested_now": new, "total": len(rows), "status": dict(Counter(r["status"] for r in rows.values()))}))
