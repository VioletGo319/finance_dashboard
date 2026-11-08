# M7 Supplier Alpha — Supply Chain Research Dashboard

中文研究版可视化看板，研究 Magnificent Seven（AAPL/MSFT/GOOGL/AMZN/NVDA/META/TSLA）上游上市供应商。**研究原型，不构成投资建议；部分数据不完整时不会制造“正式 Alpha”或收益预测概率。**

## Status / 状态

- 已入库：交互式中文网页、12家供应商基线、附来源的公开客户关系和历史事件、Python 行情/研究刷新程序、GitHub Actions 自动任务、离线单元测试。
- 已验证：首次 GitHub Actions 能下载12家供应商最近两个美股交易日的收盘价，并生成历史研究快照。
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

## Scoring / 打分

| Factor | Weight | Research implementation |
|---|---:|---|
| Relationship acceleration | 30% | 已核实客户收入占比年度变化；无披露则N/A |
| Customer demand | 25% | 可得时的SEC年度CapEx同比增速代理，非预期差 |
| Verified linkage | 15% | 已确认客户关系边及类型，非采购金额 |
| Customer momentum | 15% | 相关七巨头20交易日收益加权分位数 |
| Policy impact | 10% | 仅人工确认的政策暴露；目前自动刷新保持N/A |
| Residual momentum | 5% | 供应商20日收益 - OLS beta × XLK 20日收益 |

正式分数需要六项完整，缺失时为N/A；探索性分数仅将已可计算的因子按原比例重新归一，并同时显示数据覆盖率。当前股票池：TSM、AVGO、ANET、COHR、LITE、FN、GLW、CLS、MU、VRT、APH、STM。

**方法限制：** 供应商收入占比不同于七巨头采购额；已披露客户关系数不等于全量合作网络；合同最高金额不等于已实现订单收入。需长期监测点时可得数据、回测滑点与稳定性，才可将研究信号用于真实投资。

## Data files

- `data/latest.json`：每次自动运行的完整可审计快照
- `data/snapshots/*.json`：按日期的研究快照
- `site/data/latest.json`：此次 GitHub Pages 发布构建中生成的前端快照
- `scripts/refresh.py`：抓取、分位数计算、缺失值处理、审计候选采集
- `tests/test_refresh.py`：纯离线逻辑测试

原始来源可通过快照中每条关系的 `source`、各个价格的 `price_source` 等链接追溯。

完整离线 v2 研究包仍保留在本次 ChatGPT 会话的原始交付文件中。本仓库采用适合 GitHub Pages 的轻量自动部署实现，而非声称已上线完整版商业数据平台。
