#!/usr/bin/env python3
"""Fetch open access full texts (Europe PMC XML) for pool records with a PMCID
and isOpenAccess Y; save XML and a plain text rendering under work/fulltext/pool/
(gitignored). Writes a manifest with sizes and status."""
import csv, os, re, time, urllib.request, xml.etree.ElementTree as ET
ACCESS = "search/screening/fulltext_access_2026-10-16.csv"
OUTDIR = "work/fulltext/pool"
MANIFEST = "work/fulltext/pool/MANIFEST_epmc_2026-10-16.csv"
rows = [r for r in csv.DictReader(open(ACCESS)) if r["epmc_pmcid"] and r["is_open_access"] == "Y"]
print("open access records with PMCID:", len(rows), flush=True)

def xml_to_text(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    def walk(el, depth=0):
        tag = el.tag.split('}')[-1]
        if tag in ("title", "label"):
            out.append("\n## " + "".join(el.itertext()).strip() + "\n")
            return
        if tag in ("p", "td", "th", "caption", "abstract"):
            out.append("".join(el.itertext()).strip() + ("\t" if tag in ("td", "th") else "\n"))
            return
        if tag == "tr":
            for c in el: walk(c, depth + 1)
            out.append("\n"); return
        for c in el: walk(c, depth + 1)
    walk(root)
    text = "".join(out)
    return re.sub(r"\n{3,}", "\n\n", text)

done = 0
with open(MANIFEST, "w", newline="") as mf:
    w = csv.DictWriter(mf, fieldnames=["pool", "n", "pmcid", "doi", "status", "xml_bytes", "txt_chars", "file"])
    w.writeheader()
    for r in rows:
        pmc = r["epmc_pmcid"]
        base = f"{OUTDIR}/pool{r['pool']}_n{r['n']}_{pmc}"
        status, xb, tc = "", 0, 0
        if os.path.exists(base + ".txt") and os.path.getsize(base + ".txt") > 500:
            status = "exists"
        else:
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
            req = urllib.request.Request(url, headers={"User-Agent": "incretin-aging-biomarkers-review/1.0 (systematic review full text pool)"})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                if not data.strip():
                    status = "empty"
                else:
                    open(base + ".xml", "wb").write(data)
                    txt = xml_to_text(data)
                    open(base + ".txt", "w").write(txt)
                    xb, tc, status = len(data), len(txt), "ok"
            except Exception as e:
                status = f"error: {str(e)[:80]}"
            time.sleep(0.4)
        done += status in ("ok", "exists")
        w.writerow(dict(pool=r["pool"], n=r["n"], pmcid=pmc, doi=r["doi"], status=status, xml_bytes=xb, txt_chars=tc, file=base + ".txt"))
        mf.flush()
        if len(rows) and (rows.index(r) + 1) % 20 == 0:
            print(f"  {rows.index(r) + 1}/{len(rows)} ({done} ok)", flush=True)
print(f"done: {done} of {len(rows)} full texts saved under {OUTDIR}", flush=True)
