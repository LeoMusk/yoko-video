"""核查 M3 脚本里的事实数字是否来自原始 summary（防 LLM 幻觉）。"""
import json
from pathlib import Path

path = Path("data/scored/2026-05-28_scored.jsonl")
targets = ["Greg Brockman", "Yann Dubois"]

for line in path.open(encoding="utf-8"):
    o = json.loads(line)
    title = o.get("title", "")
    if any(t in title for t in targets):
        print(f"=== {title[:60]} ===")
        print(f"source: {o.get('source')}")
        print(f"summary 全文:")
        print(o.get("summary", "")[:1500])
        print("\n" + "=" * 60 + "\n")
