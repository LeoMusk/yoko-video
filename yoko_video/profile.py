"""Creator profile loading for prompts.

Public users should copy config/profile.example.json to config/profile.json.
The code falls back to the example profile so first-run behavior remains useful.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_PROFILE_PATH = Path("config/profile.json")
EXAMPLE_PROFILE_PATH = Path("config/profile.example.json")


@dataclass(frozen=True)
class CreatorProfile:
    creator_name: str = "你的名字"
    role: str = "中文 AI/科技短视频创作者"
    audience: str = "AI/科技爱好者、AI 创业者、想用 AI 提升效率的职场人"
    platforms: list[str] = field(default_factory=lambda: ["抖音", "视频号", "YouTube Shorts"])
    video_formats: list[str] = field(default_factory=lambda: ["60-120 秒口播", "30-90 秒信息流短视频"])
    content_lines: list[str] = field(default_factory=lambda: [
        "AI 新产品 / 新工具 / 新模型动态",
        "头部 AI 公司动态",
        "AI 创业 / AI 投融资",
        "AI 实用技能 / Prompt Engineering",
        "AI 行业商业判断",
    ])
    monetization: str = "通过短视频引流到自己的 AI 产品、服务、社群或私域"
    product_name: str = "你的 AI 产品或服务"
    cta_style: str = "自然提到你提供的 AI 产品或服务，不硬广，不夸大承诺"
    tone_keywords: list[str] = field(default_factory=lambda: [
        "口语化", "短句", "信息密度高", "不浮夸", "像跟懂行朋友分享",
    ])
    opening_address: str = "兄弟们"
    banned_phrases: list[str] = field(default_factory=lambda: [
        "不是 X，而是 Y", "这不是科幻", "颠覆认知", "细思极恐", "让我们拭目以待",
    ])
    style_samples: list[str] = field(default_factory=list)


def _as_list(value: Any, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return fallback


def _profile_path() -> Path:
    env_path = os.environ.get("YOKO_PROFILE_PATH")
    if env_path:
        return Path(env_path)
    if DEFAULT_PROFILE_PATH.exists():
        return DEFAULT_PROFILE_PATH
    return EXAMPLE_PROFILE_PATH


def load_profile(path: str | Path | None = None) -> CreatorProfile:
    chosen = Path(path) if path else _profile_path()
    if not chosen.exists():
        return CreatorProfile()

    data = json.loads(chosen.read_text(encoding="utf-8"))
    defaults = CreatorProfile()
    return CreatorProfile(
        creator_name=str(data.get("creator_name") or defaults.creator_name),
        role=str(data.get("role") or defaults.role),
        audience=str(data.get("audience") or defaults.audience),
        platforms=_as_list(data.get("platforms"), defaults.platforms),
        video_formats=_as_list(data.get("video_formats"), defaults.video_formats),
        content_lines=_as_list(data.get("content_lines"), defaults.content_lines),
        monetization=str(data.get("monetization") or defaults.monetization),
        product_name=str(data.get("product_name") or defaults.product_name),
        cta_style=str(data.get("cta_style") or defaults.cta_style),
        tone_keywords=_as_list(data.get("tone_keywords"), defaults.tone_keywords),
        opening_address=str(data.get("opening_address") or defaults.opening_address),
        banned_phrases=_as_list(data.get("banned_phrases"), defaults.banned_phrases),
        style_samples=_as_list(data.get("style_samples"), defaults.style_samples),
    )
