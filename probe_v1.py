# -*- coding: utf-8 -*-
"""
Probe v1 — falsifiable probe for the optimized idea (DESIGN frozen in
preregistration_probe_v1.md BEFORE this script runs).

Scalar reduced-order quadrotor attitude model (NOT full 6-DoF):
    phi' = omega
    J*omega' = tau + d          (d = 0 in this probe)
    tau' = (sat(tau_c) - tau)/T_m
    tau_c = -tau_max*tanh(omega/eps)   (numerical side, max-effort-like)
    impulse: omega(0+) = domega, phi(0)=0, tau(0)=0

Recovery (frozen): max|phi(t)| <= Phi_max AND |omega(T_hor)| <= omega_th.
Parameters are RESEARCH ASSUMPTIONS, not data. No RNG -> deterministic.

Everything written to probe_v1_results.json; nothing invented here.
"""
import json, math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- frozen parameters ----------------
J       = 0.015                     # kg m^2   (assumption)
TAU_MAX = 0.15                      # N m      (assumption)
PHI_MAX = math.radians(60.0)        # 1.0472 rad (assumption)
D       = 0.0                       # sustained disturbance isolated out
EPS     = 0.05                      # tanh smoothing of numerical controller
W_TH    = 0.2                       # rad/s
T_HOR   = 2.0                       # s
DT      = 2.0e-4                    # s
TM_LIST = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20]
DW_MAX  = 10.0
DW_SCAN = [0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0]
T_CHAR  = math.sqrt(J * PHI_MAX / TAU_MAX)   # natural attitude time scale
# ---------------------------------------------------


def sat(u):
    return max(-TAU_MAX, min(TAU_MAX, u))


def tau_cmd(w, eps):
    return -TAU_MAX * math.tanh(w / eps)


def simulate(dw, Tm, eps=EPS, dt=DT, horizon=T_HOR):
    """RK4 integration; returns (recover_ok, max_abs_phi, w_final, phi_peak_t)."""
    phi, w, tau = 0.0, float(dw), 0.0
    max_abs_phi = 0.0
    t_peak = 0.0
    n = int(round(horizon / dt))
    for i in range(n):
        # stage derivatives f(y)
        def deriv(phi_, w_, tau_):
            return (w_, (tau_ + D) / J, (sat(tau_cmd(w_, eps)) - tau_) / Tm)
        k1 = deriv(phi, w, tau)
        k2 = deriv(phi + 0.5*dt*k1[0], w + 0.5*dt*k1[1], tau + 0.5*dt*k1[2])
        k3 = deriv(phi + 0.5*dt*k2[0], w + 0.5*dt*k2[1], tau + 0.5*dt*k2[2])
        k4 = deriv(phi + dt*k3[0],     w + dt*k3[1],     tau + dt*k3[2])
        phi += dt/6.0*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
        w   += dt/6.0*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        tau += dt/6.0*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
        a = abs(phi)
        if a > max_abs_phi:
            max_abs_phi, t_peak = a, (i+1)*dt
    ok = (max_abs_phi <= PHI_MAX) and (abs(w) <= W_TH)
    return ok, max_abs_phi, w, t_peak


def A_of_t(t, Tm):
    """A(t) = (tau_max/J)*[t - Tm*(1-exp(-t/Tm))]; omega_lb = dw - A(t)."""
    return (TAU_MAX / J) * (t - Tm * (1.0 - math.exp(-t / Tm)))


def solve_tstar(dw, Tm):
    """A(t*) = dw, A monotone increasing -> bisection."""
    lo, hi = 0.0, 10.0
    for _ in range(120):
        mid = 0.5*(lo+hi)
        if A_of_t(mid, Tm) < dw: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)


def phi_peak_min(dw, Tm):
    """Controller-independent LOWER bound on max|phi| (necessary non-recoverability).
    omega(t) >= dw - A(t) for ANY controller since |tau(t)| <= tau_max(1-e^{-t/Tm}).
    g(t)=dw*t - int_0^t A(s)ds, max at t*, so phi(t*) >= g(t*) = phi_peak_min."""
    ts = solve_tstar(dw, Tm)
    intA = (TAU_MAX / J) * (ts*ts/2.0 - Tm*ts + Tm*Tm*(1.0 - math.exp(-ts/Tm)))
    return dw*ts - intA


def L_nec_of_Tm(Tm):
    """Solve phi_peak_min(dw*) = PHI_MAX -> L_nec = J*dw* (necessary bound)."""
    lo, hi = 0.0, DW_MAX
    for _ in range(120):
        mid = 0.5*(lo+hi)
        if phi_peak_min(mid, Tm) < PHI_MAX: lo = mid
        else: hi = mid
    dw = 0.5*(lo+hi)
    return {"L_nec_Nms": J*dw, "dw_star_rad_s": dw,
            "phi_peak_min_at_star": phi_peak_min(dw, Tm)}


def L_suff_of_Tm(Tm, eps=EPS, dt=DT):
    """Max dw such that the numerical closed loop recovers (bisection, monotone)."""
    lo, hi = 0.0, DW_MAX
    for _ in range(40):
        mid = 0.5*(lo+hi)
        ok, *_ = simulate(mid, Tm, eps=eps, dt=dt)
        if ok: lo = mid
        else: hi = mid
    dw = 0.5*(lo+hi)
    return {"L_suff_Nms": J*dw, "dw_max_rad_s": dw}


def L_suff_ideal(Tm):
    """Sanity/positive-control: ideal max-effort (eps->0) boundary should ~= L_nec."""
    return L_suff_of_Tm(Tm, eps=1e-6)["L_suff_Nms"]


# ================= self-tests (gate; run before recording numbers) =================
selftest = {}
ok0, mp0, w0, _ = simulate(0.0, 0.05)
selftest["S1_no_impact_baseline"] = {"ok": ok0, "max_abs_phi": mp0, "w_final": w0,
                                      "pass": bool(ok0 and mp0 < 1e-9 and abs(w0) < 1e-3)}
s2 = {str(dw): simulate(dw, 0.05)[0] for dw in DW_SCAN}
selftest["S2_scan_has_transition"] = {"recover_by_dw": s2,
                                      "pass": bool(s2["0.5"] is True and s2["8.0"] is False)}
r3 = phi_peak_min(8.0, 0.05) / phi_peak_min(0.5, 0.05)
selftest["S3_discrimination_ratio"] = {"phi_peak_min_8_over_0p5": r3,
                                        "threshold": 10.0, "pass": bool(r3 >= 10.0)}
# dt convergence on one representative (near-boundary) case
ok_a, mp_a, w_a, _ = simulate(3.0, 0.05, dt=DT)
ok_b, mp_b, w_b, _ = simulate(3.0, 0.05, dt=DT/2.0)
selftest["S5a_dt_convergence"] = {"max_phi_dt": mp_a, "max_phi_dt_half": mp_b,
                                   "abs_diff": abs(mp_a-mp_b), "pass": bool(abs(mp_a-mp_b) < 1e-3)}
# byte-identical rerun (determinism)
ok_r1, mp_r1, w_r1, _ = simulate(3.0, 0.05)
ok_r2, mp_r2, w_r2, _ = simulate(3.0, 0.05)
selftest["S5b_determinism"] = {"no_drift": (ok_r1, mp_r1, w_r1) == (ok_r2, mp_r2, w_r2),
                                "pass": bool((ok_r1, mp_r1, w_r1) == (ok_r2, mp_r2, w_r2))}
gate_ok = all(v.get("pass", False) for v in selftest.values())

# ================= main scan =================
rows = []
for Tm in TM_LIST:
    nec = L_nec_of_Tm(Tm)
    suf = L_suff_of_Tm(Tm)
    ideal = L_suff_ideal(Tm)
    L_nec, L_suf = nec["L_nec_Nms"], suf["L_suff_Nms"]
    rows.append({
        "T_m_s": Tm,
        "mu": Tm / T_CHAR,
        "L_nec_Nms": L_nec,
        "lambda_star": L_nec / (TAU_MAX * T_CHAR),
        "dw_star_rad_s": nec["dw_star_rad_s"],
        "L_suff_Nms": L_suf,
        "dw_max_rad_s": suf["dw_max_rad_s"],
        "gap_Nms": L_nec - L_suf,
        "gap_pct": 100.0*(L_nec - L_suf)/L_nec if L_nec > 0 else 0.0,
        "L_suff_ideal_Nms": ideal,
        "ideal_vs_nec_pct": 100.0*(ideal - L_nec)/L_nec if L_nec > 0 else 0.0,
        "G1_hard_bound_ok": bool(L_suf <= 1.05*L_nec),
    })

# S4: boundary inside scan
s4 = all(0.5 <= r["dw_star_rad_s"] <= 8.0 for r in rows)
selftest["S4_boundary_in_scan"] = {"dw_star_range": [min(r["dw_star_rad_s"] for r in rows),
                                                      max(r["dw_star_rad_s"] for r in rows)],
                                    "pass": bool(s4)}
gate_ok = all(v.get("pass", False) for v in selftest.values())

# ================= frozen GO evaluation (verbatim) =================
L_necs = [r["L_nec_Nms"] for r in rows]
g1 = all(r["G1_hard_bound_ok"] for r in rows)
mono = all(L_necs[i] > L_necs[i+1] for i in range(len(L_necs)-1))
ratio = L_necs[0] / L_necs[-1]
g2 = bool(mono and ratio >= 1.3 and selftest["S3_discrimination_ratio"]["pass"]
          and selftest["S4_boundary_in_scan"]["pass"])
g3 = {"gap_all_nonneg": all(r["gap_Nms"] >= -1e-9 for r in rows),
      "gap_min": min(r["gap_Nms"] for r in rows),
      "gap_max": max(r["gap_Nms"] for r in rows),
      "note": "scalar + near-optimal controller => necessary bound is TIGHT; "
              "gray band must be opened by multi-axis anisotropy / non-ideal "
              "controller / sustained disturbance (not forged here)."}
verdict = "GO" if (gate_ok and g1 and g2) else "NO-GO"

result = {
    "probe": "v1",
    "status": "EXECUTED",
    "frozen_criteria_source": "preregistration_probe_v1.md",
    "model": "scalar reduced-order (NOT full 6-DoF); parameters are RESEARCH ASSUMPTIONS",
    "params": {"J": J, "tau_max": TAU_MAX, "Phi_max_rad": PHI_MAX, "d": D,
               "eps": EPS, "omega_th": W_TH, "T_hor": T_HOR, "dt": DT,
               "T_char_s": T_CHAR, "T_m_list": TM_LIST},
    "self_test": selftest,
    "gate_ok": gate_ok,
    "rows": rows,
    "analytic_note": "L_nec derived WITHOUT any controller/Lyapunov: |tau(t)|<=tau_max(1-e^{-t/Tm}) "
                     "=> omega(t)>=dw-A(t) => phi(t*)>=g(t*); g(t*)=Phi_max defines dw*.",
    "go": {"G1_hard_upper_bound": g1, "G2_monotone_and_discriminating": g2,
           "G2_mono": mono, "G2_ratio_Lnec_001_over_020": ratio,
           "G3_gap": g3, "VERDICT": verdict},
}
with open(os.path.join(OUT, "probe_v1_results.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# compact stdout
print("GATE_OK =", gate_ok, "| VERDICT =", verdict)
print("T_char = %.4f s" % T_CHAR)
print("self_test:")
for k, v in selftest.items():
    print("  %-28s pass=%s  %s" % (k, v.get("pass"),
          {kk: (round(vv,4) if isinstance(vv,float) else vv) for kk,vv in v.items() if kk!="pass"}))
print("\n T_m    mu    L_nec    L_suff   gap%   ideal%  G1")
for r in rows:
    print(" %.2f  %.3f  %.5f  %.5f  %5.1f  %6.1f   %s" %
          (r["T_m_s"], r["mu"], r["L_nec_Nms"], r["L_suff_Nms"],
           r["gap_pct"], r["ideal_vs_nec_pct"], r["G1_hard_bound_ok"]))
print("\nG1=%s G2=%s (mono=%s ratio=%.3f) G3 gap in [%.5f, %.5f]" %
      (g1, g2, mono, ratio, g3["gap_min"], g3["gap_max"]))
print("lambda*(mu) curve:", [(round(r["mu"],3), round(r["lambda_star"],3)) for r in rows])
print("JSON ->", os.path.join(OUT, "probe_v1_results.json"))
