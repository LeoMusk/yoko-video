"""M1 信息源配置 — RSS 新闻源 + 宏观 AI 采用数据源。

历史：
- 首版 20 个，对应 docs/sources_status.md 的调研结论。
- Phase 1 补强（2026-05-28）：+5 个，补"头部模型动态/AI创业投融资/AI实用技能"类别 gap。
  详见 docs/sources-candidates-phase1.md
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    tier: str           # T1 / T2 / CN / DATA
    url: str
    kind: str = "news"  # paper / vendor / newsletter / podcast / media / blog / vc / news / macro-data / index / report
    needs_chrome_ua: bool = False
    mode: str = "rss"   # rss / watch
    summary_hint: str = ""
    watch_keywords: tuple[str, ...] = ()
    date_strategy: str = "published"  # published / latest / fetched / url_month


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
    # --- 宏观 AI 采用 / 企业使用数据：网页与数据集监控源 ---
    # 这类源多数没有 RSS。mode="watch" 会抓取页面、做文本哈希去重；页面内容变化时才进入 raw JSONL。
    Source(
        "census-btos-ai",
        "DATA",
        "https://www.census.gov/data/experimental-data-products/business-trends-and-outlook-survey.html",
        kind="macro-data",
        mode="watch",
        summary_hint=(
            "美国 Census BTOS：双周频率、企业层面、按行业/州/企业规模追踪 AI 使用与预期使用。"
            "这是美国企业 AI 采用率的首选官方基准源。"
        ),
        watch_keywords=("Business Trends and Outlook Survey", "Artificial Intelligence", "AI Supplement"),
        date_strategy="latest",
    ),
    Source(
        "census-ai-use-businesses",
        "DATA",
        "https://www.census.gov/library/stories/2026/05/ai-use-businesses.html",
        kind="macro-data",
        mode="watch",
        summary_hint=(
            "Census 对 BTOS AI supplement 的官方解读页，适合提取企业规模、行业、业务职能层面的采用率数字。"
        ),
        watch_keywords=("AI Use at U.S. Businesses", "BTOS", "firm size"),
    ),
    Source(
        "ramp-ai-index",
        "DATA",
        "https://ramp.com/data/ai-index",
        kind="index",
        mode="watch",
        needs_chrome_ua=True,
        summary_hint=(
            "Ramp AI Index：基于企业卡和账单支付交易衡量美国企业为 AI 产品付费的采用率，"
            "可作为问卷数据之外的真实采购领先指标。"
        ),
        watch_keywords=("Ramp AI Index", "adoption rate", "American businesses"),
        date_strategy="fetched",
    ),
    Source(
        "fed-ai-adoption-monitor",
        "DATA",
        "https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html",
        kind="macro-data",
        mode="watch",
        summary_hint=(
            "Federal Reserve FEDS Note：统一比较 BTOS、Real-Time Population Survey、Atlanta Fed SBU 等不同 AI 采用口径。"
        ),
        watch_keywords=("Monitoring AI Adoption", "Business Trends and Outlook Survey", "Survey of Business Uncertainty"),
    ),
    Source(
        "stanford-ai-index-economy",
        "DATA",
        "https://hai.stanford.edu/ai-index/2026-ai-index-report/economy",
        kind="index",
        mode="watch",
        summary_hint=(
            "Stanford HAI AI Index Economy 章节：年度权威汇总，覆盖组织采用、企业函数使用、投资、生产率和劳动力影响。"
        ),
        watch_keywords=("Organizational AI adoption", "business function", "Generative AI"),
    ),
    Source(
        "anthropic-economic-index",
        "DATA",
        "https://www.anthropic.com/research/anthropic-economic-index-september-2025-report?lang=us",
        kind="index",
        mode="watch",
        summary_hint=(
            "Anthropic Economic Index：基于 Claude 使用与企业 API 流量，观察企业把 frontier AI 用在哪些任务上。"
        ),
        watch_keywords=("enterprise", "API", "adoption"),
    ),
    Source(
        "morgan-stanley-ai-adoption",
        "DATA",
        "https://www.morganstanley.com/insights/articles/ai-adoption-accelerates-survey-find",
        kind="report",
        mode="watch",
        summary_hint=(
            "Morgan Stanley 公开 AI adoption insight：企业高管调查，关注 AI 对生产率、就业和行业采用的影响。"
        ),
        watch_keywords=("Morgan Stanley", "productivity", "survey"),
    ),
    # McKinsey State of AI 暂不进入自动源：官方网页和官方 PDF 在本地 urllib 采集下持续超时。
    # 需要时作为人工参考源使用，避免默认 M1 出现长期失败项。
    Source(
        "deloitte-state-ai-enterprise",
        "DATA",
        "https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html",
        kind="report",
        mode="watch",
        summary_hint=(
            "Deloitte State of AI in the Enterprise：企业 AI 从试点到规模化、AI fluency、agentic AI 的全球调研。"
        ),
        watch_keywords=("State of AI", "Enterprise", "Deloitte"),
    ),
    Source(
        "eurostat-enterprise-ai",
        "DATA",
        "https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2",
        kind="macro-data",
        mode="watch",
        summary_hint=(
            "Eurostat 企业 AI 使用率：EU 官方企业 ICT 调查，含 isoc_eb_ai 数据集入口，适合做欧洲横向对比。"
        ),
        watch_keywords=("EU enterprises", "AI technologies", "isoc_eb_ai"),
    ),
    Source(
        "oecd-ai-adoption-firms",
        "DATA",
        "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/05/the-adoption-of-artificial-intelligence-in-firms_8fab986b/f9ef33c3-en.pdf",
        kind="macro-data",
        mode="watch",
        summary_hint=(
            "OECD/BCG/INSEAD The Adoption of Artificial Intelligence in Firms：跨国家企业 AI 采用、应用场景和政策证据。"
        ),
        watch_keywords=(),
        date_strategy="url_month",
    ),
    Source(
        "pwc-ai-performance-study",
        "DATA",
        "https://www.pwc.com/gx/en/issues/technology/strong-foundations-trusted-ai.html",
        kind="report",
        mode="watch",
        summary_hint=(
            "PwC AI trust / performance study：企业 AI 采用后的收入、效率、成本收益和价值集中度，用于补充采用率之外的 ROI 指标。"
        ),
        watch_keywords=("AI", "CEO", "value"),
    ),
    Source(
        "uk-dsit-ai-adoption-research",
        "DATA",
        "https://www.gov.uk/government/publications/ai-adoption-research/ai-adoption-research",
        kind="macro-data",
        mode="watch",
        summary_hint=(
            "UK DSIT AI Adoption Research：英国政府委托的企业 AI 采用、障碍、规模化和影响调查。"
        ),
        watch_keywords=("AI Adoption Research", "3,500", "businesses"),
    ),
]
