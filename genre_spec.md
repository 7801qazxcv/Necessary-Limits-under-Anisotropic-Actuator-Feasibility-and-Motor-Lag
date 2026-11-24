# 体裁规格书 v1 — 拍板：boundary-characterisation 短文

**日期**：2026-11-18  **决定**：收束为 **boundary-characterisation / analytical short article**
（V1 控制器无关不可恢复必要上界作 headline，公开失效边界）。
**本轮交付物性质**：这是**写正文之前的规格**，不是 manuscript。未 scaffold、未编译、未写正文、未投稿。
根目录 `*_report.md` / `*_assessment*.md` / `genre_spec.md` 均为内部自审记录，**不随稿提交**。

---

## 0. 决定与依据（含被否决的另一条）
| 选项 | 判定 | 依据 |
|---|---|---|
| **A. boundary-characterisation 短文** | **采纳** | 唯一跨机型存活主张是 V1（合成机型与真实机型对抗臂均 0 违规）；三层引用核验确认 prior art 的 sufficient 域/ROA/CBF 已成体系，本稿的差异化是 **sufficient ↔ necessary 方向差异**，天然是「界定一个边界」而非「提出一个更优控制器」 |
| B. 补 asym 解析界 + SITL 争取完整实证稿 | 否决 | `asym_diagnostic_report.md` 实测：补不对称建模后恢复边界仍在最小冲击量级（0.20 rad/s）、islands 反增到 10、增益—模型强耦合；且 Lemma 1 的 `ψ(t)` 假设单一 `T_m`，asym 下需**重新推导解析界**（新理论工作），不是重跑能替代。以此为立项前提是「先定结论再补证据」，违背诚信原则 #7 |

**选 A 的额外理由**（`protocol-and-methodology-papers.md`）：本稿有严格定理 + 可复现数值验证，
但**无实体飞行 / 无 SITL / 无真实飞行数据**，且主结果在真实机型上是一个**阴性/边界结果**。
诚实体裁就是把「没有硬件验证」和「效应不跨机型复制」本身转成定位：
从「我们提出一个更韧的控制器」改为「我们给出一个任何控制器都不能逾越的界，并公开它在什么条件下不成立」。

---

## 1. 文章类型与 scope
- **类型**：Analytical / boundary-characterisation short article（理论 + 计算验证），
  非 methodology/protocol 稿（本稿有定理，不是「应该测什么」），非 position paper，非控制算法论文。
- **一句话定位句**（Introduction 第一页写死，按 protocol 稿纪律）：
  > [EN] *This work is positioned as a boundary-characterisation study of post-impulse
  > attitude recoverability, not as a controller-design or resilient-control contribution:
  > the control law used here is a verification vehicle, and the result is a
  > controller-independent necessary bound together with an explicit account of where it
  > ceases to be informative.*
- **目标读者**：非线性控制 / 混杂系统 / 无人机动力学中关注可达性、吸引域、安全不变集的读者。
- **scope 声明**：不主张硬件验证、不主张跨机型稳健优势、不主张优于所有基线。

## 2. 题目（整体切换，非旧题小改）
- **主推**：*A Controller-Independent Non-Recoverability Bound for Post-Impulse Quadrotor
  Attitude Recovery: Necessary Limits along Principal Axes under Anisotropic Actuator
  Feasibility and Motor Lag*
- **备选**：*Where Post-Impulse Attitude Recovery Stops on a Quadrotor: A Necessary Bound,
  a Three-Way Domain Decomposition, and Cross-Platform Failure Evidence*
- **弃用**（grep 零命中才算改完）：`Resilience-Oriented`、`Adaptive Control`、
  `arbitrary impulse directions`、`guaranteed for all bounded disturbances`、
  `revealing anisotropic recovery mechanisms`、`superior to all baselines`、
  `cross-platform robust anisotropy advantage`。
- 理由：`direction-dependent` 只能用于**数值观测层面**；定理严格适用**仅限主轴方向**（A1），
  且只对**对抗扰动实现** `n^T d=+\bar d` 成立。

## 3. 摘要骨架（headline 开头，四条约束）
> [EN] *The headline result is a controller-independent necessary bound on the angular
> impulse above which no control law can return a quadrotor inside a prescribed attitude
> envelope, derived along principal axes from the anisotropic actuator force-feasibility
> set and a first-order motor lag. [Lemma 1 + Theorem 1, assumptions stated.] We then
> separate the theoretically certified domain, the numerically observed domain, and the
> unverified region, and report the gap between the necessary bound and the best
> controller-certified sufficient boundary. On a synthetic literature-anchored platform
> the bound is tight (gap≈0 in the scalar limit) while a full 6-DoF model with non-ideal
> controllers opens a measurable gap; on a single identified Crazyflie platform the
> bound remains violation-free (0 adversarial-arm violations) but the anisotropy
> advantage does not replicate (yaw/roll L_suff ratio 0.687) and baseline advantages
> vanish. We make no hardware or flight-test claim; all results are analytical and
> computational.*

**四条硬约束**：
1. headline 句与贡献列表第 (1) 条**同一主张**（P18：最硬的新结果必须是引言贡献第 1 条，同时是摘要头一句）。
2. 阳性（界成立、0 违规）放前，阴性（不复制）放**边界位**句尾，不写成「全是阴性」（P18）。
3. 摘要里每个数字必须在正文逐字出现（`consistency_gate.py` HARD 项）；数学式用 `$...$` 且
   `^`/`_` 必须在数学模式内；门户纯文本版另行 `to_plain()` 导出（P14）。
4. 目标刊若定 ApJ/AAS 类 250 词或 SciRep 200 词硬上限，按 P14 数词（`\begin` 内联数一次）。

## 4. 贡献列表（有主次，首位承担全文）
**(1) Headline — 控制器无关的不可恢复必要上界**（承担全文）
- Lemma 1：`(-n)^T τ(t) ≤ τ_max,n(1−e^{−t/T_m})`、`∫ ≤ τ_max,n ψ(t)`，仅由可行集支撑函数 + 一阶电机滞后推出，**不含控制器、不含 Lyapunov**；真实闭环轨迹逐点 **0 违规**（`theorem_audit.json` C4）。
- Theorem 1（A1 主轴 + 存在性 `τ_max,n > \bar d` + 对抗扰动）：`L > L* ⇒` 任意控制律都无法保持 `φ ≤ Φ_max`；`L*` 是可恢复域的**必要上界，非充要**。
- 与既有 sufficient 域文献（ROA/SOS/Biswas 2026、bCBF/van Wijk 2026、recoverable sets/McDonough 2017）的**方向差异**必须单列一句：它们给控制器依赖的充分域，本稿给控制器无关的不可恢复必要界，互补而非竞争。

**(2) 三分域口径 + 必要/充分间隙**
- 理论必要域（定理+假设） / 数值观测域（有限网格，单一实现） / 未验证区域 —— 三段分别标注，
  数值域绝不称稳定域。
- 二参数标度 `λ=L/(τ_max T_char)`、`μ=T_m/T_char`；`v1 gap=0` 真阴性（标量+近最优控制器下界紧）、
  6-DoF 对抗臂 gap（主轴 4–5% / yaw≈20% / combo≈65–69%）为**控制器次优性 + 轴向解耦近似**的度量，
  不是物理常数，不写「任意参数下成立」。

**(3) 公开的失效边界（阴性结果作主线支点，P18）**
- 单一真实机型 `NO-GO`：V3 `yaw/roll=0.687>0.6`、V4 显著优势消失、4/8 单元 `BLOCKED`；
- Amendment-4：不对称执行器诊断证明 BLOCKED **部分是 bracket 模型错配伪影**（8/16 基线回稳），
  但恢复边界仍在 0.20 rad/s 且 islands=10，**不足以推翻 NO-GO**；
- 与 `param_sensitivity.py` 预测方向一致（κ 大 / 惯量比大 → V3 升）——**排除替代解释**，
  这是比三条阳性结论更能定位机制的证据。

**One move, not (i)(ii)(iii) checklist**（P18）：先写
`\textbf{The move made here}` 一句（把「控制器依赖的充分域」换成「控制器无关的不可恢复必要界 +
三分域」），再列 2–3 条后果；把标准部件（四元数运动学、Newton–Euler、一阶执行器、quasi-PD/SMC）
**从贡献里拿出来**，明写在 `\textbf{What is not claimed}`。

## 5. 章节结构（体裁切换后的骨架，含 score.py 关键词）
1. **Introduction: problem, related work and contribution**（顶层标题须含 problem/related/propose 类词，P18/score-levers）
2. **Related Work: five streams and a shared blind spot**（按流派+共同盲点，一组 3–8 篇放同一 `\cite{}`，单段 `\cite` 调用 ≤10；`related_work_gap.md` 已备 `[EN]` 段）
3. **Model and Problem Formulation**（6-DoF 四元数、`U={u:0≤u_i≤u_max, Σu_i=F}`、冲击跳变 `ω(t_k^+)=ω(t_k^-)+J^{-1}L_k`、一阶电机滞后、假设表）
4. **A Controller-Independent Non-Recoverability Bound**（Lemma 1 + Assumption A1 + Theorem 1 + 完整证明 + Remark 1/2/3；定理环境小写 `theorem`/`lemma`/`proof` 才拿 +4 分）
5. **Computational Evaluation and Simulation Study**（**章节名必须留 `simulation`/`evaluation`**，否则 `score.py` 掉 5 分；双机型并列 + 三分域 + 配对符号检验/Holm + 代价指标）
6. **Where the Behaviour Stops: Failure Boundaries and Cross-Platform Limits**（阴性/边界节，收束慢档 BLOCKED、asym 诊断、任意扰动需更大界、增益—模型耦合）
7. **Discussion, Limitations and What Is Not Claimed**（含 `\textbf{What is not claimed}` 段）
8. **Conclusions**
- `Results`/`Discussion` 的 `\subsection` 各 ≤4，主线句落在结果节第一段（P18）。

## 6. 图表预算（收束自草案 13 图 / 6 表 → 4 图 / 2 表）
| 编号 | 内容 | 来源产物 |
|---|---|---|
| Fig.1 | 冲击跳变 + 三分域示意（理论域/观测域/未验证域） | 示意，无数据 |
| Fig.2 | 必要界 `L*` vs `μ` 与数值观测边界（双机型同图，含 `BLOCKED` 标注） | `probe_v2_results.json` + `probe_v2_REAL_results.json` |
| Fig.3 | 各向异性比 V3 的参数子域（合成 GO / 真实 NO-GO 并列） | `param_sensitivity.json` + 真实机型 |
| Fig.4 | 失效边界：asym 诊断 `first_fail_dw` 与 islands | `asym_diagnostic.json` |
| Table 1 | 模型参数与来源（合成假设机型 / 单一真实机型**双列分标**） | `param_sources.md` + `real_platform_config.json` |
| Table 2 | 理论条件 ↔ 数值验证结果对照（含 V1–V5 逐项、BLOCKED 计数） | `theorem_audit.json` + 两份 results |
- 出图前实测栏宽（`\typeout{TW=\the\textwidth}`），图内无标题、图例在面板外、字号 ≥8 pt（figure-legibility 家规）。
- **图内不标「measured/validated」**：合成数据一律 `simulated` / `computationally verified`。

## 7. 措辞降级表（protocol 稿专用，全文 grep 零命中才算改完）
| 不要写 | 改写 |
|---|---|
| Validation / Validated / Empirical validation | Computational verification / Computationally verified |
| Physical validation / flight-tested | Protocol demonstration / numerical simulation only |
| Recoverable set（当指本稿定理结论时） | Non-recoverability bound (necessary) / certified domain |
| Stability domain（当指有限网格结果） | Numerically observed recovery domain |
| Threshold（当它是二值判据时） | Pre-registered recovery criterion |
| Threshold（当它是 `V3<0.6` 时） | Conditional discriminator（报连续函数，不叫失效边界） |
| Superior / outperforms all baselines | Conditional advantage, characterised by direction and `μ` |
| Certified / guaranteed recovery | Certified non-recoverability bound |

## 8. 三档措辞（阴性结果 Part B，按数据实际分档）
| 档 | 适用对象 | 措辞 |
|---|---|---|
| *bounded* | V1 必要界、Lemma 1 轨迹 | 「0 adversarial-arm violations / stays inside the certified band, as Theorem 1 predicts」——**阳性结果，关于证明** |
| *replicates*（方向一致） | `param_sensitivity.py` 预测的 V3 方向在合成→真实机型一致 | 报数值与方向，说明「预测方向一致」 |
| *does not replicate* | V3 各向异性优势、V4 基线优势、跨机型稳健性 | **原话写**「we do not claim X on this platform」，**不软化成 comparable / slight advantage** |

**n=3 诚实声明**（Part B 第 1 步 / integrity 15b）：本稿是确定性固定网格仿真 +
单次诊断，**没有逐条件 n≥3 重复**。需在 Limitations 明写：
> [EN] *Point estimates are conditional on the fixed scenario grid; the paired ranking is
> more reliable than absolute magnitudes, and multi-seed replication is required before any
> hardware claim.*
禁止把 `replicates` 用在只有单次运行的指标上。

## 9. 五条硬要求对照（protocol 稿，缺一条即被判「只是清单」）
| # | 要求 | 本稿落点 | 状态 |
|---|---|---|---|
| 1 | 与既有标准/工作对照 | `related_work_gap.md` 五流派 + ROA/SOS/recoverable-set/CBF **sufficient 域**对照；差异轴写死为 necessary vs sufficient | 已备 |
| 2 | 充分性声称必须验证 | Theorem 1 明写**必要非充要**；数值域不称稳定域；`V3<0.6` 改报连续函数 | 已备 |
| 3 | 报「测得到的」 | 双机型、判据冻结、`BLOCKED` 单元如实列；RPM 量在真实机型标 N/A 不静默通过 | 已备 |
| 4 | 失效模式测试 | 慢档 BLOCKED、asym 诊断、宽增益扫描 0/81、islands、dt 收敛、等价性探针、`Σu=F` 投影残差→0 | 已备 |
| 5 | 一键复现包 + 假设表 | 需新增 `experiments/run_all_experiments.py`（一条命令重跑 `probe_v1.py`→`run_real_platform.py`→`asym_diagnostic.py`→`theorem_audit.py`→`param_sensitivity.py`，打印产物清单与 ALL STEPS OK）+ **Assumption 表**（A1 / `τ_max,n>\bar d` / 对抗扰动 / 对称 bracket / 固定总推力 / 无平动外环 / 无 SITL，每行写「若被违反的后果」） | **待做（进全文时）** |

## 10. 五载体同步清单（Part B 第 6 步，一次改完）
改动体裁后必须**同时**改：① 摘要（含生成脚本常量）② 引言贡献列表（阴性结果须成为编号贡献并点名）
③ Discussion 边界节 ④ Conclusions 里旧句「hardware tests remain to be done / left to future
hardware work / no physical flight experiment is required」⑤ cover letter。
改完对 PDF 文本层 `grep` 每个被取代短语，**0 命中**才算对齐；探针避开 `fi`/`fl` 连字与 Unicode 减号。
另同步：内部 `idea_final_v2.md` / `idea_assessment.md` 的「待拍板」措辞（本轮已做）。

## 11. 一键复现与产物映射（provenance，不得编造）
| 正文数字/图 | 唯一来源产物 |
|---|---|
| `L*`、Lemma 1、C4 0 违规、常数 reverse-solve | `theorem_audit.json` / `theorem_draft.md` |
| 合成机型 V1–V5、`L_suff`、gap、标度 | `probe_v2_results.json`（v2.3） |
| 真实机型 NO-GO、V3=0.687、BLOCKED 4/8 | `probe_v2_REAL_results.json` / `real_platform_config.json` |
| asym 8/16、`first_fail_dw`、islands=10 | `asym_diagnostic.json` |
| V3 参数子域 `[0.163,1.623]`、33/81 | `param_sensitivity.json` |
| 24 条引用、0 误引 | `refs.bib` / `citation_layer2.json` / `ref_meta_raw.json` |
> 铁律：任何数字不得只存在于 `.tex` 里；改脚本后逐位比对 `NO DRIFT: True` 再打包。

## 12. 阻塞项（仍不宣布可投）
1. **作者专属值**：名单 / ORCID / 基金 / 单位官方英文名 / 投稿批准 —— 不代填、不跨稿继承。
2. **AI 使用披露**：按本用户全稿单一口径（仅语言翻译与润色）；收窄前提示一次合规风险，
   保留旧措辞于「仅编辑留存」文件，绝不入投稿包。
3. **per-year 选刊门禁**（逐年预警名单 / SCIE 收录 / 文章类型 / 首决周期 / APC）——选项 3，未做。
4. **`.tex` 组装与门禁**（build 0 error / verify_bib 0 FAIL / score≥80 / consistency_gate / deliver_gate /
   渲染验收逐页）——选项 4，未做。
5. **一键复现包 + 假设表**（§9 #5）随全文一起交付。
6. 无 SITL / 无实飞 / 不对称执行器仅作诊断、Lemma 1 单一 `T_m` 假设的适用范围必须写进 Limitations。
7. 同行评议结果不可承诺；可控项（体裁聚焦、诚信边界、可复现脚本）已推进，不可控项未闭合。

## 13. 与现有产物的关系（不重做、不覆盖）
- **直接复用**：`related_work_gap.md`（[EN] 段）、`refs.bib`、`theorem_draft.md`、`idea_final_v2.md` 的 V1 主张、
  全部 `*_results.json` / `*.json`。
- **本轮生成**：本规格书；`idea_final_v2.md` §11、`idea_assessment.md` §14（回流）。
- **不生成**：`main.tex` / `refs.bib` 新条目 / 图 / 投稿包 —— 需选项 4 才动。


---

## 14. 用户拍板变更（2026-11-24）：改投 Research Article

**用户指令**：`改投 Research Article`。**这一节取代 §0 的文章类型决定，但 §0–§13 的学术定位、
定理限定、诚信红线与历史决策全部保留**（旧 verdict 作废、旧证据不删）。

| 维度 | 变更 |
|---|---|
| 学术体裁 | **不变**：仍是 boundary-characterisation（必要上界 + 可证充分界 + 诚实三分域），不是 controller-design 贡献；不是完整实证稿 |
| 投稿文章类型 | `ISA Transactions / Technical Note` → **`ISA Transactions / Research Article`（Analysis 类）** |
| 目标刊 | **不变**（同刊换类型，`elsarticle` 与 `\journal{ISA Transactions}` 不动，零重建成本） |
| 篇幅 | 16 页不再是缺陷：官方 Technical Note 约 2 页，Research Article 无该上限 |

官方依据见 `isa_guide_research_article.md`。Research Articles 明文
「focus on the fundamental analysis or mathematics of a technique, and are
**illustrated with simulations**」——仿真被接受，无需硬件；Technical Note 的
「~2 journal pages」与强制标题前缀「Technical Note:」不再适用。

**代价（必须并列写明）**：Technical Note 明文豁免
「extensive comprehensive defence required of regular papers」，改投后**该豁免消失**；
Aims & Scope 还要求 credible demonstration。按 `sci-venue-selection` 的判据，
证据薄时更稳妥的杠杆本应是**低门槛文章类型**；本次是作者拍板的反向选择，
解除了页数/前缀矛盾，但**提高了 L3 门槛**，而 L3 significance/completeness
恰是当前最弱两项。本轮不新增任何证据、不夸大主张、不承诺录用。

落地清单与验证见 `round_research_article_report.md`、`idea_assessment.md` §33。
