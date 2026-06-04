"""验证：高分 arXiv 论文 ID 看着是老论文，但 published_at 是不是最近的？
确认 arXiv cross-list 机制 vs 时效过滤 bug。"""
import json
from pathlib import Path

path = Path("data/raw/2026-05-27.jsonl")
targets = ["2411.02355", "2507.13428", "2603.15500", "2602.07120", "2604.07190"]

for line in path.open(encoding="utf-8"):
    o = json.loads(line)
    url = o.get("url") or ""
    for t in targets:
        if t in url:
            print(f"{t}: published_at={o.get('published_at')}")
            print(f"   title: {o.get('title', '')[:60]}")
