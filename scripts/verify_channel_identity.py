"""验证 channel_id 实际对应的频道身份。"""
import re
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CIDS = [
    ("karpathy?",    "UCXUPKJO5MZQN11PqgIvyuvQ"),
    ("garry-tan?",   "UCIBgYfDjtWlbJhg--Z4sOgQ"),
    ("no-priors?",   "UCSI7h9hydQ40K5MJHnCrQvw"),
    ("latent (ok)",  "UCxBcwypKK-W3GHd_RZ9FZrQ"),
]
for label, cid in CIDS:
    url = f"https://www.youtube.com/channel/{cid}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")
        m = re.search(r"<title>([^<]+)</title>", html)
        title = m.group(1) if m else "<no title>"
        m2 = re.search(r'<meta property="og:title" content="([^"]+)"', html)
        og_title = m2.group(1) if m2 else ""
        print(f"{label} ({cid})")
        print(f"  title:    {title}")
        print(f"  og_title: {og_title}")
    except Exception as e:
        print(f"{label} ({cid}): ERROR {e}")
