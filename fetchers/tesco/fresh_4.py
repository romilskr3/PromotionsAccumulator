from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from fetchers._shared.leaflet_cache import (
    is_stale,
    week_dir,
    write_meta,
    write_publication,
)
from fetchers.tesco.browser import fetch_fresh_4_page_text
from fetchers.tesco.constants import FRESH_4_URL
from fetchers.tesco.parse import parse_page_text

logger = logging.getLogger(__name__)


def download_fresh_4(*, refresh: bool = False) -> Path | None:
    """Fetch Fresh 4 page and cache parsed products. Returns week cache path."""
    cached = _latest_cache_dir()
    if cached and not refresh and not is_stale(cached):
        logger.info("Using cached Tesco Fresh 4 %s", cached.name)
        return cached

    page_text = fetch_fresh_4_page_text()
    if not page_text:
        if cached and not refresh:
            logger.warning("Tesco fetch failed; using stale cache %s", cached.name)
            return cached
        return None

    promo_from, promo_until, products = parse_page_text(page_text)
    if not promo_from or not promo_until or not products:
        logger.error("Could not parse Tesco Fresh 4 products from page")
        return cached

    path = week_dir("tesco", promo_from, promo_until)
    write_publication(
        path,
        {
            "source_url": FRESH_4_URL,
            "page_text": page_text,
            "products": products,
        },
    )
    write_meta(
        path,
        store="Tesco",
        source_url=FRESH_4_URL,
        promo_from=promo_from,
        promo_until=promo_until,
        label=f"Fresh 4 {promo_from:%d %b} – {promo_until:%d %b}",
        extra={"programme": "fresh_4"},
    )
    logger.info(
        "Cached Tesco Fresh 4 (%d products) → %s", len(products), path.name
    )
    return path


def _latest_cache_dir() -> Path | None:
    from fetchers._shared.leaflet_cache import list_week_dirs

    dirs = list_week_dirs("tesco")
    return dirs[-1] if dirs else None
