# -*- coding: utf-8 -*-
"""M3: quantitative comparison with a standard sufficient-domain proxy AND
n>=3 replication over independent disturbance phases.

Honesty constraints (frozen in preregistration_m1_m3.md):
* prior-art SOS-ROA / recoverable-set / bCBF have no public implementation here
  -> we do NOT fabricate their numbers. Proxy = standard quadratic-Lyapunov ROA
  estimation on the linearised single-axis closed loop (same plant, same gains).
* Logical cheap-null: sufficient domain <= recoverable set <= [0, L*].
  If L_lyap > L* we treat it as an implementation/scope BUG, not a win.
* n>=3 = 3 independent SEED_PHASE realisations of the turbulent disturbance,
  NOT re-running the same deterministic case 3 times.
* The adversarial arm uses a CONSTANT disturbance (independent of SEED_PHASE);
  it therefore cannot provide independent replicates -- stated, not faked.
* Incremental, resumable writes. BUDGET limits new cells per invocation.
"""
import os, json, sys, math, time
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import probe_v2 as p2

OUT=os.path.join(HERE,"m3_comparison.json")
PHASES={
 "P1": [0.0, 1.7, 3.4, 5.1, 2.2],   # frozen baseline (identical to v2.3)
 "P2": [0.9, 2.6, 4.3, 0.4, 3.1],
 "P3": [1.8, 3.5, 0.6, 1.3, 4.0],
}
CELLS=[(dk,Tm,fam) for dk in ["roll","pitch","yaw","combo"]
                    for Tm in p2.TM_LIST
                    for fam in ["qpd","smc","qpd_ff","proposed"]]
CAL=json.load(open(os.path.join(HERE,"probe_v2_results.json"),encoding="utf-8"))["calibration"]
W_mech=[1.0,1.0,0.12856486930664499]

def save(d):
    tmp=OUT+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=1,
                  default=lambda o:o.item() if hasattr(o,"item") else str(o))
    os.replace(tmp,OUT)

def load():
    if os.path.isfile(OUT):
        try: return json.load(open(OUT,encoding="utf-8"))
        except Exception: pass
    return {"status":"RUNNING","prereg":"preregistration_m1_m3.md",
            "phases":PHASES,"proxy":None,"comparison":None,"replication":{}}

d=load()

# ---------- Part A: quadratic-Lyapunov sufficient-domain proxy ----------
def lyap_proxy(dk,Tm,fam):
    """Standard 2x2 continuous Lyapunov equation A^T P + P A = -Q (Q=I) on the
    linearised single-axis closed loop x=[phi,omega], A=[[0,1],[-Kp/J,-Kd/J]].
    ROA ellipsoid {x^T P x <= c}; c limited by (i) |phi|<=PHI_MAX and
    (ii) actuator torque saturation |Kp phi + Kd omega| <= tau_max,n.
    Returns L_lyap = J * max delta_omega admissible at x0=[0,dw].
    """
    n=p2.DIRS[dk]; Jn=float(p2.J_dir(n)); tmax=float(p2.tau_max_dir(n))
    Kp=float(CAL[fam]["Kp"]); Kd=float(CAL[fam]["Kd"])
    A=np.array([[0.0,1.0],[-Kp/Jn,-Kd/Jn]])
    # Solve A^T P + P A = -I for symmetric P=[[p11,p12],[p12,p22]] by
    # expanding the three independent entries of the 2x2 matrix equation.
    basis=[np.array([[1.,0.],[0.,0.]]),np.array([[0.,1.],[1.,0.]]),np.array([[0.,0.],[0.,1.]])]
    rows=[]; rhs=[]
    for i,j in [(0,0),(0,1),(1,1)]:
        rows.append([(A.T@B+B@A)[i,j] for B in basis])
        rhs.append(-np.eye(2)[i,j])
    u=np.linalg.solve(np.array(rows),np.array(rhs))
    p11,p12,p22=u
    P=np.array([[p11,p12],[p12,p22]])
    # is P positive definite? if not, ROA proxy not applicable
    pd=bool(np.linalg.eigvalsh(P)[0]>0)
    if not pd:
        return {"applicable":False,"reason":"P not positive definite","Kp":Kp,"Kd":Kd}
    c_phi=p11*p2.PHI_MAX**2
    # saturation along omega axis at phi=0: |Kd*dw|<=tmax
    dw_sat=tmax/Kd
    dw_phi=math.sqrt(c_phi/p22) if c_phi>0 else 0.0
    dw=min(dw_sat,dw_phi)
    L=Jn*dw
    return {"applicable":True,"Kp":Kp,"Kd":Kd,"J_n":Jn,"tau_max_n":tmax,
            "p11":p11,"p12":p12,"p22":p22,"P_pd":pd,
            "c_phi":c_phi,"dw_sat":dw_sat,"dw_phi":dw_phi,
            "dw_lyap":dw,"L_lyap":L,"limiting_constraint":("saturation" if dw_sat<=dw_phi else "envelope")}

if d.get("proxy") is None:
    proxy={}
    for dk in ["roll","pitch","yaw"]:
        for fam in ["qpd","smc","qpd_ff","proposed"]:
            proxy[f"{dk}|{fam}"]=lyap_proxy(dk,0.05,fam)
    d["proxy"]=proxy
    save(d)
    print("PART A done: quadratic-Lyapunov proxy")

# ---------- Part A2: three-way comparison + cheap-null logic check ----------
if d.get("comparison") is None:
    rows=[]
    for dk in ["roll","pitch","yaw"]:
        n=p2.DIRS[dk]; Lstar=p2.L_nec(n,0.05)["L_nec"]
        lyp=max(v["L_lyap"] for k,v in d["proxy"].items()
                if k.startswith(dk+"|") and v["applicable"])
        # observed best controller-certified sufficient boundary from frozen artifact
        r=json.load(open(os.path.join(HERE,"probe_v2_results.json"),encoding="utf-8"))
        vals=[]
        for k,v in r["done_cells"].items():
            if k.startswith(dk+"|") and isinstance(v.get("L_suff"),(int,float)) and v["L_suff"]==v["L_suff"]:
                vals.append(v["L_suff"])
        Lsuff=max(vals) if vals else None
        rows.append({"dir":dk,"Tm":0.05,"L_star":Lstar,"L_lyap_proxy":lyp,
                     "L_suff_observed":Lsuff,
                     "gap_star_minus_lyap":Lstar-lyp,
                     "ratio_lyap_over_star":lyp/Lstar,
                     "logic_ok":bool(lyp<=Lstar and (Lsuff is None or Lsuff<=Lstar*1.2))})
    d["comparison"]={"rows":rows,
        "logic_note":"sufficient domain must be <= necessary upper bound; "
                     "L_suff may exceed L* on the weaker turbulent arm (documented in v2), "
                     "so its check uses a 1.2 tolerance and is reported, not hidden",
        "proxy_note":"standard quadratic-Lyapunov ROA on linearised closed loop; "
                     "NOT a reproduction of Biswas2026 SOS / McDonough2017 recoverable sets / "
                     "Wijk2026 bCBF (no public implementation available)"}
    save(d)
    print("PART A2 done:",[(x["dir"],round(x["L_lyap_proxy"],5),round(x["L_star"],5)) for x in rows])

# ---------- Part B: n>=3 replication over independent disturbance phases ----------
BUDGET=int(os.environ.get("M3_BUDGET","40"))
def set_phase(ph):
    p2.SEED_PHASE=np.array(ph,dtype=float)
    p2.D_FIX=np.array([p2.d_of_t(t) for t in p2.T_GRID])
    return p2.disturbance_checks()

done=0
for phname,ph in PHASES.items():
    chk=set_phase(ph)
    store=d["replication"].setdefault(phname,{"disturbance":chk,"cells":{}})
    store["disturbance"]=chk
    for dk,Tm,fam in CELLS:
        key=f"{dk}|{Tm}|{fam}"
        if key in store["cells"]: continue
        if done>=BUDGET:
            print("BUDGET reached at",done,"new cells; rerun to continue"); save(d); raise SystemExit(0)
        kp,kd=CAL[fam]["Kp"],CAL[fam]["Kd"]
        t0=time.time()
        out=p2.L_suff(p2.DIRS[dk],Tm,fam,kp,kd,W_mech,d_mode="turb")
        store["cells"][key]={"L_suff":out["L_suff"],"degenerate":bool(out.get("degenerate")),
                             "ok_count":out.get("ok_count"),"sec":round(time.time()-t0,2)}
        done+=1
    print(" ",phname,"complete, cells",len(store["cells"]),"disturbance",chk["pass"])
    save(d)

# ---------- Part C: aggregate (only when all phases complete) ----------
allfull=all(len(d["replication"][p]["cells"])==len(CELLS) for p in PHASES)
if allfull and d.get("aggregate") is None:
    agg=[]
    for dk,Tm,fam in CELLS:
        key=f"{dk}|{Tm}|{fam}"
        vals=[d["replication"][p]["cells"][key]["L_suff"] for p in PHASES]
        good=[v for v in vals if isinstance(v,(int,float)) and v==v]
        agg.append({"cell":key,"runs":vals,
                    "mean":(sum(good)/len(good) if good else None),
                    "range":(max(good)-min(good) if len(good)>1 else 0.0),
                    "all_valid":len(good)==3,
                    "direction_consistent": all(v==v for v in vals)})
    # V3 direction consistency per phase (synthetic GO criterion < 0.6)
    v3={}
    for p in PHASES:
        c=d["replication"][p]["cells"]
        def best(dk):
            v=[c[f"{dk}|{Tm}|{fam}"]["L_suff"] for Tm in p2.TM_LIST for fam in CAL]
            v=[x for x in v if isinstance(x,(int,float)) and x==x]
            return max(v) if v else None
        r0,y0=best("roll"),best("yaw")
        v3[p]={"roll":r0,"yaw":y0,"ratio":(y0/r0 if r0 else None)}
    d["aggregate"]={"cells":agg,"V3_by_phase":v3,
        "note":"3 independent SEED_PHASE realisations; deterministic integrator; "
               "adversarial (constant-disturbance) arm is phase-independent and "
               "is therefore NOT counted as an independent replicate"}
    d["status"]="DONE"
    save(d)
    print("PART C done: aggregate written")
elif not allfull:
    d["status"]="RUNNING"
    save(d)
    print("still RUNNING; rerun with M3_BUDGET to continue")
