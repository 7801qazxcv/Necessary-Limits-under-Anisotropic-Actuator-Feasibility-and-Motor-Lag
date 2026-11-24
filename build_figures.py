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
                     "legend.fontsize":8,"axes.linewidth":0.8,"lines.linewidth":1.6,
                     "pdf.fonttype":42,"ps.fonttype":42})
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

# ---- Fig.2: necessary bound vs Tm, TWO PANELS (platform L* differs ~1000x) ----
dirs2=["roll","pitch","yaw","combo"]
fig,axes=plt.subplots(2,1,figsize=(3.5,3.8))
for ax,(tag,res) in zip(axes,[("(a) Synthetic (literature-anchored)",syn),
                              ("(b) Identified Crazyflie",real)]):
    for di,dk in enumerate(dirs2):
        if dk not in res["analytic"]: continue
        tms=sorted(res["analytic"][dk].keys(),key=float)
        xs=[float(k) for k in tms]
        ys=[res["analytic"][dk][k]["L_nec"] for k in tms]
        ax.plot(xs,ys,"-o",ms=4,label=dk,color="C%d"%di)
    ax.set_title(tag,fontsize=8,pad=2)
    ax.set_ylabel("$L^*$ (N m s)")
    style(ax)
axes[-1].set_xlabel("motor time constant $T_m$ (s)")
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,loc="lower center",bbox_to_anchor=(0.5,0.005),
           ncol=4,frameon=False,fontsize=7,handlelength=1.4)
fig.tight_layout(rect=[0,0.10,1,1])
save(fig,2)


# ---- Fig.3: anisotropy ratio V3, synthetic GO vs real NO-GO ----
fig,ax=plt.subplots(figsize=(3.5,2.4))
labels=["Synthetic","Identified\nCrazyflie"]
v3=[syn["go_evaluation"]["V3_anisotropy"]["yaw_over_roll_Lsuff"],
    real["go_evaluation"]["V3_anisotropy"]["yaw_over_roll_Lsuff"]]
tau=[syn["go_evaluation"]["V3_anisotropy"]["tau_max_yaw_over_roll"],
     real["go_evaluation"]["V3_anisotropy"]["tau_max_yaw_over_roll"]]
x=np.arange(2);w=0.34
b1=ax.bar(x-w/2,v3,w,label="$L_{\\rm suff,yaw}/L_{\\rm suff,roll}$",color="C0")
b2=ax.bar(x+w/2,tau,w,label="$\\tau_{\\rm max,yaw}/\\tau_{\\rm max,roll}$",color="C3")
for bars in (b1,b2):
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.012,
                "%.3f"%bar.get_height(),ha="center",va="bottom",fontsize=7)
ax.axhline(0.6,color="k",ls=":",lw=1,label="conditional discriminator 0.6")
ax.set_xticks(x);ax.set_xticklabels(labels);ax.set_ylim(0,0.8)
ax.set_ylabel("dimensionless ratio");style(ax)
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.24),frameon=False,ncol=1,handlelength=2.0)
save(fig,3)


# ---- Fig.4: grouped scatter, direction-shaped, n-labelled, dual range ----
dirs4=["roll","pitch","yaw","combo"]
fams4=["qpd","smc","qpd_ff","proposed"]
markers4=["o","s","^","D"]
groups4=[("sym-fast","fast","fast"),("sym-slow","slow","slow"),("asym","asym","slow")]
data4={}
for gi,(lab,m,g) in enumerate(groups4):
    data4[gi]={}
    for dk in dirs4:
        vals=[]
        for fam in fams4:
            v=asym["boundary"].get("%s|%s|%s|%s"%(m,g,dk,fam))
            if v and v.get("first_fail_dw") is not None:
                vals.append(v["first_fail_dw"])
        data4[gi][dk]=vals
fig,axes=plt.subplots(2,1,figsize=(3.5,3.9))
for ax,(ylim,ptitle) in zip(axes,[((0,25),"(a) full range, all three models"),
                                  ((0,0.9),"(b) low-value detail, slow models")]):
    for gi,(lab,m,g) in enumerate(groups4):
        if ylim[1]<1 and gi==0:   # sym-fast has no point in the detail range
            continue
        for di,dk in enumerate(dirs4):
            vals=data4[gi][dk]
            j=(np.arange(len(vals))-(len(vals)-1)/2.0)*0.022
            ax.scatter(np.full(len(vals),gi)+j,vals,s=15,marker=markers4[di],
                       color="C%d"%di,alpha=0.8,label=dk if gi==0 else None)
        allv=[v for dk in dirs4 for v in data4[gi][dk]]
        n=len(allv)
        ax.text(gi,ylim[1]*0.93,"n=%d"%n,ha="center",fontsize=7,
                bbox=dict(facecolor="white",alpha=0.75,edgecolor="none",pad=0.6))
        # median only where the group has non-zero spread (slow|slow is all grid floor)
        if n>=2 and (max(allv)-min(allv))>1e-9:
            ax.hlines(float(np.median(allv)),gi-0.30,gi+0.30,
                      color="k",lw=1.0,alpha=0.7)
    ax.set_ylim(*ylim);ax.set_ylabel("first failing $\\Delta\\omega$ (rad/s)")
    ax.set_title(ptitle,fontsize=8,pad=2);style(ax)
axes[1].set_xticks(range(3));axes[1].set_xticklabels([g[0] for g in groups4])
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,loc="lower center",bbox_to_anchor=(0.5,0.005),
           ncol=4,frameon=False,fontsize=7,handlelength=1.2)
fig.tight_layout(rect=[0,0.10,1,1])
save(fig,4)

print("WROTE 4 figures in",FIG)
for n in range(1,5): print("  fig%d.pdf"%n,os.path.getsize(os.path.join(FIG,"fig%d.pdf"%n)),"bytes")
