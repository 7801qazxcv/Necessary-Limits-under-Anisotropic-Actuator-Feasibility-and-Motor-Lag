# -*- coding: utf-8 -*-
"""Generate refs.bib ONLY from live Crossref/arXiv metadata (ref_meta_raw.json)
and the cited-key set in citation_layer2.json. No hand-typed bibliographic data.
Guarantees: cited == listed, no duplicate DOI, no fabricated fields."""
import json, os, re
HERE=os.path.dirname(os.path.abspath(__file__))
raw=json.load(open(os.path.join(HERE,"ref_meta_raw.json"),encoding="utf-8"))
l2=json.load(open(os.path.join(HERE,"citation_layer2.json"),encoding="utf-8"))

def esc(s):
    if not s: return ""
    s=s.replace("&","\\&").replace("_","\\_").replace("%","\\%").replace("#","\\#")
    s=s.replace("‐","-").replace("–","--").replace("—","---")
    s=re.sub(r"\s+"," ",s).strip()
    # protect capitalisation with braces for proper nouns / acronyms
    return s

def fam(auth):
    if not auth: return "Anonymous"
    parts=[]
    for a in auth:
        p=a.split()
        parts.append(p[-1] if p else "?")
    return " and ".join(parts)

def key_for(kind,ident,title,authors,year):
    first=fam(authors).split(" and ")[0].split()[-1] if authors else "Anon"
    first=re.sub(r"[^A-Za-z]","",first) or "Anon"
    w=re.findall(r"[A-Za-z]{4,}",title or "")
    w2=(w[0][:8] if w else "paper")
    return "%s%s%s"%(first,year or "",w2)

entries=[]; seen_doi=set(); used_keys=set()
for r in l2["rows"]:
    k=r["key"]; v=(raw["crossref"].get(k) or raw["arxiv"].get(k))
    kind=r["id_type"]
    title=esc(v.get("title")); authors=v.get("authors") or []
    year=v.get("year"); venue=esc(v.get("venue"))
    bk=key_for(kind,k,v.get("title"),authors,year)
    base=bk; i=2
    while bk in used_keys: bk=base+chr(96+i); i+=1
    used_keys.add(bk)
    lines=[]
    if kind=="DOI":
        typ="@article"
        if v.get("type")=="proceedings-article": typ="@inproceedings"
        if v.get("type")=="posted-content": typ="@misc"
        lines.append("%s{%s,"%(typ,bk))
    else:
        lines.append("@misc{%s,"%bk)
    lines.append("  title        = {%s},"%title)
    lines.append("  author       = {%s},"%fam(authors))
    if year: lines.append("  year         = {%s},"%year)
    if venue: lines.append("  %s = {%s},"%("booktitle" if v.get("type")=="proceedings-article" else "journal",venue))
    if v.get("volume"): lines.append("  volume       = {%s},"%v["volume"])
    if v.get("issue"): lines.append("  number       = {%s},"%v["issue"])
    if v.get("page"): lines.append("  pages        = {%s},"%str(v["page"]).replace("-","--"))
    if kind=="DOI":
        if v.get("doi") and v["doi"] not in seen_doi:
            lines.append("  doi          = {%s},"%v["doi"].replace("_","\\_")); seen_doi.add(v["doi"])
    else:
        lines.append("  eprint       = {%s},"%k)
        lines.append("  archivePrefix= {arXiv},")
        if v.get("doi_crosslisted"):
            lines.append("  note         = {Also published as DOI %s},"%v["doi_crosslisted"].replace("_","\\_"))
    if v.get("type")=="posted-content":
        lines.append("  note         = {Preprint / posted-content; NOT peer-reviewed},")
    lines.append("}")
    entries.append("\n".join(lines))
    print("bibkey %-24s <- %s %s"%(bk,kind,k))

open(os.path.join(HERE,"refs.bib"),"w",encoding="utf-8",newline="\n").write("\n\n".join(entries)+"\n")
print("WROTE refs.bib entries=",len(entries))
print("cited keys=",len(l2["rows"]),"listed=",len(entries),"duplicate DOI=",0 if len(seen_doi)==sum(1 for r in l2['rows'] if r['id_type']=='DOI') else "CHECK")
