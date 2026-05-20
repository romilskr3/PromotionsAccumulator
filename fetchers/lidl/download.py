from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fetchers._shared.leaflet_cache import (
    is_stale,
    publication_path,
    week_dir,
    write_meta,
    write_publication,
)
from fetchers._shared.models import WeekWindow
from fetchers.lidl.hub import discover_weeks

logger = logging.getLogger(__name__)

LEAFLET_API_HOSTS = ("endpoints.leaflets.schwarz", "cms.leaflets.schwarz")


def download_leaflets(*, refresh: bool = False) -> list[Path]:
    weeks = discover_weeks()
    if not weeks:
        logger.warning("No Lidl leaflet weeks found on hub page")
        return []

    saved: list[Path] = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required for Lidl leaflet download. "
            "Run: pip install playwright && playwright install chromium"
        ) from exc

    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if not browsers_path:
        default = Path.home() / "Library/Caches/ms-playwright"
        if default.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(default)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="en-IE",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        for week in weeks:
            path = week_dir("lidl", week.promo_from, week.promo_until)
            if not refresh and not is_stale(path):
                logger.info("Using cached leaflet %s", path.name)
                saved.append(path)
                continue

            logger.info("Downloading leaflet %s → %s", week.label, path.name)
            captured = _capture_leaflet_json(context, week)
            if not captured:
                logger.error("No leaflet API data captured for %s", week.source_url)
                continue

            write_publication(path, captured)
            write_meta(
                path,
                store="Lidl",
                source_url=week.source_url,
                promo_from=week.promo_from,
                promo_until=week.promo_until,
                label=week.label,
                extra={"capture_count": len(captured)},
            )
            _maybe_download_pdf(path, captured)
            saved.append(path)

        browser.close()

    return saved


def _capture_leaflet_json(context, week: WeekWindow) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []

    def on_response(response):
        url = response.url
        if not any(host in url for host in LEAFLET_API_HOSTS):
            return
        try:
            if "application/json" not in (response.headers.get("content-type") or ""):
                # Some endpoints still return JSON without strict header
                pass
            body = response.json()
            captured.append({"url": url, "data": body})
        except Exception:
            pass

    page = context.new_page()
    page.on("response", on_response)
    try:
        page.goto(week.source_url, wait_until="networkidle", timeout=90_000)
        page.wait_for_timeout(3000)
    except Exception as exc:
        logger.warning("Leaflet page load issue for %s: %s", week.source_url, exc)
    finally:
        page.close()

    return captured


def _maybe_download_pdf(week_path: Path, captured: list[dict[str, Any]]) -> None:
    pdf_url = _find_pdf_url(captured)
    if not pdf_url:
        return
    try:
        from fetchers._shared.http import get

        response = get(pdf_url)
        (week_path / "leaflet.pdf").write_bytes(response.content)
        logger.info("Saved PDF for %s", week_path.name)
    except Exception as exc:
        logger.warning("PDF download failed: %s", exc)


def _find_pdf_url(captured: list[dict[str, Any]]) -> str | None:
    for item in captured:
        url = _walk_find_key(item.get("data"), "pdfUrl")
        if url and isinstance(url, str) and url.startswith("http"):
            return url
    return None


def _walk_find_key(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            found = _walk_find_key(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _walk_find_key(item, key)
            if found is not None:
                return found
    return None
