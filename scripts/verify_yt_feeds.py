"""sanity check：fetch 4 个 YouTube RSS，验证 feed title 跟期望吻合。"""
import urllib.request
import feedparser

FEEDS = [
    ("karpathy-yt",     "https://www.youtube.com/feeds/videos.xml?channel_id=UCXUPKJO5MZQN11PqgIvyuvQ"),
    ("garry-tan-yt",    "https://www.youtube.com/feeds/videos.xml?channel_id=UCIBgYfDjtWlbJhg--Z4sOgQ"),
    ("latent-space-yt", "https://www.youtube.com/feeds/videos.xml?channel_id=UCxBcwypKK-W3GHd_RZ9FZrQ"),
    ("no-priors-yt",    "https://www.youtube.com/feeds/videos.xml?channel_id=UCSI7h9hydQ40K5MJHnCrQvw"),
]

for name, url in FEEDS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (yoko)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read()
        parsed = feedparser.parse(body)
        feed_title = parsed.feed.get("title", "<no title>")
        entry_count = len(parsed.entries)
        latest = parsed.entries[0].get("title", "")[:80] if parsed.entries else "<no entries>"
        print(f"{name:<18} title={feed_title!r}  entries={entry_count}")
        print(f"  latest: {latest}")
    except Exception as e:
        print(f"{name:<18} ERROR: {e}")
