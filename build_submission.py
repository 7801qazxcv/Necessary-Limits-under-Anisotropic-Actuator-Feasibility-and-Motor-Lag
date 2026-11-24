# -*- coding: utf-8 -*-
"""Build the UPLOAD package: only files that travel with the manuscript.
`paper/` remains the gate working dir (deliver_gate needs pre_review_report.md).
After build, assert no editorial-only / internal-review wording is present.
"""
import os, shutil, re
HERE=os.path.dirname(os.path.abspath(__file__))
PAPER=os.path.join(HERE,"paper")
SUB=os.path.join(HERE,"submission")
FILES=["main.tex","main.pdf","refs.bib","title_page.tex","title_page.pdf","highlights.txt"]
FIGDIR="figures"
if os.path.isdir(SUB): shutil.rmtree(SUB)
os.makedirs(os.path.join(SUB,FIGDIR))
for f in FILES:
    shutil.copy2(os.path.join(PAPER,f), os.path.join(SUB,f))
for f in sorted(os.listdir(os.path.join(PAPER,FIGDIR))):
    if f.endswith(".pdf"):
        shutil.copy2(os.path.join(PAPER,FIGDIR,f), os.path.join(SUB,FIGDIR,f))

# neutral MANIFEST (no enumerated exclusions -- those phrases themselves trip scans)
manifest="""# Manuscript files

Only the files listed below are included.

| File | Role |
|---|---|
| `main.tex` | self-contained ANONYMIZED manuscript (pure LF, no \\input) |
| `main.pdf` | compiled manuscript |
| `refs.bib` | bibliography (24 verified entries) |
| `title_page.tex` | separate title page (double-anonymized review) |
| `title_page.pdf` | compiled title page for upload |
| `highlights.txt` | 3-5 article highlights, <=85 characters each |
| `figures/fig1.pdf` .. `fig4.pdf` | four figures |

Regeneration of every displayed number: `experiments/run_all_experiments.py`
in the accompanying reproduction package (not part of this upload).
"""
open(os.path.join(SUB,"MANIFEST.md"),"w",encoding="utf-8",newline="\n").write(manifest)

# scan ALL file types in upload package (skill S11: .py/.json/.bib too)
bad=[]
pat=re.compile(r"reviewer|rebuttal|self-review|pre-submission build|editorial-only|"
               r"flagged for author|wider project audit|withheld|AI_DISCLOSURE_HISTORY",re.I)
for dp,dn,fn in os.walk(SUB):
    for f in fn:
        fp=os.path.join(dp,f)
        try: txt=open(fp,encoding="utf-8",errors="ignore").read()
        except Exception: continue
        for m in pat.finditer(txt):
            bad.append((os.path.relpath(fp,HERE),m.group(0)))
print("UPLOAD FILES:",sorted(os.path.relpath(os.path.join(dp,f),SUB) for dp,dn,fn in os.walk(SUB) for f in fn))
print("INTERNAL-WORDING HITS:",bad)
print("CLEAN:" , not bad)
assert not bad, "internal wording leaked into upload package"
