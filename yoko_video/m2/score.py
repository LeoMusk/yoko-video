"""M2 评分主程序：读 JSONL → 批量 LLM 评分 → 写 scored JSONL + Markdown 简报。

用法：
    python -m yoko_video.m2.score                        # 跑 data/raw 里最新一天
    python -m yoko_video.m2.score --date 2026-05-27      # 指定日期
    python -m yoko_video.m2.score --limit 30             # 只跑前 30 条（调试）
    python -m yoko_video.m2.score --batch 15             # 调批次大小
    python -m yoko_video.m2.score --model deepseek-v4-flash
    python -m yoko_video.m2.score --only-unscored        # 只评 scored JSONL 里没的

输出：
    data/scored/YYYY-MM-DD_scored.jsonl   每条原 entry + scores 字段
    data/scored/YYYY-MM-DD_brief.md       Top N 选题简报
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from .env import load_dotenv
from .llm import DeepSeekClient, extract_content, usage_of
from ..profile import load_profile
from .prompt import build_system_prompt, build_user_message, CATEGORY_ENUM


RAW_DIR = Path("data/raw")
SCORED_DIR = Path("data/scored")
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BATCH = 15
TOP_N_FOR_BRIEF = 30


@dataclass
class Score:
    is_ad: bool
    category: str
    importance: int
    video_fit: int
    audience_fit: int
    one_liner: str
    chinese_angle: str

    def final(self) -> float:
        """综合分。广告 / 非AI 直接打到 0，其余按加权。"""
        if self.is_ad or self.category == "非AI":
            return 0.0
        return (
            self.importance * 0.4
            + self.video_fit * 0.4
            + self.audience_fit * 0.2
        )


# ---------- IO ----------

def latest_raw_date() -> str:
    files = sorted(RAW_DIR.glob("*.jsonl"))
    if not files:
        raise FileNotFoundError("data/raw 里没有任何 .jsonl，先跑 M1")
    return files[-1].stem


def load_raw(date: str) -> list[dict[str, Any]]:
    path = RAW_DIR / f"{date}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"{path} 不存在")
    return [json.loads(l) for l in path.open(encoding="utf-8")]


def write_scored(date: str, items: list[dict[str, Any]]) -> Path:
    SCORED_DIR.mkdir(parents=True, exist_ok=True)
    path = SCORED_DIR / f"{date}_scored.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return path


def load_existing_scores(date: str) -> dict[str, dict[str, Any]]:
    """读已有 scored JSONL，返回 id → scores dict。如果文件不存在返回空。"""
    path = SCORED_DIR / f"{date}_scored.jsonl"
    if not path.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for line in path.open(encoding="utf-8"):
        it = json.loads(line)
        if it.get("scores") and it.get("id"):
            result[it["id"]] = it["scores"]
    return result


# ---------- preprocess dedup ----------

_ARXIV_ID_RE = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,6})")
_NORM_TITLE_RE = re.compile(r"[^\w]+", re.UNICODE)  # \w 已覆盖 CJK
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9._+-]{2,}", re.IGNORECASE)
_URL_TOKEN_RE = re.compile(r"https?://[^/\s]+/([^\s?#]+)")

_EVENT_STOPWORDS = {
    "about", "after", "agent", "agents", "amazon", "and", "are",
    "article", "audio", "based", "best", "blog", "build", "building",
    "comments", "company", "data", "deepmind", "from", "google", "government",
    "have", "here", "into", "latest", "model", "models", "news", "official",
    "openai", "over", "podcast", "release", "released", "report", "says",
    "statement", "this", "through", "using", "with", "http", "https", "www",
    "com", "net", "org", "jun", "june", "rss", "traffic", "megaphone",
    "pscrb", "simonwillison",
}


def _normalize_title(t: str) -> str:
    """归一化标题用于跨源去重比对：lowercase + 仅保留字母数字/中文 + 合并空白。"""
    if not t:
        return ""
    return _NORM_TITLE_RE.sub(" ", t.lower()).strip()


def _arxiv_paper_id(url: str) -> str | None:
    m = _ARXIV_ID_RE.search(url or "")
    return m.group(1) if m else None


def preprocess_dedup(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """跨源去重：
    (a) arXiv URL 提取 paper_id，同 paper_id 多次出现保留第一个（cs.AI/cs.CL/cs.LG 跨分类）
    (b) title 归一化后完全相同的保留第一个（如 hn-front + hn-best 同一文章）

    Returns (kept items, stats)
    """
    seen_paper_ids: set[str] = set()
    seen_titles: set[str] = set()
    kept: list[dict[str, Any]] = []
    arxiv_collapsed = 0
    title_collapsed = 0

    for it in items:
        pid = _arxiv_paper_id(it.get("url") or "")
        if pid:
            if pid in seen_paper_ids:
                arxiv_collapsed += 1
                continue
            seen_paper_ids.add(pid)

        ntitle = _normalize_title(it.get("title") or "")
        if ntitle:
            if ntitle in seen_titles:
                title_collapsed += 1
                continue
            seen_titles.add(ntitle)

        kept.append(it)

    return kept, {"arxiv_collapsed": arxiv_collapsed, "title_collapsed": title_collapsed}


def _canonical_url(url: str) -> str:
    """Drop tracking query/fragment for duplicate comparison."""
    if not url:
        return ""
    base = url.split("#", 1)[0]
    if "?" not in base:
        return base.rstrip("/")
    path, query = base.split("?", 1)
    kept_params = []
    for param in query.split("&"):
        key = param.split("=", 1)[0].lower()
        if key.startswith("utm_") or key in {"st", "reflink", "share", "ref", "f"}:
            continue
        kept_params.append(param)
    return (path + ("?" + "&".join(kept_params) if kept_params else "")).rstrip("/")


def _is_homepage_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return (parsed.path or "/") == "/"


def _event_surface_text(it: dict[str, Any]) -> str:
    s = it.get("scores") or {}
    return " ".join(
        str(x or "")
        for x in (
            it.get("title"),
            it.get("url"),
            s.get("one_liner"),
            s.get("chinese_angle"),
        )
    )


def _normalize_event_token(token: str) -> str:
    token = token.strip("._+-").lower()
    if len(token) > 5 and token.endswith("ing"):
        token = token[:-3]
    elif len(token) > 5 and token.endswith("ed"):
        token = token[:-2]
    elif len(token) > 4 and token.endswith("s"):
        token = token[:-1]
    return token


def _event_tokens(it: dict[str, Any]) -> set[str]:
    text = _event_surface_text(it).lower()
    text_without_urls = re.sub(r"https?://\S+", " ", text)
    raw_tokens = (_normalize_event_token(t) for t in _WORD_RE.findall(text_without_urls))
    tokens = {
        t
        for t in raw_tokens
        if len(t) >= 3 and not t.isdigit() and t not in _EVENT_STOPWORDS
    }
    for path in _URL_TOKEN_RE.findall(text):
        for part in re.split(r"[^a-z0-9]+", path.lower()):
            if len(part) >= 4 and part not in _EVENT_STOPWORDS:
                tokens.add(part)
    return tokens


def _same_event(a: dict[str, Any], b: dict[str, Any], a_tokens: set[str], b_tokens: set[str]) -> bool:
    a_url = a.get("url", "")
    b_url = b.get("url", "")
    if (
        _canonical_url(a_url)
        and _canonical_url(a_url) == _canonical_url(b_url)
        and not _is_homepage_url(a_url)
    ):
        return True

    ta = _normalize_title(a.get("title") or "")
    tb = _normalize_title(b.get("title") or "")
    if ta and tb and difflib.SequenceMatcher(None, ta, tb).ratio() >= 0.86:
        return True

    if a.get("source") == b.get("source"):
        return False

    if not a_tokens or not b_tokens:
        return False
    overlap = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)
    jaccard = overlap / max(1, union)
    return overlap >= 4 and jaccard >= 0.30


def cluster_scored_items(scored_items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Group different sources covering the same event for brief rendering."""
    # 只聚合有实质得分的条目（final=0 即非AI/广告，不进入简报）
    keep = [it for it in scored_items if it.get("scores") and it["scores"].get("final", 0) > 0]
    keep.sort(key=lambda it: it["scores"]["final"], reverse=True)

    clusters: list[list[dict[str, Any]]] = []
    cluster_tokens: list[set[str]] = []

    for it in keep:
        tokens = _event_tokens(it)
        placed = False

        for idx, cluster in enumerate(clusters):
            if any(_same_event(it, existing, tokens, _event_tokens(existing)) for existing in cluster):
                cluster.append(it)
                cluster_tokens[idx] |= tokens
                placed = True
                break

        if not placed:
            clusters.append([it])
            cluster_tokens.append(tokens)

    for cluster in clusters:
        cluster.sort(key=lambda it: it["scores"]["final"], reverse=True)
    clusters.sort(key=lambda c: c[0]["scores"]["final"], reverse=True)
    return clusters


# ---------- LLM batch ----------

def score_batch(
    client: DeepSeekClient, model: str, batch: list[dict[str, Any]], system_prompt: str
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """对一批 items 调一次 LLM，返回 (id → score dict, usage dict)。"""
    user_msg = build_user_message(batch)
    resp = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=8000,
    )
    content = extract_content(resp)
    finish_reason = (resp.get("choices") or [{}])[0].get("finish_reason", "?")
    if not content.strip():
        raise RuntimeError(
            f"LLM 返回空 content (finish_reason={finish_reason}, usage={usage_of(resp)})"
        )
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        # JSON 截断（如 max_tokens 用完）会触发，content 末尾通常残缺
        raise RuntimeError(
            f"LLM 返回非 JSON (finish_reason={finish_reason}): tail={content[-200:]!r}"
        ) from e
    scores = parsed.get("scores") or []
    by_id: dict[str, dict[str, Any]] = {}
    for s in scores:
        sid = s.get("id")
        if not sid:
            continue
        # 类别校验：未知类别 → 兜底"非AI"
        if s.get("category") not in CATEGORY_ENUM:
            s["category"] = "非AI"
        by_id[sid] = s
    return by_id, usage_of(resp)


def chunk(lst: list[Any], n: int) -> Iterable[list[Any]]:
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# ---------- brief markdown ----------

def render_brief(date: str, scored_items: list[dict[str, Any]], top_n: int) -> str:
    keep = [it for it in scored_items if it.get("scores")]
    clusters = cluster_scored_items(scored_items)
    top_clusters = clusters[:top_n]

    lines: list[str] = []
    lines.append(f"# 选题简报 — {date}\n")
    lines.append(
        f"原始条目数：{len(scored_items)}；评分成功：{len(keep)}；"
        f"聚合事件数：{len(clusters)}；展示前 {len(top_clusters)} 个事件。\n"
    )

    # 类别统计
    from collections import Counter
    cat_count = Counter(it["scores"]["category"] for it in keep)
    ad_count = sum(1 for it in keep if it["scores"]["is_ad"])
    lines.append("## 类别分布")
    for cat, cnt in cat_count.most_common():
        lines.append(f"- {cat}: {cnt}")
    lines.append(f"- 检出广告/PR: {ad_count}")
    lines.append("")

    lines.append(f"## Top {len(top_clusters)} 选题候选")
    lines.append("")
    for i, cluster in enumerate(top_clusters, 1):
        it = cluster[0]
        s = it["scores"]
        title = it.get("title", "").strip()
        url = it.get("url", "")
        src = it["source"]
        pub = (it.get("published_at") or "")[:10]
        lines.append(f"### {i}. {title}")
        lines.append(
            f"- **{s['category']}** · final={s['final']:.1f} "
            f"(imp={s['importance']} / video={s['video_fit']} / aud={s['audience_fit']}) "
            f"· {src} · {pub}"
        )
        if len(cluster) > 1:
            sources = ", ".join(dict.fromkeys(str(x.get("source", "")) for x in cluster if x.get("source")))
            lines.append(f"- 聚合：{len(cluster)} 条相关资讯 · 来源：{sources}")
        lines.append(f"- 核心：{s['one_liner']}")
        lines.append(f"- 角度：{s['chinese_angle']}")
        lines.append(f"- 链接：{url}")
        for related in cluster[1:6]:
            rs = related["scores"]
            rtitle = (related.get("title") or "").strip()
            rsrc = related.get("source", "")
            rpub = (related.get("published_at") or "")[:10]
            rurl = related.get("url", "")
            lines.append(
                f"- 相关：{rsrc} · final={rs['final']:.1f} · {rpub} · {rtitle} · {rurl}"
            )
        if len(cluster) > 6:
            lines.append(f"- 相关：另有 {len(cluster) - 6} 条同事件资讯未展开")
        lines.append("")
    return "\n".join(lines)


# ---------- main ----------

def main(argv: list[str] | None = None) -> int:
    # 确保 print 在管道/后台模式下也实时刷新（不要被 block-buffer 卡住）
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(prog="yoko_video.m2.score", description="M2 LLM scorer")
    parser.add_argument("--date", help="日期 YYYY-MM-DD，默认 data/raw 里最新一天")
    parser.add_argument("--limit", type=int, help="只取前 N 条（调试用）")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH, help=f"批大小，默认 {DEFAULT_BATCH}")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型名，默认 {DEFAULT_MODEL}")
    parser.add_argument("--top-n", type=int, default=TOP_N_FOR_BRIEF, help=f"简报展示前 N 条，默认 {TOP_N_FOR_BRIEF}")
    parser.add_argument("--max-unscored", type=int,
                        help="本轮最多评分 N 条未评分条目；用于每日批处理控制 token，未评分完的下次继续")
    parser.add_argument("--only-unscored", action="store_true",
                        help="只评估 scored JSONL 里还没有 scores 的条目（增量评分）")
    args = parser.parse_args(argv)

    load_dotenv()
    profile = load_profile()
    system_prompt = build_system_prompt(profile)
    client = DeepSeekClient.from_env()

    date = args.date or latest_raw_date()
    items = load_raw(date)
    if args.limit:
        items = items[: args.limit]

    # 跨源去重（arXiv 跨分类 + 同标题）
    items, dedup_stats = preprocess_dedup(items)
    if dedup_stats["arxiv_collapsed"] or dedup_stats["title_collapsed"]:
        print(f"  preprocess dedup: arxiv-collapsed={dedup_stats['arxiv_collapsed']}, "
              f"title-collapsed={dedup_stats['title_collapsed']}")

    existing_scores: dict[str, dict[str, Any]] = {}
    if args.only_unscored:
        existing_scores = load_existing_scores(date)
        items_to_score = [it for it in items if it["id"] not in existing_scores]
        total_unscored = len(items_to_score)
        if args.max_unscored is not None:
            if args.max_unscored <= 0:
                print("--max-unscored 必须 > 0", file=sys.stderr)
                return 2
            items_to_score = items_to_score[: args.max_unscored]
        print(f"M2 score — date={date}, total={len(items)}, "
              f"already-scored={len(existing_scores)}, to-score={len(items_to_score)}, "
              f"unscored-total={total_unscored}, "
              f"batch={args.batch}, model={args.model}")
    else:
        items_to_score = items
        if args.max_unscored is not None:
            if args.max_unscored <= 0:
                print("--max-unscored 必须 > 0", file=sys.stderr)
                return 2
            items_to_score = items_to_score[: args.max_unscored]
        print(f"M2 score — date={date}, items={len(items_to_score)}, "
              f"batch={args.batch}, model={args.model}")

    # 调用 LLM 批量评分
    t0 = time.time()
    total_prompt_tokens = 0
    total_completion_tokens = 0
    batches = list(chunk(items_to_score, args.batch))
    all_scores: dict[str, dict[str, Any]] = {}
    failed_batches = 0
    for i, batch in enumerate(batches, 1):
        try:
            by_id, usage = score_batch(client, args.model, batch, system_prompt)
            all_scores.update(by_id)
            total_prompt_tokens += usage["prompt_tokens"]
            total_completion_tokens += usage["completion_tokens"]
            missing = len(batch) - len(by_id)
            mark = "" if missing == 0 else f" ⚠ {missing} 条未返回"
            print(f"  batch {i:>3}/{len(batches)}: scored {len(by_id):>2}/{len(batch)}{mark}  "
                  f"(in={usage['prompt_tokens']}, out={usage['completion_tokens']})")
        except Exception as e:
            failed_batches += 1
            print(f"  batch {i:>3}/{len(batches)}: ❌ {e}")

    # merge scores back into items（已有 + 新评分）
    scored: list[dict[str, Any]] = []
    for it in items:
        # 优先用已有 score（增量模式下）；其次用本轮新评分
        s_existing = existing_scores.get(it["id"])
        s_new = all_scores.get(it["id"])
        s = s_existing or s_new
        if s_existing:
            it["scores"] = s_existing  # 保留旧 score 原样（已含 final）
            scored.append(it)
            continue
        if s:
            score_obj = Score(
                is_ad=bool(s.get("is_ad", False)),
                category=s.get("category", "非AI"),
                importance=int(s.get("importance", 0)),
                video_fit=int(s.get("video_fit", 0)),
                audience_fit=int(s.get("audience_fit", 0)),
                one_liner=str(s.get("one_liner", "")),
                chinese_angle=str(s.get("chinese_angle", "")),
            )
            it["scores"] = {
                **s,
                "final": round(score_obj.final(), 2),
            }
        scored.append(it)

    scored_path = write_scored(date, scored)
    brief_md = render_brief(date, scored, args.top_n)
    brief_path = SCORED_DIR / f"{date}_brief.md"
    brief_path.write_text(brief_md, encoding="utf-8")

    elapsed = time.time() - t0
    success_count = sum(1 for it in scored if it.get("scores"))
    print(f"\n--- Summary ---")
    print(f"scored: {success_count} / {len(scored)} ({success_count*100//max(1,len(scored))}%)")
    print(f"failed batches: {failed_batches} / {len(batches)}")
    print(f"tokens: prompt {total_prompt_tokens:,}, completion {total_completion_tokens:,}")
    print(f"elapsed: {elapsed:.1f}s")
    print(f"output: {scored_path}")
    print(f"brief:  {brief_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
