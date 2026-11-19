# -*- coding: utf-8 -*-
"""Task 1 / Step A: live Crossref -> ISSN, 2024 item volume, and scope-fit hits.
No recalled figures. Everything below comes from api.crossref.org responses.
Writes venue_probe.json."""
import urllib.request, urllib.parse, json, os, time, re
HERE=os.path.dirname(os.path.abspath(__file__))
UA="venue-verify/1.0 (bibliographic audit)"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=45) as f:
        return json.load(f)

# direction-level candidates from idea_final_v2.md §6 (theory/control layer),
# EXCLUDING vehicle journals (Drones/Aerospace/JGCD/TAES) and top-tier (Automatica/TAC)
CAND=[
 "Nonlinear Dynamics",
 "International Journal of Robust and Nonlinear Control",
 "Journal of the Franklin Institute",
 "Nonlinear Analysis: Hybrid Systems",
 "IET Control Theory & Applications",
 "ISA Transactions",
 "IEEE Transactions on Control Systems Technology",
]
TOPICS=[
 "quadrotor attitude recoverability impulse",
 "non-recoverability bound actuator saturation",
 "region of attraction impulsive systems",
]
out={"step":"A","generated":time.strftime("%Y-%m-%d %H:%M:%S"),"journals":{}}
for name in CAND:
    j={"name":name}
    # --- ISSN via Crossref journals query ---
    try:
        # NOTE: do NOT pass select=... here — Crossref drops the ISSN field when
        # the select list is present (verified against the no-select response).
        u="https://api.crossref.org/journals?query="+urllib.parse.quote(name,safe="")+"&rows=8"
        items=get(u)["message"]["items"]
        exact=[it for it in items if (it.get("title") or "").strip().lower()==name.lower() or
               (it.get("title") or "").strip().lower()==name.lower().replace("&","and")]
        pick=(exact or items)[0] if items else None
        j["issn"]=pick.get("ISSN") if pick else None
        j["title_matched"]=bool(exact)
        j["crossref_title"]=pick.get("title") if pick else None
        j["publisher"]=pick.get("publisher") if pick else None
        j["journal_candidates"]=[{"title":it.get("title"),"ISSN":it.get("ISSN")} for it in items[:5]]
    except Exception as e:
        j["issn"]=None; j["issn_error"]=str(e)[:120]
    # --- 2024 item volume (Crossref item count, NOT acceptance figure) ---
    # IET CTA: container-title in Crossref does not match the display name, so
    # fall back to an ISSN-scoped query; a 0 there is a DATA GAP, not zero output.
    try:
        u=("https://api.crossref.org/works?filter=container-title:"+urllib.parse.quote(name,safe="")
           +",from-pub-date:2024-01-01,until-pub-date:2024-12-31&rows=1&select=DOI")
        j["crossref_2024_items"]=get(u)["message"]["total-results"]
        if j["crossref_2024_items"]==0 and j.get("issn"):
            issn=j["issn"][0]
            u2=("https://api.crossref.org/journals/"+issn
                +"/works?filter=from-pub-date:2024-01-01,until-pub-date:2024-12-31&rows=1&select=DOI")
            j["crossref_2024_items_issn_scoped"]=get(u2)["message"]["total-results"]
            j["container_title_note"]="display-name filter returned 0; ISSN-scoped query used instead"
    except Exception as e:
        j["crossref_2024_items"]=None; j["vol_error"]=str(e)[:120]
    # --- scope-fit: read returned TITLES, never total-results (recipe §3) ---
    j["scope_hits"]={}
    for tp in TOPICS:
        try:
            u=("https://api.crossref.org/works?filter=container-title:"+urllib.parse.quote(name,safe="")
               +"&query.bibliographic="+urllib.parse.quote(tp,safe="")
               +"&rows=6&select=DOI,title,issued,container-title")
            its=get(u)["message"]["items"]
            j["scope_hits"][tp]=[
                {"title":(it.get("title") or [""])[0][:110],
                 "year":(it.get("issued") or {}).get("date-parts",[[None]])[0][0],
                 "doi":it.get("DOI")} for it in its]
        except Exception as e:
            j["scope_hits"][tp]={"error":str(e)[:120]}
    out["journals"][name]=j
    print("done:",name,"| ISSN",j.get("issn"),"| 2024 items",j.get("crossref_2024_items"),
          "| title_matched",j.get("title_matched"),flush=True)
json.dump(out,open(os.path.join(HERE,"venue_probe.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("WROTE venue_probe.json")
