# Table 1 参数溯源（草案，投稿前须替换为单一真实机型完整辨识参数）

> **状态**：本稿参数是**以公开文献区间为锚的合成假设机型**，不是某一真实平台的实测参数。
> 逐条 sanity check 后**排除 2 处文献异常/单位错误**，不盲抄。所有文献元数据经 arXiv API 核实（见 `param_sources_verified.json`）。

## 1. 已核实的公开文献锚点（真实值，非记忆）
| 编号 | 文献（已核实） | 元数据 | 提供的值 |
|---|---|---|---|
| [P1] | Eschmann, Albani, Loianno, *Data-Driven System Identification of Quadrotors Subject to Motor Delays*, arXiv:2404.07837 | arXiv API: 2024-04-11, 3 作者 ✓ | 电机一阶时间常数 **T_m = 0.072 s**（MAP 辨识）；厂商阶跃响应 ≈0.073 s；前作 0.065 s。Table II 给出多机型惯量：x500(2.0 kg, Ixx=2.20e-2, Izz=4.00e-2)、Flightmare(0.73 kg, 7.911e-3/1.231e-2)、Iris(1.5 kg, 2.913e-2/5.523e-2)、Crazyflie 中位(0.027 kg, 1.40e-5/2.734e-5)；`Izz/Ixx` 均值 **1.832**、中位 1.760 |
| [P2] | Ji, Turkoglu, *Development of a Low-Cost Experimental Quadcopter Testbed…*, arXiv:1508.04886 | arXiv API: 2015-08-20, 2 作者 ✓ | Table 3：m=1.8 kg, Ixx=Iyy=7.06e-3, Izz=7.865e-3, J_TP=1.42e-3 kg·m², b=4.5e-4, d=1.8e-5 |
| [P3] | 内部 skill `control-sim-pitfalls.md` §9 | 已 skill_view 重载 | 0.7-kg 六寸机悬停转速合理带 **400–600 rad/s** |

**文献自身的缺陷（必须记录、不盲抄）**：
- [P1] Table II 中 `Leshikar et al. 2021` 报 Ixx=54.7、Izz=57.2 kg·m²（对 2.5 kg 机型物理不可能），`Kaputa 2020` 报 Ixx=4.27e-4（对 0.25 kg 机型同样可疑）→ 未采用这两行。
- [P2] Table 3 标注 `l = 8.25 meters`（对 1.8 kg 机型物理不可能，应为 cm/英寸量级）→ 未采用该臂长。
- 跨机型参数**不可拼成一个机型**：27 g Crazyflie 的 T_m 不能与 1.8 kg testbed 的 J 混用。

## 2. 本稿参数与溯源关系（每题标注：文献锚点 / 是否实测 / sanity）
| 参数 | 本稿值（研究假设） | 文献锚点 / 依据 | 是否实测 | sanity check |
|---|---|---|---|---|
| $m$ | 0.8 kg | [P1][P2] 覆盖 0.027–3.35 kg | 否，合成 | 落在区间内 ✓ |
| $J=\mathrm{diag}(0.013,0.013,0.024)$ kg·m² | — | [P1] x500/Flightmare/Iris 的 Ixx 7.9e-3–2.9e-2；`Izz/Ixx≈1.83` 取自 [P1] 均值 1.832 | 否，以区间+比值合成 | 与 [P1] 均值一致 ✓ |
| $T_m$ | {0.02, 0.05, 0.10} s 扫描 | [P1] 实测 0.065–0.073 s | 否，扫描含实测邻域 | 0.05/0.072 覆盖实测 ✓ |
| $\Omega_{\rm hover}$ | 500 rad/s（反推 $c_T$） | [P3] 合理带 400–600 | 否，反推 | 落在带内 ✓ |
| $\Omega_{\max}$ | 900 rad/s | 工程上限假设 | 否 | $u_{\rm hov}=1.962<u_{\max}=6.357$ ✓ |
| $c_T = F/(4\Omega_{\rm hover}^2)$ | 7.848e-6 N/(rad/s)² | 由 m,g,Ω_hover 反推（[P3]） | 否，导出量 | 量纲一致 ✓ |
| $\kappa=c_Q/c_T$ | 0.02 m | 螺旋桨力矩/推力系数比量级 | 否，假设 | 决定 yaw 权限比 0.129，见敏感性 |
| $\mathrm{arm}$ | 0.22 m | 小型机几何量级；[P2] 臂长单位错误未用 | 否，假设 | 见敏感性 |
| $\Phi_{\max}$ | 60° | 姿态包线/LOC 判据（研究设定） | 否，判据 | 见敏感性 |
| $\bar d$ | 0.032 N·m | 有界零均值湍流的上界（研究设定） | 否，判据 | 存在性条件 $\tau_{\max,n}>\bar d$ 逐方向成立 |

## 3. 敏感性分析结论（`param_sensitivity.py` / `param_sensitivity.json`，真实计算）
- **OAT（7 维 × 3–4 水平）**：`L*` 与 `V3=L*_yaw/L*_roll` 对 7 个参数**全部单调可解释**（κ↑/Izz·Ixx⁻¹↑/T_m↑ → V3↑；arm↑/Φ↑/d̄↑/J↑ → V3↓）。
- **全因子交叉 81 组**（Jx_scale × Izz/Ixx × Tm × κ）：
  - 存在性条件 `τ_max,n > d̄` **100% 成立** → 定理非 vacuous 稳健；
  - `V3 ∈ [0.163, 1.623]`，**33/81 组 V3≥0.6**、个别 >1（yaw 反超 roll）→ **各向异性可判别不是全局稳健**。
- **reframe（原则 #7）**：`V3` 不是二值判据，而是 $(\kappa/a,\ I_{zz}/I_{xx},\ T_m,\ \mathrm{arm},\ \Phi_{\max},\ \bar d)$ 的**连续可解释函数**；论文须报该函数曲线与条件子域（κ 小 / arm 长 / 惯量比小 → 各向异性显著），**不得**写「任意参数下各向异性成立」。
- **口径边界**：本敏感性在**解析必要界 $L^*$** 层面完成；v2 的 V3 用的是**数值 $L_{\rm suff}$** 层面，两者口径不同。数值层面的参数敏感性**尚未跑**，列为开放项，不得外推。

## 4. 投稿前必须闭合
1. 选定**单一真实机型**，用其完整辨识参数（m, J, c_T, c_Q, arm, T_m, Ω_max）替换合成参数集并**重跑全部**探针/定理/图表；
2. 若仍用合成参数，须在 Limitations 明写「以公开文献区间为锚的合成机型，非实测」+ 给出本节敏感性表；
3. 文献条目须走 `verify_bib.py` / `bib_attribution_check.py` / `citation_content_check.py` 三层核验后才进 `refs.bib`。
