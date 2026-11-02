"""Slow Platane/snk SVG animations without desynchronizing snake and dots.

The snk SVG uses multiple synchronized CSS animations, including both the
snake's travel and the removal of contribution squares. All CSS millisecond
values in <style> must be scaled by the SAME factor.

Usage: python scripts/slow_snake.py dist/*.svg
"""
from pathlib import Path
import re
import sys

SLOWDOWN = 2.5
STYLE = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.I | re.S)
TIME = re.compile(r"(?<![\w.-])(-?\d+(?:\.\d+)?)ms\b", re.I)


def slow_svg(svg: str) -> str:
    count = 0
    def edit_style(match: re.Match) -> str:
        nonlocal count
        def scale_time(t: re.Match) -> str:
            nonlocal count
            count += 1
            number = float(t.group(1)) * SLOWDOWN
            return f"{number:g}ms"
        return match.group(1) + TIME.sub(scale_time, match.group(2)) + match.group(3)
    modified = STYLE.sub(edit_style, svg)
    if count < 2:
        raise ValueError(f"Expected multiple CSS animation timings; found {count}. SVG format may have changed.")
    return modified


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/slow_snake.py dist/*.svg")
    for filename in sys.argv[1:]:
        path = Path(filename)
        original = path.read_text(encoding="utf-8")
        updated = slow_svg(original)
        path.write_text(updated, encoding="utf-8")
        print(f"{filename}: all CSS animation timings scaled {SLOWDOWN}x")
