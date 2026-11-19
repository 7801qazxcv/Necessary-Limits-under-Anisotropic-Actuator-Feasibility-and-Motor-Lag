# -*- coding: utf-8 -*-
"""
DIAGNOSTIC for Probe v1 (NOT a new GO criterion, does not touch frozen prereg).
Purpose: principle-17/17b — a gap==0 "perfect null" must have its MECHANISM
measured, never asserted. Checks:
  D1 L_nec re-derived here == JSON (no drift).
  D2 recovery is monotone in dw, no isolated-True islands.
  D3 the binding constraint is max|phi| (terminal |omega| never binds near boundary).
  D4 tanh(eps=0.05) vs ideal max-effort phi-peak near boundary: measure the real
     (small, non-zero) difference that explains gap~=0.
  D5 a NON-IDEAL controller (weak, unsaturated: eps_big=2.0) must recover a
     STRICTLY SMALLER domain than L_nec -> gap opens. This MEASURES the mechanism
     of the null without forging a gap inside v1.
All numbers from execution; parameters identical to v1 (research assumptions).
"""
import json, math, os
OUT = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(OUT, "probe_v1_results.json"), encoding="utf-8"))
P = R["params"]
J, TAU_MAX, PHI_MAX = P["J"], P["tau_max"], P["Phi_max_rad"]
D, EPS, W_TH, T_HOR, DT = P["d"], P["eps"], P["omega_th"], P["T_hor"], P["dt"]

def sat(u): return max(-TAU_MAX, min(TAU_MAX, u))
def cmd(w, eps): return -TAU_MAX*math.tanh(w/eps)

def sim(dw, Tm, eps=EPS, dt=DT, horizon=T_HOR):
    phi, w, tau = 0.0, float(dw), 0.0
    mx, w_at_peak = 0.0, 0.0
    n = int(round(horizon/dt))
    def f(phi_, w_, tau_):
        return (w_, (tau_+D)/J, (sat(cmd(w_, eps))-tau_)/Tm)
    for i in range(n):
        k1=f(phi,w,tau); k2=f(phi+.5*dt*k1[0],w+.5*dt*k1[1],tau+.5*dt*k1[2])
        k3=f(phi+.5*dt*k2[0],w+.5*dt*k2[1],tau+.5*dt*k2[2]); k4=f(phi+dt*k3[0],w+dt*k3[1],tau+dt*k3[2])
        phi+=dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); w+=dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1]); tau+=dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
        if abs(phi)>mx: mx,w_at_peak=abs(phi),w
    return mx, w, w_at_peak   # max|phi|, terminal omega, omega at phi-peak

def recover(dw, Tm, eps=EPS, dt=DT):
    mx, wf, _ = sim(dw, Tm, eps, dt)
    return (mx <= PHI_MAX) and (abs(wf) <= W_TH)

def A(t,Tm): return (TAU_MAX/J)*(t-Tm*(1-math.exp(-t/Tm)))
def tstar(dw,Tm):
    lo,hi=0.,10.
    for _ in range(120):
        m=.5*(lo+hi)
        if A(m,Tm)<dw: lo=m
        else: hi=m
    return .5*(lo+hi)
def g_peak(dw,Tm):
    ts=tstar(dw,Tm)
    intA=(TAU_MAX/J)*(ts*ts/2-Tm*ts+Tm*Tm*(1-math.exp(-ts/Tm)))
    return dw*ts-intA
def L_nec(Tm):
    lo,hi=0.,10.
    for _ in range(120):
        m=.5*(lo+hi)
        if g_peak(m,Tm)<PHI_MAX: lo=m
        else: hi=m
    return J*.5*(lo+hi)
def L_suff(Tm,eps=EPS,dt=DT):
    lo,hi=0.,10.
    for _ in range(40):
        m=.5*(lo+hi)
        if recover(m,Tm,eps,dt): lo=m
        else: hi=m
    return J*.5*(lo+hi)

diag={}
# D1 no drift
d1=[]
for r in R["rows"]:
    d1.append(abs(L_nec(r["T_m_s"])-r["L_nec_Nms"]))
diag["D1_nec_redrift_max_abs"] = {"value":max(d1),"pass":bool(max(d1)<1e-9)}

# D2 monotonicity of recover flag (no isolated True islands)
Tm=0.05
flags=[recover(dw,Tm) for dw in [x*0.25 for x in range(2,41)]]  # 0.5..10 step .25
first_false=flags.index(False) if False in flags else None
isolated = any(flags[i] for i in range(first_false,len(flags))) if first_false is not None else False
diag["D2_monotone_no_islands"]={"first_false_index":first_false,"isolated_true_after":isolated,
                                "pass":bool(not isolated and first_false is not None)}

# D3 binding constraint: near boundary, is terminal |omega| ever the binding one?
d3=[]
for dw in [3.8,4.0,4.1,4.2,4.3]:
    mx,wf,wpk=sim(dw,Tm)
    d3.append({"dw":dw,"max_phi":round(mx,4),"phi_violates":bool(mx>PHI_MAX),
               "w_final":round(abs(wf),4),"w_violates":bool(abs(wf)>W_TH),
               "w_at_phi_peak":round(wpk,4)})
diag["D3_binding_constraint"]={"rows":d3,
   "phi_peak_drives":all(x["phi_violates"] or not x["w_violates"] for x in d3),
   "pass":bool(all(x["phi_violates"] or not x["w_violates"] for x in d3))}

# D4 tanh vs ideal phi-peak near boundary -> real small difference explaining gap~0
d4=[]
for dw in [3.8,4.0,4.1,4.2]:
    mx_t,_,_=sim(dw,Tm,eps=0.05)
    mx_i,_,_=sim(dw,Tm,eps=1e-6)
    d4.append({"dw":dw,"phi_peak_tanh":round(mx_t,5),"phi_peak_ideal":round(mx_i,5),
               "diff":round(mx_t-mx_i,5)})
diag["D4_tanh_vs_ideal_phi_peak"]={"rows":d4,
   "max_abs_diff":max(abs(x["diff"]) for x in d4),
   "pass":bool(max(abs(x["diff"]) for x in d4)<0.02)}

# D5 NON-IDEAL controller opens a measurable gap (mechanism of the null)
eps_big=2.0
d5=[]
for Tm in P["T_m_list"]:
    nec=L_nec(Tm); suf_ideal=L_suff(Tm,eps=1e-6); suf_weak=L_suff(Tm,eps=eps_big)
    d5.append({"T_m":Tm,"L_nec":round(nec,5),"L_suff_ideal":round(suf_ideal,5),
               "L_suff_weak":round(suf_weak,5),"gap_weak":round(nec-suf_weak,5),
               "gap_weak_pct":round(100*(nec-suf_weak)/nec,1)})
diag["D5_nonideal_controller_opens_gap"]={"rows":d5,
   "all_gap_positive":all(x["gap_weak"]>0 for x in d5),
   "pass":bool(all(x["gap_weak"]>0 for x in d5))}

report={"probe":"v1-DIAGNOSTIC","note":"diagnostic only; frozen GO criteria untouched",
        "diagnostics":diag,
        "all_pass":all(v.get("pass",False) for v in diag.values())}
json.dump(report,open(os.path.join(OUT,"probe_v1_diagnostic.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)

print("ALL_PASS =",report["all_pass"])
for k,v in diag.items():
    print("  %-34s pass=%s" % (k,v.get("pass")))
    if k in ("D3_binding_constraint","D4_tanh_vs_ideal_phi_peak","D5_nonideal_controller_opens_gap"):
        for row in v["rows"]: print("      ",row)
print("D2 first_false_index =",diag["D2_monotone_no_islands"]["first_false_index"],
      "isolated=",diag["D2_monotone_no_islands"]["isolated_true_after"])
print("D1 max redrift =",diag["D1_nec_redrift_max_abs"]["value"])
