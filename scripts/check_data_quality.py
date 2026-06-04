"""信息层数据质量 + 时效性体检：分析指定日期的 scored 数据。

用法：python scripts/check_data_quality.py [YYYY-MM-DD]
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

date = sys.argv[1] if len(sys.argv) > 1 else "2026-05-28"
path = Path(f"data/scored/{date}_scored.jsonl")
items = [json.loads(l) for l in path.open(encoding="utf-8")]
now = datetime.now(timezone.utc)


def parse(s):
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


print(f"===== {date} 数据体检 =====")
print(f"总条目：{len(items)}\n")

# 时效分桶
buckets = Counter()
dated = []
for it in items:
    dt = parse(it.get("published_at"))
    if dt is None:
        buckets["无日期"] += 1
        continue
    days = (now - dt).total_seconds() / 86400
    dated.append((days, it))
    if days <= 1:
        buckets["≤1天"] += 1
    elif days <= 3:
        buckets["≤3天"] += 1
    elif days <= 7:
        buckets["≤7天"] += 1
    elif days <= 30:
        buckets["8-30天(回填)"] += 1
    else:
        buckets[">30天(异常)"] += 1

print("--- 时效分布（按 published_at）---")
for k in ["≤1天", "≤3天", "≤7天", "8-30天(回填)", ">30天(异常)", "无日期"]:
    if buckets.get(k):
        print(f"  {k:<14} {buckets[k]}")

# category + 广告（仅评分成功）
scored = [it for it in items if it.get("scores")]
cats = Counter(it["scores"]["category"] for it in scored)
ads = sum(1 for it in scored if it["scores"].get("is_ad"))
print(f"\n--- 类别分布（评分 {len(scored)} 条）---")
for c, n in cats.most_common():
    print(f"  {n:>3}  {c}")
print(f"  检出广告/PR: {ads}")

# final 分布
hi = sum(1 for it in scored if it["scores"]["final"] >= 7)
mid = sum(1 for it in scored if 5 <= it["scores"]["final"] < 7)
print(f"\n--- 可用度 ---")
print(f"  final≥7 可做选题: {hi}")
print(f"  final 5-7 备选:   {mid}")

# 最旧 6 条（看时效问题）
dated.sort(key=lambda x: x[0], reverse=True)
print(f"\n--- 最旧 6 条（检查是否过时）---")
for days, it in dated[:6]:
    s = it.get("scores", {})
    print(f"  [{days:.0f}天前] {it.get('source','')}: {it.get('title','')[:42]}  (final={s.get('final','?')})")

# 最新 5 条
print(f"\n--- 最新 5 条 ---")
for days, it in sorted(dated, key=lambda x: x[0])[:5]:
    print(f"  [{days:.1f}天前] {it.get('source','')}: {it.get('title','')[:42]}")
