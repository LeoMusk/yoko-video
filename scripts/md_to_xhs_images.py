"""Render Markdown articles into Xiaohongshu-style image carousels.

Usage:
    python scripts/md_to_xhs_images.py path/to/article.md
    python scripts/md_to_xhs_images.py path/to/md_dir --out data/xhs

The renderer creates 3:4 PNG pages. Page breaks can be forced with:
    <!-- pagebreak -->
    ---PAGE---
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import markdown
from playwright.sync_api import sync_playwright


DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1440
DEFAULT_BRAND = "@YokoAI"
DEFAULT_THEME = "yoko-clean"

PAGEBREAK_MARKERS = {"<!-- pagebreak -->", "<!--pagebreak-->", "---PAGE---", "[pagebreak]"}
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SLUG_RE = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+")


@dataclass
class RenderOptions:
    width: int
    height: int
    brand: str
    theme: str
    scale: int
    out_dir: Path
    write_html: bool


def slugify(value: str) -> str:
    value = value.strip()
    if not value:
        return "article"
    value = SLUG_RE.sub("-", value)
    value = value.strip("-_")
    return value[:80] or "article"


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or fallback
    return fallback


def split_markdown_blocks(text: str) -> list[str | None]:
    """Split Markdown into renderable blocks. None marks a forced page break."""
    blocks: list[str | None] = []
    current: list[str] = []
    in_fence = False

    def flush() -> None:
        nonlocal current
        block = "\n".join(current).strip()
        if block:
            blocks.append(block)
        current = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not in_fence and stripped in PAGEBREAK_MARKERS:
            flush()
            blocks.append(None)
            continue

        if FENCE_RE.match(stripped):
            in_fence = not in_fence
            current.append(line)
            continue

        if not in_fence and not stripped:
            flush()
            continue

        current.append(line)

    flush()
    return blocks


def render_markdown_block(block: str) -> str:
    return markdown.markdown(
        block,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )


def render_markdown_page(blocks_html: list[str]) -> str:
    return "\n".join(blocks_html)


def theme_css(options: RenderOptions) -> str:
    if options.theme != DEFAULT_THEME:
        raise ValueError(f"Unsupported theme: {options.theme}")

    return f"""
    :root {{
      --page-w: {options.width}px;
      --page-h: {options.height}px;
      --ink: #171717;
      --muted: #4a4a4a;
      --faint: #8a8a8a;
      --paper: #fffdf9;
      --line: #e8e4dc;
      --accent: #111111;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
    background: transparent;
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;
      letter-spacing: 0;
    }}
    .stage {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 32px;
      padding: 32px;
      background: transparent;
    }}
    .xhs-page {{
      width: var(--page-w);
      height: var(--page-h);
      position: relative;
      overflow: hidden;
      background: var(--paper);
      padding: 92px 88px 88px;
      border-radius: 1%;
    }}
    .page-badge {{
      position: absolute;
      top: 38px;
      right: 42px;
      min-width: 74px;
      height: 42px;
      border-radius: 999px;
      background: #d4d4d4;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: 700;
      line-height: 1;
    }}
    .brand {{
      position: absolute;
      left: 88px;
      bottom: 42px;
      font-size: 22px;
      color: var(--faint);
      font-weight: 600;
      letter-spacing: 0;
    }}
    .content {{
      height: calc(var(--page-h) - 210px);
      overflow: hidden;
    }}
    .content h1 {{
      margin: 22px 0 60px;
      font-size: 82px;
      line-height: 1.15;
      font-weight: 900;
      color: var(--ink);
      text-wrap: balance;
    }}
    .content h2 {{
      margin: 42px 0 24px;
      font-size: 48px;
      line-height: 1.24;
      font-weight: 900;
      color: var(--ink);
    }}
    .content h3 {{
      margin: 32px 0 18px;
      font-size: 34px;
      line-height: 1.32;
      font-weight: 850;
      color: var(--ink);
    }}
    .content p {{
      margin: 0 0 28px;
      font-size: 31px;
      line-height: 1.72;
      font-weight: 520;
      color: var(--muted);
    }}
    .content strong {{
      color: var(--ink);
      font-weight: 850;
    }}
    .content em {{
      color: var(--ink);
      font-style: normal;
      font-weight: 760;
      background: linear-gradient(transparent 64%, #f6e7a9 0);
    }}
    .content blockquote {{
      margin: 30px 0;
      padding: 18px 28px;
      border-left: 8px solid var(--accent);
      background: #f6f3ec;
      color: var(--ink);
    }}
    .content blockquote p {{
      margin: 0;
      color: var(--ink);
      font-weight: 700;
    }}
    .content ul,
    .content ol {{
      margin: 18px 0 30px;
      padding-left: 42px;
    }}
    .content li {{
      margin: 0 0 18px;
      font-size: 30px;
      line-height: 1.62;
      color: var(--muted);
      font-weight: 520;
    }}
    .content code {{
      font-family: "SF Mono", Consolas, "Roboto Mono", monospace;
      font-size: 0.82em;
      color: var(--ink);
      background: #efebe3;
      padding: 3px 8px;
      border-radius: 6px;
    }}
    .content pre {{
      margin: 26px 0;
      padding: 24px;
      background: #171717;
      color: #f5f5f5;
      border-radius: 12px;
      overflow: hidden;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .content pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
      font-size: 22px;
      line-height: 1.55;
    }}
    .content hr {{
      border: 0;
      border-top: 2px solid var(--line);
      margin: 34px 0;
    }}
    .content img {{
      display: block;
      max-width: 100%;
      max-height: 520px;
      object-fit: contain;
      margin: 28px auto;
      border-radius: 10px;
    }}
    .content table {{
      width: 100%;
      border-collapse: collapse;
      margin: 24px 0;
      font-size: 22px;
    }}
    .content th,
    .content td {{
      border: 2px solid var(--line);
      padding: 12px 14px;
      text-align: left;
      vertical-align: top;
    }}
    .content th {{
      background: #f2eee6;
      color: var(--ink);
      font-weight: 800;
    }}
    """


def html_document(pages: list[str], title: str, options: RenderOptions) -> str:
    css = theme_css(options)
    safe_title = html.escape(title)
    total = len(pages)
    page_html = []
    for idx, page_body in enumerate(pages, 1):
        page_html.append(
            f"""
            <section class="xhs-page" data-page="{idx}">
              <div class="page-badge">{idx}/{total}</div>
              <main class="content">{page_body}</main>
              <div class="brand">{html.escape(options.brand)}</div>
            </section>
            """
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>{css}</style>
</head>
<body>
  <div class="stage">
    {''.join(page_html)}
  </div>
</body>
</html>
"""


def paginate(blocks: list[str | None], options: RenderOptions) -> list[str]:
    block_html = [None if b is None else render_markdown_block(b) for b in blocks]
    pages: list[list[str]] = []
    current: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": options.width + 100, "height": options.height + 100},
            device_scale_factor=1,
        )
        measure_html = html_document([""], "measure", options)
        page.set_content(measure_html, wait_until="load")

        def fits(candidate: list[str]) -> bool:
            html_body = render_markdown_page(candidate)
            return bool(
                page.evaluate(
                    """(htmlBody) => {
                        const content = document.querySelector('.content');
                        content.innerHTML = htmlBody;
                        return content.scrollHeight <= content.clientHeight + 2;
                    }""",
                    html_body,
                )
            )

        for block in block_html:
            if block is None:
                if current:
                    pages.append(current)
                    current = []
                continue

            candidate = current + [block]
            if not current or fits(candidate):
                current = candidate
            else:
                pages.append(current)
                current = [block]

        if current:
            pages.append(current)
        browser.close()

    return [render_markdown_page(p) for p in pages] or [""]


def render_article(path: Path, options: RenderOptions) -> list[Path]:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    title = title_from_markdown(text, path.stem)
    slug = slugify(path.stem)
    article_out = options.out_dir / slug
    article_out.mkdir(parents=True, exist_ok=True)

    blocks = split_markdown_blocks(text)
    pages = paginate(blocks, options)
    doc = html_document(pages, title, options)
    html_path = article_out / f"{slug}.html"
    if options.write_html:
        html_path.write_text(doc, encoding="utf-8")

    outputs: list[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": options.width + 100, "height": options.height + 100},
            device_scale_factor=options.scale,
        )
        page.set_content(doc, wait_until="load")
        locators = page.locator(".xhs-page")
        total = locators.count()
        for idx in range(total):
            output = article_out / f"{slug}_{idx + 1:02d}.png"
            locators.nth(idx).screenshot(path=str(output), omit_background=True)
            outputs.append(output)
        browser.close()

    return outputs


def iter_inputs(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    for item in sorted(path.glob("*.md")):
        if item.is_file():
            yield item


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Convert Markdown to Xiaohongshu PNG carousel images.")
    parser.add_argument("input", help="Markdown file or directory containing .md files")
    parser.add_argument("--out", default="data/xhs", help="Output directory. Default: data/xhs")
    parser.add_argument("--brand", default=DEFAULT_BRAND, help=f"Footer brand text. Default: {DEFAULT_BRAND}")
    parser.add_argument("--theme", default=DEFAULT_THEME, help=f"Theme name. Default: {DEFAULT_THEME}")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"Page width px. Default: {DEFAULT_WIDTH}")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help=f"Page height px. Default: {DEFAULT_HEIGHT}")
    parser.add_argument("--scale", type=int, default=1, help="Screenshot device scale factor. Default: 1")
    parser.add_argument("--no-html", action="store_true", help="Do not write preview HTML")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2

    options = RenderOptions(
        width=args.width,
        height=args.height,
        brand=args.brand,
        theme=args.theme,
        scale=args.scale,
        out_dir=Path(args.out),
        write_html=not args.no_html,
    )

    total_files = 0
    total_images = 0
    for md_path in iter_inputs(input_path):
        total_files += 1
        outputs = render_article(md_path, options)
        total_images += len(outputs)
        print(f"{md_path} -> {len(outputs)} images")
        for output in outputs:
            print(f"  {output}")

    if total_files == 0:
        print(f"No .md files found: {input_path}", file=sys.stderr)
        return 2
    print(f"\nDone: {total_files} markdown file(s), {total_images} image(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
