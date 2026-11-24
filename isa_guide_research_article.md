# ISA Transactions Guide for Authors — article-type evidence (internal)

**Verified**: 2026-11-24 by fetching https://www.sciencedirect.com/journal/isa-transactions/publish/guide-for-authors
(full fetched page archived locally as an internal verification artifact)

## Article types (verbatim)
> *ISA Transactions* publishes **Research Articles**, **Practice Articles** & **Letters**.

> **Research Articles**: These can be from either of the categories that follow, and will
> primarily relate to research, investigation, and to possibilities. Research Articles
> focus on the fundamental analysis or mathematics of a technique, and are **illustrated
> with simulations**, and are written by, and for, those in research.

> **Technical Notes**: Present new concepts or initial proof-of-concept results on
> innovative approaches. The manuscripts would be short, perhaps two journal pages, and
> would **not require extensive comprehensive defence required of regular papers**. ...
> The title must start with the identification "Technical Note:"

Consequence: a Research Article removes the ~2-page ceiling and the mandatory
"Technical Note:" title prefix, but **does** require the comprehensive defence that
Technical Notes are explicitly exempted from. Aims and scope additionally require
"credible demonstration" and "connectivity to the state of the art".

## Mandatory at initial submission (verbatim / paraphrased with quotes)
- **Peer review**: "This journal follows a double anonymized review process".
  "The title page (including author details) and anonymized manuscript (excluding
  author details) need to be submitted as separate files."
  "The anonymized manuscript should contain the main body of your paper, including
  references and tables. It is important that your manuscript and any supplementary
  materials do not contain any identifying information such as author names or
  affiliations, or acknowledgements."
  "Include acknowledgements only in the title page".
- **Abstract**: "does not exceed 125 words".
- **Keywords**: "1 to 6 keywords".
- **Highlights**: "You are required to provide article highlights at submission."
  "Submit highlights as a separate editable file ... with the word 'highlights'
  included in the file name." "3 to 5 bullet points, each a maximum of 85 characters,
  including spaces."
- **Graphical abstract**: "You are encouraged" (optional, NOT mandatory).
- **Generative-AI declaration**: "Authors must declare the use of generative AI tools
  in the manuscript preparation process upon submission". The statement "should be
  placed in a new section before the references list"; recommended section title
  *Declaration of generative AI and AI-assisted technologies in the manuscript
  preparation process.*
- **Title page** must carry the corresponding author's full postal address and email.

## What this means for the retarget
Article type is a bigger lever than venue prestige: this move raises the evidence
threshold. The manuscript's weakest formal-review dimensions are L3 novelty /
significance / completeness, and no new evidence was added in this round. The
retarget fixes FORMAT and L1/L2 compliance; it does NOT change L3.


---

## 附录：投稿门户 / 索引 / 评审模型复核（2026-11-24，web_search + 页面取回）

### Clarivate per-ISSN — **已实质闭合**
取 `https://mjl.clarivate.com/search-results?issn=0019-0578`（经 reader proxy
渲染，页面自身标注 `URL Source: https://mjl.clarivate.com/search-results?issn=0019-0578`，
`Published Time: Wed, 28 Oct 2026`）：

> Found 1 results / **Exact Match Found** — ISA TRANSACTIONS
> Publisher: ELSEVIER SCIENCE INC, 101 Park Avenue, 24th Floor, NEW YORK
> ISSN / eISSN: **0019-0578 / 1879-2022**
> *Web of Science* Core Collection: **Science Citation Index Expanded**
> Additional Web of Science Indexes: Current Contents Engineering, Computing &
> Technology | Essential Science Indicators

按 `sci-venue-selection` 的判据读的就是 "Web of Science Core Collection" 这一行，
**SCIE 通过**（不是 ESCI）。与 ScienceDirect 期刊主页的 Print ISSN 0019-0578 /
Online ISSN 1879-2022 一致，也与 Elsevier 官方 Abstracting & Indexing 页
（`journals.elsevier.com/isa-transactions/abstracting-indexing`，列
Science Citation Index Expanded）三方一致。
页面标注 `* Requires free login.` → 完整详情需免费登录；**建议作者在机构账号下
复核一次（非阻塞）**，本文件不把代理渲染冒充作者登录确认。
历史 blocker「mjl.clarivate.com 静态 JS 壳页不可用于 per-ISSN 断言」此前成立，
本次是通过可渲染代理取得实际内容，故该 blocker 解除。

### 评审模型 — **已闭合**
Guide for Authors: *"This journal follows a double anonymized review process."*
上一轮已据此拆分 Title Page + 匿名稿；本轮复核确认。

### 投稿门户 — **部分闭合（直接 EM 链接不猜）**
已验证可取回的页面：
- 期刊主页（ScienceDirect）：`https://www.sciencedirect.com/journal/isa-transactions`
- ISA 官方 contributing 页：
  `https://www.isa.org/standards-and-publications/isa-publications/isa-transactions/contributing-to-isa-transactions`
  （其「online submission and editorial system」指向旧域
  `http://www.journals.elsevier.com/isa-transactions`，可能重定向，未作为最终 URL）
- Elsevier 官方支持页「How do I find and access my journal's submission system?」：
  `https://service.elsevier.com/app/answers/detail/a_id/8000/supporthub/assessment-builder`
- Elsevier 官方 EM 说明：`https://www.elsevier.com/editor/submission-systems`

**官方口径**：投稿走 Editorial Manager，各刊有 `editorialmanager.com/xxxxx`
直接链接，但必须从期刊主页的 **"Submit your article"** 进入；期刊主页为
JS 渲染，静态抽取拿不到该链接。**按 skill 明令不猜 venue-specific EM URL**
—— 上面四个已验证入口 + 「从主页 Submit your article 进入」就是可给的全部，
直接 EM 地址标为 **unverified / 作者上传前在门户确认**。

### 出版方官方指标（ScienceDirect 期刊主页，非第三方）
Submission to first decision **1 day**；Submission to decision after review
**56 days**；Submission to acceptance **214 days**；Acceptance to online
publication **8 days**。注意 first-decision 快不代表录用快（skill：两者不同轴）。
