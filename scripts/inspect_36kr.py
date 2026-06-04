"""临时脚本：扫 36kr 全部 title，肉眼识别广告 / 软文模式。"""
import json
from pathlib import Path

path = Path("data/raw/2026-05-27.jsonl")
items = [json.loads(l) for l in path.open(encoding="utf-8")
         if json.loads(l)["source"] == "36kr"]

print(f"36kr total: {len(items)}\n")
for it in items:
    title = it["title"]
    summary = it["summary"][:120].replace("\n", " ")
    print(f"[{it['published_at'][:10]}] {title}")
    print(f"   {summary}")
    print()
