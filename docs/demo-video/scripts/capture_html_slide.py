"""Render a local HTML slide (docs/demo-video/clips/*.html) to a 1920x1080 PNG.

Usage: python capture_html_slide.py <slide.html> [<slide2.html> ...]
Writes <slide>.png next to each input file.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1920, "height": 1080}


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: capture_html_slide.py <slide.html> [...]", file=sys.stderr)
        return 2
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        page = ctx.new_page()
        for arg in argv:
            html_path = Path(arg).resolve()
            png_path = html_path.with_suffix(".png")
            page.goto(html_path.as_uri(), wait_until="networkidle")
            page.screenshot(path=str(png_path))
            print(f"OK -> {png_path}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
