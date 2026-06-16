"""Verify macro AI adoption watch sources.

This is a stability check for DATA/watch sources that do not expose RSS feeds.
It writes:
    docs/macro_ai_sources_status.md
    docs/macro_ai_sources_status.json
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from yoko_video.m1.collect import (
    _clean_html_text,
    _decode_body,
    _extract_watch_date,
    _extract_page_title,
    _is_pdf,
    _watch_body_hash,
    _watch_hash,
    fetch_url,
)
from yoko_video.m1.sources import SOURCES, Source


OUT_MD = Path("docs/macro_ai_sources_status.md")
OUT_JSON = Path("docs/macro_ai_sources_status.json")


@dataclass
class Result:
    name: str
    tier: str
    kind: str
    url: str
    http_status: int | None
    error: str
    title: str
    published_at: str | None
    date_basis: str
    body_bytes: int
    content_hash: str
    matched_keywords: list[str]
    missing_keywords: list[str]
    elapsed_ms: int

    def verdict(self) -> str:
        if self.error:
            return "❌ 失败"
        if self.missing_keywords:
            return "⚠️ 可达但需复核"
        return "✅ 稳定"


def watch_sources() -> list[Source]:
    return [s for s in SOURCES if s.mode == "watch"]


def _keyword_hits(cleaned_text: str, keywords: tuple[str, ...]) -> tuple[list[str], list[str]]:
    haystack = cleaned_text.lower()
    matched: list[str] = []
    missing: list[str] = []
    for kw in keywords:
        if kw.lower() in haystack:
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing


def verify_one(source: Source) -> Result:
    print(f"  checking {source.name} ... ", end="", flush=True)
    t0 = time.time()
    status, body, err = fetch_url(source.url, source.needs_chrome_ua)
    title = ""
    published_at = None
    date_basis = "missing"
    body_bytes = len(body or b"")
    content_hash = ""
    matched: list[str] = []
    missing = list(source.watch_keywords)
    if body and not err:
        if _is_pdf(body):
            title = source.name
            content_hash = _watch_body_hash(body)
            published_at, date_basis = _extract_watch_date(source, "", datetime.now().astimezone().isoformat())
            if source.watch_keywords:
                missing = list(source.watch_keywords)
            else:
                missing = []
        else:
            text = _decode_body(body)
            cleaned = _clean_html_text(text)
            title = _extract_page_title(text, source.name)
            content_hash = _watch_hash(cleaned)
            published_at, date_basis = _extract_watch_date(source, text, datetime.now().astimezone().isoformat())
            matched, missing = _keyword_hits(cleaned, source.watch_keywords)
    elapsed_ms = int((time.time() - t0) * 1000)
    result = Result(
        name=source.name,
        tier=source.tier,
        kind=source.kind,
        url=source.url,
        http_status=status,
        error=err,
        title=title,
        published_at=published_at,
        date_basis=date_basis,
        body_bytes=body_bytes,
        content_hash=content_hash,
        matched_keywords=matched,
        missing_keywords=missing,
        elapsed_ms=elapsed_ms,
    )
    print(result.verdict())
    return result


def emit_markdown(results: list[Result]) -> str:
    lines: list[str] = []
    lines.append("# 宏观 AI 采用信息源稳定性检查\n")
    lines.append(f"检查时间：{datetime.now().isoformat(timespec='seconds')}\n")
    lines.append(f"检查源数：{len(results)}\n")
    ok = sum(1 for r in results if r.verdict().startswith("✅"))
    warn = sum(1 for r in results if r.verdict().startswith("⚠️"))
    fail = sum(1 for r in results if r.verdict().startswith("❌"))
    lines.append(f"汇总：稳定 {ok} / 需复核 {warn} / 失败 {fail}\n")
    lines.append("| 状态 | 名称 | 类型 | HTTP | 日期 | 日期依据 | 字节 | 哈希 | 标题 | 缺失关键词 | URL |")
    lines.append("|---|---|---|---:|---|---|---:|---|---|---|---|")
    for r in results:
        title = (r.title or "").replace("|", "\\|")[:80]
        missing = ", ".join(r.missing_keywords) if r.missing_keywords else "-"
        lines.append(
            f"| {r.verdict()} | {r.name} | {r.kind} | {r.http_status or '-'} | "
            f"{(r.published_at or '-')[:10]} | {r.date_basis} | "
            f"{r.body_bytes} | `{r.content_hash or '-'}` | {title or '-'} | "
            f"{missing} | {r.url} |"
        )
    lines.append("")
    lines.append("说明：这些源为 `mode=\"watch\"`，采集器会对清洗后的页面正文做哈希去重；只有内容变化才写入 `data/raw`。")
    return "\n".join(lines)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    sources = watch_sources()
    print(f"Checking {len(sources)} macro AI sources...")
    results = [verify_one(s) for s in sources]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(emit_markdown(results), encoding="utf-8")
    OUT_JSON.write_text(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_MD} and {OUT_JSON}")
    failed = [r for r in results if r.error]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
