"""验证 _entry_url 新逻辑：跑 3 个 podcast feed + 1 个正常 blog feed，
看 URL 提取是否符合预期。"""
import feedparser
import urllib.request
from yoko_video.m1.collect import _entry_url

URLS = [
    ("training-data",     "https://feeds.megaphone.fm/trainingdata"),
    ("no-priors",         "https://feeds.megaphone.fm/nopriors"),
    ("mad-podcast",       "https://anchor.fm/s/f2ee4948/podcast/rss"),
    ("hn-front (sanity)", "https://news.ycombinator.com/rss"),
]

for name, url in URLS:
    print(f"\n=== {name} ===")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (yoko)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read()
    except Exception as e:
        print(f"  fetch failed: {e}")
        continue
    parsed = feedparser.parse(body)
    feed_link = parsed.feed.get("link") or ""
    print(f"  feed.link: {feed_link[:80]}")
    for i, e in enumerate(parsed.entries[:3]):
        url_out = _entry_url(e, feed_link)
        title = (e.get("title") or "")[:60]
        print(f"  [{i}] {title}")
        print(f"      -> {url_out[:120]}")
