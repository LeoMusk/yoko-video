"""解析 YouTube @handle / channel URL → channel_id + Atom RSS URL。

YouTube 三种 URL 形式：
1. /@handle           需 fetch HTML 提取 "channelId":"UC..."
2. /channel/UCxxx     直接拿到 channel_id
3. /playlist?list=PL  用 playlist_id 即可

输出：name, channel_id, rss_url 三列表

用法：
    python scripts/resolve_youtube_channel.py
"""
from __future__ import annotations

import re
import sys
import urllib.request


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 15


def resolve(channel_url: str) -> tuple[str | None, str | None]:
    """返回 (channel_id_or_playlist_id, rss_url)。无法解析返回 (None, None)。"""
    # 1. playlist
    m = re.search(r"[?&]list=([A-Za-z0-9_-]+)", channel_url)
    if m:
        pid = m.group(1)
        return pid, f"https://www.youtube.com/feeds/videos.xml?playlist_id={pid}"

    # 2. /channel/UC...
    m = re.search(r"/channel/(UC[A-Za-z0-9_-]+)", channel_url)
    if m:
        cid = m.group(1)
        return cid, f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"

    # 3. /@handle —— 必须 fetch HTML
    if not re.search(r"/@[A-Za-z0-9_.\-]+", channel_url):
        return None, None
    try:
        req = urllib.request.Request(
            channel_url,
            headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            html = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ! fetch error: {e}", file=sys.stderr)
        return None, None

    # 寻找 channelId — 优先级：canonical link > meta itemprop > meta og:url
    # 关键：YouTube 页面里有 10+ 个 "channelId":"UC..." 是推荐频道，不能用 first-match
    patterns = [
        r'<link\s+rel="canonical"\s+href="https://www\.youtube\.com/channel/(UC[A-Za-z0-9_-]{20,})"',
        r'<meta\s+itemprop="(?:identifier|channelId)"\s+content="(UC[A-Za-z0-9_-]{20,})"',
        r'<meta\s+property="og:url"\s+content="https://www\.youtube\.com/channel/(UC[A-Za-z0-9_-]{20,})"',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            cid = m.group(1)
            return cid, f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    return None, None


CANDIDATES = [
    ("karpathy-yt",     "https://www.youtube.com/@AndrejKarpathy"),
    ("garry-tan-yt",    "https://www.youtube.com/@garrytan"),
    ("latent-space-yt", "https://www.youtube.com/@LatentSpacePod"),
    ("no-priors-yt",    "https://www.youtube.com/@NoPriorsPodcast"),
]


def main() -> int:
    failures = 0
    print(f"{'name':<18} {'channel_id':<28} rss_url")
    print("-" * 100)
    for name, url in CANDIDATES:
        cid, rss = resolve(url)
        if cid:
            print(f"{name:<18} {cid:<28} {rss}")
        else:
            failures += 1
            print(f"{name:<18} {'FAILED':<28} ({url})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
