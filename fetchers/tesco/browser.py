from __future__ import annotations

import logging
import os
from pathlib import Path

from fetchers._shared.leaflet_cache import LEAFLETS_ROOT
from fetchers.tesco.constants import FRESH_4_URL

logger = logging.getLogger(__name__)


def _playwright_browsers_path() -> None:
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        return
    default = Path.home() / "Library/Caches/ms-playwright"
    if default.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(default)


def _storage_state_file() -> Path | None:
    env_path = os.environ.get("TESCO_STORAGE_STATE")
    if env_path:
        path = Path(env_path)
        return path if path.exists() else None
    path = LEAFLETS_ROOT / "tesco" / "storage-state.json"
    return path if path.exists() else None


def fetch_fresh_4_page_text(*, headed: bool = False) -> str | None:
    """Load Fresh 4 buy-list; requires saved browser session if Akamai blocks bots."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required for Tesco. Run: pip install playwright && "
            "playwright install chromium"
        ) from exc

    _playwright_browsers_path()
    storage = _storage_state_file()
    if not storage:
        logger.warning(
            "No Tesco browser session at %s — run: python scripts/save_tesco_session.py",
            LEAFLETS_ROOT / "storage-state.json",
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=not headed,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context_kwargs: dict = {
            "locale": "en-IE",
            "timezone_id": "Europe/Dublin",
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
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
            page.wait_for_timeout(4_000)
            _dismiss_cookie_banner(page)
            page.wait_for_selector("text=Fresh 4", timeout=30_000)
            page.wait_for_timeout(2_000)
            text = page.inner_text("body")
            if "Access Denied" in text:
                logger.error("Tesco blocked automated access (Akamai)")
                return None
            if "Clubcard Price" not in text:
                logger.warning("Fresh 4 page loaded but no Clubcard prices found")
            return text
        except Exception as exc:
            logger.error("Failed to load Tesco Fresh 4 page: %s", exc)
            return None
        finally:
            context.close()
            browser.close()


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
