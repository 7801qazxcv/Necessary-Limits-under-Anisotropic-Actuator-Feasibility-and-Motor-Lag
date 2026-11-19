# Probe v2 / Amendment 4 — 不对称执行器诊断能力（DIAGNOSTIC ONLY）

**日期**：2026-11-18  **性质**：新增诊断能力 + 代码护栏，**不改任何 V1–V5 判据、不改 GO 结果**

## 触发
上一轮真实机型 `probe_v2_REAL_results.json` 得 `NO-GO`，4/8 单元因
`Tm=0.249394`（降速时间常数）下 `dw=0` 基线发散被标 `BLOCKED`。
`real_platform_report.md` §5 当时写成「真实物理/控制后果」——措辞过强，
因为真实执行器时间常数是**不对称**的（升 0.055455 / 降 0.249394），
而 v2 用两个**对称**模型分别 bracket，「全程慢」是极端保守假设。

## 唯一代码改动（`probe_v2.py`）
1. 新增全局 `ASYM_TM = None`（默认）。
2. `rhs()` 的执行器动态分支：
   - `ASYM_TM is None`（默认）→ `udot = (u_c - u)/Tm`，**与 v2.3 逐位相同**；
   - `ASYM_TM=(T_up,T_down)` → `T_eff = np.where(u_c > u, T_up, T_down)`，
     `udot = (u_c - u)/T_eff`，逐转子、逐元素。
3. 默认行为验证：`L_nec(roll,0.05)=0.13736014943342298` 与
   `probe_v2_results_v2.3_SYNTHETIC.json` 逐位一致；`PY_COMPILE_OK`。

## 明确不做的事
- **不评估 `L_nec` / 不重跑 `evaluate()` / 不产生 GO 判据**：
  Lemma 1 的 `ψ(t)=t−T_m(1−e^{−t/T_m})` 假设单一 `T_m`，不对称下解析必要界不成立
  （诚信原则 13：定理陈述不得超过证明）。本 Amendment 只做数值诊断。
- **不重新调参**：诊断复用 `probe_v2_REAL_results.json` 中已校准的两套增益
  （`asym_diagnostic.py` 的 `gains()`），避免 re-tune to win（原则 7）。
- 不动 `refs.bib`、`theorem_draft.md`、`theorem_audit.json`、任何 `*_results.json` 的 GO 字段。

## 诊断脚本护栏（`asym_diagnostic.py`）
- 等价性探针：`ASYM(t,t)` 必须与对称 `Tm=t` 逐位一致（两族全 PASS）；
- `save()` 原子写 `os.replace`（防崩溃/被杀时截断 JSON）；
- 断点续跑：读已有 `asym_diagnostic.json`，跳过已完成 cell；
- 单次预算 `ASYM_BUDGET=30`，分 4 批跑完，规避工具 420s 时限；
- 工具超时 ≠ 进程被杀：确认残留 PID 并清理，避免并发写污染；结果清理为干净种子后重跑。

## 结果摘要（完整见 `asym_diagnostic_report.md`）
- 96 baseline + 96 boundary cell，`status=DONE`，等价性全 PASS，无残留进程，24 个 JSON 全有效。
- `dw=0` 稳定数：sym-fast 16/16、sym-slow 0/16、**asym+慢档增益 8/16**。
- 恢复边界：asym 下 `first_fail_dw` 仍几乎全为 0.20 rad/s；islands 10（最多）。
- 结论：4/8 BLOCKED **部分是模型错配伪影**，但**不足以推翻 `NO-GO`**；
  V1 仍是唯一跨机型存活主张；正式采用 asym 须重新推导解析界。

## 载体同步
`real_platform_report.md` §5 措辞已修订；`idea_assessment.md` §13、
`idea_final_v2.md` §10.2 已追加 limitation 与体裁拍板依据。
