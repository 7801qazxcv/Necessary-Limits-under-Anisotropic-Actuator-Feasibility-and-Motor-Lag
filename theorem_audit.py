# -*- coding: utf-8 -*-
"""
theorem_audit.py — 投前定理审计（针对 theorem_draft.md / probe_v2_results.json）
按 empirical-paper-integrity 原则 13/13b、sci-paper-forge P10、硬伤 A–G 逐条查。
全部结论来自真实计算/真实闭环轨迹，不凭空断言。
"""
import json, math, os, re, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p2", os.path.join(HERE, "probe_v2.py"))
p2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p2)
R = json.load(open(os.path.join(HERE, "probe_v2_results.json"), encoding="utf-8"))
DRAFT = open(os.path.join(HERE, "theorem_draft.md"), encoding="utf-8").read()

J, F, u_max = p2.J, p2.F, p2.u_max
DBAR, PHI = p2.D_BAR, p2.PHI_MAX
M_T = p2.M_T
TM_LIST = p2.TM_LIST
DIRS = p2.DIRS
out = {"checks": {}, "notes": []}

def psi(t, Tm):  return t - Tm*(1.0-math.exp(-t/Tm))
def Psi(t, Tm):  return t*t/2 - Tm*t + Tm*Tm*(1.0-math.exp(-t/Tm))

def tmax(n): return p2.tau_max_dir(n)
def Jn(n):   return float(n @ (J*n))

# ---------- 解析 φ_min 的两套扰动口径 ----------
def A_of_t(t, Tm, tm, jn, sign):
    # 代码: A = [tm*psi + sign*DBAR*t]/jn
    # sign=-1 -> A=[tm*psi - dbar*t]/jn = v2 的 A_of_t = 对抗扰动 (n·d=+dbar)
    # sign=+1 -> A=[tm*psi + dbar*t]/jn = 覆盖「任意扰动」所需的更保守界
    return (tm*psi(t, Tm) + sign*DBAR*t)/jn
def phi_min(dw, Tm, tm, jn, sign):
    lo, hi = 0.0, 20.0
    for _ in range(200):
        m = 0.5*(lo+hi)
        if A_of_t(m, Tm, tm, jn, sign) < dw: lo = m
        else: hi = m
    ts = 0.5*(lo+hi)
    intA = (tm*Psi(ts, Tm) + sign*DBAR*ts*ts/2)/jn
    return dw*ts - intA, ts
def Lstar(Tm, tm, jn, sign):
    lo, hi = 0.0, 30.0
    for _ in range(200):
        m = 0.5*(lo+hi)
        pm, _ = phi_min(m, Tm, tm, jn, sign)
        if pm < PHI: lo = m
        else: hi = m
    dw = 0.5*(lo+hi)
    return jn*dw, dw

# ---------- C0: 草稿是否残留未清理的自查文字 ----------
c0_hits = [w for w in ["更正（审计前自查）", "不成立方向", "正确读法", "TODO", "待补"] if w in DRAFT]
out["checks"]["C0_draft_uncleaned_selfnotes"] = {"hits": c0_hits, "pass": len(c0_hits)==0}

# ---------- C2: 扰动号口径裁定（核心） ----------
c2 = {}
for dk, n in DIRS.items():
    tm, jn = tmax(n), Jn(n)
    for Tm in TM_LIST:
        Ladv, dwadv = Lstar(Tm, tm, jn, -1)   # v2 adversarial (-dbar t)
        Lany, dwany = Lstar(Tm, tm, jn, +1)   # any-disturb (+dbar t, 更保守/更大)
        v2nec = R["analytic"][dk][str(Tm)]["L_nec"]
        c2[f"{dk}|{Tm}"] = {"L_star_adversarial": round(Ladv,5),
                            "L_star_any_disturbance": round(Lany,5),
                            "v2_L_nec": round(v2nec,5),
                            "v2_matches_adversarial": bool(abs(Ladv-v2nec) < 2e-4),
                            "any_over_adv_ratio": round(Lany/Ladv,4) if Ladv>0 else None}
matches = all(v["v2_matches_adversarial"] for v in c2.values())
out["checks"]["C2_disturbance_sign_verdict"] = {
    "rows": c2, "v2_uses_adversarial": matches,
    "pass": matches,
    "verdict": ("v2 解析界 = 对抗扰动(n·d=+dbar)下的界；Theorem 1 陈述必须限定为"
                "'在最坏对抗扰动实现下'，不得写'对任意扰动'。若要覆盖任意扰动，"
                "须改用 +dbar 的 L_star_any_disturbance（更大/更保守）并重算全部数值。")}

# ---------- C3: 存在性条件 τmax,n > dbar (硬伤 C) ----------
c3 = {dk: {"tau_max_n": round(tmax(n),5), "dbar": round(DBAR,5),
           "condition_holds": bool(tmax(n) > DBAR)} for dk,n in DIRS.items()}
out["checks"]["C3_existence_condition"] = {"rows": c3,
    "pass": all(v["condition_holds"] for v in c3.values()),
    "note": "τmax,n>dbar 是 A 最终单调、t* 存在、界非 vacuous 的前提；逐方向核验"}

# ---------- C4: Lemma 1 真实闭环轨迹逐点验证（含等价性探针） ----------
def rhs_record(X, t, family, Kp, Kd, W, Tm, d_mode, n_dir):
    """复制 p2.rhs 公式但返回 u_c / tau_vec；先与 p2.rhs 做等价性断言。"""
    q, w, u, dh = X[:,0:4], X[:,4:7], X[:,7:11], X[:,11:14]
    tau_c = p2.controller(X, t, family, Kp, Kd, W)
    y = np.concatenate([np.full((X.shape[0],1), F), tau_c], axis=1)
    u_c = np.clip(y @ p2.MPINV.T, 0.0, u_max)
    for _ in range(60):   # Amendment-3: iterate to convergence (matches p2.rhs)
        s = u_c.sum(axis=1) - F
        u_c = u_c - (s/4.0)[:, None]
        u_c = np.clip(u_c, 0.0, u_max)
        if np.max(np.abs(u_c.sum(axis=1)-F)) < 1e-9: break
    u_c = np.clip(u_c, 0.0, u_max)
    tau_vec = u @ M_T.T
    if d_mode == "adv":
        dvec = np.tile(DBAR*n_dir, (X.shape[0],1))
    else:
        dvec = p2.d_at(t)[None,:]
    wdot = (tau_vec - np.cross(w, J*w) + dvec)/J
    qdot = p2.quat_dot(q, w)
    udot = (u_c - u)/Tm
    dhdot = (dvec - dh)/p2.T_LP
    dX = np.concatenate([qdot, wdot, udot, dhdot], axis=1)
    return dX, u_c, tau_vec

# 等价性探针（单一 plant RHS 纪律 §7）
np.random.seed(0)
Xtest = np.random.rand(5,14); Xtest[:,0:4]/=np.linalg.norm(Xtest[:,0:4],axis=1,keepdims=True)
dXr,_,_ = rhs_record(Xtest, 0.1, "qpd_ff", 6.,1., np.ones(3), 0.05, "adv", DIRS["roll"])
dXp = p2.rhs(Xtest, 0.1, "qpd_ff", 6.,1., np.ones(3), 0.05, "adv", DIRS["roll"])
equiv = bool(np.allclose(dXr, dXp, atol=1e-12))
out["checks"]["C4b_rhs_equivalence_probe"] = {"pass": equiv, "max_abs_diff": float(np.max(np.abs(dXr-dXp)))}

def lemma_trajectory(n, Tm, dw=3.0):
    """单场景闭环，记录 (-n)·τ(t) 与 τmax,n(1-e^{-t/Tm})。"""
    N=1; X=np.zeros((N,14)); X[:,0]=1.0; X[:,4:7]=dw*n; X[:,7:11]=p2.u_hov
    h=p2.DT; nsteps=int(round(p2.T_HOR/h)); tm=tmax(n)
    viol=0; max_excess=-1e9; uc_feas_viol=0; max_sum_err=0.0; rec=[]
    for k in range(nsteps):
        t=k*h
        dX,uc,tv = rhs_record(X,t,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        # Lemma 1 逐点: (-n)·τ(t) <= tm*(1-e^{-t/Tm}); τ(t)=M_T u(t) (状态, 非 u_c)
        lhs = float((-n) @ (X[0,7:11] @ M_T.T))
        rhs = tm*(1.0-math.exp(-t/Tm))
        exc = lhs - rhs
        if exc > 1e-9: viol+=1
        max_excess=max(max_excess,exc)
        # u_c 是否严格属于可行集 U (Σu=F, bounds)
        se=float(abs(uc[0].sum()-F))
        max_sum_err=max(max_sum_err,se)
        if se>1e-6 or uc.min()<-1e-9 or uc.max()>u_max+1e-9: uc_feas_viol+=1
        if k in (0,10,50,100,200,400): rec.append({"t":round(t,4),"lhs":round(lhs,5),"rhs":round(rhs,5),"excess":round(exc,6)})
        # RK4 (same as p2.simulate), but keep rhs_record for u_c/tau at stage1 only
        k1=dX
        k2=p2.rhs(X+0.5*h*k1,t+0.5*h,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        k3=p2.rhs(X+0.5*h*k2,t+0.5*h,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        k4=p2.rhs(X+h*k3,t+h,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        X=X+(h/6.0)*(k1+2*k2+2*k3+k4)
        X[:,0:4]/=np.maximum(np.linalg.norm(X[:,0:4],axis=1,keepdims=True),1e-12)
    return {"violations":viol,"n_steps":nsteps,"max_excess":round(float(max_excess),6),
            "uc_feasible_violations":uc_feas_viol,"max_sum_u_error":round(max_sum_err,8),
            "samples":rec}
c4={}
for dk,n in DIRS.items():
    c4[dk]=lemma_trajectory(n,0.05)
out["checks"]["C4_lemma1_trajectory"] = {"rows":c4,
    "pass": all(v["violations"]==0 for v in c4.values()),
    "note": "Lemma 1 逐点式在真实闭环轨迹上验证；同时记录 u_c 是否严格 ∈ U"}

# ---------- C5/P10: 独立单轴 ODE 积分复算 φ_min ----------
def phi_min_by_ode(dw, Tm, tm, jn, sign=-1):
    """直接积分最优控制器全力减速 + 扰动的单轴 ODE，独立复现 φ_min。
    ω̇_n = -A'(t) = [-tm*(1-e^{-t/Tm}) - sign*DBAR]/jn  (与 A_of_t 同一 sign)。"""
    h=1e-4; w=dw; phi=0.0; t=0.0; peak=0.0
    for _ in range(int(p2.T_HOR/h)):
        wdot = (-tm*(1.0-math.exp(-t/Tm)) - sign*DBAR)/jn
        w += wdot*h; phi += max(w,0.0)*h; t+=h
        peak=max(peak,phi)
        if w<=0: break
    return peak
c5={}
for dk,n in DIRS.items():
    tm,jn=tmax(n),Jn(n)
    for Tm in [0.05]:
        dw=3.0
        pan, _ = phi_min(dw, Tm, tm, jn, -1)   # v2 符号 (对抗, -dbar t)
        pode = phi_min_by_ode(dw, Tm, tm, jn, -1)
        c5[f"{dk}|{Tm}"]={"phi_min_analytic":round(pan,5),"phi_min_ode_independent":round(pode,5),
                          "abs_diff":round(abs(pan-pode),5),"rel_diff":round(abs(pan-pode)/max(pan,1e-9),5)}
out["checks"]["C5_P10_independent_recompute"] = {"rows":c5,
    "pass": all(v["rel_diff"]<0.02 for v in c5.values()),
    "note": "P10：用直接 ODE 积分（非解析 φ_min 公式）独立复算，验证 ω_n≥Δω−A(t) 链条"}

# ---------- C6/13b: reverse-solve 常数自洽 ----------
c6={}
for dk,n in DIRS.items():
    tm,jn=tmax(n),Jn(n)
    Tm=0.05
    Ladv,dwadv=Lstar(Tm,tm,jn,-1)   # v2 符号
    v2nec=R["analytic"][dk][str(Tm)]["L_nec"]
    # 从声明的 L_nec 反解 Δω*，再验证 φ_min(Δω*)=Φ (常数与公式自洽)
    dw_from_claim=v2nec/jn
    pm,ts=phi_min(dw_from_claim,Tm,tm,jn,-1)   # v2 符号
    c6[dk]={"claimed_L_nec":round(v2nec,5),"dw_star_reversed":round(dw_from_claim,5),
            "phi_min_at_dw_star":round(pm,5),"Phi_max":round(PHI,5),
            "self_consistent":bool(abs(pm-PHI)<1e-3),
            "tau_max_n_LP":round(tm,5),"dbar":round(DBAR,5),"feasible_tm_gt_dbar":bool(tm>DBAR)}
out["checks"]["C6_13b_reverse_solve"] = {"rows":c6,
    "pass": all(v["self_consistent"] for v in c6.values()),
    "note": "从稿子声称的 L_nec 反解 Δω*，代回 φ_min 必须等于 Φ_max；两个常数共享输入须一致"}

# C7: 硬伤 D 裸常数扫描（排除「声明无裸常数」的元叙述行，否则假阳性）
draft_lines = DRAFT.splitlines()
proof_lines = [l for l in draft_lines if not any(w in l for w in ["无 \"", "无 '", "不得", "禁止", "裸常数"])]
proof_text = "\n".join(proof_lines)
c7 = {"for_some_c_in_proof": bool(re.search(r"for some\s+\$?c", proof_text, re.I)),
      "bare_constant_phrases": re.findall(r"for some [a-zA-Z$]+>?0", proof_text),
      "has_explicit_constants": all(s in DRAFT for s in ["\\tau_{\\max,n}","\\bar d","T_m","\\Phi_{\\max}","J_n"])}
out["checks"]["C7_hardflaw_D_bare_constants"] = {**c7, "pass": (not c7["for_some_c_in_proof"]) and c7["has_explicit_constants"]}

# ---------- C8: 硬伤 E 抬高动词/超证措辞扫描 ----------
e_patterns = ["any disturbance","任意扰动","if and only if","充要","exact boundary","精确边界",
              "arbitrary impulse direction","任意冲击方向","tight","tightness","global stability","全局稳定"]
c8_hits=[]
for p in e_patterns:
    for m in re.finditer(re.escape(p), DRAFT, re.I):
        line=DRAFT[:m.start()].count("\n")+1
        c8_hits.append({"pattern":p,"line":line,"context":DRAFT.splitlines()[line-1][:110]})
out["checks"]["C8_hardflaw_E_overclaim_wording"] = {"hits":c8_hits,
    "pass": True, "note": "命中需人工判读是否属Remark诚实限定；'任意扰动'若出现在定理陈述即为超证"}

# ---------- C9: 硬伤 F 凭空交叉引用扫描 ----------
xrefs = re.findall(r"(?:见\s*§|Section~?\\ref|\\ref\{|as shown in Section|见第)", DRAFT)
out["checks"]["C9_hardflaw_F_dangling_xref"] = {"count":len(xrefs),"pass":len(xrefs)==0,
    "note":"本草稿为内部单文件，不含指向他节的 \\ref；若命中须 grep 目标节确认字面存在"}

# ---------- C10: 组合方向 A1 失效证据（陀螺重定向） ----------
def gyro_magnitude(n, Tm=0.05, dw=3.0):
    X=np.zeros((1,14)); X[:,0]=1.0; X[:,4:7]=dw*n; X[:,7:11]=p2.u_hov
    h=p2.DT; mx=0.0
    for k in range(200):
        t=k*h
        k1=p2.rhs(X,t,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        k2=p2.rhs(X+0.5*h*k1,t+0.5*h,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        k3=p2.rhs(X+0.5*h*k2,t+0.5*h,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        k4=p2.rhs(X+h*k3,t+h,"qpd_ff",6.,1.,np.ones(3),Tm,"adv",n)
        X=X+(h/6.0)*(k1+2*k2+2*k3+k4)
        X[:,0:4]/=np.maximum(np.linalg.norm(X[:,0:4],axis=1,keepdims=True),1e-12)
        w=X[0,4:7]
        mx=max(mx,float(np.linalg.norm(np.cross(w,J*w))))
    return round(mx,5)
c10={"gyro_norm_principal_roll":gyro_magnitude(DIRS["roll"]),
     "gyro_norm_principal_yaw":gyro_magnitude(DIRS["yaw"]),
     "gyro_norm_combo":gyro_magnitude(DIRS["combo"])}
combo_ratio=[]
for Tm in TM_LIST:
    nec=R["analytic"]["combo"][str(Tm)]["L_nec"]
    vals=[v["L_suff"] for k,v in R["done_cells_adv"].items()
          if k.startswith("combo|"+str(Tm)+"|") and v["L_suff"]==v["L_suff"]]
    if vals and nec==nec: combo_ratio.append(round(min(vals)/nec,3))
c10["combo_Lsuff_over_Lnec_adv_arm"]=combo_ratio
out["checks"]["C10_A1_failure_on_combo"] = {**c10,
    "pass": bool(c10["gyro_norm_combo"]>c10["gyro_norm_principal_roll"]*5),
    "note":"组合方向 ω×Jω 非零 ⇒ A1 失效 ⇒ Theorem 1 严格适用仅限主轴；Remark 1 的限定有数值依据"}

# ---------- 汇总 ----------
must_pass=["C0_draft_uncleaned_selfnotes","C2_disturbance_sign_verdict","C3_existence_condition",
           "C4b_rhs_equivalence_probe","C4_lemma1_trajectory","C5_P10_independent_recompute",
           "C6_13b_reverse_solve","C7_hardflaw_D_bare_constants","C10_A1_failure_on_combo"]
failed=[k for k in must_pass if not out["checks"][k]["pass"]]
out["summary"]={"all_must_pass":len(failed)==0,
                "must_pass_results":{k:out["checks"][k]["pass"] for k in must_pass},
                "failed":failed,
                "draft_revision_status":"C0/C2 修订已落地：Theorem 1 限定对抗扰动、§3 自查文字已清理；Remark 1/2/3 保留主轴限定/上界非精确/存在性条件",
                "revisions_required":failed}
json.dump(out, open(os.path.join(HERE,"theorem_audit.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)

print("AUDIT ALL_MUST_PASS =", out["summary"]["all_must_pass"])
for k in must_pass:
    v=out["checks"][k]
    print("  %-38s pass=%s"%(k,v["pass"]))
print("\n-- C2 口径裁定 --")
for k,v in out["checks"]["C2_disturbance_sign_verdict"]["rows"].items():
    print("  %-14s Ladv=%.5f Lany=%.5f v2=%.5f match_adv=%s any/adv=%.3f"%(
        k,v["L_star_adversarial"],v["L_star_any_disturbance"],v["v2_L_nec"],
        v["v2_matches_adversarial"],v["any_over_adv_ratio"]))
print("\n-- C4 Lemma1 真实轨迹 --")
for k,v in out["checks"]["C4_lemma1_trajectory"]["rows"].items():
    print("  %-8s viol=%d max_excess=%.6f uc_feas_viol=%d max_sum_err=%.8f"%(
        k,v["violations"],v["max_excess"],v["uc_feasible_violations"],v["max_sum_u_error"]))
print("\n-- C5 P10 独立复算 --")
for k,v in out["checks"]["C5_P10_independent_recompute"]["rows"].items():
    print("  %-14s analytic=%.5f ode=%.5f rel=%.5f"%(k,v["phi_min_analytic"],v["phi_min_ode_independent"],v["rel_diff"]))
print("\n-- C10 A1 失效 --")
print(" ",c10)
print("\n-- C8 超证措辞命中 --",len(c8_hits))
for h in c8_hits: print("   line",h["line"],h["pattern"],":",h["context"][:90])
