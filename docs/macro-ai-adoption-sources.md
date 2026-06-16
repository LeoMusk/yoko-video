# 宏观 AI 采用数据源接入说明

接入时间：2026-06-05

## 接入策略

宏观企业 AI 采用数据源多数没有 RSS，因此 M1 新增 `mode="watch"`：

- 抓取网页或 PDF。
- 清洗页面正文或读取 PDF 二进制。
- 计算内容哈希。
- 只有哈希变化时才写入 `data/raw/YYYY-MM-DD.jsonl`。
- 可用 `python -m yoko_video.m1.collect --tier DATA` 单独采集。
- 可用 `python scripts/verify_macro_ai_sources.py` 做稳定性检查。

这样可以把 Census、Ramp、Stanford、Fed、Morgan Stanley 等低频高价值源纳入 M1，同时避免每天重复污染选题池。

## 自动接入源

| source | 类型 | 价值 |
|---|---|---|
| `census-btos-ai` | macro-data | 美国企业 AI 采用率首选官方基准，双周频率，按行业/地区/规模拆分 |
| `census-ai-use-businesses` | macro-data | Census 对 BTOS AI supplement 的官方解读 |
| `ramp-ai-index` | index | 基于企业实际付费交易的 AI 产品采用领先指标 |
| `fed-ai-adoption-monitor` | macro-data | Fed 对 BTOS/RPS/SBU 等不同口径的校准分析 |
| `stanford-ai-index-economy` | index | 年度 AI Index 经济章节，汇总组织采用、生产率和劳动力影响 |
| `anthropic-economic-index` | index | 基于 Claude 和企业 API 使用的任务级 AI 使用数据 |
| `morgan-stanley-ai-adoption` | report | 企业高管调查，关注 AI 对生产率和就业的影响 |
| `deloitte-state-ai-enterprise` | report | 企业从试点到规模化、AI fluency、agentic AI 调研 |
| `eurostat-enterprise-ai` | macro-data | EU 官方企业 AI 使用率，含 `isoc_eb_ai` 数据集入口 |
| `oecd-ai-adoption-firms` | macro-data | OECD/BCG/INSEAD 企业 AI 采用官方 PDF 报告 |
| `pwc-ai-performance-study` | report | 企业 AI 价值、ROI、收入/效率/成本收益补充指标 |
| `uk-dsit-ai-adoption-research` | macro-data | 英国政府企业 AI 采用、障碍和影响调查 |

## 暂不自动接入

| source | 原因 | 处理 |
|---|---|---|
| McKinsey State of AI | 官方网页和官方 PDF 在本地 `urllib` 采集下持续超时 | 作为人工参考源，不进入默认 M1，避免长期失败项 |
| OECD topic page | 官方网页 403 | 改用官方 PDF 报告 URL |

## 验证记录

最新稳定性结果写入：

- `docs/macro_ai_sources_status.md`
- `docs/macro_ai_sources_status.json`

2026-06-05 首次验证：12 个自动源全部可达；首次 M1 采集写入 12 条；第二次采集 `new 0`，哈希去重生效。
