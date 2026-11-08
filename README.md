# M7 Supplier Alpha — Supply Chain Research Dashboard

中文研究版可视化看板，研究 Magnificent Seven（AAPL/MSFT/GOOGL/AMZN/NVDA/META/TSLA）上游上市供应商。**研究原型，不构成投资建议；部分数据不完整时不会制造“正式 Alpha”或收益预测概率。**

## Interactive neural-style supply graph / 交互供应链图谱

研究看板的 **Supply Network** 页面新增无第三方图形依赖的 Canvas 图谱（源码 `graph-viz.js`），包含 40 家供应商 + 7 家 M7 客户：

- 默认分层布局，切换 **Orbit** 为星云布局；鼠标悬停聚焦相连节点，点击节点在右侧展开1至3跳证据路径、分数与原始出处
- 拖动节点和画布、鼠标滚轮缩放、Fit 恢复视图、按公司代码或公司名称搜索
- 动态高亮有向流动粒子、路径金色高亮；Flow 开关关闭动画，遵守系统 reduced-motion 设置
- Show all 47 nodes 可以加入全部研究候选节点，默认仅显示已验证网络节点；候选关系缺失显示 Unknown，不作为零
- 支持 English（默认）、中文、Français、Español、日本語，与原有因子、行情、政策数据同步

**GNN-inspired visual presentation only:** 本项目用 GNN 风格的分层多跳图谱呈现已核验数据，没有声称训练了 Graph Neural Network，也没有通过图形推断未知供应合同。屏幕中的发光、粒子和颜色只是展示方式；边权是证据强度代理值，不是实际采购额百分比。原 SVG 仍保留作脚本异常时的降级展示。

GitHub Actions 的 CI 增加真实 headless Chrome 浏览器测试，验证 47 个节点、关系边以及因子图 DOM 均生成；不再只依靠 JS 语法检查。

## v3.2: Data coverage and synchronized source audit

**What changed:** Added 10 new dated, primary-source M7 supply/power purchase relationships in `config/supply_graph.json`, bringing the evidence graph to 33 verifiable links. Added a reviewed set of six annual customer cash capital expenditure figures in `config/capex_primary_seed.json`; these are annual actuals from SEC or Microsoft Annual Reports and are **NOT consensus CapEx surprises**. The amount definition and fiscal-year end vary by client and are retained per record.

`scripts/enrichment.py` computes percentage-point changes from explicit customer revenue concentration disclosures (e.g. FN, ANET, STM, CRUS, SWKS). This is not proven order acceleration: source and method are attached to each factor and visible on the dashboard. True 6-factor Alpha is still `N/A` until a defensible quantitative firm-level policy exposure exists.

**New Market Monitor (P)** covers all suppliers with sufficient verified exchange-close history: cross-sectional score = 60% industry-adjusted 20-session residual momentum rank plus 40% 5-session stock return rank. It is a **PRICE-ONLY watch score**, not a supply-chain Alpha or return probability. Do not compare older v3.1 provisional scores with v3.2 proxy definitions.

**Refresh:** GitHub Actions runs twice daily at 13:30 UTC and 22:30 UTC (scheduled runs may be delayed); prior-close-only selection uses America/New_York time and discards in-progress sessions. Published GitHub Pages reads `data/latest.json` at page load and periodically checks for changes. `data/snapshots` stores dated daily snapshots.

**Optional live SEC:** Set repository Actions variable `SEC_USER_AGENT` containing an accurate research contact email. Then the script fetches newer companyfacts and recent 8-K/10-K/10-Q filing candidates from the SEC. Without this setting, six manually reviewed audited fiscal-year figures remain an explicitly labeled fallback. Companyfacts tags, ongoing news, and government policy candidates need careful validation; no keyword hit is scored as a policy shock.

The dashboard Data Audit panel lists factor completeness, CapEx source count and independent market-only monitoring coverage. Selecting a supplier opens factor-level sources and methods. Missing sources are reported as `N/A` rather than estimated contracts.
## v3.1: 40-stock and multi-hop supply graph

40家公司固定研究池（12家核心 + 28家新增候选），参见 config/universe.json。候选公司不等于已确认的M7供应商。只有双方、原始证据链接和披露日期均明确的供应关系才可进入可计算网络。未知不等于零。

有向边为供应商 → 客户。一般1至3跳路径的证据强度定义为 (沿途所有边权重的乘积) × 0.70^(跳数-1)。例如 AMAT → TSM → NVDA（2跳），UCTT → AMAT → TSM → NVDA（3跳）。权重0.65（经TSMC公开的供应商奖项）与0.80（经一手财报确认的客户/供应关系）仅为透明、可替换的定性证据代理值，不代表采购金额、Pearson相关系数或收益概率。多路径在同一个M7客户上的聚合指数上限为1，但因为路径之间可能共享节点，不能解释为独立概率之和。

原有六因子30/25/15/15/10/5权重不变，增加两跳证据加权的客户动量以及网络紧密度。研究池从12增至40，分位数口径发生变化，模型版本明确更新为 v3.1-40-multihop。v2与v3历史Alpha不可直接比较。完整6因子缺失时正式Alpha继续报告N/A。能源/电力/储能仍属独立研究属性。

新增看板「多跳 · 路径乘积」页，支持按供应商、M7客户、跳数筛选，逐段查看证据。核心代码在 scripts/network.py，数据在 config/supply_graph.json。

## Status / 状态

- 已入库：交互式中文网页、40家供应商基线、附来源的公开客户关系和历史事件、Python 行情/研究刷新程序、GitHub Actions 自动任务、离线单元测试。
- 已验证：首次 GitHub Actions 能下载40家供应商最近两个美股交易日的收盘价，并生成历史研究快照。
- 缺失：正式六因子 Alpha 在政策暴露和部分关系变化数据不足时为 **N/A**。部分股票显示的探索性评分带覆盖率，**不同缺失因子组合之间不可直接比较**。
- GitHub Pages：必须先在 **Settings → Pages → Build and deployment → Source → GitHub Actions** 开启，再到 **Actions → M7 Supplier Alpha Daily Research → Run workflow**。仓库管理权限不能由受限 GitHub connector 自动替代。
- 未实现：完整商业级行情授权、自动审核新合同/政策、经严格样本外回测的投资策略，以及与 ChatGPT 文字日报的自动历史数据同步。上述能力不能被网页原型替代。

## Website / 看板

主网页：`site/index.html`。部署成功后网址通常是：

https://violetgo319.github.io/finance_dashboard/

**仅当 Actions 完成部署后该网址才会生效。** 网页发布时自动读取 `site/data/latest.json`，在线每10分钟检查是否有新快照；网页关闭后由 Actions 在服务器定期采集。

GitHub Actions 工作流：`.github/workflows/m7-daily.yml`。每天 UTC 22:30 尝试运行（美东冬令时17:30、夏令时18:30；GitHub 的计划运行可能延迟），也支持手动运行。休市日使用最近两个已完成交易日，不把盘后价格当收盘价。脚本将每日研究快照提交到 `data/snapshots/YYYY-MM-DD.json`。

## Local / 本地运行

只依赖 Python 3.12 标准库：

```bash
python -m unittest discover -s tests -v
python scripts/refresh.py
python -m http.server 8000 --directory site
```

浏览器访问 http://localhost:8000。

行情先尝试 Stooq，再尝试 Yahoo Chart；两个公开接口都不保证持续可用、真实交易所口径或公开再分发授权，失效时该项记为 N/A。公开网站使用行情前请自行确认数据源的许可要求。

## SEC and policy / 财报和政策

如果希望采集 SEC 已公开的财报 CAPEX 与文件候选，请在 GitHub **Settings → Secrets and variables → Actions → Variables** 配置 `SEC_USER_AGENT`，内容包含真实的学术研究联系人邮箱（例如 `Institutional Research research-contact@university.edu`）；不要使用不存在的邮箱。未配置时 SEC 访问自动跳过，绝不推断缺失数据。

CAPEX 仅使用已披露的两个相邻完整财政年度的现金购置固定资产数据的同比变动，**不等于市场一致预期 surprise**。最新8-K/10-K/10-Q和 Federal Register 关键词命中只进入 `filing_candidates` / `policy_candidates`，必须人工审核后才能进入可交易因子。网页内历史重大政策仅作为背景及原文证据，不代表自动政策评分。


## Energy / Power / Storage 三维属性（v2.1）

新增加的**能源（发电与一次能源技术）、电力（输配电、UPS、功率电子）、储能（BESS、电池和备份储能）**为独立研究属性，不改变原六因子 Alpha 权重。这里的 Storage 指能量储存，而不是 MU 的 HBM/DRAM/SSD 数据存储。

- 数据库配置：`config/infrastructure_dimensions.json`，包括三个维度定义与已核验的产品层证据、官方链接、核验日期和角色。
- 自动数据快照：`scripts/refresh.py` 会将这些证据复制到每日 `data/latest.json` 的 `infrastructure` 字段，并根据日期排除未来信息。
- 网页新增「能源 · 电力 · 储能」页，按维度/公司筛选，显示官方证据和未核验状态。不存在公开资料不代表没有业务，该格记为未知，**不是零分**。
- 第一批可核验的产品能力包括 STM 太阳能逆变器器件、功率管理和商业储能器件，VRT 关键供配电与 BESS，以及 APH 电力互连产品。以上均不代表确认这些产品已向任一七巨头供货；营收、容量、订单金额也未推断。详情与原文见配置文件及网页。
- 该功能仅用于供应链研究，若之后要做 Energy/Power/Storage Alpha，需要先建立上市供应商披露数据、地域/需求冲击与可交易样本外回测，再决定新模型版本。

## Scoring / 打分

| Factor | Weight | Research implementation |
|---|---:|---|
| Relationship acceleration | 30% | 已核实客户收入占比年度变化；无披露则N/A |
| Customer demand | 25% | 可得时的SEC年度CapEx同比增速代理，非预期差 |
| Verified linkage | 15% | 已确认客户关系边及类型，非采购金额 |
| Customer momentum | 15% | 相关七巨头20交易日收益加权分位数 |
| Policy impact | 10% | 仅人工确认的政策暴露；目前自动刷新保持N/A |
| Residual momentum | 5% | 供应商20日收益 - OLS beta × XLK 20日收益 |

正式分数需要六项完整，缺失时为N/A；探索性分数仅将已可计算的因子按原比例重新归一，并同时显示数据覆盖率。v3股票池共40家，详见 config/universe.json。

**方法限制：** 供应商收入占比不同于七巨头采购额；已披露客户关系数不等于全量合作网络；合同最高金额不等于已实现订单收入。需长期监测点时可得数据、回测滑点与稳定性，才可将研究信号用于真实投资。

## Data files

- `data/latest.json`：每次自动运行的完整可审计快照
- `data/snapshots/*.json`：按日期的研究快照
- `site/data/latest.json`：此次 GitHub Pages 发布构建中生成的前端快照
- `scripts/refresh.py`：抓取、分位数计算、缺失值处理、审计候选采集
- `tests/test_refresh.py`：纯离线逻辑测试

原始来源可通过快照中每条关系的 `source`、各个价格的 `price_source` 等链接追溯。

完整离线 v2 研究包仍保留在本次 ChatGPT 会话的原始交付文件中。本仓库采用适合 GitHub Pages 的轻量自动部署实现，而非声称已上线完整版商业数据平台。

### 2026-11-07 股票池公司事件修订

NASDAQ公告 Qorvo (QRVO) 与 Skyworks (SWKS) 于2026-10-05合并，QRVO最后交易日为2026-10-02。为避免将退市股票错误放在实时40股池，QRVO已替换为仍上市的 UCTT（Ultra Clean Holdings）。UCTT 2025财年年报明确其客户包含 Lam Research 和 Applied Materials，因此可以通过公开关系形成3跳候选路径。资料链接：https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2026-702 与 https://www.sec.gov/Archives/edgar/data/1275014/000162828026010744/uctt-20251226.htm 。

台积电2025年供应商表彰名单官方披露日期为2025-11-28，并已据此更正所有对应关系边的时间戳。原始公告：https://pr.tsmc.com/schinese/news/3274 。
