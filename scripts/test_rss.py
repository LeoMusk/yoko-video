"""
RSS 源测活脚本 — 一次性可行性验证。
对每个候选 URL：GET → feedparser 解析 → 报告状态、最新条目日期、数量。
输出 markdown 表，附送 JSON 详情供后续审阅。
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

import feedparser

UA = "Mozilla/5.0 (yoko-video-rss-tester/0.1)"
TIMEOUT = 15

# (tier, name, url, note) — note 用于标记需要后续处理的信息
SOURCES: list[tuple[str, str, str, str]] = [
    # Tier 1: 一手核心信源
    ("T1", "arXiv cs.AI",          "http://export.arxiv.org/rss/cs.AI", ""),
    ("T1", "arXiv cs.CL",          "http://export.arxiv.org/rss/cs.CL", ""),
    ("T1", "arXiv cs.LG",          "http://export.arxiv.org/rss/cs.LG", ""),
    ("T1", "HackerNews front",     "https://news.ycombinator.com/rss", ""),
    ("T1", "HackerNews best (hnrss)", "https://hnrss.org/best", ""),
    ("T1", "OpenAI Blog (rss.xml)", "https://openai.com/blog/rss.xml", "uncertain"),
    ("T1", "OpenAI News (alt)",     "https://openai.com/news/rss.xml", "uncertain alt"),
    ("T1", "Anthropic news rss",    "https://www.anthropic.com/news/feed.xml", "uncertain"),
    ("T1", "Anthropic rss.xml",     "https://www.anthropic.com/rss.xml", "uncertain alt"),
    ("T1", "Google DeepMind blog",  "https://deepmind.google/blog/rss.xml", "uncertain"),
    ("T1", "Google AI (blog.google)", "https://blog.google/technology/ai/rss/", ""),
    ("T1", "Meta AI Blog",          "https://ai.meta.com/blog/rss/", "uncertain"),
    ("T1", "Microsoft Research",    "https://www.microsoft.com/en-us/research/feed/", ""),
    ("T1", "HuggingFace Blog",      "https://huggingface.co/blog/feed.xml", ""),
    # Tier 2: 深度信源 (Newsletter / 播客)
    ("T2", "The Batch (deeplearning.ai)", "https://www.deeplearning.ai/the-batch/feed/", ""),
    ("T2", "Import AI",            "https://importai.substack.com/feed", ""),
    ("T2", "Latent Space",         "https://www.latent.space/feed", ""),
    ("T2", "Ben's Bites",          "https://bensbites.beehiiv.com/feed", "uncertain platform"),
    ("T2", "Last Week in AI",      "https://lastweekin.ai/feed", ""),
    ("T2", "Stratechery",          "https://stratechery.com/feed/", "most posts paywalled"),
    ("T2", "Dwarkesh Podcast",     "https://www.dwarkesh.com/feed", ""),
    # 中文头部
    ("CN", "36氪 (官方 feed?)",    "https://36kr.com/feed", "uncertain"),
    ("CN", "36氪 (RSSHub 公共)",   "https://rsshub.app/36kr/news/latest", ""),
    ("CN", "量子位 (官方?)",       "https://www.qbitai.com/feed", "uncertain"),
    ("CN", "量子位 (RSSHub)",      "https://rsshub.app/qbitai", "RSSHub route may differ"),
    ("CN", "机器之心 (官方?)",     "https://www.jiqizhixin.com/rss", "uncertain"),
    ("CN", "机器之心 (RSSHub)",    "https://rsshub.app/jiqizhixin/latest", ""),
]


@dataclass
class Result:
    tier: str
    name: str
    url: str
    note: str
    http_status: int | None = None
    error: str = ""
    feed_title: str = ""
    bozo: bool = False
    entries_count: int = 0
    latest_entry_title: str = ""
    latest_entry_date: str = ""
    days_since_latest: float | None = None
    elapsed_ms: int = 0

    def verdict(self) -> str:
        if self.error:
            return "❌ 死/拒绝"
        if self.bozo and self.entries_count == 0:
            return "❌ 解析失败"
        if self.entries_count == 0:
            return "⚠️ 无条目"
        if self.days_since_latest is None:
            return "⚠️ 无日期"
        if self.days_since_latest <= 7:
            return "✅ 活跃"
        if self.days_since_latest <= 30:
            return "✅ 在更新"
        if self.days_since_latest <= 90:
            return "⚠️ 慢更新"
        return "⚠️ 沉睡"


def fetch_and_parse(url: str) -> tuple[int | None, bytes | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read(), ""
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = None
        return e.code, body, f"HTTPError {e.code}"
    except urllib.error.URLError as e:
        return None, None, f"URLError: {e.reason}"
    except TimeoutError:
        return None, None, "Timeout"
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def parse_feed(data: bytes) -> dict[str, Any]:
    parsed = feedparser.parse(data)
    out: dict[str, Any] = {
        "feed_title": parsed.feed.get("title", "") if parsed.feed else "",
        "bozo": bool(parsed.bozo),
        "entries_count": len(parsed.entries),
        "latest_entry_title": "",
        "latest_entry_date": "",
        "days_since_latest": None,
    }

    def entry_dt(e) -> datetime | None:
        for key in ("published_parsed", "updated_parsed", "created_parsed"):
            t = e.get(key)
            if t:
                try:
                    return datetime(*t[:6], tzinfo=timezone.utc)
                except Exception:
                    pass
        return None

    if parsed.entries:
        entries_with_dt = [(e, entry_dt(e)) for e in parsed.entries]
        entries_with_dt.sort(key=lambda p: p[1] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        latest, dt = entries_with_dt[0]
        out["latest_entry_title"] = (latest.get("title") or "")[:80]
        if dt:
            out["latest_entry_date"] = dt.isoformat()
            out["days_since_latest"] = round((datetime.now(tz=timezone.utc) - dt).total_seconds() / 86400, 1)
    return out


def test_one(src: tuple[str, str, str, str]) -> Result:
    tier, name, url, note = src
    print(f"  testing {name} ... ", flush=True, end="")
    t0 = time.time()
    status, body, err = fetch_and_parse(url)
    r = Result(tier=tier, name=name, url=url, note=note, http_status=status, error=err)
    if body and not err:
        try:
            parsed = parse_feed(body)
            r.feed_title = parsed["feed_title"]
            r.bozo = parsed["bozo"]
            r.entries_count = parsed["entries_count"]
            r.latest_entry_title = parsed["latest_entry_title"]
            r.latest_entry_date = parsed["latest_entry_date"]
            r.days_since_latest = parsed["days_since_latest"]
        except Exception as e:
            r.error = f"ParseError: {type(e).__name__}: {e}"
    r.elapsed_ms = int((time.time() - t0) * 1000)
    print(r.verdict())
    return r


def emit_markdown(results: list[Result]) -> str:
    lines = []
    lines.append(f"# RSS 源测活结果\n")
    lines.append(f"测试时间：{datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"测试源数：{len(results)}\n")
    by_v = {}
    for r in results:
        by_v.setdefault(r.verdict(), 0)
        by_v[r.verdict()] += 1
    summary = " / ".join(f"{k}: {v}" for k, v in sorted(by_v.items()))
    lines.append(f"汇总：{summary}\n")

    for tier_label, tier_name in [("T1", "Tier 1 — 一手核心"), ("T2", "Tier 2 — Newsletter/播客"), ("CN", "中文头部")]:
        lines.append(f"\n## {tier_name}\n")
        lines.append("| 状态 | 名称 | HTTP | 最新条目日期 | 距今(天) | 条目数 | 最新标题 | 备注 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in results:
            if r.tier != tier_label:
                continue
            title = r.latest_entry_title.replace("|", "\\|") if r.latest_entry_title else "—"
            note = r.note or ""
            if r.error:
                note = f"{note}; err={r.error}" if note else f"err={r.error}"
            days = "—" if r.days_since_latest is None else str(r.days_since_latest)
            lines.append(f"| {r.verdict()} | {r.name} | {r.http_status or '—'} | {r.latest_entry_date or '—'} | {days} | {r.entries_count} | {title} | {note} |")
        lines.append("")
    return "\n".join(lines)


def main():
    print(f"Testing {len(SOURCES)} sources...")
    results = [test_one(s) for s in SOURCES]
    md = emit_markdown(results)
    out_md = "docs/sources_status.md"
    out_json = "docs/sources_status.json"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)
    print(f"\nWrote {out_md} and {out_json}")


if __name__ == "__main__":
    main()
