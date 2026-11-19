# -*- coding: utf-8 -*-
"""Task 2 / Layer 1: existence + field-by-field metadata verification.
Every field comes from a LIVE Crossref / arXiv API response; nothing from memory.
Writes ref_meta_raw.json. No abstract is fabricated: missing -> null + flag."""
import urllib.request, urllib.parse, json, re, time, sys, os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "ref-verify/1.0 (bibliographic audit; contact via publisher)"

# Candidate pool: DOI/arXiv ids found in prior_art_scan + cites_verified + ledger.
DOIS = [
 "10.3390/app14093639", "10.1016/j.isatra.2025.08.030",
 "10.1155/2020/5493686", "10.1109/TCSII.2020.3045769",
 "10.1002/acs.3484", "10.1007/s12555-024-0402-6",
 "10.2514/6.2014-0786", "10.1007/s11071-019-05301-1",
 "10.1049/itr2.70219", "10.3390/drones10050363",
 "10.1002/rnc.6001", "10.1002/rnc.70606",
 "10.1371/journal.pone.0360921", "10.2514/6.2013-5172",
 "10.2514/6.2012-2429",
]
ARXIV = ["2002.09425","2603.14698","2303.10243","2404.07837","1508.04886",
         "2610.15867","2606.16513","1907.11673","2603.18450","2210.10868"]

def clean_abs(s):
    if not s: return None
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def crossref(doi):
    u = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=45) as fh:
            m = json.load(fh)["message"]
        auth = []
        for a in (m.get("author") or []):
            fam = a.get("family",""); giv = a.get("given","")
            auth.append((giv+" "+fam).strip())
        return {"ok": True,
                "title": (m.get("title") or [""])[0],
                "authors": auth,
                "venue": (m.get("container-title") or [""])[0],
                "year": (m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts",[[None]])[0][0],
                "volume": m.get("volume"), "issue": m.get("issue"), "page": m.get("page"),
                "type": m.get("type"),
                "abstract": clean_abs(m.get("abstract")),
                "doi": doi}
    except Exception as e:
        return {"ok": False, "error": "%s: %s" % (type(e).__name__, str(e)[:120]), "doi": doi}

def arxiv(aid):
    u = "http://export.arxiv.org/api/query?id_list=" + aid
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=45) as fh:
            raw = fh.read()
        root = ET.fromstring(raw)
        ns = {"a":"http://www.w3.org/2005/Atom"}
        e = root.find("a:entry", ns)
        if e is None:
            return {"ok": False, "error":"no entry", "arxiv": aid}
        ti = e.find("a:title", ns); summ = e.find("a:summary", ns)
        pub = e.find("a:published", ns)
        auth = [a.find("a:name", ns).text for a in e.findall("a:author", ns) if a.find("a:name", ns) is not None]
        jr = e.find("a:journal_ref", ns)
        doi_f = e.find("{http://arxiv.org/schemas/atom}doi")
        return {"ok": True,
                "title": re.sub(r"\s+"," ", ti.text).strip() if ti is not None else None,
                "authors": auth,
                "venue": ("arXiv preprint arXiv:%s"%aid) if jr is None else jr.text.strip(),
                "year": int(pub.text[:4]) if pub is not None else None,
                "published": pub.text if pub is not None else None,
                "abstract": clean_abs(summ.text) if summ is not None else None,
                "journal_ref": jr.text.strip() if jr is not None else None,
                "doi_crosslisted": doi_f.text.strip() if doi_f is not None else None,
                "arxiv": aid}
    except Exception as e:
        return {"ok": False, "error": "%s: %s" % (type(e).__name__, str(e)[:120]), "arxiv": aid}

out = {"layer": 1, "crossref": {}, "arxiv": {}, "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
for d in DOIS:
    out["crossref"][d] = crossref(d); print("DOI", d, "->", out["crossref"][d]["ok"], flush=True)
for a in ARXIV:
    out["arxiv"][a] = arxiv(a); print("ARX", a, "->", out["arxiv"][a]["ok"], flush=True)
json.dump(out, open(os.path.join(HERE,"ref_meta_raw.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE ref_meta_raw.json")
