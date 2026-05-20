from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import fitz
import requests

from fetchers._shared.http import get
from fetchers._shared.leaflet_cache import (
    best_cached_week_dir,
    dublin_today,
    is_stale,
    week_dir,
    write_meta,
    write_publication,
)
from fetchers.supervalu.constants import PDF_BASE_URL, STORE_NAME
from fetchers.supervalu.discover import discover_current_leaflet
from fetchers.supervalu.parse import parse_dates_from_pdf

logger = logging.getLogger(__name__)


def download_leaflet(*, refresh: bool = False) -> Path | None:
    """Download the current SuperValu leaflet, or keep the best local cache.

    Cached PDFs under leaflets/supervalu/ are never deleted automatically.
    """
    cache = best_cached_week_dir("supervalu")
    info = discover_current_leaflet()
    if not info:
        return _use_cache(
            cache,
            reason="no full leaflet manifest on supervalu.ie (hub or /offers/leaflet/{id})",
        )

    pdf_url = PDF_BASE_URL.format(filename=info.source_pdf)
    logger.info(
        "SuperValu online leaflet PA%s → %s",
        info.leaflet_id,
        pdf_url,
    )

    try:
        pdf_bytes = get(pdf_url).content
    except requests.RequestException as exc:
        return _use_cache(
            cache,
            reason=f"PDF download failed ({pdf_url}): {exc}",
        )

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    promo_from, promo_until = parse_dates_from_pdf(doc)
    doc.close()
    if not promo_from or not promo_until:
        return _use_cache(
            cache,
            reason="could not read promo dates from downloaded PDF",
        )

    today = dublin_today()
    if promo_until < today:
        return _use_cache(
            cache,
            reason=(
                f"online leaflet PA{info.leaflet_id} ended {promo_until.isoformat()} "
                f"(today {today.isoformat()})"
            ),
        )

    path = week_dir("supervalu", promo_from, promo_until)
    if not refresh and not is_stale(path) and (path / "leaflet.pdf").exists():
        logger.info("Using cached SuperValu leaflet %s", path.name)
        return path

    (path / "leaflet.pdf").write_bytes(pdf_bytes)
    write_publication(
        path,
        {
            "leaflet_id": info.leaflet_id,
            "source_pdf": info.source_pdf,
            "source_url": info.source_url,
            "page_count": info.page_count,
            "created_at": info.created_at,
        },
    )
    write_meta(
        path,
        store=STORE_NAME,
        source_url=info.source_url,
        promo_from=promo_from,
        promo_until=promo_until,
        label=f"PA{info.leaflet_id}",
        extra={"leaflet_id": info.leaflet_id, "pdf_url": pdf_url},
    )
    logger.info("Cached SuperValu leaflet %s → %s", info.leaflet_id, path.name)
    return path


def _use_cache(cache: Path | None, *, reason: str) -> Path | None:
    if cache:
        logger.warning(
            "SuperValu: %s — using local cache %s (leaflets are never auto-deleted)",
            reason,
            cache.name,
        )
        return cache
    logger.warning("SuperValu: %s — no local cache available", reason)
    return None
