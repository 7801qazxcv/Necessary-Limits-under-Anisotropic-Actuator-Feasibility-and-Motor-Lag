# -*- coding: utf-8 -*-
"""INDEPENDENT math red-team re-derivation (ChatGPT review problems 1,2,5).

Deliberately does NOT import probe_v2.py. Rebuilds A(t), g(t), t*, phi_min,
Delta_omega*, L* from the raw formulas with stdlib math only, reading ONLY the
physical parameters (tau_max_n, J_n, dbar, Tm, Phi_max, T) from the frozen
artifacts. Purpose: check whether t* <= T (finite recovery horizon) for every
reported case, and whether the critical root is unique.
"""
import math, json, os
HERE=os.path.dirname(os.path.abspath(__file__))

def psi(t,Tm): return t-Tm*(1.0-math.exp(-t/Tm))
def int_psi(t,Tm): return t*t/2.0-Tm*t+Tm*Tm*(1.0-math.exp(-t/Tm))
def A(t,tmx,Jn,dbar,Tm): return (tmx*psi(t,Tm)-dbar*t)/Jn
def intA(t,tmx,Jn,dbar,Tm): return (tmx*int_psi(t,Tm)-dbar*t*t/2.0)/Jn
def g(t,dw,tmx,Jn,dbar,Tm): return dw*t-intA(t,tmx,Jn,dbar,Tm)

def t_star(dw,tmx,Jn,dbar,Tm,tmax=50.0):
    """unique positive root of A(t)=dw, if it exists"""
    if tmx<=dbar: return None
    lo,hi=0.0,tmax
    if A(hi,tmx,Jn,dbar,Tm)<dw: return None   # never reaches
    for _ in range(200):
        mid=.5*(lo+hi)
        if A(mid,tmx,Jn,dbar,Tm)<dw: lo=mid
        else: hi=mid
    return .5*(lo+hi)

def phi_min(dw,tmx,Jn,dbar,Tm,T=None):
    """max_{t in [0,T]} g(t;dw). If T is None -> g(t*)."""
    ts=t_star(dw,tmx,Jn,dbar,Tm)
    if ts is None: return float("inf"),None
    tt=ts if T is None else min(ts,T)
    return g(tt,dw,tmx,Jn,dbar,Tm),ts

def solve_Lstar(tmx,Jn,dbar,Tm,Phi,T=None):
    """smallest dw with max_[0,T] g >= Phi  -> L*=Jn*dw"""
    lo,hi=0.0,60.0
    for _ in range(200):
        mid=.5*(lo+hi)
        v,_=phi_min(mid,tmx,Jn,dbar,Tm,T)
        if v<Phi: lo=mid
        else: hi=mid
    dw=.5*(lo+hi)
    v,ts=phi_min(dw,tmx,Jn,dbar,Tm,T)
    return dw,Jn*dw,v,ts

out={"status":"RUNNING","T":1.5,"Phi_max_deg":60.0,"rows":[]}
for fn,tag in [("probe_v2_results.json","synthetic"),
               ("probe_v2_REAL_results.json","identified")]:
    r=json.load(open(os.path.join(HERE,fn),encoding="utf-8"))
    p=r["meta"]["params"]
    Phi=float(p["Phi_max"]); T=float(p["T_hor"]); dbar=float(p["D_bar"])
    Tms=[float(x) for x in p["T_m_list"]]
    for dk in ["roll","pitch","yaw","combo"]:
        for Tm in Tms:
            a=r["analytic"][dk][str(Tm) if str(Tm) in r["analytic"][dk] else format(Tm,"g")]
            if a is None: continue
            tmx=float(a["tau_max_n"]); Jn=float(a["J_n"])
            L_paper=float(a["L_nec"]) if a["L_nec"]==a["L_nec"] else None
            # INDEPENDENT re-derivation, no finite horizon (what the paper does)
            dw,L,v,ts=solve_Lstar(tmx,Jn,dbar,Tm,Phi,None)
            # WITH finite horizon T
            dwT,LT,vT,tsT=solve_Lstar(tmx,Jn,dbar,Tm,Phi,T)
            # monotonicity / uniqueness of critical root: sample phi_min over dw grid
            samples=[]
            for k in range(0,61):
                w=k*0.5
                vv,_=phi_min(w,tmx,Jn,dbar,Tm,None)
                if math.isfinite(vv): samples.append((w,vv))
            mono=all(samples[i][1]<=samples[i+1][1]+1e-9 for i in range(len(samples)-1))
            row={"platform":tag,"dir":dk,"Tm":Tm,"tau_max_n":tmx,"J_n":Jn,
                 "dbar":dbar,"L_paper":L_paper,
                 "L_independent":L,"L_abs_diff":abs(L-L_paper) if L_paper else None,
                 "t_star":ts,"t_star_le_T":bool(ts<=T) if ts else None,
                 "T":T,"L_finiteT":LT,"L_finiteT_minus_L":LT-L,
                 "phi_min_monotone":mono,
                 "n_dw_grid":len(samples)}
            out["rows"].append(row)
            print("  %-11s %-6s Tm=%-9s t*=%-9s <=T=%-5s L_paper=%-12s L_indep=%-12s diff=%-9s L_T=%-12s dL_T=%s"%(
                tag,dk,Tm,round(ts,4) if ts else None,row["t_star_le_T"],
                round(L_paper,6) if L_paper else None,round(L,6),
                round(abs(L-L_paper),8) if L_paper else None,round(LT,6),round(LT-L,6)))
out["status"]="DONE"
json.dump(out,open(os.path.join(HERE,"math_redteam.json"),"w",encoding="utf-8"),
          ensure_ascii=False,indent=1)
print("WROTE math_redteam.json")
