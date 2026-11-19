# -*- coding: utf-8 -*-
"""ONE-COMMAND reproduction entry point (protocol requirement #5).

DEFAULT mode: verify every frozen result artifact's key fields, then regenerate
the derived products (number macros, four figures, manuscript assembly) and
print an artifact manifest. This is exactly what the manuscript claims.

--full mode: additionally RE-RUN the complete probe chain first (scalar probe,
6-DoF probe on both platforms, asymmetric diagnostic, theorem audit,
parameter sensitivity) before regenerating derived products. Can take several
minutes; use it when the frozen artifacts must be reproduced from code.

No number is invented: every macro/figure is rebuilt from on-disk JSON.
Prints ALL STEPS OK on success, exits non-zero otherwise."""
import os, subprocess, sys, json, glob, re
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root (parent of experiments/)
PY=sys.executable
FULL=("--full" in sys.argv)

FULL_CHAIN=[
 ("scalar probe",             "probe_v1.py"),
 ("6-DoF probe (synthetic)",  "probe_v2.py"),
 ("6-DoF probe (identified)", "run_real_platform.py"),
 ("asymmetric diagnostic",    "asym_diagnostic.py"),
 ("theorem audit",            "theorem_audit.py"),
 ("parameter sensitivity",    "param_sensitivity.py"),
 ("M1 lemma + measured Omega","m1_lemma.py"),
 ("M1 correction (downgrade)","m1_lemma_correction.py"),
 ("M3 comparison + n>=3",     "m3_comparison.py"),
 ("math red-team (finite horizon)","math_redteam.py"),
 ("review followup (P2/P5/P8/P13)","review_followup.py"),
]
DERIVED=[
 ("number macros","build_manuscript_numbers.py"),
 ("figures","build_figures.py"),
 ("manuscript assembly","build_manuscript.py"),
 ("upload package","build_submission.py"),
]
def L(f): return json.load(open(os.path.join(HERE,f),encoding="utf-8"))
def run(name,script):
    r=subprocess.run([PY,os.path.join(HERE,script)],cwd=HERE,capture_output=True,text=True)
    ok=(r.returncode==0)
    print("  [%s] %s (%s)"%("OK" if ok else "FAIL",name,script))
    if not ok: print("      ",(r.stderr or r.stdout)[-400:])
    return ok

def verify_artifacts():
    """Assert the key claims against the frozen JSONs (not against prose)."""
    print("=== frozen-artifact field verification ===")
    ok=True
    syn=L("probe_v2_results.json"); real=L("probe_v2_REAL_results.json")
    th=L("theorem_audit.json"); asym=L("asym_diagnostic.json"); l2=L("citation_layer2.json")
    m1=L("m1_lemma.json"); m3=L("m3_comparison.json")
    mr=L("math_redteam.json"); fu=L("review_followup.json")
    checks=[
      ("synthetic V1 violations == 0", syn["go_evaluation"]["V1_hard_upper_bound"]["n_violations"]==0),
      ("identified V1 violations == 0", real["go_evaluation"]["V1_hard_upper_bound"]["n_violations"]==0),
      ("identified verdict == NO-GO", real["go_evaluation"]["VERDICT"]=="NO-GO"),
      ("theorem audit all_must_pass", th["summary"]["all_must_pass"] is True),
      ("theorem audit failed == []", th["summary"]["failed"]==[]),
      ("asym diagnostic status == DONE", asym["status"]=="DONE"),
      ("asym sym-slow stable == 0", asym["summary"]["sym_slow_slowgain_stable"]==0),
      ("asym slow-gain stable == 8", asym["summary"]["asym_slowgain_stable"]==8),
      ("citation rows == 24", l2["n_rows"]==24),
      ("misattributions == 0", l2["summary"]["MISATTRIBUTION"]==0),
      ("m1 lemma status == DONE_CORRECTED", m1["status"]=="DONE_CORRECTED"),
      ("m1 attitude extension NOT claimed", all(
          v["attitude_extension_valid"] is False for v in m1["a1free_bounds"].values())),
      ("m3 comparison status == DONE", m3["status"]=="DONE"),
      ("m3 logic cheap-null all pass", all(r["logic_ok"] for r in m3["comparison"]["rows"])),
      ("n>=3 three phases complete", all(
          len(m3["replication"][ph]["cells"])==48 for ph in m3["phases"])),
      ("red-team: all t* <= T", all(r["t_star_le_T"] for r in mr["rows"])),
      ("red-team: L* re-derived bit-identical", max(r["L_abs_diff"] for r in mr["rows"])==0.0),
      ("red-team: finite-horizon L_T == L", max(abs(r["L_finiteT_minus_L"]) for r in mr["rows"])==0.0),
      ("red-team: critical root unique", fu["checks"]["P5_root_uniqueness"]["all_monotone"]
          and fu["checks"]["P5_root_uniqueness"]["all_Aprime_single_sign_change"]),
      ("red-team: first passage before wrap", fu["checks"]["P2_first_passage"]["all_wrap_impossible"]),
      ("L_suff independent of analytic L_nec", not fu["checks"]["P8_independence"]["L_suff_calls_L_nec"]),
    ]
    bib=open(os.path.join(HERE,"refs.bib"),encoding="utf-8").read()
    keys=re.findall(r"@\w+\{([^,]+),",bib)
    checks.append(("refs.bib 24 unique keys", len(keys)==24 and len(set(keys))==24))
    for name,cond in checks:
        print("  [%s] %s"%("OK" if cond else "FAIL",name)); ok &= bool(cond)
    return ok

print("=== run_all_experiments (mode: %s) ==="%("FULL" if FULL else "verify+regenerate"))
allok=True
if FULL:
    for n,s in FULL_CHAIN: allok &= run(n,s)
allok &= verify_artifacts()
print("\n=== regenerate derived products ===")
for n,s in DERIVED: allok &= run(n,s)
print("\n=== artifact manifest ===")
for f in sorted(glob.glob(os.path.join(HERE,"*.json"))):
    try:
        json.load(open(f,encoding="utf-8")); print("  OK   ",os.path.basename(f))
    except Exception as e:
        print("  BAD  ",os.path.basename(f),str(e)[:60]); allok=False
for f in ["refs.bib","numbers.tex","paper/main.tex","paper/refs.bib"]:
    p=os.path.join(HERE,f); exists=os.path.exists(p)
    print("  %s  %s"%("OK  " if exists else "MISS",f), os.path.getsize(p) if exists else "")
    allok &= exists
print("\nALL STEPS OK" if allok else "\nSOME STEPS FAILED")
sys.exit(0 if allok else 1)
