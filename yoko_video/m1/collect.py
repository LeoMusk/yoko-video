"""M1 信息采集：拉 RSS → 规整 schema → 时效过滤 → JSONL 追加 + SQLite 去重。

用法：
    python -m yoko_video.m1.collect                  # 全跑（默认窗口最近 7 天）
    python -m yoko_video.m1.collect --since-days 1   # 仅取最近 24 小时
    python -m yoko_video.m1.collect --since-days 30  # 拉一个月（追历史用）
    python -m yoko_video.m1.collect --tier T1
    python -m yoko_video.m1.collect --only hn-front arxiv-cs.AI
    python -m yoko_video.m1.collect --dry-run

输出：
    data/raw/YYYY-MM-DD.jsonl   当日新鲜 items（陈旧的不写）
    data/m1.db                  SQLite，跨日去重用（含 stale 条目，防止反复处理）

时效规则：
    published_at 在 (now - since-days) 之后 → 新鲜，入 JSONL
    其他（含无 published_at）→ 陈旧，仅入 seen_items
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import feedparser

from .sources import SOURCES, Source

DEFAULT_UA = "Mozilla/5.0 (yoko-video/m1 RSS collector)"
CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 20
FETCH_RETRIES = 1
SUMMARY_MAX_CHARS = 4000
DEFAULT_SINCE_DAYS = 3

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "m1.db"

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_STYLE_RE = re.compile(r"<(script|style|noscript|svg)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_RE = re.compile(
    r"<meta\b(?=[^>]*(?:name|property)=[\"'](?:description|og:description|twitter:description)[\"'])"
    r"(?=[^>]*content=[\"']([^\"']+)[\"'])[^>]*>",
    re.IGNORECASE | re.DOTALL,
)
_META_DATE_RE = re.compile(
    r"<meta\b(?=[^>]*(?:name|property|itemprop)=[\"']"
    r"(?:article:published_time|article:modified_time|date|datePublished|dateModified|pubdate|"
    r"dc\.date|dcterms\.created|dcterms\.modified)"
    r"[\"'])(?=[^>]*content=[\"']([^\"']+)[\"'])[^>]*>",
    re.IGNORECASE | re.DOTALL,
)
_JSON_DATE_RE = re.compile(r"\"(?:datePublished|dateModified)\"\s*:\s*\"([^\"]+)\"", re.IGNORECASE)
_TIME_DATETIME_RE = re.compile(r"<time\b[^>]*datetime=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE | re.DOTALL)
_DMY_DATE_RE = re.compile(
    r"\b(\d{1,2})\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(20\d{2})\b",
    re.IGNORECASE,
)
_MDY_DATE_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(\d{1,2}),\s+(20\d{2})\b",
    re.IGNORECASE,
)
_URL_MONTH_RE = re.compile(r"/(20\d{2})/(0[1-9]|1[0-2])(?:/|$)")
_WHITESPACE_RE = re.compile(r"\s+")

_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


# ---------- storage ----------

def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_items (
            item_id        TEXT PRIMARY KEY,
            source         TEXT NOT NULL,
            url            TEXT NOT NULL,
            title          TEXT,
            published_at   TEXT,
            first_seen_at  TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_seen_source ON seen_items(source)")
    conn.commit()
    return conn


# ---------- fetch ----------

def fetch_url(url: str, use_chrome_ua: bool) -> tuple[int | None, bytes | None, str]:
    ua = CHROME_UA if use_chrome_ua else DEFAULT_UA
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    last_error = ""
    for attempt in range(FETCH_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.status, resp.read(), ""
        except urllib.error.HTTPError as e:
            return e.code, None, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            last_error = f"URLError: {e.reason}"
        except TimeoutError:
            last_error = "Timeout"
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
        if attempt < FETCH_RETRIES:
            time.sleep(0.5 * (attempt + 1))
    return None, None, last_error


# ---------- normalize ----------

def _entry_published_at(entry: dict) -> str | None:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        t = entry.get(key)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    return None


def _entry_summary(entry: dict) -> str:
    text = ""
    contents = entry.get("content") or []
    if contents:
        text = contents[0].get("value", "") or ""
    if not text:
        text = entry.get("summary", "") or ""
    if not text:
        return ""
    text = _HTML_TAG_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text[:SUMMARY_MAX_CHARS]


def _decode_body(body: bytes) -> str:
    for encoding in ("utf-8", "gb18030", "latin-1"):
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")


def _clean_html_text(text: str) -> str:
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def _extract_page_title(text: str, fallback: str) -> str:
    m = _TITLE_RE.search(text)
    if not m:
        return fallback
    title = _clean_html_text(m.group(1))
    return title[:200] or fallback


def _extract_meta_description(text: str) -> str:
    m = _META_DESC_RE.search(text)
    if not m:
        return ""
    return _WHITESPACE_RE.sub(" ", html.unescape(m.group(1))).strip()


def _watch_hash(cleaned_text: str) -> str:
    # Limit the hash window to keep large pages cheap while still catching meaningful report updates.
    return hashlib.sha256(cleaned_text[:200_000].encode("utf-8")).hexdigest()[:16]


def _is_pdf(body: bytes) -> bool:
    return body[:4] == b"%PDF"


def _watch_body_hash(body: bytes) -> str:
    return hashlib.sha256(body[:2_000_000]).hexdigest()[:16]


def _parse_date_value(value: str) -> datetime | None:
    value = html.unescape(value or "").strip()
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    m = _DMY_DATE_RE.search(value)
    if m:
        day, month, year = m.groups()
        return datetime(int(year), _MONTHS[month.lower()], int(day), tzinfo=timezone.utc)

    m = _MDY_DATE_RE.search(value)
    if m:
        month, day, year = m.groups()
        return datetime(int(year), _MONTHS[month.lower()], int(day), tzinfo=timezone.utc)
    return None


def _candidate_dates_from_html(text: str) -> list[datetime]:
    candidates: list[datetime] = []
    for regex in (_META_DATE_RE, _JSON_DATE_RE, _TIME_DATETIME_RE):
        for value in regex.findall(text):
            dt = _parse_date_value(value)
            if dt:
                candidates.append(dt)

    cleaned = _clean_html_text(text)
    for regex in (_DMY_DATE_RE, _MDY_DATE_RE):
        for match in regex.finditer(cleaned):
            dt = _parse_date_value(match.group(0))
            if dt:
                candidates.append(dt)
    return candidates


def _latest_reasonable_date(candidates: list[datetime], now: datetime) -> datetime | None:
    reasonable = [dt for dt in candidates if dt <= now + timedelta(days=1)]
    if not reasonable:
        return None
    return max(reasonable)


def _published_date_from_url(url: str) -> datetime | None:
    m = _URL_MONTH_RE.search(url)
    if not m:
        return None
    year, month = m.groups()
    return datetime(int(year), int(month), 1, tzinfo=timezone.utc)


def _extract_watch_date(source: Source, text: str, fetched_at: str) -> tuple[str | None, str]:
    if source.date_strategy == "fetched":
        return fetched_at, "fetched_at"

    if source.date_strategy == "url_month":
        dt = _published_date_from_url(source.url)
        if dt:
            return dt.isoformat(), "url_month"

    candidates = _candidate_dates_from_html(text)
    now = _parse_iso(fetched_at) or datetime.now(tz=timezone.utc)
    if source.date_strategy == "latest":
        dt = _latest_reasonable_date(candidates, now)
        if dt:
            return dt.isoformat(), "latest_page_date"
    else:
        if candidates:
            return candidates[0].isoformat(), "published_page_date"

    return None, "missing"


def _entry_authors(entry: dict) -> list[str]:
    out: list[str] = []
    for a in entry.get("authors") or []:
        if isinstance(a, dict):
            name = a.get("name")
            if name:
                out.append(name)
    return out


def _entry_categories(entry: dict) -> list[str]:
    out: list[str] = []
    for t in entry.get("tags") or []:
        if isinstance(t, dict):
            term = t.get("term")
            if term:
                out.append(term)
    return out


def _compute_id(source_name: str, entry: dict) -> str:
    key = entry.get("id") or entry.get("link") or entry.get("title") or ""
    return hashlib.sha256(f"{source_name}::{key}".encode("utf-8")).hexdigest()[:16]


def _entry_url(entry: dict, feed_link: str) -> str:
    """提取 entry URL。优先级：link → rel=alternate → enclosure 音频 → feed 主页。
    megaphone/anchor 等 podcast feed 经常没 <link>，如果先用 feed link 会落到官网根目录。
    """
    url = entry.get("link") or ""
    if url:
        return url
    for L in entry.get("links") or []:
        if L.get("rel") == "alternate" and L.get("href"):
            return L["href"]
    encs = entry.get("enclosures") or []
    if encs and encs[0].get("href"):
        return encs[0]["href"]
    for L in entry.get("links") or []:
        if L.get("rel") == "enclosure" and L.get("href"):
            return L["href"]
    if feed_link:
        return feed_link
    return ""


def normalize_entry(source: Source, entry: dict, fetched_at: str, feed_link: str = "") -> dict[str, Any]:
    url = _entry_url(entry, feed_link)
    published_at = _entry_published_at(entry)

    # URL 日期交叉校验：若文章 URL 嵌入的发布年月比 RSS 日期早 2 年以上，
    # 说明这是被 HN 等聚合器翻出的旧文章，用 URL 日期替换 RSS 日期。
    # 这样旧文章会在 is_fresh() 里被过滤掉，不进入当日 JSONL。
    url_date = _published_date_from_url(url)
    if url_date:
        rss_dt = _parse_iso(published_at)
        if rss_dt is None or url_date < rss_dt - timedelta(days=730):
            published_at = url_date.isoformat()

    return {
        "id":           _compute_id(source.name, entry),
        "source":       source.name,
        "tier":         source.tier,
        "kind":         source.kind,
        "fetched_at":   fetched_at,
        "published_at": published_at,
        "title":        (entry.get("title") or "").strip(),
        "url":          url,
        "authors":      _entry_authors(entry),
        "categories":   _entry_categories(entry),
        "summary":      _entry_summary(entry),
    }


def normalize_watch_source(source: Source, body: bytes, fetched_at: str) -> dict[str, Any]:
    if _is_pdf(body):
        content_hash = _watch_body_hash(body)
        title = source.name
        published_at, date_basis = _extract_watch_date(source, "", fetched_at)
        summary_parts = [
            source.summary_hint,
            "PDF source. The collector monitors the binary hash and uses this configured summary as the item context.",
        ]
    else:
        text = _decode_body(body)
        cleaned = _clean_html_text(text)
        content_hash = _watch_hash(cleaned)
        title = _extract_page_title(text, source.name)
        meta_desc = _extract_meta_description(text)
        published_at, date_basis = _extract_watch_date(source, text, fetched_at)
        excerpt = cleaned[:1600]
        summary_parts = [p for p in (source.summary_hint, meta_desc, f"Page excerpt: {excerpt}") if p]
    summary = "\n\n".join(summary_parts)[:SUMMARY_MAX_CHARS]
    return {
        "id":           hashlib.sha256(f"{source.name}::{source.url}::{content_hash}".encode("utf-8")).hexdigest()[:16],
        "source":       source.name,
        "tier":         source.tier,
        "kind":         source.kind,
        "mode":         source.mode,
        "fetched_at":   fetched_at,
        "published_at": published_at,
        "date_basis":   date_basis,
        "title":        title,
        "url":          source.url,
        "authors":      [],
        "categories":   ["macro-ai-adoption", source.kind],
        "summary":      summary,
        "content_hash": content_hash,
    }


# ---------- freshness ----------

def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    # 容错：若解析出 naive datetime，按 UTC 处理
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def is_fresh(item: dict[str, Any], cutoff: datetime) -> bool:
    """published_at 在 cutoff 之后视为新鲜；缺失或更早视为陈旧。"""
    pub = _parse_iso(item.get("published_at"))
    return pub is not None and pub >= cutoff


# ---------- dedup + write ----------

def dedup_filter(conn: sqlite3.Connection, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return []
    ids = [it["id"] for it in items]
    seen: set[str] = set()
    # SQLite 默认变量上限 999，分批查询保险
    for i in range(0, len(ids), 500):
        chunk = ids[i : i + 500]
        placeholders = ",".join("?" * len(chunk))
        cur = conn.execute(
            f"SELECT item_id FROM seen_items WHERE item_id IN ({placeholders})",
            chunk,
        )
        seen.update(row[0] for row in cur.fetchall())
    return [it for it in items if it["id"] not in seen]


def record_seen(conn: sqlite3.Connection, items: list[dict[str, Any]], now_iso: str) -> None:
    if not items:
        return
    conn.executemany(
        "INSERT OR IGNORE INTO seen_items "
        "(item_id, source, url, title, published_at, first_seen_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(it["id"], it["source"], it["url"], it["title"], it["published_at"], now_iso) for it in items],
    )
    conn.commit()


def append_jsonl(items: list[dict[str, Any]], date: str) -> Path:
    path = RAW_DIR / f"{date}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return path


# ---------- main ----------

def _base_result(source: Source) -> dict[str, Any]:
    return {
        "source": source.name, "tier": source.tier, "kind": source.kind, "mode": source.mode,
        "status": None, "error": "",
        "fetched": 0, "fresh": 0, "stale": 0, "new": 0, "elapsed_ms": 0,
    }


def collect_watch_one(
    source: Source,
    conn: sqlite3.Connection,
    fetched_at: str,
    today: str,
    cutoff: datetime,
) -> dict[str, Any]:
    t0 = time.time()
    status, body, err = fetch_url(source.url, source.needs_chrome_ua)
    result = _base_result(source)
    result["status"] = status
    result["error"] = err
    if err or not body:
        result["elapsed_ms"] = int((time.time() - t0) * 1000)
        return result

    item = normalize_watch_source(source, body, fetched_at)
    result["fetched"] = 1
    fresh = is_fresh(item, cutoff)
    result["fresh"] = 1 if fresh else 0
    result["stale"] = 0 if fresh else 1
    new_items = dedup_filter(conn, [item])
    if fresh and new_items:
        append_jsonl(new_items, today)
    record_seen(conn, new_items, fetched_at)
    result["new"] = len(new_items) if fresh else 0
    result["elapsed_ms"] = int((time.time() - t0) * 1000)
    return result


def collect_one(
    source: Source,
    conn: sqlite3.Connection,
    fetched_at: str,
    today: str,
    cutoff: datetime,
) -> dict[str, Any]:
    if source.mode == "watch":
        return collect_watch_one(source, conn, fetched_at, today, cutoff)
    if source.mode != "rss":
        result = _base_result(source)
        result["error"] = f"Unsupported source mode: {source.mode}"
        return result

    t0 = time.time()
    status, body, err = fetch_url(source.url, source.needs_chrome_ua)
    result = _base_result(source)
    result["status"] = status
    result["error"] = err
    if err or not body:
        result["elapsed_ms"] = int((time.time() - t0) * 1000)
        return result

    parsed = feedparser.parse(body)
    feed_link = (parsed.feed.get("link") or "") if hasattr(parsed, "feed") else ""
    items = [normalize_entry(source, e, fetched_at, feed_link) for e in parsed.entries]
    result["fetched"] = len(items)

    # 时效过滤
    fresh_items = [it for it in items if is_fresh(it, cutoff)]
    stale_items = [it for it in items if not is_fresh(it, cutoff)]
    result["fresh"] = len(fresh_items)
    result["stale"] = len(stale_items)

    # 去重：fresh 走 JSONL + seen；stale 仅入 seen 防反复
    new_fresh = dedup_filter(conn, fresh_items)
    new_stale = dedup_filter(conn, stale_items)
    if new_fresh:
        append_jsonl(new_fresh, today)
    record_seen(conn, new_fresh + new_stale, fetched_at)
    result["new"] = len(new_fresh)
    result["elapsed_ms"] = int((time.time() - t0) * 1000)
    return result


def run(sources: Iterable[Source], since_days: int) -> list[dict[str, Any]]:
    ensure_dirs()
    now = datetime.now(tz=timezone.utc)
    fetched_at = now.isoformat(timespec="seconds")
    today = now.strftime("%Y-%m-%d")
    cutoff = now - timedelta(days=since_days)
    results: list[dict[str, Any]] = []
    with closing(open_db()) as conn:
        for s in sources:
            print(f"  [{s.tier}/{s.mode}] {s.name:<28} ", end="", flush=True)
            r = collect_one(s, conn, fetched_at, today, cutoff)
            if r["error"]:
                print(f"❌ {r['error']}")
            else:
                print(
                    f"got {r['fetched']:>4} (fresh {r['fresh']:>3} / stale {r['stale']:>4}), "
                    f"new {r['new']:>3}   ({r['elapsed_ms']}ms)"
                )
            results.append(r)
    return results


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(prog="yoko_video.m1.collect", description="M1 RSS collector")
    parser.add_argument("--only", nargs="*", help="只跑指定 source name")
    parser.add_argument("--tier", help="只跑指定 tier (T1 / T2 / CN / DATA)")
    parser.add_argument("--mode", choices=("rss", "watch"), help="只跑指定 source mode")
    parser.add_argument(
        "--since-days",
        type=int,
        default=DEFAULT_SINCE_DAYS,
        help=f"时效窗口（天），published_at 早于此或缺失则视为陈旧。默认 {DEFAULT_SINCE_DAYS}",
    )
    parser.add_argument("--dry-run", action="store_true", help="解析参数但不执行")
    args = parser.parse_args(argv)

    if args.since_days <= 0:
        print("--since-days 必须 > 0", file=sys.stderr)
        return 2

    sources = list(SOURCES)
    if args.tier:
        sources = [s for s in sources if s.tier == args.tier]
    if args.mode:
        sources = [s for s in sources if s.mode == args.mode]
    if args.only:
        names = set(args.only)
        sources = [s for s in sources if s.name in names]
    if not sources:
        print("No sources matched.", file=sys.stderr)
        return 2

    if args.dry_run:
        for s in sources:
            print(f"  would fetch: [{s.tier}/{s.mode}] {s.name}  {s.url}")
        print(f"  (since-days = {args.since_days})")
        return 0

    print(
        f"M1 collect — {len(sources)} sources, since-days={args.since_days}, "
        f"{datetime.now().isoformat(timespec='seconds')}"
    )
    results = run(sources, args.since_days)
    total_fetched = sum(r["fetched"] for r in results)
    total_fresh = sum(r["fresh"] for r in results)
    total_stale = sum(r["stale"] for r in results)
    total_new = sum(r["new"] for r in results)
    failed = [r for r in results if r["error"]]
    print(
        f"\nSummary: fetched {total_fetched} "
        f"(fresh {total_fresh} / stale {total_stale}), new {total_new}, "
        f"failed {len(failed)} / {len(results)}"
    )
    for r in failed:
        print(f"  ❌ {r['source']:<22} {r['error']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
