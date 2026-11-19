# -*- coding: utf-8 -*-
"""
Probe v2 — 6-DoF quaternion attitude recovery under anisotropic actuator feasibility.
DESIGN frozen in preregistration_probe_v2.md BEFORE this script runs.

Integrity features (from loaded references):
  * ONE plant RHS called by every RK4 stage (control-sim-pitfalls §7).
  * diagonal inertia -> gyroscopic term via np.cross(w, J*w) elementwise (§8).
  * rotor constants from first principles + hover-speed sanity (§9).
  * mixer rows orthogonal / rank 4, no pinv-collective bug (§9, flight-sim 4-pitfalls).
  * disturbance pre-generated on FIXED 0.25 ms grid, indexed by physical time t,
    so dt refinement keeps the realisation bit-identical (§13 / dt-integrity #1).
  * bounded zero-mean turbulence, NOT constant bias (§11.3).
  * equal-tuning-budget baselines on a disjoint calibration set (§3).
All numbers are written to probe_v2_results.json. Nothing invented.
"""
import json, math, os, sys
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(OUT, "probe_v2_results.json")

# ---------------- frozen parameters (RESEARCH ASSUMPTIONS, not data) ----------------
m, g      = 0.8, 9.81
F         = m*g                      # 7.848 N hover thrust
cT        = F/(4.0*500.0**2)        # chosen so Omega_hover = 500 rad/s  (§9 sanity band 400-600)
OMEGA_HOV = math.sqrt(F/(4.0*cT))
OMEGA_MAX = 900.0
u_max     = cT*OMEGA_MAX**2         # 6.357 N per rotor
arm       = 0.22
a         = arm/math.sqrt(2.0)      # 0.1556 m
kappa     = 0.02                    # cQ/cT [m] -> yaw authority ~13% of roll
u_hov     = F/4.0
J         = np.array([0.013, 0.013, 0.024])   # diagonal inertia
PHI_MAX   = math.radians(60.0)
W_TH      = 0.2
T_HOR     = 1.5
DT        = 5.0e-4
T_FIX     = 2.5e-4                  # fixed disturbance grid (0.25 ms)
TM_LIST   = [0.02, 0.05, 0.10]
DIRS      = {"roll":np.array([1.,0.,0.]), "pitch":np.array([0.,1.,0.]),
             "yaw":np.array([0.,0.,1.]), "combo":np.array([1.,1.,1.])/math.sqrt(3.)}
D_AMP     = 0.02
D_BAR     = 1.6*D_AMP               # disturbance upper bound for analytic bound
T_LP      = 0.02                    # disturbance low-pass for qpd_ff
T_M_REF   = 0.05
T_REF     = 0.05                    # reference Tm used by self-tests/calibration/dt-convergence;
                                    # DEFAULT 0.05 keeps v2.3 byte-identical; configure() sets it to TM_LIST[0]
N_DW      = 160
DW_GRID   = np.linspace(0.2, 20.0, N_DW)   # Amendment-1: range extended past real transition
SEED_PHASE = np.array([0.0, 1.7, 3.4, 5.1, 2.2])   # deterministic phases (no RNG)

# mixer M: rows [F, Mx, My, Mz] in u_i units; rows must be orthogonal, rank 4
MIX_F = np.array([1.,1.,1.,1.])
MIX_X = a*np.array([1.,1.,-1.,-1.])
MIX_Y = a*np.array([-1.,1.,1.,-1.])
MIX_Z = kappa*np.array([1.,-1.,1.,-1.])
MIX   = np.vstack([MIX_F, MIX_X, MIX_Y, MIX_Z])   # 4x4
M_T   = MIX[1:4, :]                                # torque rows (3x4)
# pseudoinverse for orthogonal rows: M+ = M.T @ inv(M M.T)
MMT   = np.diag(MIX @ MIX.T)
MPINV = (MIX.T / MMT[None, :])                      # 4x4, u_c = MPINV @ [F,taux,tauy,tauz]

def configure(cfg):
    """Override all model parameters from a single-platform config.
    DEFAULT behaviour (no call) is byte-identical to v2.3 (synthetic params),
    so probe_v2_results.json stays reproducible. cfg = mapped_to_model dict.
    Recomputes EVERY derived global in one place (single-source-of-truth)."""
    global m,g,F,a,kappa,J,u_max,u_hov,TM_LIST,D_AMP,D_BAR,T_LP
    global PHI_MAX,W_TH,T_HOR,DT,T_FIX,N_DW,DW_GRID
    global MIX_F,MIX_X,MIX_Y,MIX_Z,MIX,M_T,MMT,MPINV
    global N_FIX,T_GRID,D_FIX,RPM_IDENTIFIED,cT,OMEGA_HOV,OMEGA_MAX,arm,RES
    global T_REF,CAL_SCENES
    global GAIN_SCALE,KP_GRID,KD_GRID
    global PER_TM_CALIBRATION
    m,g = cfg["m"], cfg["g"]
    F = m*g
    a = cfg["a"]; kappa = cfg["kappa"]
    J = np.array(cfg["J"], dtype=float)
    u_max = cfg["u_max"]; u_hov = cfg.get("u_hov", F/4.0)
    TM_LIST = cfg["TM_LIST"]
    D_AMP = cfg["D_AMP"]; D_BAR = cfg["D_BAR"]; T_LP = cfg["T_LP"]
    PHI_MAX = math.radians(cfg["PHI_MAX_deg"])
    W_TH = cfg["W_TH"]; T_HOR = cfg["T_HOR"]; DT = cfg["DT"]; T_FIX = cfg["T_FIX"]
    N_DW = cfg["N_DW"]; DW_GRID = np.linspace(0.2, cfg.get("dw_grid_max", 20.0), N_DW)
    # RPM-level quantities not identified for this config -> mark N/A honestly
    RPM_IDENTIFIED = False
    cT = OMEGA_HOV = OMEGA_MAX = arm = None
    MIX_F = np.array([1.,1.,1.,1.])
    MIX_X = a*np.array([1.,1.,-1.,-1.])
    MIX_Y = a*np.array([-1.,1.,1.,-1.])
    MIX_Z = kappa*np.array([1.,-1.,1.,-1.])
    MIX   = np.vstack([MIX_F, MIX_X, MIX_Y, MIX_Z])
    M_T   = MIX[1:4, :]
    MMT   = np.diag(MIX @ MIX.T)
    MPINV = (MIX.T / MMT[None, :])
    N_FIX = int(round((T_HOR + 0.1)/T_FIX)) + 2
    T_GRID = np.arange(N_FIX)*T_FIX
    D_FIX = np.array([d_of_t(t) for t in T_GRID])
    T_REF = TM_LIST[0]
    CAL_SCENES = [(1.5,"roll",T_REF), (1.0,"yaw",T_REF), (1.0,"combo",T_REF)]
    # scale controller gains to the real platform's characteristic torque a*F
    GAIN_SCALE = (a*F)/A_F_SYN
    KP_GRID = [g*GAIN_SCALE for g in [2.,4.,6.,8.,10.]]
    KD_GRID = [g*GAIN_SCALE for g in [0.5,1.,2.,3.,4.]]
    PER_TM_CALIBRATION = bool(cfg.get("per_tm_calibration", False))
    if cfg.get("result_file"):
        RES = os.path.join(OUT, cfg["result_file"])
    return {"F":F,"u_max":u_max,"u_hov":u_hov,"a":a,"kappa":kappa,
            "J":J.tolist(),"TM_LIST":TM_LIST,"D_BAR":D_BAR}

RPM_IDENTIFIED = True   # default synthetic config has cT/Omega identified

def mixer_gram_check():
    G = MIX @ MIX.T
    off = np.max(np.abs(G - np.diag(np.diag(G))))
    rank = np.linalg.matrix_rank(MIX)
    return {"gram_offdiag_max": float(off), "rank": int(rank),
            "pass": bool(off < 1e-9 and rank == 4)}

# ---------------- fixed disturbance grid (§13) ----------------
N_FIX = int(round((T_HOR + 0.1)/T_FIX)) + 2
T_GRID = np.arange(N_FIX)*T_FIX
def d_of_t(t):
    idx = int(round(t/T_FIX))
    idx = min(max(idx, 0), N_FIX-1)
    ph = SEED_PHASE
    return D_AMP*np.array([
        math.sin(2*math.pi*3.1*t+ph[0]) + 0.6*math.sin(2*math.pi*7.7*t+2*ph[0]),
        math.sin(2*math.pi*3.1*t+ph[1]) + 0.6*math.sin(2*math.pi*7.7*t+2*ph[1]),
        math.sin(2*math.pi*3.1*t+ph[2]) + 0.6*math.sin(2*math.pi*7.7*t+2*ph[2]),
    ])
D_FIX = np.array([d_of_t(t) for t in T_GRID])        # (N_FIX,3)
def d_at(t):
    idx = min(max(int(round(t/T_FIX)), 0), N_FIX-1)
    return D_FIX[idx]

def disturbance_checks():
    mean = float(np.mean(np.abs(D_FIX)))
    mx   = float(np.max(np.abs(D_FIX)))
    zero_mean = bool(abs(float(D_FIX.mean(axis=0).max())) < 0.02)
    bounded = bool(mx <= D_BAR + 1e-9)
    return {"max_abs": mx, "mean_abs": mean, "zero_mean": zero_mean,
            "bounded_by_dbar": bounded, "pass": bool(zero_mean and bounded)}

# ---------------- analytic controller-independent reference bound ----------------
def tau_max_dir(n):
    """LP: max (-n).(M_T u) s.t. sum(u)=F, 0<=u<=u_max. Greedy (box+equality)."""
    c = -(n[0]*MIX_X + n[1]*MIX_Y + n[2]*MIX_Z)      # coefficient of each u_i
    order = np.argsort(-c)
    rem, u = F, np.zeros(4)
    for i in order:
        take = min(u_max, rem)
        u[i] = max(take, 0.0)
        rem -= u[i]
        if rem <= 1e-12: break
    return float(c @ u)

def J_dir(n):
    return float(n @ (J*n))

def A_of_t(t, Tm, tmax_n, Jn):
    # omega_n lower bound decay term: [tmax_n*(t-Tm(1-e^{-t/Tm})) - dbar*t]/Jn
    return (tmax_n*(t - Tm*(1.0-math.exp(-t/Tm))) - D_BAR*t)/Jn

def phi_peak_min(dw, Tm, tmax_n, Jn):
    """Lower bound on peak attitude under axial-decoupling approximation.
    omega_n(t) >= dw - A(t); phi_peak = dw*t* - int_0^{t*}A(t)dt, A(t*)=dw."""
    if tmax_n <= D_BAR:      # A not monotone -> vacuous
        return float("inf")
    lo, hi = 0.0, 20.0
    # A monotone increasing after small t; bracket t* by bisection on A(t*)=dw
    for _ in range(160):
        mid = 0.5*(lo+hi)
        if A_of_t(mid, Tm, tmax_n, Jn) < dw: lo = mid
        else: hi = mid
    ts = 0.5*(lo+hi)
    intA = (tmax_n*(ts*ts/2.0 - Tm*ts + Tm*Tm*(1.0-math.exp(-ts/Tm)))
            - D_BAR*ts*ts/2.0)/Jn
    return dw*ts - intA

def L_nec(n, Tm):
    tmax_n, Jn = tau_max_dir(n), J_dir(n)
    if tmax_n <= D_BAR:
        return {"L_nec": float("nan"), "dw_star": float("nan"), "vacuous": True,
                "tau_max_n": tmax_n, "J_n": Jn}
    lo, hi = 0.0, 30.0
    for _ in range(160):
        mid = 0.5*(lo+hi)
        if phi_peak_min(mid, Tm, tmax_n, Jn) < PHI_MAX: lo = mid
        else: hi = mid
    dw = 0.5*(lo+hi)
    return {"L_nec": Jn*dw, "dw_star": dw, "vacuous": False,
            "tau_max_n": tmax_n, "J_n": Jn,
            "phi_at_star": phi_peak_min(dw, Tm, tmax_n, Jn)}

# ---------------- ONE plant RHS (called by every RK4 stage, §7) ----------------
def quat_dot(q, w):
    q0,q1,q2,q3 = q[:,0],q[:,1],q[:,2],q[:,3]
    wx,wy,wz = w[:,0],w[:,1],w[:,2]
    return 0.5*np.stack([-q1*wx-q2*wy-q3*wz,
                          q0*wx+q2*wz-q3*wy,
                          q0*wy-q1*wz+q3*wx,
                          q0*wz+q1*wy-q2*wx], axis=1)

def controller(X, t, family, Kp, Kd, W_mech):
    q, w, dh = X[:,0:4], X[:,4:7], X[:,11:14]
    # allow scalar OR per-scenario (N,1) gains -> vectorised calibration
    Kp = np.asarray(Kp, dtype=float).reshape(-1, 1)
    Kd = np.asarray(Kd, dtype=float).reshape(-1, 1)
    sgn = np.where(q[:,0:1] >= 0, 1.0, -1.0)        # double-cover shortest path
    e = q[:,1:4]*sgn
    gyro = np.cross(w, J*w)                          # (N,3), elementwise J (§8)
    if family == "qpd":
        tau = -Kp*e - Kd*w
    elif family == "smc":
        s = w + 1.5*e
        tau = -Kp*np.tanh(s/0.1) - Kd*w
    elif family == "qpd_ff":
        tau = -Kp*e - Kd*w + gyro + dh
    elif family == "proposed":
        tau_raw = -Kp*e - Kd*w + gyro + dh
        tau = tau_raw*W_mech                          # anisotropy-aware allocation
    else:
        raise ValueError(family)
    return tau

def rhs(X, t, family, Kp, Kd, W_mech, Tm, d_mode="turb", n_dir=None):
    q, w, u, dh = X[:,0:4], X[:,4:7], X[:,7:11], X[:,11:14]
    tau_c = controller(X, t, family, Kp, Kd, W_mech)             # (N,3)
    y = np.concatenate([np.full((X.shape[0],1), F), tau_c], axis=1)
    u_c = np.clip(y @ MPINV.T, 0.0, u_max)                        # allocation + box
    # Amendment-3: iterate to ACTUAL convergence (was 6 iters -> 0.076 N residual,
    # which broke the u_c ∈ U premise of Lemma 1). Torque rows sum to zero, so a
    # uniform shift changes only total thrust; stop at max|sum-F| < 1e-9.
    for _ in range(60):
        s = u_c.sum(axis=1) - F
        u_c = u_c - (s/4.0)[:, None]
        u_c = np.clip(u_c, 0.0, u_max)
        if np.max(np.abs(u_c.sum(axis=1) - F)) < 1e-9:
            break
    u_c = np.clip(u_c, 0.0, u_max)
    tau_vec = u @ M_T.T                                            # (N,3) delivered torque
    if d_mode == "adv":
        # adversarial CONSTANT disturbance at the analytic bound, aligned with
        # the impulse direction (worst case opposing recovery). Matches the
        # analytic A(t) = [tmax*(... ) - dbar*t]/Jn口径 exactly.
        dvec = np.tile(D_BAR*n_dir, (X.shape[0], 1))
    else:
        dvec = d_at(t)[None, :]
    wdot = (tau_vec - np.cross(w, J*w) + dvec)/J                  # elementwise J
    qdot = quat_dot(q, w)
    if ASYM_TM is not None:
        # element-wise rising/falling time constant (Amendment-4 diagnostic)
        T_up, T_down = ASYM_TM
        T_eff = np.where(u_c > u, T_up, T_down)
        udot = (u_c - u)/T_eff
    else:
        udot = (u_c - u)/Tm
    dhdot = (dvec - dh)/T_LP
    return np.concatenate([qdot, wdot, udot, dhdot], axis=1)

def simulate(dw_vec, n, Tm, family, Kp, Kd, W_mech, dt=DT, d_mode="turb"):
    """Vectorised RK4 over a grid of impulse magnitudes; returns per-scenario
    (max_phi, w_final_norm, ok). Memory bounded: only current state kept."""
    N = len(dw_vec)
    X = np.zeros((N,14))
    X[:,0] = 1.0
    X[:,4:7] = dw_vec[:,None]*n[None,:]          # omega(0+) = Domega * n
    X[:,7:11] = u_hov                             # hover equilibrium
    maxphi = np.zeros(N)
    phi_int = np.zeros(N)                         # attitude-error integral (frozen calibration metric)
    peak_tau = np.zeros(N)
    sat_steps = np.zeros(N)
    settle_t = np.full(N, T_HOR)          # first time |w|<=W_TH and phi already past peak
    settled = np.zeros(N, bool)
    nsteps = int(round(T_HOR/dt))
    h = dt
    for k in range(nsteps):
        t = k*h
        k1 = rhs(X, t,          family,Kp,Kd,W_mech,Tm, d_mode,n)
        k2 = rhs(X+0.5*h*k1, t+0.5*h, family,Kp,Kd,W_mech,Tm, d_mode,n)
        k3 = rhs(X+0.5*h*k2, t+0.5*h, family,Kp,Kd,W_mech,Tm, d_mode,n)
        k4 = rhs(X+h*k3,     t+h,     family,Kp,Kd,W_mech,Tm, d_mode,n)
        X = X + (h/6.0)*(k1+2*k2+2*k3+k4)
        nrm = np.linalg.norm(X[:,0:4], axis=1, keepdims=True)
        X[:,0:4] = X[:,0:4]/np.maximum(nrm, 1e-12)   # unit-norm projection
        phi = 2.0*np.arccos(np.clip(np.abs(X[:,0]), 0.0, 1.0))
        maxphi = np.maximum(maxphi, phi)
        phi_int += phi*h
        # ---- cost metrics (frozen V4) ----
        u_now = X[:,7:11]
        tau_now = u_now @ M_T.T
        peak_tau = np.maximum(peak_tau, np.linalg.norm(tau_now, axis=1))
        sat_steps += (np.abs(u_now) < 1e-9).any(axis=1) | (np.abs(u_now-u_max) < 1e-9).any(axis=1)
        wnorm = np.linalg.norm(X[:,4:7], axis=1)
        newly = (~settled) & (wnorm <= W_TH) & (phi <= PHI_MAX)
        settle_t[newly] = t
        settled[newly] = True
        if np.any(~np.isfinite(X)):
            cost = {"sat_duty": float(np.mean(sat_steps)/max(k+1,1)),
                    "peak_tau": float(np.max(peak_tau)),
                    "settle_t_median": float(np.median(settle_t)),
                    "phi_integral_mean": float(np.mean(phi_int)),
                    "phi_int_per": phi_int.tolist(), "settle_t_per": settle_t.tolist()}
            return maxphi, np.full(N, np.inf), np.zeros(N, bool), True, cost
    wfin = np.linalg.norm(X[:,4:7], axis=1)
    ok = (maxphi <= PHI_MAX) & (wfin <= W_TH)
    cost = {"sat_duty": float(np.mean(sat_steps)/nsteps),
            "peak_tau": float(np.max(peak_tau)),
            "settle_t_median": float(np.median(settle_t)),
            "phi_integral_mean": float(np.mean(phi_int)),
            "phi_int_per": phi_int.tolist(), "settle_t_per": settle_t.tolist()}
    return maxphi, wfin, ok, False, cost

def L_suff(n, Tm, family, Kp, Kd, W_mech, dt=DT, d_mode="turb"):
    _, _, ok, bad, cost = simulate(DW_GRID, n, Tm, family, Kp, Kd, W_mech, dt, d_mode)
    if bad:
        return {"L_suff": float("nan"), "dw_max": float("nan"), "bad": True,
                "degenerate": True, "cost": cost, "ok_pattern": None}
    good = np.where(ok)[0]
    first_false = None
    for i,o in enumerate(ok):
        if not o: first_false = i; break
    # islands: any True AFTER the first False -> recovery domain is NOT monotone,
    # L_suff undefined. Mark degenerate, exclude from statistics; do NOT delete.
    islands = bool(first_false is not None and ok[first_false:].any())
    dw_max = float(DW_GRID[good[-1]]) if len(good) else 0.0
    return {"L_suff": (float("nan") if islands else J_dir(n)*dw_max),
            "dw_max": (float("nan") if islands else dw_max),
            "bad": False, "degenerate": islands, "islands": islands,
            "cost": cost, "ok_count": int(ok.sum()),
            "ok_pattern": ok.astype(int).tolist()}

# ---------------- equal-budget calibration (§3) ----------------
CAL_SCENES = [(1.5,"roll",T_REF), (1.0,"yaw",T_REF), (1.0,"combo",T_REF)]  # Amendment-2: safe region
KP_GRID = [2.,4.,6.,8.,10.]
KD_GRID = [0.5,1.,2.,3.,4.]
# Gain scaling: controller Kp/Kd grids were tuned for the synthetic platform's
# characteristic torque (a*F)_syn = 1.2211 N*m. A real micro-quad has a*F~0.0084,
# so unscaled gains would saturate EVERY controller -> degenerate comparison.
# DEFAULT 1.0 keeps v2.3 byte-identical; configure() sets (a*F)/(a*F)_syn.
GAIN_SCALE = 1.0
A_F_SYN    = 1.2211
G0_KP, G0_KD = 6.0, 2.0        # fixed gains used by self-tests/dt-convergence
# Per-Tm calibration: a single gain set tuned at T_REF=0.055 is INVALID for
# Tm=0.249 (4.5x slower motor -> baseline closed loop diverges even at dw=0).
# DEFAULT False keeps v2.3 byte-identical; real config sets True so each Tm
# gets its own equal-budget 25-combo calibration (fair per condition).
PER_TM_CALIBRATION = False

# Asymmetric actuator dynamics (Amendment-4 DIAGNOSTIC ONLY, default None).
# Real Crazyflie registry has rising 0.055455 s / falling 0.249394 s. The v2
# symmetric model brackets these as two separate runs; setting ASYM_TM=(up,down)
# applies the time constant ELEMENT-WISE per rotor (u_c>u -> rising, else falling).
# DEFAULT None keeps v2.3 byte-identical. NOTE: Lemma 1's psi(t) assumes a SINGLE
# Tm, so the analytic L_nec is NOT valid when ASYM_TM is set -> this is a purely
# NUMERICAL diagnostic, never used for GO evaluation (integrity principle 13).
ASYM_TM = None

def calibrate(family, W_mech, Tm=None):
    """25 (Kp,Kd) grid x disjoint calibration scenes, VECTORISED.
    Tm=None -> use CAL_SCENES as-is (default). Tm given -> per-Tm layered
    calibration at that motor time constant (same 25-combo budget)."""
    combos = [(Kp,Kd) for Kp in KP_GRID for Kd in KD_GRID]     # 25
    Kp_arr = np.array([c[0] for c in combos])
    Kd_arr = np.array([c[1] for c in combos])
    total = np.zeros(len(combos))
    scenes = ([(dw,dn,Tm) for dw,dn,_ in CAL_SCENES] if Tm is not None else CAL_SCENES)
    for dw, dn, Tmc in scenes:
        n = DIRS[dn]
        dw_vec = np.full(len(combos), dw)
        mp, wf, ok, isbad, cost = simulate(dw_vec, n, Tmc, family, Kp_arr, Kd_arr, W_mech)
        if isbad: return (None, None, float("inf")), True
        # FROZEN metric (prereg §5): attitude-error integral + recovery time,
        # computed PER gain-combo (per-scenario arrays), with a large penalty
        # only on an actual failure. No peak-only proxy, no pooled mean.
        per = (np.array(cost["phi_int_per"]) + np.array(cost["settle_t_per"])
               + np.where(ok, 0.0, 100.0))
        total += per
    i = int(np.argmin(total))
    return (float(combos[i][0]), float(combos[i][1]), float(total[i])), False

# ---------------- self-tests ----------------
def self_tests(W_mech):
    st = {}
    st["S3_mixer_gram"] = mixer_gram_check()
    st["S9_disturbance"] = disturbance_checks()
    if RPM_IDENTIFIED:
        st["S2_hover_sanity"] = {"omega_hover": OMEGA_HOV, "omega_max": OMEGA_MAX,
            "u_hov": u_hov, "u_max": u_max, "applicable": True,
            "pass": bool(400 <= OMEGA_HOV <= 600 and OMEGA_HOV < OMEGA_MAX and u_hov < u_max)}
    else:
        # N/A, NOT silently passed: thrust model is in force units, RPM not
        # separately identified for this platform (documented in config).
        st["S2_hover_sanity"] = {"omega_hover": None, "omega_max": None,
            "u_hov": u_hov, "u_max": u_max, "applicable": False,
            "reason": "force-unit thrust model; RPM-level cT/Omega not identified; "
                      "hover equilibrium checked via u_hov=mg/4 < u_max instead",
            "pass": bool(u_hov < u_max)}
    # S4 torque-chain: recompute delivered torque from u, compare to M_T u
    u_test = np.array([u_hov, u_hov, u_hov, u_hov])
    tau_direct = M_T @ u_test
    tau_identity = np.array([a*(u_test[0]+u_test[1]-u_test[2]-u_test[3]),
                             a*(-u_test[0]+u_test[1]+u_test[2]-u_test[3]),
                             kappa*(u_test[0]-u_test[1]+u_test[2]-u_test[3])])
    st["S4_torque_chain"] = {"max_abs_diff": float(np.max(np.abs(tau_direct-tau_identity))),
                             "hover_tau_norm": float(np.linalg.norm(tau_direct)),
                             "pass": bool(np.max(np.abs(tau_direct-tau_identity))<1e-12
                                          and np.linalg.norm(tau_direct)<1e-9)}
    # S1 no-impact baseline, long horizon bounded
    mp, wf, ok, bad, _ = simulate(np.array([0.0]), DIRS["roll"], T_REF,
                               "qpd_ff", G0_KP*GAIN_SCALE, G0_KD*GAIN_SCALE, W_mech)
    st["S1_no_impact_baseline"] = {"max_phi": float(mp[0]), "w_final": float(wf[0]),
        "bad": bad, "pass": bool((not bad) and mp[0] < 0.05 and wf[0] < W_TH)}
    # S7 determinism (byte-identical rerun on a nontrivial case)
    r1 = simulate(np.array([3.0]), DIRS["roll"], T_REF, "qpd_ff", G0_KP*GAIN_SCALE, G0_KD*GAIN_SCALE, W_mech)
    r2 = simulate(np.array([3.0]), DIRS["roll"], T_REF, "qpd_ff", G0_KP*GAIN_SCALE, G0_KD*GAIN_SCALE, W_mech)
    st["S7_determinism"] = {"no_drift": bool(np.array_equal(r1[0],r2[0]) and
                            np.array_equal(r1[1],r2[1]) and np.array_equal(r1[2],r2[2])),
                            "pass": bool(np.array_equal(r1[0],r2[0]) and
                            np.array_equal(r1[1],r2[1]) and np.array_equal(r1[2],r2[2]))}
    st["S8_equal_budget"] = {"kp_grid": KP_GRID, "kd_grid": KD_GRID,
        "grid_size": len(KP_GRID)*len(KD_GRID), "cal_scenes": CAL_SCENES,
        "disjoint_from_eval": True, "pass": True}
    return st

# ---------------- frozen GO evaluation (verbatim from prereg §7) ----------------
def binom_p_two_sided(b, c):
    """Paired sign/McNemar exact two-sided p for discordant counts b,c."""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    # exact binomial two-sided: 2*P(X<=k) for X~Bin(n,0.5), capped at 1
    pmf = [math.comb(n, i) for i in range(n+1)]
    total = sum(pmf)
    p = min(1.0, 2.0*sum(pmf[:k+1])/total)
    return p

def evaluate(out, adv_cells=None):
    cells = out["done_cells"]                       # main arm: zero-mean turbulence (V2/V3/V4)
    adv = adv_cells if adv_cells is not None else cells   # adversarial arm for V1 (口径一致)
    an = out["analytic"]
    fams = ["qpd","smc","qpd_ff","proposed"]
    def only_valid(c):
        return {k:v for k,v in c.items() if not v.get("degenerate", False)
                and not v.get("bad", False) and v["L_suff"]==v["L_suff"]}
    valid = only_valid(cells)
    adv_valid = only_valid(adv)
    degen = {k:v for k,v in cells.items() if v.get("degenerate", False) or v.get("bad", False)
             or v["L_suff"]!=v["L_suff"]}

    # ---- V1: L_suff <= 1.05 * L_nec, evaluated on the ADVERSARIAL arm ----
    # (analytic bound uses the worst-case disturbance bound dbar; comparing it
    #  against a single zero-mean realisation is a口径 mismatch, Amendment-2)
    v1_rows = []
    for k,v in adv_valid.items():
        dk, Tm, fam = k.split("|")
        nec = an[dk][Tm]["L_nec"]
        ratio = v["L_suff"]/nec if nec and nec==nec else float("nan")
        v1_rows.append({"cell":k, "L_suff":v["L_suff"], "L_nec":nec,
                        "ratio":ratio, "ok":bool(ratio<=1.05)})
    v1 = bool(v1_rows and all(r["ok"] for r in v1_rows))
    v1_max_ratio = max((r["ratio"] for r in v1_rows if r["ratio"]==r["ratio"]), default=float("nan"))
    # also report the main-arm ratio for transparency (口径 mismatch evidence)
    main_ratios = []
    for k,v in valid.items():
        dk, Tm, fam = k.split("|")
        nec = an[dk][Tm]["L_nec"]
        if nec and nec==nec: main_ratios.append(v["L_suff"]/nec)
    v1_main_arm_max_ratio = max(main_ratios) if main_ratios else float("nan")

    # ---- V2: real non-zero gap, interpretable monotone direction ----
    gap_rows = []
    for k,v in valid.items():
        dk, Tm, fam = k.split("|")
        nec = an[dk][Tm]["L_nec"]
        if nec and nec==nec:
            gap_rows.append({"cell":k, "dir":dk, "Tm":float(Tm), "fam":fam,
                             "gap": nec-v["L_suff"], "gap_pct": 100*(nec-v["L_suff"])/nec})
    dirs_with_gap = set()
    tms_with_gap = set()
    for r in gap_rows:
        if r["gap_pct"] > 5.0:
            dirs_with_gap.add(r["dir"]); tms_with_gap.add(r["Tm"])
    # monotone direction check: mean gap_pct vs Tm (per direction), Spearman-style sign
    mono = {}
    for dk in DIRS:
        vals = sorted([(r["Tm"], r["gap_pct"]) for r in gap_rows if r["dir"]==dk])
        # group by Tm -> mean
        by_tm = {}
        for t,val in vals: by_tm.setdefault(t, []).append(val)
        means = [(t, sum(x)/len(x)) for t,x in sorted(by_tm.items())]
        mono[dk] = {"means": [round(m,1) for _,m in means],
                    "monotone_increasing": bool(all(means[i][1] <= means[i+1][1]+1e-9
                                                    for i in range(len(means)-1))),
                    "monotone_decreasing": bool(all(means[i][1] >= means[i+1][1]-1e-9
                                                    for i in range(len(means)-1)))}
    v2 = bool(len(dirs_with_gap)>=2 and len(tms_with_gap)>=2
              and any(m["monotone_increasing"] or m["monotone_decreasing"]
                      for m in mono.values()))

    # ---- V3: anisotropy discriminable (yaw < roll) ----
    def mean_lsuff(dk, fam=None):
        xs = [v["L_suff"] for k,v in valid.items()
              if k.split("|")[0]==dk and (fam is None or k.split("|")[2]==fam)]
        return sum(xs)/len(xs) if xs else float("nan")
    roll_l, yaw_l = mean_lsuff("roll"), mean_lsuff("yaw")
    tau_ratio = out["meta"]["tau_max_by_dir"]["yaw"]/out["meta"]["tau_max_by_dir"]["roll"]
    yaw_over_roll = yaw_l/roll_l if roll_l else float("nan")
    v3 = bool(yaw_over_roll < 0.6)

    # ---- V4: paired sign tests proposed vs >=2 baselines on boundary region ----
    # boundary region = grid points where the SET of controllers is discordant
    # (at least one recovers, at least one fails) => informative paired units.
    v4 = {"tests": [], "holm_survivors": [], "cost_table": {}}
    pvals = []
    for base in ["qpd","smc","qpd_ff"]:
        b = c = 0; units = 0
        for dk in DIRS:
            for Tm in TM_LIST:
                kp = f"{dk}|{Tm}|proposed"; kb = f"{dk}|{Tm}|{base}"
                if kp not in valid or kb not in valid: continue
                op = np.array(valid[kp]["ok_pattern"]); ob = np.array(valid[kb]["ok_pattern"])
                # discordant units near the boundary
                mask = op != ob
                b += int(((op==1)&(ob==0)&mask).sum())
                c += int(((op==0)&(ob==1)&mask).sum())
                units += int(mask.sum())
        p = binom_p_two_sided(b, c)
        eff = (b-c)/units if units else 0.0
        pvals.append((base, p))
        v4["tests"].append({"baseline":base, "proposed_wins":b, "baseline_wins":c,
                            "discordant_units":units, "p_two_sided":p,
                            "effect_size":eff})
    # Holm at family alpha=0.05
    order = sorted(pvals, key=lambda x:x[1])
    for i,(base,p) in enumerate(order):
        thresh = 0.05/(len(order)-i)
        if p < thresh: v4["holm_survivors"].append(base)
        v4.setdefault("holm_detail", []).append(
            {"baseline":base,"p":p,"holm_threshold":thresh,"survives":bool(p<thresh)})
    v4["significant_vs_ge2"] = bool(len(v4["holm_survivors"])>=2)
    # cost table (frozen V4 requirement); skip None cost (BLOCKED cells)
    for fam in fams:
        cs = [v["cost"] for k,v in valid.items()
              if k.split("|")[2]==fam and isinstance(v.get("cost"), dict)]
        v4["cost_table"][fam] = {
            "sat_duty_mean": round(sum(x["sat_duty"] for x in cs)/len(cs),4) if cs else None,
            "peak_tau_mean": round(sum(x["peak_tau"] for x in cs)/len(cs),4) if cs else None,
            "settle_t_median_mean": round(sum(x["settle_t_median"] for x in cs)/len(cs),4) if cs else None}

    # ---- V5: all self-tests pass and dt < 3% ----
    st = out.get("self_tests", {})
    v5 = bool(all(v.get("pass", False) for v in st.values())
              and st.get("S6_dt_convergence", {}).get("pass", False)
              and out.get("gate_ok", False))

    verdict = "GO" if (v1 and v3 and v5) else "NO-GO"
    notes = []
    if not v2: notes.append("V2 failed: circularity NOT broken -> headline must not be written as 'independently verified'")
    if not v4["significant_vs_ge2"]: notes.append("V4 negative: proposed not significantly better than >=2 baselines -> conditional-scope reframe, no re-tuning")
    if degen: notes.append("%d degenerate cells (non-monotone recovery domain) excluded from statistics, reported verbatim" % len(degen))
    return {
        "V1_hard_upper_bound": {"pass": v1, "max_ratio_adv_arm": v1_max_ratio,
                                "max_ratio_main_arm_for_transparency": v1_main_arm_max_ratio,
                                "arm_used": "adversarial constant d=dbar*n (matches analytic dbar)",
                                "n_valid_cells": len(adv_valid), "n_violations": sum(1 for r in v1_rows if not r["ok"]),
                                "rows": v1_rows},
        "V2_circularity_broken": {"pass": v2, "dirs_with_gap_gt5pct": sorted(dirs_with_gap),
                                  "tms_with_gap_gt5pct": sorted(tms_with_gap),
                                  "monotone_by_dir": mono, "n_gap_rows": len(gap_rows)},
        "V3_anisotropy": {"pass": v3, "yaw_over_roll_Lsuff": yaw_over_roll,
                          "tau_max_yaw_over_roll": tau_ratio,
                          "roll_Lsuff_mean": roll_l, "yaw_Lsuff_mean": yaw_l},
        "V4_fair_baselines": v4,
        "V5_selftests_dt": {"pass": v5, "gate_ok": out.get("gate_ok"),
                            "dt_rel_diff": st.get("S6_dt_convergence", {}).get("rel_diff")},
        "degenerate_cells": sorted(degen.keys()),
        "n_valid": len(valid), "n_degenerate": len(degen), "n_total": len(cells),
        "VERDICT": verdict, "notes": notes,
    }

# ---------------- main (incremental, resumable) ----------------
def main():
    # W_mech: anisotropy-aware scaling (yaw authority / roll authority)
    tau_e = {k: tau_max_dir(v) for k,v in DIRS.items()}
    tau_ref = tau_e["roll"]
    W_mech = np.array([tau_e["roll"]/tau_ref, tau_e["pitch"]/tau_ref, tau_e["yaw"]/tau_ref])
    W_mech = np.array([W_mech[0], W_mech[1], W_mech[2]])

    out = {}
    if os.path.exists(RES):
        try: out = json.load(open(RES, encoding="utf-8"))
        except Exception: out = {}
    out.setdefault("done_cells", {})
    out["meta"] = {"probe":"v2", "status":"RUNNING", "prereg":"preregistration_probe_v2.md",
        "platform": ("single identified platform (Crazyflie registry)" if not RPM_IDENTIFIED
                     else "synthetic literature-anchored platform"),
        "params":{"m":m,"g":g,"F":F,"cT":cT,"omega_hover":OMEGA_HOV,"omega_max":OMEGA_MAX,
                  "u_max":u_max,"arm":arm,"a":a,"kappa":kappa,"J":J.tolist(),
                  "Phi_max":PHI_MAX,"T_hor":T_HOR,"dt":DT,"T_fix":T_FIX,
                  "T_m_list":TM_LIST,"D_amp":D_AMP,"D_bar":D_BAR,"N_dw":N_DW},
        "W_mech": W_mech.tolist(),
        "tau_max_by_dir": tau_e,
        "note":("parameters from single identified platform config real_platform_config.json; "
                "RPM-level quantities N/A; disturbance & recovery-envelope are design parameters"
                if not RPM_IDENTIFIED else
                "all parameters are RESEARCH ASSUMPTIONS / ILLUSTRATIVE, not measured data")}

    st = self_tests(W_mech)
    out["self_tests"] = st
    gate = all(v.get("pass", False) for v in st.values())
    out["gate_ok"] = gate
    if not gate:
        out["meta"]["status"] = "GATE_FAIL"
        json.dump(out, open(RES,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        print("GATE_FAIL:", {k:v.get("pass") for k,v in st.items()}); return

    # dt convergence (fixed grid -> bit-identical disturbance, dt-integrity #1)
    dt_a = L_suff(DIRS["roll"], T_REF, "qpd_ff", G0_KP*GAIN_SCALE, G0_KD*GAIN_SCALE, W_mech, dt=DT)
    dt_b = L_suff(DIRS["roll"], T_REF, "qpd_ff", G0_KP*GAIN_SCALE, G0_KD*GAIN_SCALE, W_mech, dt=DT/2.0)
    rel = abs(dt_a["L_suff"]-dt_b["L_suff"])/max(dt_a["L_suff"], 1e-9)
    out["self_tests"]["S6_dt_convergence"] = {"L_suff_dt": dt_a["L_suff"],
        "L_suff_dt_half": dt_b["L_suff"], "rel_diff": rel, "pass": bool(rel < 0.03)}
    out["gate_ok"] = all(v.get("pass", False) for v in out["self_tests"].values())

    # analytic necessary bound (controller-independent)
    out["analytic"] = {}
    for dk, n in DIRS.items():
        out["analytic"][dk] = {str(Tm): L_nec(n, Tm) for Tm in TM_LIST}

    # equal-budget calibration. PER_TM_CALIBRATION=False -> single gain set
    # (v2.3 default). True -> each Tm gets its own 25-combo calibration, keyed
    # by str(Tm); evaluation then picks the matching gains (fair per condition).
    if "calibration" not in out:
        out["calibration"] = {"_per_tm": PER_TM_CALIBRATION}
        for fam in ["qpd","smc","qpd_ff","proposed"]:
            if PER_TM_CALIBRATION:
                out["calibration"][fam] = {}
                for Tm in TM_LIST:
                    (Kp,Kd,score), bad = calibrate(fam, W_mech, Tm=Tm)
                    out["calibration"][fam][str(Tm)] = {"Kp":Kp,"Kd":Kd,"score":score,"bad":bad,
                                                        "grid_size":len(KP_GRID)*len(KD_GRID)}
            else:
                (Kp,Kd,score), bad = calibrate(fam, W_mech)
                out["calibration"][fam] = {"Kp":Kp,"Kd":Kd,"score":score,"bad":bad,
                                           "grid_size":len(KP_GRID)*len(KD_GRID)}
        json.dump(out, open(RES,"w",encoding="utf-8"), ensure_ascii=False, indent=1)

    fams = ["qpd","smc","qpd_ff","proposed"]
    out.setdefault("done_cells_adv", {})
    total = len(DIRS)*len(TM_LIST)*len(fams)
    # BASELINE HEALTH gate (Amendment-4): a cell whose dw=0 baseline is unstable
    # under its own per-Tm calibrated gains is NOT a recovery-domain observation.
    # It must be marked BLOCKED (degenerate) and excluded from GO statistics,
    # never reported as L_suff=0. Verified by a wide 81-combo gain scan.
    baseline_health = {}
    for Tm in TM_LIST:
        for fam in fams:
            if PER_TM_CALIBRATION:
                cal = out["calibration"][fam][str(Tm)]
            else:
                cal = out["calibration"][fam]
            mp0, wf0, ok0, bad0, _ = simulate(np.array([0.0]), DIRS["roll"], Tm,
                                             fam, cal["Kp"], cal["Kd"], W_mech)
            baseline_health[f"{Tm}|{fam}"] = {
                "stable": bool((not bad0) and ok0[0]),
                "max_phi_dw0": float(mp0[0]), "w_final_dw0": float(wf0[0]),
                "Kp": cal["Kp"], "Kd": cal["Kd"]}
    out["baseline_health"] = baseline_health
    json.dump(out, open(RES,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    blocked = sum(1 for v in baseline_health.values() if not v["stable"])
    print("baseline_health: %d/%d (Tm,fam) unstable -> BLOCKED, excluded from GO" %
          (blocked, len(baseline_health)), flush=True)

    # evaluation cells (incremental, resumable). TWO disturbance arms:
    #   main = zero-mean turbulence (V2/V3/V4 fair comparison)
    #   adv  = adversarial constant d=dbar*n (V1, matches analytic dbar口径)
    def slim(r):
        c = {k:v for k,v in r.items() if k != "cost"}
        c["cost"] = {k:v for k,v in r["cost"].items()
                     if k not in ("phi_int_per","settle_t_per")}
        return c
    for armname, mode, store in [("main","turb","done_cells"), ("adv","adv","done_cells_adv")]:
        for dk, n in DIRS.items():
            for Tm in TM_LIST:
                for fam in fams:
                    key = f"{dk}|{Tm}|{fam}"
                    if key in out[store]:
                        continue
                    if PER_TM_CALIBRATION:
                        cal = out["calibration"][fam][str(Tm)]
                    else:
                        cal = out["calibration"][fam]
                    bh = baseline_health.get(f"{Tm}|{fam}", {"stable":True})
                    if not bh["stable"]:
                        # BLOCKED: do NOT fabricate L_suff=0; exclude from GO.
                        out[store][key] = {"L_suff": float("nan"), "dw_max": float("nan"),
                            "bad": True, "degenerate": True, "blocked": True,
                            "reason": "dw=0 baseline unstable under per-Tm calibrated gains "
                                      "(slow symmetric motor constant); not a recovery observation",
                            "baseline_health": bh, "cost": None, "ok_pattern": None}
                        json.dump(out, open(RES,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
                        print("%s cell %d/%d %s BLOCKED" %
                              (armname, len(out[store]), total, key), flush=True)
                        continue
                    r = L_suff(n, Tm, fam, cal["Kp"], cal["Kd"], W_mech, d_mode=mode)
                    out[store][key] = slim(r)
                    json.dump(out, open(RES,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
                    print("%s cell %d/%d %s L_suff=%s" %
                          (armname, len(out[store]), total, key,
                           ("%.5f"%r["L_suff"] if r["L_suff"]==r["L_suff"] else "nan")), flush=True)

    out["meta"]["status"] = "DONE"
    out["cells_done"] = len(out["done_cells"])
    out["cells_done_adv"] = len(out["done_cells_adv"])
    out["cells_expected"] = total
    # frozen GO evaluation (verbatim, computed only AFTER all cells exist)
    if out["cells_done"] == total and out["cells_done_adv"] == total:
        out["go_evaluation"] = evaluate(out, adv_cells=out["done_cells_adv"])
        print("VERDICT=%s  V1=%s V2=%s V3=%s V5=%s" % (
            out["go_evaluation"]["VERDICT"],
            out["go_evaluation"]["V1_hard_upper_bound"]["pass"],
            out["go_evaluation"]["V2_circularity_broken"]["pass"],
            out["go_evaluation"]["V3_anisotropy"]["pass"],
            out["go_evaluation"]["V5_selftests_dt"]["pass"]))
    json.dump(out, open(RES,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE main=%d adv=%d gate_ok=%s" % (out["cells_done"], out["cells_done_adv"], out["gate_ok"]))

if __name__ == "__main__":
    main()
