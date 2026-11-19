# -*- coding: utf-8 -*-
"""Generate the 4 manuscript figures FROM ON-DISK ARTIFACTS ONLY.
House style: single-column 3.5 in canvas, >=8 pt fonts, no in-figure title,
legend outside panel, bottom+left spines only, tight limits, dashed grid.
Writes paper/figures/fig1.pdf..fig4.pdf (+ .png)."""
import json, os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__))
FIG=os.path.join(HERE,"paper","figures")
os.makedirs(FIG,exist_ok=True)
def L(f): return json.load(open(os.path.join(HERE,f),encoding="utf-8"))
syn=L("probe_v2_results.json"); real=L("probe_v2_REAL_results.json")
ps=L("param_sensitivity.json"); asym=L("asym_diagnostic.json")

plt.rcParams.update({"font.size":9,"axes.labelsize":9,"xtick.labelsize":8,"ytick.labelsize":8,
                     "legend.fontsize":8,"axes.linewidth":0.8,"lines.linewidth":1.6})
def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(True,which="both",ls="--",alpha=0.3); ax.tick_params(direction="in")
def save(fig,n):
    for ext in ("pdf","png"):
        fig.savefig(os.path.join(FIG,"fig%d.%s"%(n,ext)),dpi=300,bbox_inches="tight")
    plt.close(fig)

# ---- Fig.1: three-way domain schematic, FULLY NORMALISED (no data values) ----
# A schematic must not mix a real L* value on its axis with a
# hand-drawn curve. All axes are dimensionless; no artifact number is plotted.
fig,ax=plt.subplots(figsize=(3.5,2.4))
t=np.linspace(0,1.0,200)
cert=1.0*np.ones_like(t)                        # normalised certified bound
obs=0.9*(1-np.exp(-t/0.35))+0.02                 # purely illustrative shape
ax.plot(t,cert,"k-",label="Certified necessary bound (normalised)")
ax.plot(t,obs,"C0--",label="Observed sufficient boundary (illustrative)")
ax.fill_between(t,obs,cert,color="C2",alpha=0.18,label="Unverified region")
ax.set_xlabel("normalised recovery horizon $t/T$")
ax.set_ylabel("normalised impulse $L/L^*$ (conceptual)")
ax.set_xlim(0,1.0); ax.set_ylim(0,1.25); ax.set_yticks([0,0.5,1.0]); style(ax)
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.22),frameon=False,ncol=1,handlelength=2.2)
save(fig,1)

# ---- Fig.2: necessary bound vs mu, dual platform, from analytic dicts ----
fig,ax=plt.subplots(figsize=(3.5,2.6))
for tag,res,ms,fmt in [("Synthetic (literature-anchored)",syn,"o","-"),
                       ("Identified Crazyflie",real,"s","--")]:
    Tm=sorted({float(k) for dk in res["analytic"].values() for k in dk.keys()})
    xs=[];ys=[]
    for tm in Tm:
        vals=[res["analytic"][dk][str(tm)]["L_nec"] for dk in res["analytic"]
              if str(tm) in res["analytic"][dk] and res["analytic"][dk][str(tm)]["L_nec"]==res["analytic"][dk][str(tm)]["L_nec"]]
        if vals: xs.append(tm);ys.append(float(np.mean(vals)))
    ax.plot(xs,ys,fmt,marker=ms,label=tag)
ax.set_xlabel("motor time constant $T_m$ (s)"); ax.set_ylabel("$L^*$ (N m s, mean over axes)")
ax.set_xlim(0,max(max(ax.get_xlim()),0.26)); style(ax)
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.20),frameon=False,handlelength=2.2)
save(fig,2)

# ---- Fig.3: anisotropy ratio V3, synthetic GO vs real NO-GO ----
fig,ax=plt.subplots(figsize=(3.5,2.4))
labels=["Synthetic","Identified\nCrazyflie"]
v3=[syn["go_evaluation"]["V3_anisotropy"]["yaw_over_roll_Lsuff"],
    real["go_evaluation"]["V3_anisotropy"]["yaw_over_roll_Lsuff"]]
tau=[syn["go_evaluation"]["V3_anisotropy"]["tau_max_yaw_over_roll"],
     real["go_evaluation"]["V3_anisotropy"]["tau_max_yaw_over_roll"]]
x=np.arange(2);w=0.34
ax.bar(x-w/2,v3,w,label="$L_{\\rm suff,yaw}/L_{\\rm suff,roll}$",color="C0")
ax.bar(x+w/2,tau,w,label="$\\tau_{\\max,yaw}/\\tau_{\\max,roll}$",color="C3")
ax.axhline(0.6,color="k",ls=":",lw=1,label="conditional discriminator 0.6")
ax.set_xticks(x);ax.set_xticklabels(labels);ax.set_ylim(0,0.8)
ax.set_ylabel("dimensionless ratio");style(ax)
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.24),frameon=False,ncol=1,handlelength=2.0)
save(fig,3)

# ---- Fig.4: failure boundary, first_fail_dw from asym diagnostic ----
fig,ax=plt.subplots(figsize=(3.5,2.5))
models=[("sym-fast","fast","fast"),("sym-slow","slow","slow"),("asym","asym","slow")]
for i,(lab,m,g) in enumerate(models):
    vals=[]
    for dk in ["roll","pitch","yaw","combo"]:
        for fam in ["qpd","qpd_ff","proposed"]:
            v=asym["boundary"].get(f"{m}|{g}|{dk}|{fam}")
            if v and v.get("first_fail_dw") is not None: vals.append(v["first_fail_dw"])
    ax.scatter([i]*len(vals),vals,s=18,label=lab,alpha=0.8)
ax.set_xticks(range(3));ax.set_xticklabels(["sym-fast","sym-slow","asym"])
ax.set_ylabel("first failing $\\Delta\\omega$ (rad/s)")
ax.set_ylim(0,25);style(ax)
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.20),frameon=False,ncol=3,handlelength=1.4)
save(fig,4)
print("WROTE 4 figures in",FIG)
for n in range(1,5): print("  fig%d.pdf"%n,os.path.getsize(os.path.join(FIG,"fig%d.pdf"%n)),"bytes")
