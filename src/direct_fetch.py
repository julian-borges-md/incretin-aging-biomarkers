#!/usr/bin/env python3
"""Direct (unauthenticated) fetch of the publisher landing page for every pool
record that still needs a full text: resolves the DOI, saves the page text,
and classifies it as full text, abstract only, or blocked, by simple marks
(section headings and length). Preprints on bioRxiv or medRxiv are fetched as
JATS XML through the preprint API. Everything lands under work/fulltext/direct/
(gitignored) with a manifest. No credentials, no proxy."""
import csv, html, json, os, re, sys, time, urllib.request, urllib.error
import xml.etree.ElementTree as ET
TODO = "work/closed_access_todo.csv"
OUTDIR = "work/fulltext/direct"
MANIFEST = f"{OUTDIR}/MANIFEST_direct_2026-10-16.csv"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) incretin-aging-biomarkers-review/1.0 (systematic review full text pool)"}

class Strip(html.parser.HTMLParser if hasattr(html, "parser") else object):
    pass

from html.parser import HTMLParser
class TextOf(HTMLParser):
    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg", "nav", "header", "footer"): self.skip += 1
        if tag in ("p", "div", "br", "h1", "h2", "h3", "h4", "li", "tr", "section", "table"): self.out.append("\n")
        if tag in ("td", "th"): self.out.append("\t")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "nav", "header", "footer"): self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip: self.out.append(data)
    def text(self):
        t = html.unescape("".join(self.out)); return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", t))

def html_to_text(raw):
    p = TextOf(); p.feed(raw); return p.text()

def xml_to_text(xml_bytes):
    root = ET.fromstring(xml_bytes); out = []
    def walk(el):
        tag = el.tag.split('}')[-1]
        if tag in ("title", "label"): out.append("\n## " + "".join(el.itertext()).strip() + "\n"); return
        if tag in ("p", "td", "th", "caption", "abstract"): out.append("".join(el.itertext()).strip() + ("\t" if tag in ("td", "th") else "\n")); return
        for c in el: walk(c)
        if tag == "tr": out.append("\n")
    walk(root); return re.sub(r"\n{3,}", "\n\n", "".join(out))

PAYWALL = re.compile(r"Buy article|Access this article|Institutional subscription|Purchase PDF|Get access|Access options|Rent this article|Sign in to access|Subscribe to journal", re.I)

def classify(t):
    if len(t) < 1500: return "blocked_or_empty"
    if PAYWALL.search(t) and not re.search(r"Creative Commons|This is an open access article|Open Access This article", t):
        return "paywalled_page"
    marks = sum(bool(re.search(p, t)) for p in (r"\bMethods\b|\bMETHODS\b|\bMaterials and methods\b", r"\bResults\b|\bRESULTS\b", r"\bDiscussion\b|\bDISCUSSION\b", r"\bReferences\b|\bREFERENCES\b"))
    if marks >= 3 and len(t) > 12000: return "fulltext"
    return "abstract_or_partial"

def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.geturl(), resp.read()

rows = list(csv.DictReader(open(TODO)))
# A rerun keeps every manifest row whose text is already on disk as a full text (including rows
# added by hand for records found by title, such as pool1_n605, Fan 2013 on SciELO): the first
# rerun (2026-10-16 12:35, pool 3 joining) rewrote that row as no_doi and the screen lost the text.
kept = {}
if os.path.exists(MANIFEST):
    for r in csv.DictReader(open(MANIFEST)):
        if r["status"].startswith("fulltext") and r["file"] and os.path.exists(r["file"]):
            kept[(r["pool"], r["n"])] = r
with open(MANIFEST, "w", newline="") as mf:
    w = csv.DictWriter(mf, fieldnames=["pool", "n", "doi", "final_url", "status", "chars", "file"]); w.writeheader()
    for r in rows:
        key = f"pool{r['pool']}_n{r['n']}"
        doi = r["doi"]
        status, final, chars, path = "", "", 0, ""
        if (r["pool"], r["n"]) in kept:
            k = kept[(r["pool"], r["n"])]
            w.writerow(k); mf.flush(); print(key, "kept", k["status"], k["chars"], flush=True)
            continue
        if not doi:
            status = "no_doi"
        elif doi.startswith("10.1101/"):
            try:
                server = "medrxiv"
                _, meta = fetch(f"https://api.{server}.org/details/{server}/{doi}")
                m = json.loads(meta)
                coll = m.get("collection", [])
                if not coll:
                    server = "biorxiv"; _, meta = fetch(f"https://api.{server}.org/details/{server}/{doi}"); coll = json.loads(meta).get("collection", [])
                if coll:
                    jats = coll[-1].get("jatsxml", "")
                    final, data = fetch(jats)
                    t = xml_to_text(data); path = f"{OUTDIR}/{key}_preprint.txt"; open(path, "w").write(t)
                    chars, status = len(t), classify(t) + "_preprint"
                else:
                    status = "preprint_not_found"
            except Exception as e:
                status = f"error: {str(e)[:60]}"
        else:
            try:
                final, data = fetch(f"https://doi.org/{doi}")
                t = html_to_text(data.decode("utf-8", errors="replace"))
                path = f"{OUTDIR}/{key}.txt"; open(path, "w").write(t)
                chars, status = len(t), classify(t)
            except urllib.error.HTTPError as e:
                status = f"http {e.code}"
            except Exception as e:
                status = f"error: {str(e)[:60]}"
        w.writerow(dict(pool=r["pool"], n=r["n"], doi=doi, final_url=final[:120], status=status, chars=chars, file=path)); mf.flush()
        print(key, status, chars, flush=True)
        time.sleep(1.5)
print("done", flush=True)
