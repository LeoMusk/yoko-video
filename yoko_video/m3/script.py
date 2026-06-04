"""M3 脚本合成：读 M2 选题 → LLM 生成形态无关结构化脚本 → 渲染 markdown。

用法：
    python -m yoko_video.m3.script                      # 当日 brief 取 final 最高 2 条
    python -m yoko_video.m3.script --top 3              # 取前 3 条
    python -m yoko_video.m3.script --date 2026-05-28
    python -m yoko_video.m3.script --ids 5544e5b 77d1c4 # 指定条目 id

输出：
    data/scripts/YYYY-MM-DD_scripts.md   可直接拍摄的脚本
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from ..m2.env import load_dotenv
from ..m2.llm import DeepSeekClient, extract_content, usage_of
from .prompt import SYSTEM_PROMPT, build_user_message


SCORED_DIR = Path("data/scored")
SCRIPTS_DIR = Path("data/scripts")
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TOP = 2


def latest_scored_date() -> str:
    files = sorted(SCORED_DIR.glob("*_scored.jsonl"))
    if not files:
        raise FileNotFoundError("data/scored 里没有 *_scored.jsonl，先跑 M2")
    return files[-1].stem.replace("_scored", "")


def load_scored(date: str) -> list[dict[str, Any]]:
    path = SCORED_DIR / f"{date}_scored.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"{path} 不存在")
    return [json.loads(l) for l in path.open(encoding="utf-8")]


_CLICHE_RE = re.compile(
    r"不是[^，。,！!]{1,15}[，,]\s*(而)?是"
    r"|这不是(幻觉|科幻|危言)"
    r"|你以为.{0,20}其实"
    r"|震惊[！!]|颠覆认知|细思极恐|拭目以待"
)


def _find_cliche(script: dict[str, Any]) -> str | None:
    """检测 hook/voiceover 是否含被禁的 AI 腔套路。返回命中片段或 None。"""
    text = f"{script.get('hook', '')} {script.get('voiceover', '')}"
    m = _CLICHE_RE.search(text)
    return m.group(0) if m else None


def generate_script(
    client: DeepSeekClient, model: str, item: dict[str, Any], max_retries: int = 2
) -> tuple[dict[str, Any], dict[str, int]]:
    """生成脚本；若命中 AI 腔套路则降温重试，最多 max_retries 次。"""
    user_msg = build_user_message(item)
    last: tuple[dict[str, Any], dict[str, int]] | None = None
    for attempt in range(max_retries + 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        if attempt > 0:
            print(f" [套路重试{attempt}]", end="", flush=True)
            messages.append({
                "role": "user",
                "content": "上一版用了被禁止的 AI 腔套路（如'不是X，是Y'对仗句）。重写，钩子和口播绝不出现这类对仗/套路句，直接用事实和数字开场。",
            })
        resp = client.chat(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7 if attempt == 0 else 0.3,
            max_tokens=3000,
        )
        content = extract_content(resp)
        if not content.strip():
            raise RuntimeError("LLM 返回空 content")
        script = json.loads(content)
        last = (script, usage_of(resp))
        if _find_cliche(script) is None:
            return last
    return last  # type: ignore[return-value]  # 重试用尽，返回最后一版


def render_scripts(date: str, scripts: list[tuple[dict[str, Any], dict[str, Any]]]) -> str:
    lines: list[str] = []
    lines.append(f"# 短视频脚本 — {date}\n")
    lines.append(f"共 {len(scripts)} 条。脚本为形态无关结构，可用于真人口播 / 数字人 / Remotion 信息流。\n")

    for i, (item, s) in enumerate(scripts, 1):
        scores = item.get("scores") or {}
        lines.append(f"\n---\n")
        lines.append(f"## 脚本 {i}：{s.get('title_caption', '')}\n")
        lines.append(
            f"> 选题：{item.get('title', '')}　"
            f"（{item.get('source', '')} · {scores.get('category', '')} · "
            f"final={scores.get('final', '?')} · 建议时长 {s.get('duration_sec', '?')}s）"
        )
        url = item.get("url", "")
        if url:
            lines.append(f"> 原文：{url}")
        lines.append("")

        lines.append(f"### 钩子（0-3s）")
        lines.append(s.get("hook", ""))
        lines.append("")

        dps = s.get("data_points") or []
        if dps:
            lines.append("### 关键数据")
            for dp in dps:
                lines.append(f"- **{dp.get('value', '')}** — {dp.get('label', '')}")
            lines.append("")

        lines.append("### 核心信息点")
        for kp in s.get("key_points", []):
            lines.append(f"- {kp}")
        lines.append("")

        lines.append("### yoko 观点（差异化灵魂）")
        lines.append(s.get("yoko_take", ""))
        lines.append("")

        lines.append("### 引流 CTA")
        lines.append(s.get("cta", ""))
        lines.append("")

        lines.append("### 口播逐字稿")
        lines.append(s.get("voiceover", ""))
        lines.append("")

        lines.append("### 画面建议")
        for vc in s.get("visual_cues", []):
            lines.append(f"- {vc}")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(prog="yoko_video.m3.script", description="M3 脚本合成")
    parser.add_argument("--date", help="日期 YYYY-MM-DD，默认最新 scored")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, help=f"取 final 最高 N 条，默认 {DEFAULT_TOP}")
    parser.add_argument("--ids", nargs="*", help="指定条目 id（前缀匹配），覆盖 --top")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)

    load_dotenv()
    client = DeepSeekClient.from_env()

    date = args.date or latest_scored_date()
    items = load_scored(date)

    if args.ids:
        prefixes = tuple(args.ids)
        selected = [it for it in items if it.get("id", "").startswith(prefixes)]
    else:
        candidates = [
            it for it in items
            if it.get("scores")
            and not it["scores"].get("is_ad")
            and it["scores"].get("category") != "非AI"
        ]
        candidates.sort(key=lambda it: it["scores"]["final"], reverse=True)
        selected = candidates[: args.top]

    if not selected:
        print("没有符合条件的选题（检查 is_ad / 非AI 过滤或 --ids）", file=sys.stderr)
        return 2

    print(f"M3 script — date={date}, 生成 {len(selected)} 条脚本, model={args.model}")
    results: list[tuple[dict[str, Any], dict[str, Any]]] = []
    tot_in = tot_out = 0
    for it in selected:
        title = (it.get("title") or "")[:40]
        print(f"  生成中: {title} ...", end="", flush=True)
        try:
            script, usage = generate_script(client, args.model, it)
            results.append((it, script))
            tot_in += usage["prompt_tokens"]
            tot_out += usage["completion_tokens"]
            print(f" ok ({usage['completion_tokens']} tok)")
        except Exception as e:
            print(f" 失败: {e}")

    if not results:
        print("全部生成失败", file=sys.stderr)
        return 1

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out_md = SCRIPTS_DIR / f"{date}_scripts.md"
    out_md.write_text(render_scripts(date, results), encoding="utf-8")

    # 结构化 JSON 供 Remotion 消费
    out_json = SCRIPTS_DIR / f"{date}_scripts.json"
    payload = {
        "date": date,
        "scripts": [
            {
                "title_caption": s.get("title_caption", ""),
                "hook": s.get("hook", ""),
                "data_points": s.get("data_points", []),
                "key_points": s.get("key_points", []),
                "yoko_take": s.get("yoko_take", ""),
                "cta": s.get("cta", ""),
                "voiceover": s.get("voiceover", ""),
                "visual_cues": s.get("visual_cues", []),
                "duration_sec": s.get("duration_sec", 60),
                "meta": {
                    "title": it.get("title", ""),
                    "source": it.get("source", ""),
                    "url": it.get("url", ""),
                    "category": (it.get("scores") or {}).get("category", ""),
                    "final": (it.get("scores") or {}).get("final"),
                },
            }
            for it, s in results
        ],
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\ntokens: in={tot_in}, out={tot_out}")
    print(f"输出: {out_md}")
    print(f"      {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
