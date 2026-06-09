from __future__ import annotations

import logging
import os
from pathlib import Path

from fetchers.tesco.constants import FRESH_4_URL
from fetchers.tesco.session import has_storage_state, storage_state_path

logger = logging.getLogger(__name__)


def _playwright_browsers_path() -> None:
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        return
    default = Path.home() / "Library/Caches/ms-playwright"
    if default.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(default)


def _launch_chromium(playwright, *, headed: bool):
    launch_kwargs = {
        "headless": not headed,
        "args": ["--disable-blink-features=AutomationControlled"],
    }
    try:
        return playwright.chromium.launch(channel="chrome", **launch_kwargs)
    except Exception:
        logger.debug("Google Chrome not available; using Playwright Chromium")
        return playwright.chromium.launch(**launch_kwargs)


def _is_access_denied(page) -> bool:
    try:
        if "Access Denied" in page.title():
            return True
        text = page.inner_text("body", timeout=5_000)
        return "Access Denied" in text
    except Exception:
        return False


def fetch_fresh_4_page_text(*, headed: bool = False) -> str | None:
    """Load the public Fresh 4 buy-list page (Clubcard prices, no sign-in)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required for Tesco. Run: pip install playwright && "
            "playwright install chrome"
        ) from exc

    _playwright_browsers_path()
    storage = storage_state_path() if has_storage_state() else None

    with sync_playwright() as playwright:
        browser = _launch_chromium(playwright, headed=headed)
        context_kwargs: dict = {
            "locale": "en-IE",
            "timezone_id": "Europe/Dublin",
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "viewport": {"width": 1440, "height": 900},
        }
        if storage:
            context_kwargs["storage_state"] = str(storage)

        context = browser.new_context(**context_kwargs)
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = context.new_page()
        try:
            page.goto(FRESH_4_URL, wait_until="domcontentloaded", timeout=90_000)
            page.wait_for_timeout(2_000)
            _dismiss_cookie_banner(page)
            if _is_access_denied(page):
                logger.error(
                    "Tesco blocked automated access (Akamai). "
                    "Install Google Chrome for Playwright: playwright install chrome"
                )
                return None
            text = _wait_for_product_listing(page)
            if not text:
                logger.error("Fresh 4 page loaded but no Clubcard prices found")
                return None
            return text
        except Exception as exc:
            if _is_access_denied(page):
                logger.error("Tesco blocked automated access (Akamai)")
                return None
            logger.error("Failed to load Tesco Fresh 4 page: %s", exc)
            return None
        finally:
            context.close()
            browser.close()


def _wait_for_product_listing(page) -> str | None:
    """Poll page body until Fresh 4 product rows render (title tag alone is not enough)."""
    for _ in range(30):
        if _is_access_denied(page):
            logger.error("Tesco blocked automated access (Akamai)")
            return None
        text = page.inner_text("body")
        if "Write a review" in text and "Clubcard Price" in text:
            return text
        page.wait_for_timeout(1_000)
    return None


def _dismiss_cookie_banner(page) -> None:
    for selector in (
        "button:has-text('Accept all')",
        "#onetrust-accept-btn-handler",
    ):
        try:
            page.locator(selector).first.click(timeout=3_000)
            page.wait_for_timeout(1_000)
            return
        except Exception:
            continue
