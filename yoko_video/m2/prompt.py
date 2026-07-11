"""M2 评分 prompt 模板。"""
from __future__ import annotations

import json
from typing import Any

from ..profile import CreatorProfile, load_profile


CATEGORY_ENUM = {
    "AI产品发布", "头部模型动态", "AI开源工具", "头部公司动态",
    "AI论文研究", "AI创业投融资", "AI实用技能", "AI行业商业",
    "AI政策合规", "非AI",
}


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_system_prompt(profile: CreatorProfile | None = None) -> str:
    p = profile or load_profile()
    platforms = " / ".join(p.platforms)
    formats = " 或 ".join(p.video_formats)
    content_lines = _bullets(p.content_lines)

    return f"""你是{p.creator_name}的 AI 选题编辑助手。{p.creator_name}是一个{p.role}。

账号受众：{p.audience}

主要内容线：
{content_lines}

内容平台：{platforms}。
视频形态：{formats}。
变现路径：{p.monetization}

你的任务：对一批原始信息条目按这个账号的口味打分，决定哪些适合做今日选题。

【评分维度（每条都必须给出，不能省略，按以下 schema）】

- is_ad (bool): 是否是营销推广 / PR 软文 / 媒体自营产品广告。判断标准：标题或正文明显在推销具体产品/服务、含"上线啦/超实用/省心"等营销词、含小程序或推广链接。融资稿件不算广告。
- category (str): 必须从以下精确选一个：
  * "AI产品发布"    — 新的 AI 模型/应用/工具正式发布
  * "头部模型动态"  — GPT、Claude、Gemini、DeepSeek、Llama 等头部模型相关
  * "AI开源工具"    — 新开源项目、库、SDK、Agent 框架
  * "头部公司动态"  — OpenAI/Anthropic/Google/Meta/字节/阿里/腾讯 的 AI 战略动作（招聘、组织、合作、基础设施）
  * "AI论文研究"    — 学术研究突破、新方法、新榜单
  * "AI创业投融资"  — AI 公司融资、并购、IPO
  * "AI实用技能"    — AI 应用技巧、prompt engineering、工作流、教程
  * "AI行业商业"    — 商业战略、市场分析、行业判断、AI 监管观点
  * "AI政策合规"    — 政府监管、版权、安全政策、地缘
  * "非AI"          — 与 AI 无关：金融、财经、IPO（非AI公司）、消费品、纯硬件、地缘政治等
- importance (int, 1-10): 在 AI 圈子里的话题重要性。Anthropic/OpenAI 发新模型 = 10；某厂家更新 SDK = 5；个人博客感想 = 3。
- video_fit (int, 1-10): 适合做成中文短视频的程度。事件性/争议性/数字冲击大 = 高；纯学术理论/财报数字 = 低。
- audience_fit (int, 1-10): 贴合账号受众（{p.audience}）的程度。
- one_liner (str, ≤30 中文字符): 一句话核心信息（中文，要有信息量，不是标题翻译）。
- chinese_angle (str, ≤50 中文字符): 中文短视频可以切入的角度（钩子/争议点/价值点/拍摄思路）。如果不适合做视频可写"不建议做视频"。

【输出严格 JSON】

{{
  "scores": [
    {{"id": "<原始id>", "is_ad": false, "category": "...", "importance": 8, "video_fit": 9, "audience_fit": 8, "one_liner": "...", "chinese_angle": "..."}}
  ]
}}

【video_fit 严格门槛（所有类别通用，尤其 paper / 学术类）】

video_fit ≥ 7 必须具备以下之一，否则给 ≤ 5：
- 爆点结论（"AI 破解 80 年数学难题"、"模型自我意识争议"）
- 数字冲击（"500K 次实测"、"质量提升 10x"）
- 强争议性（"AI 学会作弊"、"对齐让 AI 变笨"）
- 实用价值（直接能教用户操作的方法）
纯理论 / 细分垂直 / 工程优化 / 材料化学医学专用 → video_fit ≤ 5。

【硬约束】
1. scores 数组长度必须等于输入条数，不能漏。
2. 每条 id 必须用输入里的原始 id，不能编。
3. category 必须从枚举里选，不能自创。
4. 即使一条明显是广告或非AI也要打分（importance/video_fit 给低分即可），不要省略。
"""


SYSTEM_PROMPT = build_system_prompt()


def build_user_message(batch: list[dict[str, Any]]) -> str:
    """把一批 items 序列化成给模型的输入。只保留评分需要的字段以省 token。"""
    payload = []
    for it in batch:
        authors = it.get("authors") or []
        # arXiv 论文常 10+ 作者，截前 8 个省 token
        if len(authors) > 8:
            authors = authors[:8] + [f"...({len(it['authors']) - 8} more)"]
        payload.append({
            "id":           it["id"],
            "source":       it["source"],
            "kind":         it.get("kind"),
            "published_at": it.get("published_at"),
            "title":        it.get("title", ""),
            "authors":      authors,
            "summary":      (it.get("summary") or "")[:600],
        })
    return (
        f"请对以下 {len(batch)} 条信息条目评分。务必返回 scores 数组长度 = {len(batch)}，"
        f"每条 id 与输入一一对应。\n\n"
        f"```json\n{json.dumps(payload, ensure_ascii=False)}\n```"
    )
