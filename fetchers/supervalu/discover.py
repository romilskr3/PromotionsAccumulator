from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from fetchers._shared.http import get
from fetchers.supervalu.constants import (
    LEAFLET_URL,
    MIN_FULL_LEAFLET_PAGES,
    OFFERS_HUB_URL,
)

logger = logging.getLogger(__name__)

_MANIFEST_RE = re.compile(r"var manifest = (\{.*?\});", re.DOTALL)


@dataclass(frozen=True)
class LeafletInfo:
    leaflet_id: str
    source_pdf: str
    page_count: int
    created_at: str | None
    source_url: str


def fetch_leaflet_manifest(leaflet_id: str | int) -> LeafletInfo | None:
    url = LEAFLET_URL.format(leaflet_id=leaflet_id)
    try:
        html = get(url).text
    except Exception:
        return None
    match = _MANIFEST_RE.search(html)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    source = data.get("source") or ""
    pages = data.get("pages") or []
    if not source or not pages:
        return None
    return LeafletInfo(
        leaflet_id=str(leaflet_id),
        source_pdf=source,
        page_count=len(pages),
        created_at=data.get("createdAt"),
        source_url=url,
    )


def discover_current_leaflet() -> LeafletInfo | None:
    """Return the newest full special-offers leaflet (not the short /offers teaser).

    Sources (in order of preference for candidates):
    - https://supervalu.ie/offers (hub embeds the current flip-book manifest)
    - https://supervalu.ie/offers/leaflet/{id} (numeric PA ids; older cycles stay online)
    """
    candidates: list[LeafletInfo] = []

    hub = fetch_leaflet_manifest_from_hub()
    if hub and hub.page_count >= MIN_FULL_LEAFLET_PAGES:
        candidates.append(hub)

    misses_after_hit = 0
    for leaflet_id in range(620, 500, -1):
        info = fetch_leaflet_manifest(leaflet_id)
        if info and info.page_count >= MIN_FULL_LEAFLET_PAGES:
            candidates.append(info)
            misses_after_hit = 0
        elif candidates:
            misses_after_hit += 1
            if misses_after_hit >= 12:
                break

    # Hub + per-id scan can return the same PA id twice.
    by_id = {c.leaflet_id: c for c in candidates}
    candidates = list(by_id.values())

    if not candidates:
        logger.warning(
            "No SuperValu full leaflet found online (hub + leaflet IDs 620–501)"
        )
        return None

    def sort_key(info: LeafletInfo) -> datetime:
        if info.created_at:
            try:
                return datetime.fromisoformat(info.created_at.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.min

    best = max(candidates, key=sort_key)
    logger.info(
        "SuperValu leaflet %s (%d pages, %s)",
        best.leaflet_id,
        best.page_count,
        best.source_pdf,
    )
    return best


def fetch_leaflet_manifest_from_hub() -> LeafletInfo | None:
    try:
        html = get(OFFERS_HUB_URL).text
    except Exception:
        return None
    match = _MANIFEST_RE.search(html)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    source = data.get("source") or ""
    pages = data.get("pages") or []
    if not source:
        return None
    leaflet_id = _leaflet_id_from_pdf(source)
    return LeafletInfo(
        leaflet_id=leaflet_id,
        source_pdf=source,
        page_count=len(pages),
        created_at=data.get("createdAt"),
        source_url=OFFERS_HUB_URL,
    )


def _leaflet_id_from_pdf(filename: str) -> str:
    match = re.search(r"PA[- ]?(\d{3})[A-Z]?", filename, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"PA(\d{3})", filename, re.IGNORECASE)
    return match.group(1) if match else "unknown"
