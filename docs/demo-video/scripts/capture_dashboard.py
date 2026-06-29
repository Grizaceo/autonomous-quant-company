"""Capture screenshots of the AQTC FastAPI dashboard at :8010.

Writes PNGs into docs/demo-video/clips/.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8010"
OUT = Path("docs/demo-video/clips")
OUT.mkdir(parents=True, exist_ok=True)

ENDPOINTS = [
    ("dashboard", "/"),
    ("provenance_api", "/provenance"),
    ("status_api", "/status"),
]

VIEWPORT = {"width": 1280, "height": 800}


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()
        for name, path in ENDPOINTS:
            url = f"{BASE}{path}"
            page.goto(url, wait_until="networkidle")
            png = OUT / f"{name}.png"
            page.screenshot(path=str(png), full_page=True)
            print(f"OK -> {png}  ({url})")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
