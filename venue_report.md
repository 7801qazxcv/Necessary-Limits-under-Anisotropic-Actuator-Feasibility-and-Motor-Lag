# 任务 1 报告：per-year 选刊门禁（boundary-characterisation 短文）

**日期**：2026-11-18  **状态**：完成，推荐已定  **证据**：`venue_gate.json`、`venue_probe.json`、`warning_verdict.json`、三份 `venue_*_search*.json`

---

## 0. 先钉死的约束（skill 第 1 步）
| 约束 | 取值 | 理由 |
|---|---|---|
| 索引 | **SCIE**（按 ISSN 核 WoS Core = Science Citation Index Expanded） | 用户要 SCI；ESCI 不计 |
| 预警名单 | **零历史**（同时满足「当前不在」与「从未在」两种机构口径） | 用户未指定读法，零历史不会被任一口径推翻 |
| 文章类型 | 匹配**边界/初始概念验证短文**，无硬件验证 | 体裁拍板结论；skill：文章类型是比刊物声望更大的录用杠杆 |
| 排除 | 载体刊（Drones/Aerospace/JGCD/TAES）、顶刊（Automatica/TAC）、任一年命中预警的刊 | 理论核心控制论文送 vehicle 刊会被 discipline 退 |
| 费用 | 优先 hybrid 免费订阅路线 | 作者基金状态未闭合，不得假定付得起 APC |

## 1. 逐年预警名单（最容易造假的一层，已用技能脚本验证）
- **版本集**：2020 / 2021 / 2023 / 2024 / 2025。**2022 无版**（中心调整发布节奏）；**2026 起无版**——CAS 官方声明（2026-03-27，`las.cas.cn/news/tzgg/202603/t20260327_8178738.html`）：「自2026年起，中国科学院文献情报中心将不再更新与发布期刊分区表」。**2025 是最后一版**。
- **源**：`kyc.fjut.edu.cn/2025/1105/c6371a260318/page.htm`（**HTML 表格**，含全部 5 版）。另两份汇总页（`kjc.zhku.edu.cn`、`journals.csu.edu.cn`）把名单做成**图片**，按 skill 纪律**不用**——图片页会假阴性。
- **验证方式**：`research/sci-venue-selection/scripts/verify_warning_list.py`，按 date marker 切分 + 每版阳性对照 + HTML 实体还原 + 词边界大小写不敏感 grep。
- **阳性对照结果**：5 版**全部通过**（2020 IEEE Access/Sustainability、2021 Vaccines/Shock and Vibration、2023 MACHINES/AEROSPACE/IJCAS、2024 CANCERS/MULTIMEDIA TOOLS、2025 NUMERICAL HEAT TRANSFER/SCALABLE COMPUTING）→ 切分对齐、表格已渲染，**「零命中」是可信的阴性判定，不是假阴性**。
- **候选结果**：8 个名称变体（含 IET CTA 的 `&`/`and` 两种写法）**5 版零命中 → 全部 never_warned**。
- 无命中故不需 ISSN 消歧；但已记录同名词陷阱（`JOURNAL OF SENSORS` 1687-725X ≠ `Sensors` 1424-8220；2023 名单里的 IJCAS **不是**我们的候选）。

## 2. SCIE 索引（按 ISSN）——含一个必须记录的失败通道
- `mjl.clarivate.com/search-results?issn=<ISSN>` 对**每个** ISSN 返回**同一份 11427 字节 JS 壳页**，页脚同时含 SCIE 与 ESCI 字样（通用介绍文本，不是该刊结果）→ **拒绝使用**，不拿壳页伪造 per-ISSN 结论。
- 改用可静态核验的 per-ISSN 档案（WoS 期刊档案镜像 `wos-journal.info`，逐刊一条）+ 出版社 A&I 段交叉；**IET CTA 有 Wiley 官方 A&I 明写 "Science Citation Index Expanded (Clarivate Analytics)"**。

| 刊 | ISSN | WoS Core | 状态 | JIF | 2024 Crossref 条目数 |
|---|---|---|---|---|---|
| Nonlinear Dynamics | 0924-090X | SCIE | Active | 5.7 | 1586 |
| Int. J. Robust & Nonlinear Control | 1049-8923 | SCIE | Active | 3.1 | 647 |
| **J. Franklin Institute** | 0016-0032 | SCIE | Active | 3.7 | 745 |
| Nonlinear Analysis: Hybrid Systems | 1751-570X | SCIE | Active | 3.2 | 98 |
| IET Control Theory & Appl. | 1751-8644 | SCIE | Active | 2.0 | 数据缺口* |
| **ISA Transactions** | 0019-0578 | SCIE | Active | 6.5 | 474 |
| IEEE Trans. Control Syst. Technol. | 1063-6536 | SCIE | Active | 4.4 | 210 |

\* IET CTA 的 Crossref `container-title` 与刊名不匹配，按名过滤返回 0；已标为**数据缺口**而非零产出（真实 ISSN 由 journals 反查得到 `1751-8644/1751-8652`）。
**开放项**：Clarivate 官方 MJL 的 per-ISSN 确认需免费登录，静态通道未闭合 → 列为投稿前作者侧核验项，**不冒充已在 Clarivate 核过**。

## 3. Scope fit（读标题，不读 total-results）
对每个刊跑 3 组 Crossref `container-title` 查询并逐条读回标题：
- **JFI**：2025「Adaptive practical prescribed-time attitude tracking control for quadrotor UAV」、2019「Robust estimations of the Region of Attraction using invariant sets」→ 控制 + 吸引域**双命中**。
- **ISA Trans**：2023「Estimation of non-symmetric and unbounded region of attraction using shifted shape functions」、2014「Estimation of region of attraction for polynomial nonlinear systems」→ 吸引域/边界分析命中。
- **IEEE TCST**：2016「Enlarging the Region of Attraction ... Using Impulsive ...」→ 脉冲+吸引域命中。
- **NAHS**：2025「Lyapunov-like prescribed-time stability of impulsive systems」→ 脉冲系统命中，但年条目数仅 98（窄门）。
- 结论：7 刊均在控制理论层 scope 内，符合 skill「理论核心控制论文送 control 刊、不送 vehicle 刊」。

## 4. 文章类型（决定性杠杆，来自官方 Guide for Authors）
- **ISA Transactions — Technical Notes**：官方原文「Present new concepts or **initial proof-of-concept results** ... manuscripts would be **short, perhaps two journal pages**, and would **not require extensive comprehensive defence required of regular papers**」；且 Research Articles「focus on the fundamental analysis or mathematics of a technique, and are **illustrated with simulations**」→ **仿真被明文接受**。这与本稿「诚实边界结果、无硬件验证、必要界 + 公开失效边界」**精确匹配**。
- **JFI — Short Communications**：4–5 页，但「accepted **only if** in the opinion of the editors they are of exceptional interest and urgency」→ 门槛高；常规为「original research papers of substance」。强制 **Novelty Statement**、competing-interest 声明、**generative-AI 声明**。
- **预筛**：三份官方 Guide 中**未检索到明文 editorial triage / pre-screening 政策**——按纪律记为「未检索到」而非「确认没有」。
- ISA Trans 出版社页的「**1 day Submission to first decision**」按 skill 纪律判为**初筛速度（多快被拒）**，**不作速度排名输入**；可比数字是「56 days Submission to decision after review」与「214 days Submission to acceptance」。JFI 为 203 天投稿→录用、6 天录用→上线。

## 5. 费用（基金状态未闭合 → 免费订阅路线优先）
- **JFI**（出版社官方）：OA APC **USD 3,420**；**Subscription「No publication fee charged to authors」**、IF 3.7、CiteScore 6.4。
- **ISA Trans**：Elsevier hybrid，wos 档案标 Subscription。
- **IET CTA**：wos 档案标 **Fully Open Access（可能有版面费）** → 基金未闭合时不优先。
- **IEEE TCST**：IEEE 系有超页费 + 彩图强制费 → 对 4 图短文需按 `(页数−免费额)×每页 + 彩图数×每图` 算，本轮未列为主推。

## 6. 推荐（含改投成本）
**主投：ISA Transactions，文章类型 Technical Note。**
理由：唯一一个明确接受「初始概念验证、短、不需 regular paper 全面论证、仿真即可」的低门槛短文类型，与本稿证据形态精确匹配；SCIE/Active per ISSN；5 版预警零历史；Elsevier hybrid 免费订阅路线；scope 含 modelling & simulation / loss prevention / fundamental analysis。

**风险（如实列）**：JIF 6.5 是候选里最高门槛；Aims & Scope 写「bridge the gap between theory and practice」+「credible demonstration」，纯理论稿必须在定位句/Novelty Statement 里把「fundamental analysis of recoverability, simulation-illustrated」讲清；1 天首决提示编辑初筛，定位句是承重的。

**备选：J. Franklin Institute**（Regular paper + 强制 Novelty Statement）。理由：Aims & Scope 最理论友好（Engineering and Applied Mathematics，Control Systems 是三大主题之一）、JIF 3.7 门槛更低、745 条目/年、同样免费订阅、203 天投稿→录用。代价：无低门槛短文类型，边界稿要按 regular paper 站住。

**第三：Nonlinear Analysis: Hybrid Systems**（脉冲/混杂系统 scope 最贴、JIF 3.2，但 2024 仅 98 条目 = 窄门，不推荐）。

**改投成本**：ISA Trans 与 JFI **同为 Elsevier** → 同一个 `elsarticle.cls`（已确认本机安装）、同一套声明块、零类下载，换刊几乎零成本。

## 7. 门户与开放项（不凭记忆给 URL）
- JFI 的「Submit your article」→ `https://www.editorialmanager.com/FI/default.aspx`（出版社页实取）；ISA Trans 的投稿 URL 需投稿时从其官方作者页取，**本轮未猜**。
- **开放项**：① Clarivate MJL per-ISSN 登录确认（作者侧）；② ISA Trans 门户 URL 与文章类型标签上传前确认；③ 作者专属值（名单/ORCID/基金/单位英文名/AI 披露批准）未闭合；④ JCR/CAS 分区是年份与体系相关数字，未凭记忆断言，且 CAS 自 2026 停发分区表。

## 8. 不承诺录用
本门禁把可控项（scope fit、文章类型匹配、索引、零预警历史、免费路线、完整证据表）推到极限；不可控项（编辑读法、初筛、审稿随机性、尚未闭合的作者值与正文门禁）仍在。零预警历史 ≠ 初筛存活，两者是不同列，不互相替代。


---

## 9. 2026-11-24 改投：article type Technical Note → Research Article（同刊）

用户拍板 `改投 Research Article`。**主投期刊不变**（ISA Transactions），
只换文章类型。§1–§8 的 per-year 预警核验、SCIE 索引、免费订阅路线、
scope-fit 证据全部继续有效；§6 的「主投 Technical Note / 备选 JFI Short
Communications」这一行由本节取代。

新核实的官方硬门禁（`isa_guide_research_article.md`）：
摘要 **≤125 词**（原 191，已压到 123）、keywords 1–6（现 5）、
**Highlights 强制**（3–5 条，每条 ≤85 字符，单独可编辑文件，已产出）、
**双盲**（Title Page 与匿名稿分开，已拆分）、
生成式 AI 声明须在 References 前独立小节（已对齐官方小节标题）、
Graphical abstract 仅「encouraged」（不强制，未做）。

`gate_check.py` 的摘要上限从上一轮误用的 250 改为官方 **125**；
改后 `abstract 123 words (cap 125) PASS`、`OVERALL PASS`。

**开放项新增**：① 通讯作者完整邮政地址（官方要求，作者侧填 portal，
未编造）；② AI 声明按官方范例应写明工具名，当前保留作者既定
「language translation and polishing only」口径，未擅自扩大或编造工具名；
③ Clarivate per-ISSN、ISA 门户 URL、单双盲模型（已核为 double anonymized）、
投稿批准仍未闭合。④ 结构项（拆声明独立小标题 / Nomenclature / 章节标题精简）
仍交作者拍板，本轮只调了顺序（Conclusions → Declarations → AI → References）。


## 10. 2026-11-24：门户 / 索引 / 评审模型复核与 licence

- **Clarivate per-ISSN**：`mjl.clarivate.com/search-results?issn=0019-0578`
  经可渲染代理取回实际内容：Found 1 / Exact Match / ISA TRANSACTIONS /
  ISSN 0019-0578 / eISSN 1879-2022 /
  *Web of Science* Core Collection: **Science Citation Index Expanded**。
  与 ScienceDirect 官方 ISSN、Elsevier A&I 页三方一致。§7 的「Clarivate 登录确认
  未闭合」这一**实质部分已闭合**（页面标注部分详情需免费登录，建议作者机构
  账号复核一次，非阻塞）；历史「静态 JS 壳页不可用于断言」不再适用。
- **评审模型**：Guide 明文 double anonymized，§7 的该项闭合。
- **门户**：4 个已验证入口（ScienceDirect 期刊主页、ISA 官方 contributing 页、
  Elsevier 官方「How do I find and access my journal's submission system?」、
  Elsevier EM 说明）+ 官方「从期刊主页 Submit your article 进入」；
  `editorialmanager.com/<acronym>` 直连 **unverified、不猜**，投稿时确认。
- **出版方指标**（ScienceDirect 官方页）：首决 1 天、审后决定 56 天、
  投稿→录用 214 天、录用→上线 8 天；首决快 ≠ 录用快。
- **仓库 licence**：作者确认 MIT LICENSE，已写入并公开。
- **通讯作者完整邮政地址**：作者确认主校区地址，已写入 Title Page。

仍开放：预印本政策、公开仓库与双盲张力、投稿时 EM 直连确认、投稿批准。
不承诺录用、不宣布可直接投稿。
