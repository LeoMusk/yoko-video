"""临时脚本：探查 training-data podcast feed 的 entry 字段结构，
找出"链接缺失"的根因 + 哪个 fallback 字段能拿到 episode 页面 URL。
"""
import feedparser
import urllib.request

URL = "https://feeds.megaphone.fm/trainingdata"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (yoko)"})
with urllib.request.urlopen(req, timeout=20) as r:
    body = r.read()

parsed = feedparser.parse(body)
print(f"Feed: {parsed.feed.get('title', 'unknown')}")
print(f"Entries: {len(parsed.entries)}\n")

# 看前 2 条 entry 的关键字段
for i, e in enumerate(parsed.entries[:2]):
    print(f"--- Entry {i} ---")
    print(f"title:  {e.get('title', '')[:80]}")
    print(f"link:   {e.get('link', '<MISSING>')}")
    print(f"id:     {e.get('id', '')}")
    print(f"links:  (count={len(e.get('links') or [])})")
    for L in (e.get("links") or [])[:5]:
        print(f"   - rel={L.get('rel')!r}, type={L.get('type')!r}, href={L.get('href', '')[:100]}")
    encs = e.get("enclosures") or []
    print(f"enclosures: (count={len(encs)})")
    for enc in encs[:3]:
        print(f"   - type={enc.get('type')!r}, href={enc.get('href', '')[:100]}")
    print()
