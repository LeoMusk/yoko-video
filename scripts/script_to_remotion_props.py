"""Convert an M3 scripts.json item into remotion/props.json.

Usage:
    python scripts/script_to_remotion_props.py --latest --index 1
    python scripts/script_to_remotion_props.py --date 2026-06-20 --index 2
    python scripts/script_to_remotion_props.py examples/script_sample.json --out remotion/props.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPTS_DIR = Path("data/scripts")
DEFAULT_OUT = Path("remotion/props.json")


def latest_scripts_file() -> Path:
    files = sorted(SCRIPTS_DIR.glob("*_scripts.json"))
    if not files:
        raise FileNotFoundError("data/scripts 里没有 *_scripts.json，请先运行 M3")
    return files[-1]


def file_for_date(date: str) -> Path:
    path = SCRIPTS_DIR / f"{date}_scripts.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} 不存在")
    return path


def normalize_props(script: dict[str, Any]) -> dict[str, Any]:
    creator_take = script.get("creator_take") or script.get("yoko_take") or ""
    return {
        "title_caption": script.get("title_caption", ""),
        "hook": script.get("hook", ""),
        "data_points": script.get("data_points") or [],
        "key_points": script.get("key_points") or [],
        "creator_take": creator_take,
        # Backward-compatible field consumed by older Remotion templates.
        "yoko_take": creator_take,
        "cta": script.get("cta", ""),
        "voiceover": script.get("voiceover", ""),
        "visual_cues": script.get("visual_cues") or [],
        "duration_sec": int(script.get("duration_sec") or 60),
        "meta": script.get("meta") or {},
    }


def load_script(path: Path, index: int) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    scripts = payload.get("scripts") or []
    if not scripts:
        raise ValueError(f"{path} 中没有 scripts 数组")
    if index < 1 or index > len(scripts):
        raise IndexError(f"--index 必须在 1..{len(scripts)} 之间")
    return scripts[index - 1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert M3 scripts.json to Remotion props.json")
    parser.add_argument("input", nargs="?", help="scripts.json 路径；不传则使用 --date 或 --latest")
    parser.add_argument("--latest", action="store_true", help="使用 data/scripts 下最新的 *_scripts.json")
    parser.add_argument("--date", help="使用 data/scripts/YYYY-MM-DD_scripts.json")
    parser.add_argument("--index", type=int, default=1, help="选择 scripts 数组里的第 N 条，默认 1")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help=f"输出路径，默认 {DEFAULT_OUT}")
    args = parser.parse_args()

    if args.input:
        src = Path(args.input)
    elif args.date:
        src = file_for_date(args.date)
    else:
        src = latest_scripts_file()

    script = load_script(src, args.index)
    props = normalize_props(script)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"source: {src}")
    print(f"index:  {args.index}")
    print(f"output: {out}")
    print(f"title:  {props.get('title_caption', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
