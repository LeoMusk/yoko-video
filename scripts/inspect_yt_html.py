"""探查 YouTube @handle 页面里 channelId 在哪些位置出现，
找到一个最稳的提取锚点。"""
import re
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

URL = "https://www.youtube.com/@AndrejKarpathy"

req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept-Language": "en-US"})
with urllib.request.urlopen(req, timeout=15) as r:
    html = r.read().decode("utf-8", errors="replace")

print(f"HTML 长度: {len(html)}")

# 关键锚点 1：canonical link
m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
print(f"\ncanonical link: {m.group(1) if m else '<not found>'}")

# 关键锚点 2：meta itemprop=channelId
m = re.search(r'<meta\s+itemprop="(?:identifier|channelId)"\s+content="(UC[A-Za-z0-9_-]{20,})"', html)
print(f"meta itemprop=channelId: {m.group(1) if m else '<not found>'}")

# 关键锚点 3：meta property=og:url
m = re.search(r'<meta\s+property="og:url"\s+content="([^"]+)"', html)
print(f"meta og:url: {m.group(1) if m else '<not found>'}")

# 关键锚点 4：所有 "channelId":"UC..." 的前 5 个出现位置
all_cids = re.findall(r'"channelId":"(UC[A-Za-z0-9_-]{20,})"', html)
print(f"\n所有 channelId 出现次数: {len(all_cids)}, 前 5 个独立 ID:")
seen = []
for cid in all_cids:
    if cid not in seen:
        seen.append(cid)
    if len(seen) >= 5:
        break
for cid in seen:
    print(f"  {cid}")
