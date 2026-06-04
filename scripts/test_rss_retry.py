"""
对第一轮失败的源做重试：换 Chrome UA + 尝试备选 URL。
针对 Anthropic / Meta AI / Microsoft Research / The Batch / Ben's Bites / 机器之心 / RSSHub 公共实例。
"""
from __future__ import annotations
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
import feedparser

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 15

# 每行：(分组, 名称, [url1, url2, ...])
RETRIES = [
    ("Anthropic", "Anthropic news", [
        "https://www.anthropic.com/news/rss.xml",
        "https://www.anthropic.com/feed.xml",
        "https://www.anthropic.com/news.xml",
        "https://www.anthropic.com/news/feed",
        "https://anthropic.com/rss",
    ]),
    ("MetaAI", "Meta AI Blog", [
        "https://ai.meta.com/blog/feed/",
        "https://ai.meta.com/blog/rss.xml",
        "https://ai.meta.com/feed/",
        "https://about.fb.com/news/category/research/feed/",
    ]),
    ("MSR", "Microsoft Research (Chrome UA)", [
        "https://www.microsoft.com/en-us/research/feed/",
        "https://www.microsoft.com/en-us/research/blog/feed/",
    ]),
    ("TheBatch", "The Batch", [
        "https://www.deeplearning.ai/the-batch/feed/",
        "https://www.deeplearning.ai/the-batch/rss/",
        "https://read.deeplearning.ai/the-batch/feed",
        "https://www.deeplearning.ai/feed/",
        "https://blog.deeplearning.ai/feed",
    ]),
    ("BensBites", "Ben's Bites", [
        "https://bensbites.beehiiv.com/feed",
        "https://news.bensbites.com/feed",
        "https://bensbites.com/feed",
        "https://bensbites.substack.com/feed",
    ]),
    ("JiQiZhiXin", "机器之心", [
        "https://www.jiqizhixin.com/rss",
        "https://www.jiqizhixin.com/rss/all",
        "https://www.jiqizhixin.com/feed",
        "https://www.jiqizhixin.com/feeds",
    ]),
    ("RSSHub-36kr", "RSSHub 公共 36kr (Chrome UA)", [
        "https://rsshub.app/36kr/news/latest",
        "https://rsshub.rssforever.com/36kr/news/latest",
    ]),
    # 顺便补几个可能有用的源
    ("Extra", "Smol AI News (AINews)", [
        "https://buttondown.email/ainews/rss",
        "https://news.smol.ai/rss",
    ]),
    ("Extra", "Sequoia Capital Perspectives", [
        "https://www.sequoiacap.com/feed/",
    ]),
    ("Extra", "a16z (Andreessen Horowitz)", [
        "https://a16z.com/feed/",
    ]),
    ("Extra", "Simon Willison's Weblog", [
        "https://simonwillison.net/atom/everything/",
    ]),
    ("Extra", "Hugging Face Papers (no native RSS, just check page)", [
        "https://huggingface.co/papers",  # 应该返回 HTML 而非 feed，验证用
    ]),
]


def fetch(url: str) -> tuple[int | None, bytes | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": CHROME_UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read(), ""
    except urllib.error.HTTPError as e:
        return e.code, None, f"HTTPError {e.code}"
    except urllib.error.URLError as e:
        return None, None, f"URLError: {e.reason}"
    except TimeoutError:
        return None, None, "Timeout"
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def check_url(url: str) -> dict:
    t0 = time.time()
    status, body, err = fetch(url)
    info = {"url": url, "status": status, "err": err, "elapsed_ms": int((time.time() - t0) * 1000)}
    if body and not err:
        parsed = feedparser.parse(body)
        info["bozo"] = bool(parsed.bozo)
        info["entries"] = len(parsed.entries)
        info["feed_title"] = parsed.feed.get("title", "") if parsed.feed else ""
        if parsed.entries:
            e = parsed.entries[0]
            dt = None
            for k in ("published_parsed", "updated_parsed"):
                t = e.get(k)
                if t:
                    try:
                        dt = datetime(*t[:6], tzinfo=timezone.utc)
                        break
                    except Exception:
                        pass
            info["latest_title"] = (e.get("title") or "")[:80]
            if dt:
                info["latest_date"] = dt.isoformat()
                info["days_since"] = round((datetime.now(tz=timezone.utc) - dt).total_seconds() / 86400, 1)
    return info


def main():
    print(f"Retrying {sum(len(urls) for _,_,urls in RETRIES)} candidate URLs with Chrome UA\n")
    results = []
    for group, name, urls in RETRIES:
        print(f"## {group} — {name}")
        group_results = []
        for url in urls:
            info = check_url(url)
            mark = "❌"
            if info.get("entries", 0) > 0:
                mark = "✅"
            elif info["status"] == 200:
                mark = "⚠️ 200 但无 entries"
            elif info["status"]:
                mark = f"❌ {info['status']}"
            else:
                mark = f"❌ {info['err']}"
            entries = info.get("entries", "—")
            latest = info.get("latest_date", "—")
            print(f"  {mark}  entries={entries}  latest={latest}  {url}")
            group_results.append(info)
        results.append({"group": group, "name": name, "candidates": group_results})

    with open("docs/sources_status_retry.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nWrote docs/sources_status_retry.json")


if __name__ == "__main__":
    main()
