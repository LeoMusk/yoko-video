"""M1 信息源配置 — 25 个源。

历史：
- 首版 20 个，对应 docs/sources_status.md 的调研结论。
- Phase 1 补强（2026-05-28）：+5 个，补"头部模型动态/AI创业投融资/AI实用技能"类别 gap。
  详见 docs/sources-candidates-phase1.md
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    tier: str           # T1 / T2 / CN
    url: str
    kind: str = "news"  # paper / vendor / newsletter / podcast / media / blog / vc / news
    needs_chrome_ua: bool = False


SOURCES: list[Source] = [
    # --- Tier 1：一手 ---
    # arXiv 三源已禁用（2026-05-28）：论文层与"应用/产品价值"产品定位错位，
    # 且量占 84% 掩盖了其他源的真实结构。如需恢复科研线，取消下列注释即可：
    #   Source("arxiv-cs.AI", "T1", "http://export.arxiv.org/rss/cs.AI", kind="paper"),
    #   Source("arxiv-cs.CL", "T1", "http://export.arxiv.org/rss/cs.CL", kind="paper"),
    #   Source("arxiv-cs.LG", "T1", "http://export.arxiv.org/rss/cs.LG", kind="paper"),
    Source("hn-front",           "T1", "https://news.ycombinator.com/rss"),
    Source("hn-best",            "T1", "https://hnrss.org/best"),
    Source("openai-news",        "T1", "https://openai.com/news/rss.xml", kind="vendor"),
    Source("deepmind-blog",      "T1", "https://deepmind.google/blog/rss.xml", kind="vendor"),
    Source("google-ai-blog",     "T1", "https://blog.google/technology/ai/rss/", kind="vendor"),
    Source("huggingface-blog",   "T1", "https://huggingface.co/blog/feed.xml", kind="vendor"),
    Source("microsoft-research", "T1", "https://www.microsoft.com/en-us/research/feed/",
           kind="vendor", needs_chrome_ua=True),
    # --- Tier 2：Newsletter / 播客 / 博客 ---
    Source("import-ai",          "T2", "https://importai.substack.com/feed", kind="newsletter"),
    Source("latent-space",       "T2", "https://www.latent.space/feed",      kind="newsletter"),
    Source("last-week-in-ai",    "T2", "https://lastweekin.ai/feed",          kind="newsletter"),
    Source("stratechery",        "T2", "https://stratechery.com/feed/",       kind="newsletter"),
    Source("dwarkesh-podcast",   "T2", "https://www.dwarkesh.com/feed",       kind="podcast"),
    Source("bens-bites",         "T2", "https://bensbites.com/feed",          kind="newsletter"),
    Source("simon-willison",     "T2", "https://simonwillison.net/atom/everything/", kind="blog"),
    Source("sequoia",            "T2", "https://www.sequoiacap.com/feed/",    kind="vc"),
    # --- Phase 1 补强：Podcast（补 AI 创业投融资 / 头部模型动态 类别）---
    Source("training-data",       "T2", "https://feeds.megaphone.fm/trainingdata",  kind="podcast"),
    Source("no-priors",           "T2", "https://feeds.megaphone.fm/nopriors",      kind="podcast"),
    Source("mad-podcast",         "T2", "https://anchor.fm/s/f2ee4948/podcast/rss", kind="podcast"),
    # --- Phase 1 补强：KOL 个人渠道 ---
    Source("sam-altman-blog",     "T2", "https://blog.samaltman.com/posts.atom",    kind="blog"),
    Source("peter-yang",          "T2", "https://creatoreconomy.so/feed",           kind="newsletter"),
    # --- 中文头部 ---
    Source("36kr",               "CN", "https://36kr.com/feed",               kind="media"),
    Source("qbitai",             "CN", "https://www.qbitai.com/feed",         kind="media"),
]
