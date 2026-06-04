"""试 Uploads playlist endpoint 作为 channel_id RSS 的 fallback。
YouTube 每个频道都有 uploads playlist，ID = channel_id 的 UC 换 UU。"""
import urllib.request
import feedparser

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CHANNELS = [
    ("karpathy",    "UCXUPKJO5MZQN11PqgIvyuvQ"),
    ("garry-tan",   "UCIBgYfDjtWlbJhg--Z4sOgQ"),
    ("no-priors",   "UCSI7h9hydQ40K5MJHnCrQvw"),
    ("latent (control)", "UCxBcwypKK-W3GHd_RZ9FZrQ"),
]

for name, cid in CHANNELS:
    uploads_pid = "UU" + cid[2:]  # UC... -> UU...
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={uploads_pid}"
    print(f"\n=== {name} (uploads={uploads_pid}) ===")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read()
        parsed = feedparser.parse(body)
        feed_title = parsed.feed.get("title", "<no title>")
        entry_count = len(parsed.entries)
        latest = (parsed.entries[0].get("title") or "")[:80] if parsed.entries else "<empty>"
        print(f"  HTTP OK, feed={feed_title!r}, entries={entry_count}")
        print(f"  latest: {latest}")
        print(f"  USE: {url}")
    except Exception as e:
        print(f"  ERROR {e}")
