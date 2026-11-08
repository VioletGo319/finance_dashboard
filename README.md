# M7 Supplier Alpha — Research Dashboard v2

**定位：美国科技七巨头可核验证据支持的上游供应链研究。** 本项目包括 Python 公开数据采集、带时间戳的可解释六因子研究引擎、SQLite / JSON 历史归档、无需前端构建的交互式中文看板，以及 GitHub Actions 定期刷新 + GitHub Pages 部署工作流。

> **重要：本包有真实的历史公开披露，但截至本次交付并没有在本地获得最新交易日行情。** 因此初始快照显示价格 `N/A`。有些公司显示带 `†` 的**探索性评分**（仅由可得、已核验部分因子计算），不是正式六因子 Alpha，也不是收益上涨概率。未获得可靠的数据绝不造数。

## 目录

```
.github/workflows/research-dashboard.yml   定时采集 + 自动提交快照 + GitHub Pages 部署
m7alpha/sources.py                         Stooq/Yahoo 每日收盘价 + SEC + Federal Register
m7alpha/core.py                            点时过滤、六因子分数、收益与OLS beta
m7alpha/pipeline.py                        端到端调度、打分、导出
m7alpha/storage.py                         SQLite审计、JSON快照
config/research_seed.json                  12家池子 + 核实的供应关系/合同/政策历史
config/policy_effects.json                 经人工确认的供应商政策暴露（默认空）
site/index.html                             手机/桌面响应式交互看板
site/data/latest.json,latest.js            网页每日快照（可本地 file:// 读取）
site/data/history.json                     最近90个研究快照
site/data/candidates.json                  尚未审核的SEC文件/政策候选
site/data/                                    JSON每日数据
 data/history.sqlite                       本地研究数据库（不纳入Git版本控制）
 data/snapshots/YYYY-MM-DD.json             每个日期的完整点时研究快照（纳入Git）
tests/                                     可重复离线单元测试
```

## 本地运行：无需安装 Python 第三方包

在项目根目录：

```bash
python -m unittest discover -s tests -v
python -m m7alpha.pipeline
python -m http.server 8000 --directory site
```

浏览器访问 `http://localhost:8000`。也可以直接双击 `site/index.html`；它通过 `data/latest.js` 加载与其相邻的真实快照，不需要服务器。在线托管时会每10分钟检查一次新快照，数据变更后自动刷新；关闭网页时不会自己执行采集。采集任务必须由 Python 命令、定时任务或 GitHub Actions 运行。

若只想验证无网络环境下的**严格缺失值处理**：

```bash
python -m m7alpha.pipeline --offline --as-of 2026-11-07
```

命令不会生成真实价格。因子缺失保持 null；若某个股票有足够的**部分已核实因子**，可显示明确标注的 `provisional_alpha`。不要将离线输出作为正式收盘后的报告。

## 自动部署到 GitHub（前置条件：你拥有的新/现有目标仓库）

1. 在 GitHub 上新建一个**空的 Public repository**，例如 `m7-supplier-alpha`。如研究包含非公开数据，请使用私有仓库并先核查 Pages 套餐、发布内容的权限。**本包仅包含公共研究数据**，不包含任何私钥。
2. 把 ZIP 里项目的所有文件放到仓库**根目录**，保持 `.github/workflows/research-dashboard.yml` 路径。网页位于 `site/`，不是项目根目录。
3. 在该仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。GitHub Pages 并非本地工具能够代替你启用的开关。
4. 可选但建议：**Settings → Secrets and variables → Actions → Variables** 新增 `SEC_USER_AGENT`，例如 `Your Research Project contact=your-real-email@university.edu`，使 SEC 公司财报资本开支数据与最新 8-K 列表可以被合法请求。不配置该值时，价格更新仍可尝试，SEC 采集会跳过，不会捏造。
5. 在 **Actions** 中执行 `M7 Supplier Alpha — Daily Research Dashboard → Run workflow` 一次。后续每日 UTC 23:20 自动运行（约美东 18:20 冬令时 / 19:20 夏令时；GitHub Actions 不保证到秒）。成功运行将：拉取行情和文件 → 跑测试 → 生成 `site/data/*` → 提交日期快照到仓库 → 部署 Pages。
6. 部署完成后，GitHub Pages URL 通常为 `https://<账号>.github.io/<仓库名>/`，实际请以 GitHub Actions 运行结果返回的 URL 为准。若首次没有启动 Pages，请按第3步开启。

[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)

**避免在尚未设定目标仓库时将项目上传到与你无关的公开仓库。** ChatGPT 已有的晚间定时文字日报与 GitHub Actions 是两个独立任务，不会自动共享持久数据库；本项目未来的自动看板更新由 GitHub Actions 自行负责。

## 每天会获得的数据

1. 12家股票（TSM、AVGO、ANET、COHR、LITE、FN、GLW、CLS、MU、VRT、APH、STM）的最近与前一交易日**收盘价**，两日日期、来源 URL 和数据质量。行情优先使用 Stooq CSV，失败回退 Yahoo Chart JSON。二者皆非交易所保证的收费行情，变化、限流、口径差异都可能发生；切换来源时历史分数比较会被禁止。
2. 七巨头相关披露的已核验供应链关系、收入占比与多年度合同。**未披露不等于零，合同上限不等于已实现收入。** 初始记录来自 SEC 10-K/20-F 及公司IR，有披露日期与源链接。
3. 经人工审核的事件及政策时间线。系统每天自动获取 SEC 客户8-K/10-K/10-Q 候选文件和 Federal Register 关键词搜索候选；这些**只放进待审清单，不会自动生成利好/利空政策打分**。需要研究员核查原文后才能添加到经审核关系或政策暴露库。
4. 历史快照归档至 `data/snapshots`、研究数据库至本地 SQLite。无需保留一个长期运行的服务器。

## 模型：严格六因子 vs 探索性分数

固定预注册权重：

| 因子 | 权重 | v2可审计实现 |
|---|---:|---|
| 合作加速度 | 30% | SEC/IR 公告的客户收入占比年度变化（百分点）；缺公开历史则N/A |
| 客户需求超预期 | 25% | **只做代理**：七巨头SEC最近两个已公布财政年度的CAPEX同比增长，按已核验关系加权；它并非一致预期 surprise |
| 合作紧密度 | 15% | 已公开核实的关系边数量与证据类别；只衡量**documented links**，绝不等价于实际采购量 |
| 客户动量 | 15% | 已披露客户的20交易日收益（按证据关系加权） |
| 政策暴露 | 10% | **仅审核过**的公司级政策影响映射；没有合格证据则N/A |
| 残差动量 | 5% | 供应商过去20交易日收益减去OLS beta×XLK收益；beta基于60个同步日收益估计 |

各个原始因子采用可得股票的横截面中位秩百分位转换至0–100。可比样本不足3家则该因子N/A。注意：按部分行业暴露的XLK对冲不是完整的风险中性回归，更不是已证明的超额收益。正式评分只在六项都有效时计算：`sum(w_k * factor_k)`。探索性分数 `†` 是对可用因子的固定权重重新归一化，并列出总覆盖权重，**不能跨不同可得因子集合直接比较**。自动日报对缺失依旧标明。

### 方法的局限（论文写作必须保留）

- 合同公告可能与后续销售不对应；关系边有不均匀的披露概率，不能把未披露边设为零关系。
- SEC公司财报的年度CAPEX同比增长 **不等于分析师预期偏差**；正式研究中应以事前预测或市场一致预期的数据来替换。
- 加速度仅使用有历史披露比例的少量公司，对无披露公司必须标记N/A。没有自动化 NLP 审核不能把未来新闻转成合格的交易信号。
- 用横截面分位排名构造股票间信号，不能保证小样本的统计效力。任何实盘部署都需要数据授权、样本外回测、费用/滑点和风险约束。
- SEC接口遵循不高于10次/秒的公平访问要求。没有 `SEC_USER_AGENT` 不自动请求。
- Stooq/Yahoo仅用于非商业研究和原型。商业发行/公开批量分发前，请审核数据许可证或替换授权行情供应商。
- 工作流执行时间与是否获取价格受 GitHub、网络及第三方行情服务可用性影响，不应向使用者保证每天所有字段都有分数。

## 高质量论文扩展

推荐进一步引入：FactSet Revere 等**合法授权的历史关系库**、基于历史披露时间的因果/事件研究、封闭式动态网络建模、样本外回测及足够的样本维数。初始12家仅是可审计的种子池，不支持强泛化推断。

## 来源

- [SEC EDGAR 官方数据接口](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC Fair Access 指南](https://www.sec.gov/about/developer-resources)
- [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1)
- [GitHub Pages Actions 部署](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

版权所有用户自己的研究项目；本包作为研究开发原型交付，不构成证券投资建议。