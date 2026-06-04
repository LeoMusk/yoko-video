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
SUMMARY_MAX_CHARS = 4000
DEFAULT_SINCE_DAYS = 7

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "m1.db"

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


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
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read(), ""
    except urllib.error.HTTPError as e:
        return e.code, None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, None, f"URLError: {e.reason}"
    except TimeoutError:
        return None, None, "Timeout"
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


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
    """提取 entry URL。优先级：link → rel=alternate → feed 主页 → enclosure 音频。
    megaphone/anchor 等 podcast feed 经常没 <link>，需要 enclosure 兜底。
    """
    url = entry.get("link") or ""
    if url:
        return url
    for L in entry.get("links") or []:
        if L.get("rel") == "alternate" and L.get("href"):
            return L["href"]
    if feed_link:
        return feed_link
    encs = entry.get("enclosures") or []
    if encs and encs[0].get("href"):
        return encs[0]["href"]
    for L in entry.get("links") or []:
        if L.get("rel") == "enclosure" and L.get("href"):
            return L["href"]
    return ""


def normalize_entry(source: Source, entry: dict, fetched_at: str, feed_link: str = "") -> dict[str, Any]:
    return {
        "id":           _compute_id(source.name, entry),
        "source":       source.name,
        "tier":         source.tier,
        "kind":         source.kind,
        "fetched_at":   fetched_at,
        "published_at": _entry_published_at(entry),
        "title":        (entry.get("title") or "").strip(),
        "url":          _entry_url(entry, feed_link),
        "authors":      _entry_authors(entry),
        "categories":   _entry_categories(entry),
        "summary":      _entry_summary(entry),
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

def collect_one(
    source: Source,
    conn: sqlite3.Connection,
    fetched_at: str,
    today: str,
    cutoff: datetime,
) -> dict[str, Any]:
    t0 = time.time()
    status, body, err = fetch_url(source.url, source.needs_chrome_ua)
    result: dict[str, Any] = {
        "source": source.name, "tier": source.tier,
        "status": status, "error": err,
        "fetched": 0, "fresh": 0, "stale": 0, "new": 0, "elapsed_ms": 0,
    }
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
            print(f"  [{s.tier}] {s.name:<22} ", end="", flush=True)
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
    parser = argparse.ArgumentParser(prog="yoko_video.m1.collect", description="M1 RSS collector")
    parser.add_argument("--only", nargs="*", help="只跑指定 source name")
    parser.add_argument("--tier", help="只跑指定 tier (T1 / T2 / CN)")
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
    if args.only:
        names = set(args.only)
        sources = [s for s in sources if s.name in names]
    if not sources:
        print("No sources matched.", file=sys.stderr)
        return 2

    if args.dry_run:
        for s in sources:
            print(f"  would fetch: [{s.tier}] {s.name}  {s.url}")
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
