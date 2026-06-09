from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from fetchers._shared.http import get, get_optional
from fetchers.supervalu.constants import (
    LEAFLET_SCAN_HI,
    LEAFLET_SCAN_LO,
    LEAFLET_URL,
    MIN_FULL_LEAFLET_PAGES,
    OFFERS_HUB_URL,
)

logger = logging.getLogger(__name__)

_MANIFEST_RE = re.compile(r"var manifest = (\{.*?\});", re.DOTALL)
_PDF_IN_HTML_RE = re.compile(
    r"pdf2web/([A-Za-z0-9._\-]+PA[-_]?\d+[A-Za-z]?[^\"'\s]*\.pdf)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LeafletInfo:
    leaflet_id: str
    source_pdf: str
    page_count: int
    created_at: str | None
    source_url: str


def fetch_leaflet_manifest(leaflet_id: str | int) -> LeafletInfo | None:
    url = LEAFLET_URL.format(leaflet_id=leaflet_id)
    response = get_optional(url)
    if not response:
        return None
    return _manifest_from_html(response.text, leaflet_id=str(leaflet_id), source_url=url)


def discover_current_leaflet() -> LeafletInfo | None:
    """Return the current SuperValu special-offers leaflet from the hub or ID scan.

    The /offers hub redirects to the active flip-book (often a short teaser such as
    PA608B). Full multi-page leaflets remain at /offers/leaflet/{id}.
    """
    hub = fetch_leaflet_manifest_from_hub()
    if hub:
        logger.info(
            "SuperValu leaflet %s from hub (%d pages, %s)",
            hub.leaflet_id,
            hub.page_count,
            hub.source_pdf,
        )
        return hub

    candidates: list[LeafletInfo] = []
    misses_after_hit = 0
    for leaflet_id in range(LEAFLET_SCAN_HI, LEAFLET_SCAN_LO, -1):
        info = fetch_leaflet_manifest(str(leaflet_id))
        if info and info.page_count >= MIN_FULL_LEAFLET_PAGES:
            candidates.append(info)
            misses_after_hit = 0
        elif candidates:
            misses_after_hit += 1
            if misses_after_hit >= 8:
                break

    if not candidates:
        logger.warning(
            "No SuperValu leaflet found online (hub + leaflet IDs %d–%d)",
            LEAFLET_SCAN_HI,
            LEAFLET_SCAN_LO + 1,
        )
        return None

    best = max(candidates, key=_sort_key)
    logger.info(
        "SuperValu leaflet %s (%d pages, %s)",
        best.leaflet_id,
        best.page_count,
        best.source_pdf,
    )
    return best


def fetch_leaflet_manifest_from_hub() -> LeafletInfo | None:
    try:
        response = get(OFFERS_HUB_URL)
    except Exception as exc:
        logger.debug("SuperValu hub fetch failed: %s", exc)
        return None
    leaflet_id = _leaflet_id_from_url(response.url)
    return _manifest_from_html(
        response.text,
        leaflet_id=leaflet_id,
        source_url=response.url,
    )


def _manifest_from_html(
    html: str,
    *,
    leaflet_id: str | None,
    source_url: str,
) -> LeafletInfo | None:
    match = _MANIFEST_RE.search(html)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    pages = data.get("pages") or []
    source = data.get("source") or _pdf_from_html(html) or ""
    if not source or not pages:
        return None
    resolved_id = leaflet_id or _leaflet_id_from_pdf(source)
    return LeafletInfo(
        leaflet_id=resolved_id,
        source_pdf=source,
        page_count=len(pages),
        created_at=data.get("createdAt"),
        source_url=source_url,
    )


def _sort_key(info: LeafletInfo) -> datetime:
    if info.created_at:
        try:
            return datetime.fromisoformat(info.created_at.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.min


def _leaflet_id_from_pdf(filename: str) -> str:
    match = re.search(r"PA[- ]?(\d{3})([A-Z])?", filename, re.IGNORECASE)
    if match:
        suffix = (match.group(2) or "").lower()
        return f"{match.group(1)}{suffix}"
    match = re.search(r"PA(\d{3})", filename, re.IGNORECASE)
    return match.group(1) if match else "unknown"


def _leaflet_id_from_url(url: str) -> str | None:
    match = re.search(r"/offers/leaflet/(\d+[a-z]?)", url, re.IGNORECASE)
    return match.group(1).lower() if match else None


def _pdf_from_html(html: str) -> str | None:
    match = _PDF_IN_HTML_RE.search(html)
    return match.group(1) if match else None
