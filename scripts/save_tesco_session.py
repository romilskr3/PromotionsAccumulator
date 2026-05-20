#!/usr/bin/env python3
"""One-time helper: sign in to Tesco.ie and save cookies for Fresh 4 scraping."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fetchers._shared.leaflet_cache import LEAFLETS_ROOT
from fetchers.tesco.constants import FRESH_4_URL


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install Playwright first: pip install playwright && playwright install chromium")
        return 1

    out = LEAFLETS_ROOT / "tesco" / "storage-state.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    print("A Chromium window will open.")
    print("1. Sign in to Tesco.ie (Clubcard) if you want promo prices.")
    print("2. Open the Fresh 4 page and confirm products are visible.")
    print("3. Return here and press Enter to save the session.\n")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(locale="en-IE", timezone_id="Europe/Dublin")
        page = context.new_page()
        page.goto("https://www.tesco.ie/", wait_until="domcontentloaded")
        input("Press Enter when signed in… ")
        page.goto(FRESH_4_URL, wait_until="domcontentloaded")
        input("Press Enter when Fresh 4 products are visible… ")
        context.storage_state(path=str(out))
        browser.close()

    print(f"Saved session to {out}")
    print("Run: python scripts/update_promotions.py --store tesco")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
