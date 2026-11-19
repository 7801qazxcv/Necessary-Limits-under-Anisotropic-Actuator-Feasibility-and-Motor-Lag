# 预注册：M1 引理 + M3 定量对比（运行前冻结，2026-11-19）

**对应指令**：用户 `1+4+5`。本文件在任何计算脚本运行前冻结判据；事后不改判据。

## 通用纪律
- 默认 `probe_v2.py` **不得改动**（v2.3 byte-identical 约束）；新计算走独立脚本，
  通过 import + 显式覆盖扰动相位实现，不改默认 `D_FIX` 的持久化产物。
- 所有数字落盘 JSON，正文数字经 `numbers.tex` 宏生成，零手抄。
- 扰动/结果是确定性的；「n≥3 复现」定义为 **3 个独立扰动相位**（SEED_PHASE 变体），
  不是把同一确定性 case 重跑 3 次拿 3 个相同数（skill #15/#25b）。
- 结果「太干净」（gap=0、全档通过）先当 bug 查，按 integrity #17 测机制。
- 灾难性结果先诊断，不 re-tune 到赢。

## M1（任务 5）：A1 放宽引理 —— 真推导 + 实测
**待证命题（不预设结论）**：控制器注入正交轴力矩能否改善主轴恢复？
- 对 $J=\mathrm{diag}(J_x,J_y,J_z)$、$n=e_i$，沿 $n$ 的角动量满足
  $\dot p = n^\top\tau + n^\top d - n^\top(\omega\times J\omega)$，
  且 $n^\top(\omega\times J\omega)=(J_k-J_l)\,\omega_k\omega_l$（$k,l$ 为另两轴）。
- **该陀螺项符号不定、一般非零** → 「正交注入不能改善」这一命题**可能为假**，
  不得预先写成引理结论（skill：不要为立项先定结论再补证据）。
- 冻结的可证方向：用 $|n^\top(\omega\times J\omega)|\le |J_k-J_l|\,\|\omega_\perp\|^2/2$
  （柯西/AM-GM）把陀螺项并入等效扰动上界
  $\bar d_{\rm eff}=\bar d+\gamma\Omega_\perp^2/2$，$\gamma=|J_k-J_l|$，
  得到 **A1-free 但更保守**的必要界；存在性条件收紧为
  $\tau_{\max,n}>\bar d_{\rm eff}$。$L^*_{\rm free}\le L^*$（更早判定不可恢复）。
- $\Omega_\perp$ 从 6-DoF 轨迹**实测**（不编造），标为观测上界而非理论保证。
- **弃用规则**：若 $\bar d_{\rm eff}\ge\tau_{\max,n}$ 则该方向界 vacuous，
  如实标 `outside certified envelope`，不硬凑一个数。
- 交付：Lemma 2（含显式常数）+ 数值表 + 与 Theorem 1 的关系说明；
  明确写「这不是解除 A1，是把 A1 换成可测的正交分量界」。

## M3（任务 4）：最强对手定量对比 + n≥3 复现 —— 真计算
**冻结的对手定义（proxy，诚实标注）**：
- prior art 的 SOS-ROA / recoverable-set / bCBF **无公开实现与算例参数**，
  无法逐行复现 → 不伪造其数值。
- 用**标准二次 Lyapunov 充分域**（能量法，同一动力学与可行集）作为
  sufficient-domain 方法族的**可复现代理**，明确标注是 proxy 而非复现
  `Biswas2026Control` 的具体 SOS 程序。
- 对比三方在同一算例 (roll, $T_m=0.05$ s) 的值：
  (a) 本文解析必要上界 $L^*$；
  (b) proxy 充分域 $L_{\rm lyap}$；
  (c) 观测到的最优控制器充分边界 $L_{\rm suff}$（已有产物，非新造）。
- **逻辑判据（cheap null）**：充分域必须 ⊂ 可恢复集 ⊂ $[0,L^*]$，
  故应有 $L_{\rm lyap}\le L^*$ 且 $L_{\rm suff}\le L^*$。
  若 $L_{\rm lyap}>L^*$，**先判实现/口径 bug**，不许报「我们更紧」。
- 报告三者 gap 与排序，明说「引用了 ≠ 对比了」是否已闭合到数值层。

**n≥3 复现定义**：
- 3 个独立扰动相位 $\phi_1,\phi_2,\phi_3$（固定、预注册），
  每个相位下重跑主臂关键 cell 的 $L_{\rm suff}$ 与 V1 对抗臂比例。
- 报 mean + 每个单次值 + 方向一致性（排序是否在每个相位都保持，skill #25b）。
- 若三次方向不一致 → 报「does not replicate」，不主张优势。
- 如实说明：确定性内核 + 独立扰动实现；点估计条件于相位集。

## 任务 1（文本清理，零编造）
- NEW-1：正文 AI 披露只留两句作者既定口径，删 4 行内部元叙述；
  在项目根建 `AI_DISCLOSURE_HISTORY_EDITORIAL_ONLY.md`（**不进投稿包**）保存旧措辞。
- NEW-2：`deliver_gate` 需要 `pre_review_report.md` 在 `paper/`，
  故**不移动**（移动会让门禁 FAIL）。改为建立干净的 `submission/` 上传包，
  只含随稿文件；`paper/` 定位为门禁工作目录。上传包扫描零命中内部审稿语气。
- 重跑全套门禁 + `NO DRIFT: True`。

## 门禁
`py_compile` → `run_all_experiments.py` → 四步编译 → score / consistency /
verify_bib / deliver_gate / gate_check → 渲染验收（新增页）→ 干净目录重编译。
