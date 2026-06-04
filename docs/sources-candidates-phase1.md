# Phase 1 信息源补强候选（待 M2 brief 出来后决策）

来源：follow-builders 项目（zarazhangrui）调研后筛出的可直接拉 RSS 的渠道，全部为国外、零成本、无第三方付费依赖。

**决策时机**：等 M2 全量 brief 跑完，看类别分布发现哪类信号薄弱后再选择加哪几个。

**当前 M1 已有源（不重复加）**：arxiv-cs.AI/CL/LG、hn-front、hn-best、openai-news、deepmind-blog、google-ai-blog、huggingface-blog、microsoft-research、import-ai、latent-space、last-week-in-ai、stratechery、dwarkesh-podcast、bens-bites、simon-willison、sequoia、36kr、qbitai。

---

## A. Podcast（6 个，全部 follow-builders 在用，URL 已验证可拉）

业务定位：**长篇深度观点**，与 Newsletter / Blog 互补。短视频可拿 episode title + show notes + 嘉宾名做选题，无需 transcript。

| name | url | kind | 价值定位 |
|---|---|---|---|
| `training-data` | `https://feeds.megaphone.fm/trainingdata` | podcast | Sequoia 出品，AI 创业/投资视角，对你"AI 创业"线最相关 |
| `no-priors` | `https://feeds.megaphone.fm/nopriors` | podcast | Sarah Guo + Elad Gil 主理，AI builder 一手对话 |
| `unsupervised-learning` | `https://feeds.simplecast.com/dOSE_bdP` | podcast | Redpoint AI 系列 |
| `mad-podcast` | `https://anchor.fm/s/f2ee4948/podcast/rss` | podcast | Matt Turck 主持，数据/AI 商业战略 |
| `ai-and-i` | `https://anchor.fm/s/ed1f5584/podcast/rss` | podcast | Every / Dan Shipper，AI 应用实战 |

> Latent Space podcast 已经覆盖在我们的 `latent-space` newsletter feed 里，不重复加。

### sources.py 落地代码（决定加哪些时拷贝）

```python
Source("training-data",        "T2", "https://feeds.megaphone.fm/trainingdata",    kind="podcast"),
Source("no-priors",            "T2", "https://feeds.megaphone.fm/nopriors",        kind="podcast"),
Source("unsupervised-learning","T2", "https://feeds.simplecast.com/dOSE_bdP",      kind="podcast"),
Source("mad-podcast",          "T2", "https://anchor.fm/s/f2ee4948/podcast/rss",   kind="podcast"),
Source("ai-and-i",             "T2", "https://anchor.fm/s/ed1f5584/podcast/rss",   kind="podcast"),
```

---

## B. KOL 个人博客 / Substack（4 个，零成本，未验证需补 test_rss）

业务定位：**Builder 一手观点**，弥补当前"全是机构源"的盲点。

| name | url | kind | 价值定位 |
|---|---|---|---|
| `sam-altman-blog` | `https://blog.samaltman.com/posts.atom` | blog | 更新极慢（数月一篇）但每篇是行业事件级；OpenAI CEO |
| `guillermo-rauch` | `https://rauchg.com/rss.xml` | blog | Vercel CEO，AI 基础设施 + 产品视角 |
| `matt-turck` | `https://mattturck.com/feed/` | blog | MAD Podcast 主持的博客，年度 ML/AI Landscape 报告产地 |
| `peter-yang` | `https://creatoreconomy.so/feed` | newsletter | Roblox PM，AI 教程 / 案例为主，14万订阅 |

### sources.py 落地代码

```python
Source("sam-altman-blog", "T2", "https://blog.samaltman.com/posts.atom", kind="blog"),
Source("guillermo-rauch", "T2", "https://rauchg.com/rss.xml",            kind="blog"),
Source("matt-turck",      "T2", "https://mattturck.com/feed/",           kind="blog"),
Source("peter-yang",      "T2", "https://creatoreconomy.so/feed",        kind="newsletter"),
```

---

## C. YouTube 频道 — **跳过（2026-05-28 调研结论）**

### 调研结果

`scripts/resolve_youtube_channel.py` 已经写好，正确从 `<link rel="canonical">` 提取所有 4 个候选频道的 channel_id。但**直接 fetch YouTube Atom RSS endpoint 时**：

| 频道 | channel_id 正确性 | Atom RSS 状态 |
|---|---|---|
| Karpathy (`UCXUPKJO5MZQN11PqgIvyuvQ`) | ✓ | HTTP **500** 持续 |
| Garry Tan (`UCIBgYfDjtWlbJhg--Z4sOgQ`) | ✓ | HTTP **404** 持续 |
| Latent Space (`UCxBcwypKK-W3GHd_RZ9FZrQ`) | ✓ | HTTP 200 ✓ |
| No Priors (`UCSI7h9hydQ40K5MJHnCrQvw`) | ✓ | HTTP **404** 持续 |

直接访问 `https://www.youtube.com/channel/UC...` 都能跳到正确频道，但 `feeds/videos.xml?channel_id=UC...` 这个 Atom endpoint 对**部分频道返回错误**。也尝试了 uploads playlist (`UU...`) fallback 同样无效。

### 这是 YouTube 端的 quirk

这就是 follow-builders 的 `generate-feed.js` 写了 `parseYouTubePageData` HTML 爬虫 fallback 的原因 — 解析 `ytInitialData` JSON。但该方案：
- YouTube 内部 schema 不稳定，时常变化
- 需要额外维护代码（30-60 行）
- 跟"零成本零依赖"的初衷脱离

### 决策：跳过 YouTube

理由：
1. 已经加了 3 个 podcast (training-data / no-priors / mad-podcast) 覆盖了 No Priors / Latent Space / MAD 这几个本来想加 YT 版的内容
2. Karpathy / Garry Tan 暂时缺位 — 接受这个损失
3. 节省 30-60 分钟工程时间转去做 M2 prompt v2 ROI 更高

未来如需补 YouTube：
- 用 yt-dlp 库（成熟但 200+ MB 依赖）
- 或写 ytInitialData 爬虫（仿 follow-builders 第 170-224 行）
- 或等 YouTube 修复 Atom endpoint（被动）

### 已写但未启用的脚本

保留以下脚本作为未来恢复参考（不在主流程使用）:
- `scripts/resolve_youtube_channel.py` — @handle → channel_id
- `scripts/verify_yt_feeds.py` — RSS Atom endpoint 可达性测试
- `scripts/verify_channel_identity.py` — 通过 channel page title 验证 ID 对应频道

---

## D. 不建议加的（说明原因，避免后续重复评估）

| 候选 | 不加的原因 |
|---|---|
| **Anthropic Engineering** | 网页爬虫成本高，已在 [sources_status.md](sources_status.md) 评估过；其内容会在 HN / Latent Space / Import AI 转引覆盖 |
| **Claude Blog** | 同上，且产品发布会在 OpenAI/Anthropic 类厂商动态里被覆盖 |
| **国内 KOL** | 用户已明确：本项目核心信号源是国外，国内由 36kr + 量子位 覆盖足够 |
| **X / Twitter 自动化** | 用户已明确：不付费 API。X List 走半人工浏览 |
| **Substack: Eugene Yan / Sebastian Raschka / Chip Huyen / Lilian Weng** | 这些是技术 ML 实践型博客，与 yoko 的"AI 产品/创业/动态"主线 audience_fit 较低；保留作为 Phase 2 候选 |

---

## 决策格子（M2 brief 出来后填）

待 M2 brief 跑完看类别分布后填：

- [ ] 5 个 Podcast 全加 → 加哪几个？理由？
- [ ] 4 个 KOL 博客全加 → 加哪几个？理由？
- [ ] 4 个 YouTube 是否需要（先做 resolve_youtube_channel.py 工具）？

最终决定后落到 `sources.py`，跑一次 `test_rss` 验证可达性，再跑一次 M1+M2 看类别分布变化。
