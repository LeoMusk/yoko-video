# 信息源可行性调研结果

测试时间：2026-05-27
测试范围：Tier 1（一手） + Tier 2（Newsletter/播客） + 3 个中文头部（36氪/量子位/机器之心）
共测候选 URL 数：59（含重试和补充候选）

> 备注：所有"X、付费 API、其他中文 RSS"按用户指示**不在本次调研范围**内。
> 自动化测试原始结果保存在 `sources_status.json` 和 `sources_status_retry.json`。

---

## ✅ 可直接接入（17 个，覆盖 80%+ 信息需求）

按价值密度 × 更新频率排序：

### Tier 1 一手（10 个）

| 名称 | URL | 最新更新 | 日均量 | 说明 |
|---|---|---|---|---|
| **arXiv cs.AI** | `http://export.arxiv.org/rss/cs.AI` | 当日 | 461 篇 | 量大，依赖 M2 强过滤 |
| **arXiv cs.CL** | `http://export.arxiv.org/rss/cs.CL` | 当日 | 253 篇 | 自然语言/LLM 论文集中区 |
| **arXiv cs.LG** | `http://export.arxiv.org/rss/cs.LG` | 当日 | 410 篇 | 机器学习论文 |
| **HackerNews Front** | `https://news.ycombinator.com/rss` | 实时 | 30 条 | 科技舆论风向 |
| **HackerNews Best** | `https://hnrss.org/best` | 滚动 | 30 条 | 高质量内容沉淀 |
| **OpenAI News** | `https://openai.com/news/rss.xml` | 2-7 天 | 低频 | 厂商一手；`/blog/rss.xml` 是同源别名 |
| **Google DeepMind** | `https://deepmind.google/blog/rss.xml` | 1-7 天 | 低频 | 厂商一手 |
| **Google AI Blog** | `https://blog.google/technology/ai/rss/` | 1-7 天 | 低频 | Google 产品+研究 AI 频道 |
| **HuggingFace Blog** | `https://huggingface.co/blog/feed.xml` | 1-3 天 | 中 | 开源模型/技术 trick |
| **Microsoft Research** | `https://www.microsoft.com/en-us/research/feed/` | 1-7 天 | 低频 | **必须用 Chrome UA**，默认 UA 被 403 |

### Tier 2 Newsletter/播客（6 个）

| 名称 | URL | 更新频率 | 说明 |
|---|---|---|---|
| **Import AI** | `https://importai.substack.com/feed` | 周更 | Anthropic 联创 Jack Clark 周记，独到视角 |
| **Latent Space** | `https://www.latent.space/feed` | 多更 | 含 [AINews] 每日精选 + Swyx 访谈 |
| **Last Week in AI** | `https://lastweekin.ai/feed` | 周更 | 综合 AI 新闻周报 |
| **Stratechery** | `https://stratechery.com/feed/` | 多更 | 多数付费墙；headlines + 偶尔免费篇有战略级解读 |
| **Dwarkesh Podcast** | `https://www.dwarkesh.com/feed` | 不定期 | 与大佬深度对话，含 transcript |
| **Ben's Bites** | `https://bensbites.com/feed` | 日更 | AI 圈日报，**正确 URL 是裸域** |

### 中文头部（2 个）

| 名称 | URL | 更新 | 说明 |
|---|---|---|---|
| **36氪** | `https://36kr.com/feed` | 实时 | 官方 RSS 可用，AI/科技/商业综合 |
| **量子位** | `https://www.qbitai.com/feed` | 日更 | 官方 RSS 可用，AI 科普为主 |

### 调研中发现的额外好源（建议加入）

| 名称 | URL | 价值 |
|---|---|---|
| **Simon Willison's Weblog** | `https://simonwillison.net/atom/everything/` | LLM 工程实践高质量个人博客，更新极勤 |
| **Sequoia Perspectives** | `https://www.sequoiacap.com/feed/` | 红杉 AI 投资视角，文章稀但每篇有信号 |

不建议加入但顺便测过的：
- `https://buttondown.email/ainews/rss` ⚠️ 最近 entry 2025-04，疑似停更
- `https://rsshub.rssforever.com/...` 备用 RSSHub 镜像可用，但目前现状下用不到

---

## ❌ 调研无解（4 个，需替代策略或放弃）

| 名称 | 失败原因 | 建议 |
|---|---|---|
| **Anthropic News** | 官方完全不提供 RSS（所有 `/feed.xml`、`/rss.xml`、`/news/feed` 都 404） | **放弃。** Anthropic 官宣会在 HN 前页和 Import AI / Latent Space / Ben's Bites 出现，覆盖丢失可控 |
| **Meta AI Blog** | 所有候选路径 404/400/SSL 错。Meta 不提供原生 RSS | **放弃。** 重要发布（Llama 系列）会出现在 HN + HuggingFace + Last Week in AI |
| **The Batch (deeplearning.ai)** | `deeplearning.ai` 所有 RSS 路径 404，疑似官方已下线 | **放弃。** 内容会被 Import AI / Last Week in AI 覆盖 |
| **机器之心** | 官方 RSS 端点返回 200 但 feed 体为空（坏的）；RSSHub 公共实例 403 | **暂时放弃**，由 36氪 + 量子位 覆盖中文头部 |

**核心判断**：放弃这 4 个不会显著降低 MVP 信号覆盖度。重要事件具有"跨源出现"特性——任何 OpenAI/Anthropic/Meta 的大事件都会在 1-3 个其他源出现。损失的是"获知速度"和"独家解读"两个维度，对周频出片够用。

如果未来确实需要补回：
- **Anthropic / Meta** — 用 changedetection.io 这类页面变更监控工具
- **The Batch** — 邮件订阅 + 写邮件解析脚本
- **机器之心** — 微信公众号第三方服务（WeRSS 等）或 RSSHub 自建

这些都放到"MVP 跑通之后"再做。

---

## 关键工程结论（决定 M1 设计）

1. **Tier 1 + Tier 2 + 中文 共 18 个源足以驱动 MVP**（含 2 个额外好源），工程量很小（HTTP GET + feedparser 解析，单次几十秒）
2. **arXiv 三个分类合计 1100+ 条/天**——M2 过滤压力主要来自这里，需要专门的论文过滤策略（重要性评分要考虑 author、citation potential、topic match）
3. **需要 User-Agent 处理**：至少要支持 Chrome UA（Microsoft Research 强制要求），默认 UA 会被部分源 403
4. **不依赖 RSSHub 公共实例**：`rsshub.app` SSL 握手不稳定，按需用 `rsshub.rssforever.com` 备用镜像或自建（目前已无强需求）
5. **厂商官方 feed 更新慢**（OpenAI/Google/DeepMind 2-7 天）→ 实时性不能指望它们，靠 HN + Newsletter 抢首发
6. **18 个源里有 13 个英文 + 2 个中文 + 3 个 arXiv** → 中文权重低，符合用户"优先国外一手"的指示

---

## 下一步建议

1. **直接进入 M1 实现**：源已收敛，可以开始写采集脚本（18 个 feed，目标每日产出 JSONL）
2. **并行准备 M2 prompt**：等 M1 跑出 1-2 天的 raw data，再针对实际样本调评分 prompt
3. **暂不再为信息源花更多时间**：可行性已确认；剩余的"完美主义"补源工作收益递减
