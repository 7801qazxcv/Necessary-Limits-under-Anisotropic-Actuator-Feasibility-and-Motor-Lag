# -*- coding: utf-8 -*-
"""M1 CORRECTION (2026-11-19): the preregistered attitude-envelope extension
was WRONG. When A1 fails, qdot has off-axis components and the geodesic
attitude angle phi is NOT int(omega_n dt); the phi_min construction used by
Theorem 1 no longer applies.

Honest downgrade: Lemma 2 gives an ANGULAR-MOMENTUM / angular-velocity level
necessary condition only (pointwise bound on p = J_n omega_n), not an attitude
envelope bound. We recompute exactly that, record the downgrade explicitly,
and do NOT claim an A1-free L*.

Reads the already-measured Omega_perp from m1_lemma.json (81 rollouts done),
so no rollout is repeated.
"""
import os, json, math
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(HERE,"m1_lemma.json"),encoding="utf-8"))
Omega=float(d["observed_omega_perp_max"])
gamma=d["gamma"]
dbar=0.032
T_HOR=1.5

import probe_v2 as p2
rows={}
for nm in ["roll","pitch","yaw"]:
    n=p2.DIRS[nm]; tmax=float(p2.tau_max_dir(n)); Jn=float(p2.J_dir(n))
    g=float(gamma[nm])
    d_eff=dbar+g*Omega**2/2.0
    exists=bool(tmax>d_eff)
    # A_eff(t) = [tmax*(t - Tm(1-e^{-t/Tm})) - d_eff*t]/Jn
    Tm=0.05
    def A_eff(t):
        return (tmax*(t-Tm*(1.0-math.exp(-t/Tm)))-d_eff*t)/Jn
    ts=np.linspace(0,T_HOR,3001)
    Amax=float(max(A_eff(t) for t in ts))
    # Angular-momentum-level necessary condition: if Delta_omega > max A_eff,
    # omega_n(t) >= Delta_omega - A_eff(t) > 0 for all t in [0,T_HOR],
    # i.e. the n-axis angular velocity never reverses -> recovery cannot be
    # certified at the momentum level. This is WEAKER than Theorem 1's L*.
    rows[nm]={"tau_max_n":tmax,"J_n":Jn,"gamma":g,"dbar":dbar,
              "d_eff":d_eff,"existence":exists,
              "omega_lower_bound_max_Aeff":Amax,
              "L_momentum_threshold":Jn*Amax,
              "claim_level":"angular-momentum necessary condition (NOT attitude envelope)",
              "attitude_extension_valid":False}
d["a1free_bounds_ORIGINAL_preregistered_WRONG"]=d.get("a1free_bounds")
d["a1free_bounds"]=rows
d["downgrade_note"]=(
 "PREREG ERROR FOUND AND CORRECTED: with A1 relaxed, quaternion kinematics make "
 "phi != int(omega_n dt), so the phi_min/L* construction of Theorem 1 does not "
 "extend. Lemma 2 is downgraded to an angular-momentum-level necessary condition "
 "(pointwise omega_n lower bound). The original 'L_free <= L*' numbers are kept "
 "under a1free_bounds_ORIGINAL_preregistered_WRONG for audit and MUST NOT be "
 "quoted as a theorem. No A1-free attitude-envelope bound is claimed.")
d["status"]="DONE_CORRECTED"
tmp=os.path.join(HERE,"m1_lemma.json.tmp")
with open(tmp,"w",encoding="utf-8") as f:
    json.dump(d,f,ensure_ascii=False,indent=1,
              default=lambda o:o.item() if hasattr(o,"item") else str(o))
os.replace(tmp,os.path.join(HERE,"m1_lemma.json"))
print("CORRECTED. Omega",Omega)
for k,v in rows.items():
    print(" ",k,{x:(round(y,6) if isinstance(y,float) else y) for x,y in v.items()})
