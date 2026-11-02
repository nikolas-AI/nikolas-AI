"""Synchronously slow Platane/snk SVGs, with fail-closed validation.

The generator gives three animated CSS classes the same cycle duration:
  .c = contribution cells   .u = collected tally   .s = snake segments
Change ONLY the animation duration for all three, and reject unknown formats.
"""
import re
import sys
from pathlib import Path

SLOWDOWN = 2.5
STYLE = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.I | re.S)
# Match the *duration* in the animation shorthand of the three base classes.
RULE = re.compile(r"(?P<begin>\.(?P<class>[cus])\s*\{(?:(?!\}).)*?\banimation\s*:\s*[^;{}]*?\b)(?P<time>\d+(?:\.\d+)?)(?P<unit>ms|s)\b", re.S | re.I)


def slow_svg(svg: str) -> str:
    if not STYLE.search(svg):
        raise ValueError("SVG has no embedded CSS style; cannot apply safe slowdown")
    styles = STYLE.findall(svg)
    if len(styles) != 1:
        raise ValueError("Expected exactly one SVG style block")
    css = styles[0][1]
    matches = list(RULE.finditer(css))
    names = [m.group('class') for m in matches]
    if sorted(names) != ['c', 's', 'u']:
        raise ValueError(f"Expected one .c, .s, .u animation duration, got: {names}")
    times_ms = [float(m.group('time')) * (1000 if m.group('unit') == 's' else 1) for m in matches]
    if max(times_ms) - min(times_ms) > .01:
        raise ValueError(f"Original CSS animations already out of sync: {times_ms}")

    def scale(m):
        value = float(m.group('time')) * SLOWDOWN
        return m.group('begin') + f"{value:g}" + m.group('unit')

    updated_css, count = RULE.subn(scale, css)
    if count != 3:
        raise ValueError(f"Changed {count} durations; need exactly 3")
    return STYLE.sub(lambda m: m.group(1) + updated_css + m.group(3), svg, count=1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: python scripts/slow_snake.py dist/*.svg')
    for arg in sys.argv[1:]:
        p = Path(arg)
        original = p.read_text(encoding='utf-8')
        modified = slow_svg(original)
        p.write_text(modified, encoding='utf-8')
        print(f'{p}: snake, cells and tally synchronized at {SLOWDOWN}x slowdown')
