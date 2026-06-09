#!/usr/bin/env python3
"""Optional helper: save Tesco.ie cookies if automated Fresh 4 fetches are blocked."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fetchers.tesco.browser import _dismiss_cookie_banner, _launch_chromium
from fetchers.tesco.constants import FRESH_4_URL
from fetchers.tesco.session import storage_state_path


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install Playwright first: pip install playwright && playwright install chrome")
        return 1

    out = storage_state_path()
    out.parent.mkdir(parents=True, exist_ok=True)

    print("A Chrome window will open.")
    print("1. Sign in to Tesco.ie (Clubcard) if prompted.")
    print("2. Confirm Fresh 4 Clubcard prices are visible.")
    print("3. Return here and press Enter to save the session.\n")

    with sync_playwright() as playwright:
        browser = _launch_chromium(playwright, headed=True)
        context = browser.new_context(
            locale="en-IE",
            timezone_id="Europe/Dublin",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = context.new_page()
        page.goto(FRESH_4_URL, wait_until="domcontentloaded")
        _dismiss_cookie_banner(page)
        input("Press Enter when Fresh 4 Clubcard prices are visible… ")
        context.storage_state(path=str(out))
        browser.close()

    print(f"Saved session to {out}")
    print("Run: .venv/bin/python scripts/update_promotions.py --store tesco --refresh-leaflets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
