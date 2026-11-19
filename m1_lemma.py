# -*- coding: utf-8 -*-
"""M1: derive & measure the gyroscopic-term bound for relaxing A1.
Independent script: imports frozen probe_v2 (default behaviour untouched),
measures ||omega_perp|| on real 6-DoF roll trajectories, computes the
A1-free conservative necessary bound. All numbers land in m1_lemma.json.
"""
import os, json, math, sys
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import probe_v2 as p2

OUT=os.path.join(HERE,"m1_lemma.json")
res={"status":"RUNNING","prereg":"preregistration_m1_m3.md"}

# ---- 1. Symbolic/algebraic identity check (numeric verification of the form) ----
J=np.array(p2.J,dtype=float).reshape(-1)[:3]   # elementwise diag J in probe_v2
gamma={}
# [w x Jw]_i = (J_l - J_k) w_k w_l with (i,k,l) the CYCLIC permutation
# (0,1,2),(1,2,0),(2,0,1); gamma_i = |J_k - J_l| is the AM-GM coefficient.
cyc={0:(1,2),1:(2,0),2:(0,1)}
for i,nm in enumerate(["roll","pitch","yaw"]):
    k,l=cyc[i]
    gamma[nm]=abs(J[k]-J[l])
rng=np.random.default_rng(20261119)
maxerr=0.0; maxbound_violation=0.0
for i,nm in enumerate(["roll","pitch","yaw"]):
    n=np.eye(3)[i]; k,l=cyc[i]
    for _ in range(200):
        w=rng.normal(size=3)
        lhs=float(n@np.cross(w,J*w)); rhs=(J[l]-J[k])*w[k]*w[l]
        maxerr=max(maxerr,abs(lhs-rhs))
        # the bound the lemma actually uses: |lhs| <= gamma*||w_perp||^2/2
        bound=gamma[nm]*(w[k]**2+w[l]**2)/2.0
        maxbound_violation=max(maxbound_violation,abs(lhs)-bound)
res["identity_max_abs_error"]=maxerr
res["bound_max_violation"]=maxbound_violation   # <=0 means inequality holds
res["gamma"]=gamma
res["J_diag"]=[float(x) for x in J]
print("identity max err",maxerr,"bound violation",maxbound_violation,"gamma",gamma)

# ---- 2. Measure ||omega_perp|| on real 6-DoF roll trajectories ----
# use the frozen calibrated gains from the v2.3 result artifact
r=json.load(open(os.path.join(HERE,"probe_v2_results.json"),encoding="utf-8"))
cal=r.get("calibration",{})
def pick(fam):
    for key,v in cal.items():
        if fam in key and isinstance(v,dict) and "Kp" in v: return v["Kp"],v["Kd"]
    return 6.0,2.0
kp,kd=pick("proposed")
W_mech=r["meta"].get("W_mech",[1,1,0.1286])
print("cal gains",kp,kd,"W_mech",W_mech)

# Instrument simulate: replicate RK4 but record omega_perp each step.
# Default probe_v2.D_FIX / d_at used verbatim (no change to frozen artifacts).
def rollout_with_perp(dw,Tm,fam,Kp,Kd,W):
    n=p2.DIRS["roll"]; dt=p2.DT
    X=np.zeros((1,14)); X[0,0]=1.0; X[0,4:7]=np.array([dw,0,0]); X[0,7:11]=p2.u_hov
    h=dt; nsteps=int(round(p2.T_HOR/h)); maxperp=0.0; maxgyro=0.0; maxphi=0.0
    for k in range(nsteps):
        t=k*h
        k1=p2.rhs(X,t,fam,Kp,Kd,W,Tm,"turb",n)
        k2=p2.rhs(X+0.5*h*k1,t+0.5*h,fam,Kp,Kd,W,Tm,"turb",n)
        k3=p2.rhs(X+0.5*h*k2,t+0.5*h,fam,Kp,Kd,W,Tm,"turb",n)
        k4=p2.rhs(X+h*k3,t+h,fam,Kp,Kd,W,Tm,"turb",n)
        X=X+(h/6.0)*(k1+2*k2+2*k3+k4)
        X[:,0:4]/=np.maximum(np.linalg.norm(X[:,0:4],axis=1,keepdims=True),1e-12)
        w=X[0,4:7]; perp=float(np.hypot(w[1],w[2]))
        g=abs(float(np.array([1.,0,0])@np.cross(w,J*w)))
        maxperp=max(maxperp,perp); maxgyro=max(maxgyro,g)
        phi=2*math.acos(min(1.0,abs(X[0,0]))); maxphi=max(maxphi,phi)
    return maxperp,maxgyro,maxphi

DW=[0.5,1.0,2.0,3.0,4.0,5.0,6.0,8.0,10.0]
obs=[]
for Tm in p2.TM_LIST:
    for fam in ["qpd","qpd_ff","proposed"]:
        for dw in DW:
            mp,mg,mphi=rollout_with_perp(dw,Tm,fam,kp if fam=="proposed" else 6.0,
                                         kd if fam=="proposed" else 2.0,W_mech)
            obs.append({"Tm":Tm,"family":fam,"dw":dw,"max_omega_perp":mp,
                        "max_gyro_n":mg,"max_phi":mphi})
        print("  Tm",Tm,fam,"done")
Omega=max(o["max_omega_perp"] for o in obs)
Gyr=max(o["max_gyro_n"] for o in obs)
res["observed_omega_perp_max"]=Omega
res["observed_gyro_n_max"]=Gyr
res["n_rollouts"]=len(obs)
print("Omega_perp max",Omega,"measured gyro_n max",Gyr)

# ---- 3. A1-free conservative bound ----
# |n^T(w x Jw)| <= gamma * ||w_perp||^2 / 2  (AM-GM on |w_k w_l|)
dbar=float(p2.D_BAR)
bound_rows={}
for nm in ["roll","pitch","yaw"]:
    n=p2.DIRS[nm]; tmax=float(p2.tau_max_dir(n)); Jn=float(p2.J_dir(n))
    g=gamma[nm]
    d_eff=dbar+g*Omega**2/2.0
    # A(t) with dbar -> d_eff ; existence condition
    exists=tmax>d_eff
    L_free=None; L_adv=None
    if exists:
        # same construction as L_nec but with effective disturbance
        def A_eff(t,Tm):
            return (tmax*(t-Tm*(1.0-math.exp(-t/Tm)))-d_eff*t)/Jn
        def phi_min(dw,Tm):
            lo,hi=0.0,20.0
            for _ in range(160):
                mid=.5*(lo+hi)
                if A_eff(mid,Tm)<dw: lo=mid
                else: hi=mid
            ts=.5*(lo+hi)
            intA=(tmax*(ts*ts/2-Tm*ts+Tm*Tm*(1-math.exp(-ts/Tm)))-d_eff*ts*ts/2)/Jn
            return dw*ts-intA
        lo,hi=0.0,30.0
        for _ in range(160):
            mid=.5*(lo+hi)
            if phi_min(mid,0.05)<p2.PHI_MAX: lo=mid
            else: hi=mid
        L_free=Jn*.5*(lo+hi)
        L_adv=p2.L_nec(n,0.05)["L_nec"]
    bound_rows[nm]={"tau_max_n":tmax,"J_n":Jn,"gamma":g,"dbar":dbar,
                    "d_eff":d_eff,"existence":exists,
                    "L_free":L_free,"L_adversarial":L_adv,
                    "ratio_free_over_adv":(L_free/L_adv if (L_free and L_adv) else None)}
res["a1free_bounds"]=bound_rows
res["status"]="DONE"
# atomic write + numpy scalar coercion (np.bool_ / np.float64 are not JSON-native)
def _coerce(o):
    return o.item() if hasattr(o,"item") else str(o)
tmp=OUT+".tmp"
with open(tmp,"w",encoding="utf-8") as fh:
    json.dump(res,fh,ensure_ascii=False,indent=1,default=_coerce)
os.replace(tmp,OUT)
print("WROTE",OUT)
for k,v in bound_rows.items(): print(" ",k,v)
