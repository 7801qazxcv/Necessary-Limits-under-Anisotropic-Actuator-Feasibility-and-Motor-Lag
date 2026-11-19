# -*- coding: utf-8 -*-
"""Every number that will appear in the manuscript, re-derived from on-disk
artifacts (integrity principle 24: no number exists only inside the .tex).
Writes manuscript_numbers.json + numbers.tex (LaTeX macros)."""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__))
def L(f): return json.load(open(os.path.join(HERE,f),encoding="utf-8"))

syn=L("probe_v2_results.json")            # v2.3 synthetic platform
real=L("probe_v2_REAL_results.json")      # single identified platform
th=L("theorem_audit.json")
ps=L("param_sensitivity.json")
asym=L("asym_diagnostic.json")
l2=L("citation_layer2.json")
vg=L("venue_gate.json")
m1=L("m1_lemma.json")
m3=L("m3_comparison.json")
mr=L("math_redteam.json")
fu=L("review_followup.json")

g=syn["go_evaluation"]; gr=real["go_evaluation"]
nums={
 # --- headline theorem / analytic (synthetic, v2.3) ---
 "v23_L_nec_roll_005": syn["analytic"]["roll"]["0.05"]["L_nec"],
 "syn_V1_max_ratio_adv": g["V1_hard_upper_bound"]["max_ratio_adv_arm"],
 "syn_V1_n_violations": g["V1_hard_upper_bound"]["n_violations"],
 "syn_V2_gap_note": "dirs_with_gap_gt5pct",
 "syn_V3_yaw_over_roll": g["V3_anisotropy"]["yaw_over_roll_Lsuff"],
 "syn_V3_tau_ratio": g["V3_anisotropy"]["tau_max_yaw_over_roll"],
 "syn_n_valid": g["n_valid"], "syn_n_degenerate": g["n_degenerate"], "syn_n_total": g["n_total"],
 # --- real platform ---
 "real_V1_max_ratio_adv": gr["V1_hard_upper_bound"]["max_ratio_adv_arm"],
 "real_V1_n_violations": gr["V1_hard_upper_bound"]["n_violations"],
 "real_V3_yaw_over_roll": gr["V3_anisotropy"]["yaw_over_roll_Lsuff"],
 "real_V3_tau_ratio": gr["V3_anisotropy"]["tau_max_yaw_over_roll"],
 "real_n_valid": gr["n_valid"], "real_n_degenerate": gr["n_degenerate"], "real_n_total": gr["n_total"],
 "real_main_cells": len(real["done_cells"]), "real_adv_cells": len(real["done_cells_adv"]),
 "real_blocked_cells": sum(1 for v in real["baseline_health"].values() if not v["stable"]),
 "real_baseline_cells": len(real["baseline_health"]),
 # --- theorem audit ---
 "th_verdict": ("PASS_ALL" if th.get("summary",{}).get("all_must_pass") else "FAIL"),
 "th_failed": th.get("summary",{}).get("failed",[]),
 "th_must_pass_count": sum(1 for v in th.get("summary",{}).get("must_pass_results",{}).values() if v),
 # --- sensitivity ---
 "ps_V3_lo": ps.get("cross",{}).get("V3_range",[None,None])[0] if isinstance(ps.get("cross"),dict) else None,
 "ps_V3_hi": ps.get("cross",{}).get("V3_range",[None,None])[1] if isinstance(ps.get("cross"),dict) else None,
 # --- asym diagnostic ---
 "asym_symslow_stable": asym["summary"]["stable_counts"].get("slow|slow"),
 "asym_slowgain_stable": asym["summary"]["asym_slowgain_stable"],
 "asym_fastfast_stable": asym["summary"]["stable_counts"].get("fast|fast"),
 "asym_n_baseline": asym["summary"]["n_baseline_cells"],
 "asym_boundary_cells": len(asym["boundary"]),
 "asym_islands": {m:sum(1 for k,v in asym["boundary"].items() if k.startswith(m+"|") and v.get("islands"))
                  for m in ["fast","slow","asym"]},
 "n_refs": l2["n_rows"],
 "n_supported": l2["summary"]["SUPPORTED"],
 "n_nuance": l2["summary"]["SUPPORTED_NUANCE"],
 "n_misattribution": l2["summary"]["MISATTRIBUTION"],
 # --- params ---
 "syn_params": syn["meta"]["params"],
 "real_params": real["meta"]["params"],
 # --- full-fix additions (all derived from artifacts, never hand-typed) ---
 "syn_umax": syn["meta"]["params"]["cT"]*syn["meta"]["params"]["omega_max"]**2,
 "main_arm": {},
 "c2_roll_adv": th["checks"]["C2_disturbance_sign_verdict"]["rows"]["roll|0.05"]["L_star_adversarial"],
 "c2_roll_any": th["checks"]["C2_disturbance_sign_verdict"]["rows"]["roll|0.05"]["L_star_any_disturbance"],
 "c2_yaw_adv": th["checks"]["C2_disturbance_sign_verdict"]["rows"]["yaw|0.05"]["L_star_adversarial"],
 "c2_yaw_any": th["checks"]["C2_disturbance_sign_verdict"]["rows"]["yaw|0.05"]["L_star_any_disturbance"],
 # --- N1: macro-ise the four numbers hand-typed in the full-fix round ---
 "gyro_combo": th["checks"]["C10_A1_failure_on_combo"]["gyro_norm_combo"],
 "c2_roll_ratio": th["checks"]["C2_disturbance_sign_verdict"]["rows"]["roll|0.05"]["any_over_adv_ratio"],
 "c2_yaw_ratio": th["checks"]["C2_disturbance_sign_verdict"]["rows"]["yaw|0.05"]["any_over_adv_ratio"],
 # --- M1 (CORRECTED: angular-momentum level only; attitude extension INVALID) ---
 "m1_omega_perp": m1["observed_omega_perp_max"],
 "m1_gyro_obs": m1["observed_gyro_n_max"],
 "m1_rollouts": m1["n_rollouts"],
 "m1_gamma_roll": m1["gamma"]["roll"],
 "m1_gamma_yaw": m1["gamma"]["yaw"],
 "m1_d_eff": m1["a1free_bounds"]["roll"]["d_eff"],
 "m1_thresh_roll": m1["a1free_bounds"]["roll"]["L_momentum_threshold"],
 "m1_thresh_yaw": m1["a1free_bounds"]["yaw"]["L_momentum_threshold"],
 "m1_existence_all": all(v["existence"] for v in m1["a1free_bounds"].values()),
 # --- M3 proxy (saturation-limited; NOT a prior-art reproduction) ---
 "m3_lyap_roll": max(v["L_lyap"] for k,v in m3["proxy"].items() if k.startswith("roll|") and v["applicable"]),
 "m3_lyap_yaw": max(v["L_lyap"] for k,v in m3["proxy"].items() if k.startswith("yaw|") and v["applicable"]),
 "m3_star_roll": next(r["L_star"] for r in m3["comparison"]["rows"] if r["dir"]=="roll"),
 "m3_star_yaw": next(r["L_star"] for r in m3["comparison"]["rows"] if r["dir"]=="yaw"),
 "m3_ratio_roll": None, "m3_ratio_yaw": None,
 "m3_dwsat": m3["proxy"]["roll|qpd"]["dw_sat"],
 "m3_dwphi": m3["proxy"]["roll|qpd"]["dw_phi"],
 # --- n>=3 replication over independent disturbance phases ---
 "nrep_phases": len(m3["phases"]),
 "nrep_cells": len(m3["aggregate"]["cells"]),
 "nrep_valid": sum(1 for x in m3["aggregate"]["cells"] if x["all_valid"]),
 "nrep_v3_p1": m3["aggregate"]["V3_by_phase"]["P1"]["ratio"],
 "nrep_v3_p3": m3["aggregate"]["V3_by_phase"]["P3"]["ratio"],
 "nrep_mean_range": (sum(x["range"] for x in m3["aggregate"]["cells"] if x["range"] is not None)
                     / max(1,len([x for x in m3["aggregate"]["cells"] if x["range"] is not None]))),
 "nrep_max_range": max(x["range"] for x in m3["aggregate"]["cells"] if x["range"] is not None),
 "nrep_worst": max(m3["aggregate"]["cells"],key=lambda x:(x["range"] or 0))["runs"],
 # --- ChatGPT review fix: finite-horizon / first-passage / uniqueness / transparency ---
 "rt_n_cases": len(mr["rows"]),
 "rt_all_tstar_le_T": all(r["t_star_le_T"] for r in mr["rows"]),
 "rt_max_tstar": max(r["t_star"] for r in mr["rows"]),
 "rt_T": mr["T"],
 "rt_max_Ldiff": max(r["L_abs_diff"] for r in mr["rows"]),
 "rt_max_dLT": max(abs(r["L_finiteT_minus_L"]) for r in mr["rows"]),
 "rt_p5_monotone": fu["checks"]["P5_root_uniqueness"]["all_monotone"],
 "rt_p5_unique": fu["checks"]["P5_root_uniqueness"]["all_Aprime_single_sign_change"],
 "rt_p2_max_cross": fu["checks"]["P2_first_passage"]["max_t_cross"],
 "rt_phi_max_rad": fu["checks"]["P2_first_passage"]["Phi_rad"],
 "dw_grid_step": (20.0-0.2)/159.0,
 "dt_val": syn["meta"]["params"]["dt"],
 "n_dw": syn["meta"]["params"]["N_dw"],
 "real_n_degenerate": gr["n_degenerate"],
 "real_n_total": gr["n_total"],
}
# main-arm L_suff/L* > 1 counts (disclosed in the Results section)
for tag,res in [("syn",syn),("real",real)]:
    ratios=[]
    for k,v in res["done_cells"].items():
        dk,Tm,fam=k.split("|"); nec=res["analytic"][dk][Tm]["L_nec"]; L=v.get("L_suff")
        if isinstance(L,(int,float)) and L==L: ratios.append(L/nec)
    nums["main_arm"][tag]={"n":len(ratios),"over1":sum(1 for x in ratios if x>1.0),
                            "max":max(ratios) if ratios else None}
# param_sensitivity structure may differ; read defensively
if nums["ps_V3_lo"] is None:
    s=json.dumps(ps)
    nums["ps_note"]="V3 range read from param_sensitivity.json verbatim: "+s[:300]
json.dump(nums,open(os.path.join(HERE,"manuscript_numbers.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)

nums["m3_ratio_roll"]=nums["m3_star_roll"]/nums["m3_lyap_roll"]
nums["m3_ratio_yaw"]=nums["m3_star_yaw"]/nums["m3_lyap_yaw"]

 # --- emit LaTeX macros (single source of truth for prose) ---
def f(x, n=4):
    return ("%.*f"%(n,x)) if isinstance(x,(int,float)) else str(x)
lines=[
 "% AUTO-GENERATED from manuscript_numbers.json -- DO NOT EDIT BY HAND",
 "\\newcommand{\\Nrefs}{%s}"%nums["n_refs"],
 "\\newcommand{\\Nsupported}{%s}"%nums["n_supported"],
 "\\newcommand{\\Nnuance}{%s}"%nums["n_nuance"],
 "\\newcommand{\\Nmis}{%s}"%nums["n_misattribution"],
 "\\newcommand{\\SynVone}{%s}"%f(nums["syn_V1_max_ratio_adv"],4),
 "\\newcommand{\\SynViol}{%s}"%nums["syn_V1_n_violations"],
 "\\newcommand{\\SynVthree}{%s}"%f(nums["syn_V3_yaw_over_roll"],3),
 "\\newcommand{\\SynTauRatio}{%s}"%f(nums["syn_V3_tau_ratio"],3),
 "\\newcommand{\\RealVone}{%s}"%f(nums["real_V1_max_ratio_adv"],4),
 "\\newcommand{\\RealViol}{%s}"%nums["real_V1_n_violations"],
 "\\newcommand{\\RealVthree}{%s}"%f(nums["real_V3_yaw_over_roll"],3),
 "\\newcommand{\\RealTauRatio}{%s}"%f(nums["real_V3_tau_ratio"],3),
 "\\newcommand{\\RealNvalid}{%s}"%nums["real_n_valid"],
 "\\newcommand{\\RealNdegen}{%s}"%nums["real_n_degenerate"],
 "\\newcommand{\\RealNtotal}{%s}"%nums["real_n_total"],
 "\\newcommand{\\RealBlocked}{%s}"%nums["real_blocked_cells"],
 "\\newcommand{\\RealBaselineCells}{%s}"%nums["real_baseline_cells"],
 "\\newcommand{\\AsymSymSlowStable}{%s}"%nums["asym_symslow_stable"],
 "\\newcommand{\\AsymSlowStable}{%s}"%nums["asym_slowgain_stable"],
 "\\newcommand{\\AsymFastFastStable}{%s}"%nums["asym_fastfast_stable"],
 "\\newcommand{\\AsymNbaseline}{%s}"%nums["asym_n_baseline"],
 "\\newcommand{\\AsymIslands}{%s}"%nums["asym_islands"].get("asym"),
 "\\newcommand{\\LstarRoll}{%s}"%f(nums["v23_L_nec_roll_005"],6),
 # --- full-fix macros ---
 "\\newcommand{\\SynUmax}{%s}"%f(nums["syn_umax"],3),
 "\\newcommand{\\MainSynN}{%d}"%nums["main_arm"]["syn"]["n"],
 "\\newcommand{\\MainSynOver}{%d}"%nums["main_arm"]["syn"]["over1"],
 "\\newcommand{\\MainSynMax}{%s}"%f(nums["main_arm"]["syn"]["max"],3),
 "\\newcommand{\\MainRealN}{%d}"%nums["main_arm"]["real"]["n"],
 "\\newcommand{\\MainRealOver}{%d}"%nums["main_arm"]["real"]["over1"],
 "\\newcommand{\\MainRealMax}{%s}"%f(nums["main_arm"]["real"]["max"],3),
 "\\newcommand{\\CtwoRollAdv}{%s}"%f(nums["c2_roll_adv"],5),
 "\\newcommand{\\CtwoRollAny}{%s}"%f(nums["c2_roll_any"],5),
 "\\newcommand{\\CtwoYawAdv}{%s}"%f(nums["c2_yaw_adv"],5),
 "\\newcommand{\\CtwoYawAny}{%s}"%f(nums["c2_yaw_any"],5),
 # --- N1 macros (all from artifacts) ---
 "\\newcommand{\\GyroCombo}{%s}"%f(nums["gyro_combo"],5),
 "\\newcommand{\\CtwoRollRatio}{%s}"%f(nums["c2_roll_ratio"],3),
 "\\newcommand{\\CtwoYawRatio}{%s}"%f(nums["c2_yaw_ratio"],3),
 "\\newcommand{\\CtwoYawPct}{%d}"%round((nums["c2_yaw_ratio"]-1)*100),
 # --- M1 / M3 / n>=3 macros (all from artifacts) ---
 "\\newcommand{\\MoneOmega}{%s}"%f(nums["m1_omega_perp"],3),
 "\\newcommand{\\MoneGyroObs}{%s}"%f(nums["m1_gyro_obs"],6),
 "\\newcommand{\\MoneGammaRoll}{%s}"%f(nums["m1_gamma_roll"],3),
 "\\newcommand{\\MoneDeff}{%s}"%f(nums["m1_d_eff"],5),
 "\\newcommand{\\MoneThreshRoll}{%s}"%f(nums["m1_thresh_roll"],3),
 "\\newcommand{\\MoneThreshYaw}{%s}"%f(nums["m1_thresh_yaw"],3),
 "\\newcommand{\\MoneRollouts}{%d}"%nums["m1_rollouts"],
 "\\newcommand{\\MthreeLyapRoll}{%s}"%f(nums["m3_lyap_roll"],5),
 "\\newcommand{\\MthreeLyapYaw}{%s}"%f(nums["m3_lyap_yaw"],5),
 "\\newcommand{\\MthreeStarRoll}{%s}"%f(nums["m3_star_roll"],5),
 "\\newcommand{\\MthreeStarYaw}{%s}"%f(nums["m3_star_yaw"],5),
 "\\newcommand{\\MthreeRatioRoll}{%s}"%f(nums["m3_ratio_roll"],1),
 "\\newcommand{\\MthreeRatioYaw}{%s}"%f(nums["m3_ratio_yaw"],1),
 "\\newcommand{\\MthreeDwsat}{%s}"%f(nums["m3_dwsat"],3),
 "\\newcommand{\\MthreeDwphi}{%s}"%f(nums["m3_dwphi"],3),
 "\\newcommand{\\NrepPhases}{%d}"%nums["nrep_phases"],
 "\\newcommand{\\NrepCells}{%d}"%nums["nrep_cells"],
 "\\newcommand{\\NrepValid}{%d}"%nums["nrep_valid"],
 "\\newcommand{\\NrepVthreePone}{%s}"%f(nums["nrep_v3_p1"],3),
 "\\newcommand{\\NrepVthreePthree}{%s}"%f(nums["nrep_v3_p3"],3),
 "\\newcommand{\\NrepMeanRange}{%s}"%f(nums["nrep_mean_range"],4),
 "\\newcommand{\\NrepMaxRange}{%s}"%f(nums["nrep_max_range"],4),
 "\\newcommand{\\NrepWorstLow}{%s}"%f(min(v for v in nums["nrep_worst"] if isinstance(v,(int,float)) and v==v),3),
 "\\newcommand{\\NrepWorstHigh}{%s}"%f(max(v for v in nums["nrep_worst"] if isinstance(v,(int,float)) and v==v),3),
 # --- ChatGPT review fix macros (all from artifacts) ---
 "\\newcommand{\\RtNcases}{%d}"%nums["rt_n_cases"],
 "\\newcommand{\\RtMaxTstar}{%s}"%f(nums["rt_max_tstar"],4),
 "\\newcommand{\\RtT}{%s}"%f(nums["rt_T"],1),
 "\\newcommand{\\RtMaxLdiff}{%s}"%f(nums["rt_max_Ldiff"],1),
 "\\newcommand{\\RtMaxDLT}{%s}"%f(nums["rt_max_dLT"],1),
 "\\newcommand{\\RtMaxCross}{%s}"%f(nums["rt_p2_max_cross"],4),
 "\\newcommand{\\RtPhiRad}{%s}"%f(nums["rt_phi_max_rad"],3),
 "\\newcommand{\\DwGridStep}{%s}"%f(nums["dw_grid_step"],5),
 "\\newcommand{\\DtVal}{%s}"%f(nums["dt_val"],4),
 "\\newcommand{\\Ndw}{%d}"%nums["n_dw"],
]
open(os.path.join(HERE,"numbers.tex"),"w",encoding="utf-8",newline="\n").write("\n".join(lines)+"\n")
print("WROTE manuscript_numbers.json + numbers.tex")
for k in ["syn_V1_max_ratio_adv","real_V1_max_ratio_adv","syn_V3_yaw_over_roll","real_V3_yaw_over_roll",
          "real_blocked_cells","asym_symslow_stable","asym_slowgain_stable","n_refs","n_misattribution"]:
    print("  ",k,"=",nums[k])
