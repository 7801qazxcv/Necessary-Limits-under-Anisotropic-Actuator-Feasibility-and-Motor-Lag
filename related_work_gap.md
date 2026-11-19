# 层 3 交付：Related Work 与 Research Gap（批判性论证，非文献罗列）

**日期**：2026-11-18  **配套**：`ref_meta_raw.json`（层1）、`citation_layer2.json`（层2）、`refs.bib`（24 条，cited==listed）
**语言**：正文论证用中文说明；给出可直接写入英文稿的段落（标注 `[EN]`）。
**纪律**：全部引用已在层 1 由 live Crossref/arXiv 核验元数据、层 2 逐条做 claim↔摘要配对；
无虚构文献/DOI；`10.2139/ssrn.7536970` 明确标注为**未同行评议预印本**；
NASA NTRS 20120014563 无 DOI，标为「需出版社核验」，不进 `refs.bib`。

---

## 0. 一句话结论（先说最硬的）
ChatGPT 草案判断「已有研究只是有限时间控制+扰动观测+饱和的组合，不能算创新」**低估了 prior art**。
真实核验发现三块已成体系的硬工作，任何「首次」式定位都会被审稿人一票否决：
1. **recoverable / safe set** 在飞机失控（LOC）领域 2012–2017 已正式定义并期刊发表；
2. **饱和控制 + 脉冲校正 → 镇定** 已在 *Nonlinear Analysis: Hybrid Systems* 2023 发表，
   且 2026 年有预印本进一步做「有限时间 + 有限脉冲调节 + 吸引域最大化」；
3. **四旋翼大初始扰动/碰撞后恢复** 已有 Monte-Carlo **与实飞**验证（2020 ICRA、2026 REFLEX）。

因此本稿**不能**主张「可恢复域」「混杂/脉冲建模」「电机滞后建模」「韧性恢复控制」为新颖。
唯一经得住核验的差异化，是下面 §4 的**控制器无关的不可恢复必要上界**及其三分域口径。

## 1. 五个流派 + 各自的共同盲点（[EN] 可直接入稿）

### Stream A — 有限/固定时间姿态控制 + 饱和 + 扰动补偿
`\cite{Zhang2024Finite, Najafi2025Fixed, Gao2020Finite, Hu2025Adaptive, Xu2022Adaptive, Liu2021Antisatu, Yu2022Fault}`

> [EN] A large body of work addresses quadrotor attitude tracking under actuator saturation
> and bounded lumped disturbances by combining (fixed-)time sliding-mode or dynamic-inversion
> laws with disturbance observers and anti-saturation auxiliary systems
> \cite{Zhang2024Finite,Najafi2025Fixed,Gao2020Finite,Hu2025Adaptive,Xu2022Adaptive,Liu2021Antisatu,Yu2022Fault}.
> These results are **convergence certificates for a specified closed loop**: the recovery
> guarantee is *sufficient* and *controller-dependent*, the disturbance is continuous and
> bounded, and validation is numerical simulation. None states a bound that **any** controller
> must respect after an exogenous state jump, and none separates what is provable from what
> is merely observed in a finite grid of simulations.

**共同盲点**：都是「给定控制律 → 证明收敛」，不是「给定物理约束 → 证明任何控制律都不可能」。
另有两处必须精确（层 2 已标）：
- `Yu2022Fault` 是 **practical** finite-time（收敛到残差集，UUB 型），不得写成严格有限时间；
- `Xu2022Adaptive` 摘要**没有** input saturation，不得把抗饱和归给它；
- `Liu2021Antisatu` 发表于 **2021**（TCSII 68(6):2047–2051），ChatGPT 草案写「2020」是错的；
- `Najafi2025Fixed` / `Hu2025Adaptive` / `Liu2021Antisatu` Crossref 无 abstract，
  内容判断依据出版社页片段（层 2 `abstract_available=false`，已登记）。

### Stream B — 四旋翼大扰动 / 碰撞后恢复（含实飞）
`\cite{Sun2020Upset, Hermeler2026REFLEX, Gaucher2026Dual}`

> [EN] Recovery of a quadrotor from large initial attitude and angular-rate conditions has
> been demonstrated with Monte-Carlo evaluation and real flight tests after a complete rotor
> failure \cite{Sun2020Upset}, and autonomous post-collision recovery has hardware evidence
> from real wall impacts \cite{Hermeler2026REFLEX}; impulse reset maps with normal/tangential
> coupling have also been formulated on SE(3) \cite{Gaucher2026Dual}. These are
> *controller designs* validated on specific vehicles — a fault-tolerant cascaded controller,
> a learned on-board reflex, an energy-dissipating recovery law. The recovery set they
> exhibit is **empirical/observational**; no controller-independent upper limit on the
> recoverable angular impulse is derived, and the actuator model is either idealised or
> learned rather than an explicit anisotropic force-feasibility set with first-order motor lag.

**共同盲点**：证据强（含实飞）但都是「这个控制器在这些条件下恢复了」；没有回答
「给定执行器能力，多大的外生角冲量是**任何**控制器都无法恢复的」。
`Gaucher2026Dual` 的冲量模型比本稿的 `ω(t⁺)=ω(t⁻)+J⁻¹L` **更完备**（对偶四元数、
法/切向耦合），必须作为 **limitation 证据**引用，不能当作我们更新。

### Stream C — 可恢复集 / 吸引域 / 受控不变集
`\cite{McDonough2017Fast, McDonough2014Recovera, Biswas2026Control, Ferrante2022Control, Engelbrecht2013Multi, Dongmo2012Aircraft}`

> [EN] The notion of a *recoverable set* is not new: it was introduced for aircraft
> loss-of-control handling \cite{McDonough2014Recovera,McDonough2017Fast} and upset/stall
> recovery with explicit state and control constraints
> \cite{Engelbrecht2013Multi,Dongmo2012Aircraft}. Region-of-attraction enlargement under
> saturation is available via sum-of-squares with Monte-Carlo verification
> \cite{Biswas2026Control}, and explicit ellipsoidal basin estimates exist in hybrid-systems
> frameworks \cite{Ferrante2022Control}. All of these are **sufficient, controller-dependent
> regions** — the set of initial conditions from which a *designed* controller is certified
> to converge. A **necessary, controller-independent non-recoverability bound** (a limit no
> controller may exceed) is a different mathematical object and is not supplied by this line.

**共同盲点（也是本稿定位的支点）**：**sufficient ↔ necessary 的方向差异**。
ROA/SOS/bCBF 说「这套控制器能到达这些初态」；本稿说「任何控制器都不能超过这个 L」。
两者互补而非竞争——写清楚这一点，比说「他们没做可恢复域」更准确也更锋利
（citation-content-audit 原则 5：改我们的句子，不改文献）。

### Stream D — 脉冲 / 混杂系统理论与安全
`\cite{Yu2023Exponent, Gao2026Finite, Breeden2023Safety, Haimovich2019characte, Wijk2026Generali}`

> [EN] Impulsive and hybrid stability theory is mature: strong iISS characterisations for
> time-varying impulsive systems \cite{Haimovich2019characte}, CBF/CLF extensions to systems
> with impulsive actuators and dwell-time constraints \cite{Breeden2023Safety}, generalised
> backup CBFs constructing controlled-invariant safe sets under input bounds
> \cite{Wijk2026Generali}, and exponential stabilisation of nonlinear systems under saturated
> control **with impulse correction** \cite{Yu2023Exponent}. A recent preprint further studies
> finite-time stabilisation via saturated control with finite impulsive regulation and
> maximises the estimated domain of attraction \cite{Gao2026Finite}.

**两处必须精确的区分（层 2 标为 P1 高危，写错即 P1 误述）**：
1. `Yu2023Exponent` 与 `Gao2026Finite` 的 "impulse" 是**控制输入侧的脉冲校正/调节**
   （impulsive control / regulation），本稿的 impulse 是**外生角冲量导致的状态跳变**
   （exogenous angular impulse）。两者方向相反，绝不能写「他们已研究冲击后恢复」。
2. `Gao2026Finite` 是 **SSRN posted-content 预印本、未同行评议**，且做的是
   *sufficient* DOA 最大化；引用时必须带 "preprint, not peer-reviewed"，且不得与
   `Yu2023Exponent` 当作两篇独立期刊工作重复计数（同一 Xiaodi Li 组）。
3. `Breeden2023Safety` 的领域是**航天器对接**、脉冲执行器；不得移植成四旋翼姿态恢复。

### Stream E — 执行器非理想建模
`\cite{Le2026Residual, Eschmann2024Data, Ji2015Developm}`

> [EN] Motor lag, dead-zone, thrust saturation, rotor drag and partial loss of motor
> effectiveness have been modelled with UUB guarantees and gain-matched ablations for
> attitude–altitude tracking \cite{Le2026Residual}; inertia, thrust curves, torque
> coefficients and first-order motor delay are identifiable from proprioceptive flight data
> \cite{Eschmann2024Data}, and low-cost testbeds with CIFER identification provide an
> independent parameter source \cite{Ji2015Developm}.

**共同盲点**：建模与辨识成熟，但问题设定是**跟踪**；没有把「冲击跳变 + 各向异性可行集 +
电机滞后」一起放进一个**可恢复性上界**里。本稿不得宣称「首次考虑电机动态」。

## 2. [EN] 可直接入稿的 gap 段（一条主线，非人名清单）

> [EN] **What is shared.** Across these five streams, recovery or stabilisation is certified
> for a *specified* controller: the guarantee is sufficient and controller-dependent, the
> disturbance is either continuous and bounded or a control-side impulse, and the reported
> recovery region is either a Lyapunov/SOS region of attraction or a finite set of
> simulated/trial outcomes. The recoverable-set concept itself dates to aircraft
> loss-of-control work \cite{McDonough2014Recovera,McDonough2017Fast}, and impulsive-system
> stability theory is mature \cite{Haimovich2019characte,Breeden2023Safety}.
>
> **The gap.** What is absent is a **controller-independent necessary bound** on post-impact
> recoverability: given the anisotropic actuator force-feasibility set, a first-order motor
> lag and a bounded post-impact disturbance, determine an angular-impulse magnitude above
> which **no** control law — however designed — can return the vehicle inside a prescribed
> attitude envelope. This is the converse direction to a region of attraction: it bounds what
> is impossible rather than certifying what a particular controller achieves. It also forces a
> three-way distinction that the literature keeps implicit: the **theoretically certified
> domain** (theorem + assumptions), the **numerically observed domain** (finite simulation
> grid), and the **unverified region** — and it requires that the gap between the necessary
> bound and the best observed sufficient boundary be reported rather than hidden.

## 3. [EN] What is NOT claimed（防 incremental desk-reject，必写入 Introduction）

> [EN] We do **not** claim that hybrid/impulsive modelling, recoverable sets, motor-lag
> modelling, or resilient attitude control are new: all are established
> \cite{McDonough2017Fast,Haimovich2019characte,Eschmann2024Data,Le2026Residual}. The
> attitude controller used here is a verification vehicle, not a contribution; the standard
> quaternion kinematics, Newton--Euler dynamics and first-order actuator model are borrowed.
> We do not claim superiority over all baselines, recovery for arbitrary impulse directions,
> or guarantees for all bounded disturbances. The formal result is restricted to **principal
> axes under an adversarial disturbance realisation** (Assumption A1); combined-axis behaviour
> is reported only as numerical observation, and the extension to arbitrary bounded
> disturbances requires a strictly larger bound (quantified in the theorem audit). No
> hardware or flight-test evidence is claimed; conclusions are analytical plus numerical.

## 4. 本稿唯一可辩护的差异化（经三层核验后仍存活）
**给定各向异性执行器可行集 `U={u: 0≤u_i≤u_max, Σu_i=F}`、一阶电机滞后 `T_m`、
有界冲击后扰动，推导主轴方向、对抗扰动下「任何控制器都无法恢复」的角冲量必要上界 `L*`，
并把理论域 / 数值观测域 / 未验证域三分标注，报告必要界与最佳可证充分界之间的间隙。**

支撑证据（全部来自本会话实测产物）：
- `theorem_draft.md` 的 Lemma 1 + Theorem 1 + 完整证明，`theorem_audit.py` 9 项全 PASS；
- `probe_v2_results.json`（合成机型）V1 对抗臂 0 violations；
- `probe_v2_REAL_results.json`（单一真实机型）**V1 仍 True、0 violations** →
  唯一跨机型存活的主张就是这条必要上界。

**必须同时报告的阴性结果（不得藏）**：
- 真实机型全量重跑 `NO-GO`：`V3` 各向异性比 0.687>0.6、`V4` 显著优势消失；
- 慢电机常数档 4/8 单元闭环不可稳，已标 `BLOCKED`（见 `real_platform_report.md`）；
- 因此**不得**把论文重新包装成「揭示各向异性恢复机理」或「所提控制器更优」。

## 5. 引用完整性状态（三层门禁逐项）
| 层 | 内容 | 结果 | 产物 |
|---|---|---|---|
| 1 | DOI/arXiv 存在性 + title/author/year/venue/vol/page 逐字段核实 | 18 DOI + 10 arXiv 全部 live 命中；4 处年份/卷期纠正已登记 | `ref_meta_raw.json` |
| 2 | claim ↔ 真实标题/摘要配对 + P1–P8 扫描 | 24 行，16 SUPPORTED / 8 SUPPORTED_NUANCE / **0 MISATTRIBUTION** | `citation_layer2.json` |
| 3 | cited==listed、无重复 DOI、无编造字段 | `refs.bib` 24 条 = 24 cited，0 重复，0 CR 字节 | `refs.bib` |

层 2 的 8 处 `SUPPORTED_NUANCE` 已逐条处置（见 `citation_layer2.json` 的
`verdict_rationale`）：4 篇 Crossref 无 abstract → 依据出版社页/arXiv；
`Gao2026Finite` 标预印本；`Yu2023Exponent`/`Gao2026Finite` 的 P1 方向区分；
`Hu2025Adaptive` 的「非对称饱和 ≠ 非对称时间常数」；`Breeden2023Safety` 的域移植。

**仍待作者/出版社核验**：NASA NTRS 20120014563（无 DOI，仅作 LOC 背景，
未进 `refs.bib`）；`10.2139/ssrn.7536970` 预印本状态需在投稿前复核是否已正式发表。

## 6. 对「大概率录用」的诚实判断
三层核验把**可控项**推到了极限：文献真实、归因无误、gap 精确、claim 不越界、
阴性结果如实。但**不可控项仍在**：真实机型 `NO-GO` 削弱了 V3/V4 卖点，
尚无 SITL/实飞，选刊未做 per-year 门禁，`.tex` 尚未 build/score/deliver_gate。
因此本轮**不宣布可投**，只宣布「Related Work / gap 论证已具备投稿包所需的诚信基础」。
