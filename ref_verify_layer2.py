# -*- coding: utf-8 -*-
"""Task 2 / Layer 2: citation-content audit (claim vs SOURCE title+abstract).
Real metadata is INJECTED from ref_meta_raw.json (live Crossref/arXiv), never
retyped. Each row carries the sentence we intend to write, a manual P1-P8
verdict and the reason. Writes citation_layer2.json (re-checkable artifact)."""
import json, os, textwrap
HERE=os.path.dirname(os.path.abspath(__file__))
raw=json.load(open(os.path.join(HERE,"ref_meta_raw.json"),encoding="utf-8"))

# key -> intended attribution claim (what our Related Work sentence will assert)
# plus the P-flag we pre-screen for. Verdict is MANUAL, judged against the abstract.
CLAIMS = {
 # ---- Stream A: finite/fixed-time attitude control with saturation & disturbances ----
 "10.3390/app14093639": dict(stream="A", claim="Finite-time attitude control combined with a finite-time disturbance observer and an anti-saturation auxiliary system has been demonstrated in simulation.", p="P3", verdict="SUPPORTED", note="Abstract: NDI + FT disturbance observer + anti-saturation auxiliary, Simulink simulation. Pure simulation, no impulse, no recoverability bound."),
 "10.1016/j.isatra.2025.08.030": dict(stream="A", claim="Fixed-time anti-saturation fault-tolerant control with event-triggered adaptive barrier sliding mode addresses faults, saturation and disturbances.", p="P9", verdict="SUPPORTED_NUANCE", note="Crossref has NO abstract; publisher (ScienceDirect) abstract fragment in prior_art_scan confirms ABNFTSMC with faults/saturation/disturbances. Mark abstract_source=publisher."),
 "10.1155/2020/5493686": dict(stream="A", claim="Finite-time output-feedback attitude control with saturation suppression and fuzzy lumped-disturbance compensation exists (2020).", p="P3", verdict="SUPPORTED", note="Abstract: nonsingular terminal SMMC + fuzzy adaptive + saturation suppression, finite-time tracking, simulation. No impulse/state-jump."),
 "10.1007/s12555-024-0402-6": dict(stream="A", claim="Adaptive finite-time control with ASYMMETRIC input saturation has been studied for quadrotors.", p="P9", verdict="SUPPORTED_NUANCE", note="Crossref NO abstract; title confirms asymmetric input saturation. Note: 'asymmetric saturation' is NOT the same as the asymmetric rising/falling motor time constants in our real-platform config."),
 # ---- Stream B: quadrotor upset / collision recovery (empirical) ----
 "2002.09425": dict(stream="B", claim="Quadrotor recovery from arbitrary large initial attitude/angular-rate conditions has been validated with Monte-Carlo AND real flight tests.", p="P3", verdict="SUPPORTED", note="Abstract + ICRA DOI 10.1109/ICRA40945.2020.9197239: fault-tolerant recovery from COMPLETE ROTOR FAILURE; real flight tests. Disturbance is actuator loss, NOT external angular impulse; guarantee is controller-dependent sufficiency, no controller-independent non-recoverability bound."),
 "2610.15867": dict(stream="B", claim="Autonomous post-collision recovery has hardware evidence (47 real collisions, 19/22 wall-impact recovery).", p="P3", verdict="SUPPORTED", note="Abstract: on-board RL reflex, hardware experiments. Learning-based controller; no analytic recovery boundary; soft collision-resilient airframe."),
 "2603.14698": dict(stream="B", claim="Impulse reset maps on SE(3) with normal/tangential coupling have been modeled for collision recovery.", p="P9", verdict="SUPPORTED_NUANCE", note="Abstract: dual-quaternion impulse reset map, HIL + MuJoCo MC. This is a MORE complete impact model than our angular-impulse jump; cite as limitation evidence, not novelty."),
 # ---- Stream C: recoverable sets / ROA / invariant sets ----
 "10.2514/1.g001747": dict(stream="C", claim="Recoverable/safe sets for aircraft loss-of-control have been formally defined and published in a peer-reviewed journal.", p="P2", verdict="SUPPORTED", note="Crossref NO abstract, but title + the 2014 AIAA predecessor's nomenclature (safe set R_inf / recoverable set S) establish the concept. DOMAIN: large transport aircraft, linearized model, flight planning - NOT quadrotor, NOT impulsive jump, NOT actuator feasibility set."),
 "10.2514/6.2014-0786": dict(stream="C", claim="The recoverable-set concept originates in aircraft LOC literature (2014 AIAA conference predecessor).", p="P2", verdict="SUPPORTED", note="Nomenclature in prior_art_scan explicitly lists 'A safe set' and 'A recoverable set'. Conference predecessor of the 2017 JGCD paper."),
 "10.1002/rnc.70606": dict(stream="C", claim="Region-of-attraction enlargement under actuator saturation with Monte-Carlo verification of the estimated ROA has been done via SOS.", p="P5", verdict="SUPPORTED", note="Abstract: SOS + shape functions, enlarged ROA for polynomial systems under saturation/state constraints, MC verification. This is a CONTROLLER-DEPENDENT SUFFICIENT region; ours is a CONTROLLER-INDEPENDENT NECESSARY non-recoverability bound - complementary, not competing."),
 "2210.10868": dict(stream="C", claim="Explicit ellipsoidal basin-of-attraction estimates under input saturation exist in a hybrid-systems framework.", p="P5", verdict="SUPPORTED", note="Abstract: hybrid controller, regional exponential stability, explicit ellipsoidal basin estimates, SDP design. The state JUMP here is the controller state at measurement arrival, NOT an exogenous impact jump."),
 # ---- Stream D: impulsive / hybrid systems + saturation + safety ----
 "10.1016/j.nahs.2023.101335": dict(stream="D", claim="Exponential stabilization of nonlinear systems under saturated control WITH impulse correction has been published (NAHS 2023).", p="P1", verdict="SUPPORTED_NUANCE", note="CRITICAL DISTINCTION: 'impulse correction' is an impulsive CONTROL input used to stabilize, NOT an exogenous disturbance causing a state jump. Writing 'post-impulse recovery studied' would be P1 mischaracterisation. Correct gap: they design impulsive control; we bound recovery after an exogenous angular impulse."),
 "10.2139/ssrn.7536970": dict(stream="D", claim="A 2026 preprint studies finite-time stabilization via saturated control with finite impulsive regulation AND maximizes the estimated attraction domain.", p="P1", verdict="SUPPORTED_NUANCE", note="posted-content (SSRN preprint, NOT peer-reviewed); abstract confirms FTS + saturation + finite impulsive regulation + 'maximum estimation of the attraction domain'. Same Xiaodi Li group as NAHS 2023. Closest neighbour; must be cited as a preprint and distinguished (impulsive regulation vs exogenous jump; sufficient DOA vs controller-independent necessary bound)."),
 "2303.10243": dict(stream="D", claim="CBF/CLF theory has been extended to systems with impulsive actuators and dwell-time constraints, with forward-invariance conditions.", p="P2", verdict="SUPPORTED", note="Abstract: impulsive ACTUATORS (control-side jumps), spacecraft docking simulation. Domain is spacecraft, not quadrotor attitude recovery."),
 # ---- Stream E: actuator non-idealities including motor lag ----
 "10.1371/journal.pone.0360921": dict(stream="E", claim="Actuator non-idealities (motor lag, dead-zone, thrust saturation, partial motor-effectiveness loss) are modeled with UUB guarantees and a gain-matched ablation.", p="P3", verdict="SUPPORTED", note="Abstract explicitly lists motor lag/dead-zone/saturation/rotor drag/loss; UUB + asymptotic nominal; PID/SMC/ASMC/ablation baselines. Problem is attitude-altitude TRACKING, not post-impulse recovery; no controller-independent bound."),
 # ---- Method / parameter sources ----
 "2404.07837": dict(stream="P", claim="[9] First-order motor delay, inertia, thrust curve and torque coefficients are identifiable from proprioceptive flight data (MAP).", p="P5", verdict="SUPPORTED", note="Abstract: MAP-based identification of inertia, thrust curves, torque coefficients and first-order motor delay; ~1 min of flight data. Source of T_m=0.072s and K_tau."),
 "1508.04886": dict(stream="P", claim="[10] A low-cost quadcopter testbed with CIFER system identification supplies m, inertia and thrust/torque coefficients.", p="P5", verdict="SUPPORTED", note="Abstract: Arduino testbed, sweep data + CIFER ID. Rejected l=8.25 meters as unit error in earlier round."),
 # ---- additional coverage: the two ChatGPT-named papers + theory/LOC origins ----
 "10.1002/acs.3484": dict(stream="A", claim="Adaptive finite-time attitude tracking under actuator faults and external disturbances with prescribed performance has been studied (2022).", p="P9", verdict="SUPPORTED", note="Abstract: fast terminal SMC + prescribed performance + Nussbaum for passive fault handling; Lyapunov finite-time stability; numerical simulations. NOTE: abstract mentions NO input saturation - do not attribute anti-saturation to this paper."),
 "10.1109/TCSII.2020.3045769": dict(stream="A", claim="An anti-saturation finite-time attitude tracking observer for a quadrotor exists (2021).", p="P9", verdict="SUPPORTED_NUANCE", note="Crossref NO abstract; title supports anti-saturation + finite-time + observer. Published 2021 (NOT 2020 as ChatGPT draft claimed); vol 68(6) 2047-2051."),
 "10.1002/rnc.6001": dict(stream="A", claim="Adaptive fault-tolerant attitude control achieves PRACTICAL finite-time convergence (error to a residual set) under faults, input saturation and disturbances.", p="P5", verdict="SUPPORTED", note="Abstract: quaternion model, nonsingular terminal SMC, 'practical finite time ... converges to a small residual set' = UUB-type, NOT strict finite-time. Useful contrast for our theorem downgrade (memory: hard-flaw E)."),
 "1907.11673": dict(stream="D", claim="Strong iISS characterisation for time-varying impulsive systems is established Lyapunov/converse theory.", p="P8", verdict="SUPPORTED", note="Abstract: iISS = 0-GUAS + UBEBS remains valid for time-varying impulsive systems in the strong sense. Evidence that impulsive/hybrid stability theory is mature -> our 'hybrid modelling' is NOT itself novel."),
 "2603.18450": dict(stream="D", claim="Generalized backup CBFs construct controlled-invariant safe sets under input bounds with formal forward-invariance guarantees.", p="P5", verdict="SUPPORTED", note="Abstract: separates set-expanding vs backup controller, forward invariance, online adaptation with input bounds. Controlled-invariant (sufficient) set, not a controller-independent non-recoverability bound."),
 "10.2514/6.2013-5172": dict(stream="C", claim="Multi-mode upset recovery flight control (state machine reducing angular rates, restoring envelope) predates quadrotor recovery work.", p="P2", verdict="SUPPORTED_NUANCE", note="Crossref NO abstract; prior_art_scan publisher fragment confirms state-machine upset recovery for LARGE TRANSPORT AIRCRAFT. Domain differs from quadrotor."),
 "10.2514/6.2012-2429": dict(stream="C", claim="Aircraft stall recovery with explicit STATE and CONTROL constraints has been studied with nonlinear smooth regulators.", p="P2", verdict="SUPPORTED_NUANCE", note="Crossref NO abstract; prior_art_scan fragment confirms constrained stall recovery. Fixed-wing LOC domain, not quadrotor impulsive jump."),
}

def src(key):
    if key in raw["crossref"]:
        v=raw["crossref"][key]; return ("DOI", key, v)
    if key in raw["arxiv"]:
        v=raw["arxiv"][key]; return ("arXiv", key, v)
    return (None,None,None)

rows=[]
for key,c in CLAIMS.items():
    kind,ident,v=src(key)
    assert v is not None, "no live metadata for "+key
    rows.append({
        "key":key, "id_type":kind, "id":ident,
        "source_title":v.get("title"),
        "source_venue":v.get("venue"),
        "source_year":v.get("year"),
        "source_authors":v.get("authors"),
        "source_abstract":v.get("abstract") or None,
        "abstract_available": bool(v.get("abstract")),
        "our_claim":c["claim"], "stream":c["stream"],
        "p_flag_prescreen":c["p"], "manual_verdict":c["verdict"],
        "verdict_rationale":c["note"],
    })

out={
 "layer":2, "n_rows":len(rows),
 "red_flags_checked":["P1 mischaracterising prior work","P2 domain transplant","P3 method/experiment-type mismatch","P4 duplicate DOI","P5 over-strong attribution","P6 polarity flip","P7 right conclusion wrong key","P8 self-coined term","P9 no Crossref abstract -> publisher/arXiv needed"],
 "summary":{
   "SUPPORTED":sum(1 for r in rows if r["manual_verdict"]=="SUPPORTED"),
   "SUPPORTED_NUANCE":sum(1 for r in rows if r["manual_verdict"]=="SUPPORTED_NUANCE"),
   "MISATTRIBUTION":sum(1 for r in rows if r["manual_verdict"].startswith("MIS")),
   "preprints":["10.2139/ssrn.7536970"],
   "no_doi_requires_publisher_verification":["NASA_NTRS_20120014563"],
 },
 "rows":rows,
}
json.dump(out,open(os.path.join(HERE,"citation_layer2.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)

print("=== PAIRED TABLE: SOURCE SAYS  vs  WE CLAIM (Layer 2) ===")
for r in rows:
    print("\n[%s] %s (%s %s)"%(r["stream"],r["key"],r["id_type"],r["id"]))
    print("  SOURCE TITLE :",r["source_title"])
    print("  SOURCE ABS   :", (r["source_abstract"][:300]+"..." if r["source_abstract"] and len(r["source_abstract"])>300 else (r["source_abstract"] or "[NO ABSTRACT via Crossref -> publisher/arXiv]")))
    print("  WE CLAIM     :",r["our_claim"])
    print("  VERDICT      :",r["manual_verdict"],"|",r["p_flag_prescreen"])
    print("  WHY          :",r["verdict_rationale"][:240])
print("\nWROTE citation_layer2.json  n_rows=",len(rows))
print("SUMMARY:",out["summary"])
