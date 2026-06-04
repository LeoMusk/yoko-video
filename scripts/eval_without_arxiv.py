"""评估移除 arXiv 后的数据丰富度：
统计 27 号 + 28 号 scored 数据里非 arXiv 部分的条数、类别、final 分布。
"""
import json
from collections import Counter
from pathlib import Path

files = ["data/scored/2026-05-27_scored.jsonl", "data/scored/2026-05-28_scored.jsonl"]

non_arxiv = []
arxiv_count = 0
for fp in files:
    p = Path(fp)
    if not p.exists():
        continue
    for line in p.open(encoding="utf-8"):
        o = json.loads(line)
        src = o.get("source", "")
        if src.startswith("arxiv"):
            arxiv_count += 1
            continue
        non_arxiv.append(o)

print(f"arXiv 条数（将移除）: {arxiv_count}")
print(f"非 arXiv 条数（保留）: {len(non_arxiv)}")
print()

# 按 source 统计
by_source = Counter(o["source"] for o in non_arxiv)
print("=== 非 arXiv 按 source ===")
for s, c in by_source.most_common():
    print(f"  {c:>4}  {s}")

# 按 category 统计（仅评分成功的）
scored = [o for o in non_arxiv if o.get("scores")]
by_cat = Counter(o["scores"]["category"] for o in scored)
print(f"\n=== 非 arXiv 按 category（评分成功 {len(scored)} 条）===")
for cat, c in by_cat.most_common():
    print(f"  {c:>4}  {cat}")

# final 分布
finals = sorted((o["scores"]["final"] for o in scored), reverse=True)
buckets = {">=8": 0, "7-8": 0, "6-7": 0, "5-6": 0, "<5": 0}
for f in finals:
    if f >= 8: buckets[">=8"] += 1
    elif f >= 7: buckets["7-8"] += 1
    elif f >= 6: buckets["6-7"] += 1
    elif f >= 5: buckets["5-6"] += 1
    else: buckets["<5"] += 1
print(f"\n=== 非 arXiv final 分布 ===")
for k, v in buckets.items():
    print(f"  {k:>5}: {v}")
print(f"\n可做选题（final>=7）: {buckets['>=8'] + buckets['7-8']} 条")
