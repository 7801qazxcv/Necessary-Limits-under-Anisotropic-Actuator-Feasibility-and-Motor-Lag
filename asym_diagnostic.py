# -*- coding: utf-8 -*-
"""Amendment-4 DIAGNOSTIC: is the real-platform NO-GO (4/8 BLOCKED cells) a
model-mismatch artifact of bracketing an ASYMMETRIC actuator as two SYMMETRIC runs?

Falsifiable design (integrity principle 6/7/13):
  - NO new tuning: reuse the ALREADY calibrated gains from probe_v2_REAL_results.json
    (both per-Tm sets), only swap the actuator model. No re-tuning to win.
  - Equivalence probe FIRST: ASYM_TM=(t,t) must be byte-identical to symmetric Tm=t.
  - PURELY NUMERICAL: L_nec (single-Tm Lemma 1) is NOT evaluated here. No GO verdict
    is produced. This only answers "is the slow-bracket divergence an artifact?".
  - Three actuator models: sym-fast(0.055455), sym-slow(0.249394), asym(0.055455/0.249394).
Writes asym_diagnostic.json incrementally."""
import json, os, importlib.util, numpy as np, time
HERE=os.path.dirname(os.path.abspath(__file__))
sp=importlib.util.spec_from_file_location("p2",os.path.join(HERE,"probe_v2.py"))
p2=importlib.util.module_from_spec(sp); sp.loader.exec_module(p2)

cfg=json.load(open(os.path.join(HERE,"real_platform_config.json"),encoding="utf-8"))["mapped_to_model"]
cfg["result_file"]="asym_diagnostic_results_placeholder.json"   # never written by this script
p2.configure(cfg)
REAL=json.load(open(os.path.join(HERE,"probe_v2_REAL_results.json"),encoding="utf-8"))
CAL=REAL["calibration"]
T_FAST,T_SLOW=p2.TM_LIST
W=np.array(REAL["meta"]["W_mech"],dtype=float)
FAMS=["qpd","smc","qpd_ff","proposed"]

def gains(fam,which):
    return CAL[fam][str(T_FAST if which=="fast" else T_SLOW)]

def set_model(model):
    if model=="asym": p2.ASYM_TM=(T_FAST,T_SLOW)
    else:
        p2.ASYM_TM=None   # Tm passed to simulate carries the symmetric value

def sym_tm(model):
    return T_FAST if model=="fast" else (T_SLOW if model=="slow" else T_FAST)

out={"probe":"amendment4_asym_diagnostic","status":"RUNNING",
     "config":{"T_fast":T_FAST,"T_slow":T_SLOW,"W_mech":W.tolist(),
               "models":["fast","slow","asym"],"gain_sets":["fast","slow"]},
     "equivalence":{}, "baseline":{}, "boundary":{}, "notes":[]}
DPath=os.path.join(HERE,"asym_diagnostic.json")
# ---- resume: long-compute-runner discipline (silent death -> restart continues) ----
if os.path.exists(DPath):
    try:
        prev=json.load(open(DPath,encoding="utf-8"))
        if prev.get("status") in ("RUNNING","DONE") and prev.get("baseline"):
            out=prev
            print("RESUMED: equivalence=%d baseline=%d boundary=%d"%(
                len(out["equivalence"]),len(out["baseline"]),len(out["boundary"])),flush=True)
    except Exception as e:
        print("resume skipped:",e,flush=True)
def save():
    # atomic write: a killed/crashed process must never leave a truncated JSON
    tmp=DPath+".tmp"
    with open(tmp,"w",encoding="utf-8") as fh:
        json.dump(out,fh,ensure_ascii=False,indent=1)
    os.replace(tmp,DPath)

# ---------- 0) default guard ----------
# ASYM_TM must be None here; the byte-identical DEFAULT check is done separately
# on the untouched module (see verify_default.py output in the report). The
# EQUIVALENCE probe below is the real proof that the new branch preserves symmetry.
assert p2.ASYM_TM is None
out["notes"].append("configured with real platform; ASYM_TM=None at start; default v2.3 byte-identical verified separately")

# ---------- 1) EQUIVALENCE PROBE: ASYM(t,t) == symmetric Tm=t ----------
# Use a mid configuration: ASYM with equal rising/falling must reproduce symmetric.
for fam in ["qpd_ff","proposed"]:
    if fam in out["equivalence"] and out["equivalence"][fam].get("pass"):
        continue
    Kp,Kd=gains(fam,"fast")["Kp"],gains(fam,"fast")["Kd"]
    dwv=np.array([0.0,1.0,3.0,8.0])
    p2.ASYM_TM=None; a=p2.simulate(dwv,p2.DIRS["roll"],T_FAST,fam,Kp,Kd,W)
    p2.ASYM_TM=(T_FAST,T_FAST); b=p2.simulate(dwv,p2.DIRS["roll"],T_FAST,fam,Kp,Kd,W)
    dmax=float(np.max(np.abs(a[0]-b[0]))); dwmax=float(np.max(np.abs(a[1]-b[1])))
    ok_eq=bool(np.array_equal(a[2],b[2]))
    out["equivalence"][fam]={"maxphi_absdiff":dmax,"wfin_absdiff":dwmax,
                             "ok_pattern_identical":ok_eq,"pass":bool(dmax<1e-12 and dwmax<1e-12 and ok_eq)}
p2.ASYM_TM=None
save()
print("EQUIVALENCE:",{k:v["pass"] for k,v in out["equivalence"].items()},flush=True)

# ---------- 2) BASELINE HEALTH: dw=0 under each (model, gain_set, dir, fam) ----------
t0=time.time()
for model in ["fast","slow","asym"]:
    set_model(model)
    for gset in ["fast","slow"]:
        for dk,n in p2.DIRS.items():
            for fam in FAMS:
                key=f"{model}|{gset}|{dk}|{fam}"
                if key in out["baseline"]:
                    continue
                g=gains(fam,gset)
                mp,wf,ok,bad,_=p2.simulate(np.array([0.0]),n,sym_tm(model),fam,g["Kp"],g["Kd"],W)
                out["baseline"][key]={"stable":bool((not bad) and ok[0]),
                                      "maxphi_dw0":float(mp[0]),"wfin_dw0":float(wf[0])}
        save()
        print("baseline %s/%s done (%.0fs)"%(model,gset,time.time()-t0),flush=True)
p2.ASYM_TM=None

# ---------- 3) BOUNDARY: first_fail_dw on wide grid (vectorised) ----------
wide=np.linspace(0.2,30.0,160)
BUDGET=int(os.environ.get("ASYM_BUDGET","40"))   # max NEW boundary cells per invocation
new_cells=0
for model in ["fast","slow","asym"]:
    set_model(model)
    for gset in ["fast","slow"]:
        for dk,n in p2.DIRS.items():
            for fam in FAMS:
                bkey=f"{model}|{gset}|{dk}|{fam}"
                if bkey in out["boundary"]:
                    continue
                if new_cells>=BUDGET:
                    print("BUDGET reached (%d new cells), saving & exiting for resume"%new_cells,flush=True)
                    save(); raise SystemExit(0)
                g=gains(fam,gset)
                mp,wf,ok,bad,c=p2.simulate(wide,n,sym_tm(model),fam,g["Kp"],g["Kd"],W)
                ff=None; islands=False
                for i,o in enumerate(ok):
                    if not o and ff is None: ff=float(wide[i])
                    elif ff is not None and o: islands=True
                out["boundary"][bkey]={
                    "first_fail_dw":ff,"islands":islands,"n_ok":int(ok.sum()),"bad":bad}
                new_cells+=1
        save()
        print("boundary %s/%s done (+%d new, total %d)"%(model,gset,new_cells,len(out["boundary"])),flush=True)
p2.ASYM_TM=None

# ---------- 4) aggregate verdict ----------
def n_stable(model,gset):
    return sum(1 for k,v in out["baseline"].items() if k.startswith(model+"|"+gset+"|") and v["stable"])
out["summary"]={
  "stable_counts":{f"{m}|{g}":n_stable(m,g) for m in ["fast","slow","asym"] for g in ["fast","slow"]},
  "n_baseline_cells":len(out["baseline"]),
  "asym_slowgain_stable":n_stable("asym","slow"),
  "sym_slow_slowgain_stable":n_stable("slow","slow"),
}
out["status"]="DONE"
save()
print("\n=== SUMMARY ===")
for k,v in out["summary"]["stable_counts"].items(): print("  stable",k,"=",v,"/16")
print("  equivalence all pass:",all(v["pass"] for v in out["equivalence"].values()))
print("WROTE asym_diagnostic.json  elapsed %.0fs"%(time.time()-t0))
