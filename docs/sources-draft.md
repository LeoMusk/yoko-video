# 信息源候选清单（待筛选）

> 这是初稿，列了 ~40 个候选信源，按"价值密度 × 接入成本"分级。请逐项标记 **保留 / 待评估 / 剔除**，对保留的可以加优先级。所有 URL 标记为"待验证"——开源 RSS 项目死亡率确实高，最终需要逐个 ping 测活。

## 优先级判断维度

判断一个源该不该接，看这 4 个维度：

1. **信号密度**：每天产出的内容里"值得做视频"的比例（5% vs 50%）
2. **首发性**：内容是源头首发，还是已经在其他渠道被消费过
3. **接入成本**：RSS 直连 < 第三方聚合 < 官方 API < 爬虫
4. **稳定性**：源是否在持续更新、接入方式是否容易失效

---

## Tier 1：核心信源（必接，RSS 优先）

| 信源 | 类型 | 接入方式 | 价值 | 备注 |
|---|---|---|---|---|
| **arXiv cs.AI / cs.CL / cs.LG** | 论文 | 官方 RSS | 顶级一手信源，AI 研究 0 延迟 | 量大（每日数百篇），M2 过滤压力高 |
| **Hacker News (front page)** | 综合科技 | 官方 RSS | AI/科技舆论风向标 | 评论区也有价值 |
| **GitHub Trending (daily/weekly)** | 开源动态 | RSSHub 自建 | 新工具、新项目首发地 | 官方无 RSS，RSSHub 实现已知稳定 |
| **OpenAI Blog** | 厂商动态 | 官方 RSS（待验证） | OpenAI 一手发布 | 频率低但每条价值极高 |
| **Anthropic News** | 厂商动态 | 官方 RSS（待验证） | Anthropic 一手发布 | 同上 |
| **Google DeepMind Blog** | 厂商动态 | 官方 RSS（待验证） | Google AI 一手 | — |
| **Meta AI Blog** | 厂商动态 | 官方 RSS（待验证） | Meta（含开源 LLaMA 系列） | — |
| **Microsoft Research Blog** | 厂商动态 | 官方 RSS | 重要论文/产品 | 频率中 |
| **HuggingFace Blog / Papers** | 开源生态 | RSS / API | 模型发布、技术 trick | Papers 频道含每日热门论文 |
| **ProductHunt - AI 分类** | 产品发布 | API / RSS | AI 工具发布趋势 | 噪音多但发现性好 |

## Tier 2：深度信源（Newsletter / 播客 / 社区）

| 信源 | 类型 | 接入方式 | 价值 | 备注 |
|---|---|---|---|---|
| **The Batch (deeplearning.ai)** | 周刊 | RSS | Andrew Ng 团队精选 | 周更，浓度高 |
| **Import AI (Jack Clark)** | 周刊 | Substack RSS | Anthropic 联创的周记 | 个人视角，独到 |
| **Latent Space** | 双周刊 + 播客 | Substack RSS | 技术深度 | 含 Swyx 访谈 |
| **Ben's Bites** | 日刊 | Substack RSS | AI 圈日报 | 简洁，适合做"晨报"源 |
| **Last Week in AI** | 周刊 + 播客 | RSS | 综合 AI 新闻 | — |
| **The Information AI 频道** | 媒体 | 付费 / RSS | 商业角度深度报道 | 付费墙，需评估订阅 |
| **Stratechery / Ben Thompson** | 评论 | Substack RSS | 战略/商业视角解读 | 偶有 AI 深度内容 |
| **Dwarkesh Podcast transcripts** | 长播客 | RSS | 与 AI 大佬深度对话 | transcript 含金量高 |
| **Lex Fridman transcripts** | 长播客 | RSS | 同上，更多元 | — |
| **Y Combinator Launch HN** | 创业动态 | HN 标签筛选 | AI 公司首发 | — |

## Tier 3：Twitter / X（核心账号监控）

> 这是难点区域：X 官方 API 月费 $100 起，Nitter 等开源镜像已大量停服，第三方聚合服务质量参差。建议作为**独立可行性专题**研究。

候选关键账号（人/组织，待筛减到 30 个以内）：
- 厂商官号：@OpenAI, @AnthropicAI, @GoogleDeepMind, @Meta, @MistralAI, @xAI, @perplexity_ai
- 厂商高管：@sama, @darioamodei, @ylecun, @sundarpichai, @elonmusk
- 研究者：@karpathy, @ylecun, @jeremyphoward, @ilyasut, @goodside
- 产品/创业方向：@swyx, @AravSrinivas, @amasad, @levelsio
- 中文 AI KOL：（待补充，需选）

接入方案候选（按可靠性 × 成本）：
1. **官方 X API Basic** ($100/月)：稳定但贵；推文上限有约束
2. **第三方聚合服务**（如 socialdata.tools、TweetScout）：成本较低但有合规风险
3. **自建 Nitter / 现存镜像**：免费但稳定性差，反爬升级后失效快
4. **完全放弃 Twitter**：用 HN + arXiv + Newsletter 覆盖大部分核心信号（损失独家爆料）

## Tier 4：中文同行 / 竞品监控

> 目的是避免选题撞车 + 反向情报（看同行在做什么）。

| 信源 | 类型 | 接入方式 | 备注 |
|---|---|---|---|
| **36 氪 AI 频道** | 媒体 | 官方 RSS / RSSHub | — |
| **机器之心** | 媒体 | RSSHub | 偏研究 |
| **量子位** | 媒体 | RSSHub | 偏科普 |
| **AIGC 开放社区** | 媒体 | RSSHub（待验证） | — |
| **Founder Park** | 媒体 | 公众号 → 第三方 | 关注创业/产品 |
| **微信公众号头部 AI 号** | 自媒体 | 第三方服务（WeRSS / wxnmp 等） | 列 10-20 个，待筛 |
| **知乎"人工智能"话题** | 社区 | RSSHub | — |
| **即刻 AI 圈子 / 小红书 AI 博主** | 社区 | RSSHub / 手动 | C 端用户视角 |
| **抖音同赛道账号** | 视频 | 第三方监控工具 | 用于"看同行爆款" |

## Tier 5：暂缓 / 待评估

可能有价值但接入成本或合规风险较高，先不接，看 MVP 是否真的需要：

- **Reddit r/MachineLearning, r/LocalLLaMA** — 价值高但需 API
- **Discord AI 社区**（OpenAI Dev、LM Studio 等）— 没标准化接入方案
- **Telegram 频道** — 有价值的频道存在但难批量
- **arXiv 之外的预印本**（biorxiv、ssrn 等）— 离 AI 主线远，暂不需
- **Github Releases**（特定 repo 监控）— 重要项目可加，普遍接入价值低
- **专利数据库** — 商业 AI 应用风向标但延迟太大

---

## 请你做的事

1. 逐项标记：**保留** / **待评估** / **剔除**
2. 对保留项加优先级（P0 / P1 / P2）
3. 补充我漏掉的源——尤其是**你已经在用的中文公众号 / 即刻 / 小红书博主**，这些是冷启动选题的关键
4. 对 Twitter 那一栏直接选一个方向：付费 API / 第三方服务 / 自建镜像 / 不接

筛完之后我针对保留的源逐一做接入可行性验证（RSS 是否活、是否需要 RSSHub 自建等），输出最终的 `sources.md`。
