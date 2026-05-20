from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fetchers._shared.http import get
from fetchers._shared.leaflet_cache import is_stale, week_dir, write_meta
from fetchers._shared.models import WeekWindow
from fetchers.aldi.hub import discover_weeks

logger = logging.getLogger(__name__)


def download_leaflets(*, refresh: bool = False) -> list[Path]:
    weeks = discover_weeks()
    if not weeks:
        logger.warning("No Aldi leaflet weeks found on hub page")
        return []

    saved: list[Path] = []
    for week in weeks:
        path = week_dir("aldi", week.promo_from, week.promo_until)
        if not refresh and not is_stale(path):
            logger.info("Using cached Aldi leaflet %s", path.name)
            saved.append(path)
            continue

        slug = _slug_from_url(week.source_url)
        logger.info("Downloading Aldi leaflet %s → %s", week.label, path.name)
        spreads = _fetch_spreads(slug)
        if not spreads:
            logger.error("No leaflet JSON captured for %s", week.source_url)
            continue

        payload = {"slug": slug, "spreads": spreads}
        (path / "publication.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        write_meta(
            path,
            store="Aldi",
            source_url=week.source_url,
            promo_from=week.promo_from,
            promo_until=week.promo_until,
            label=week.label,
            extra={"slug": slug},
        )
        saved.append(path)

    return saved


def _slug_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def _fetch_spreads(slug: str) -> list[Any] | None:
    try:
        data = get(f"https://leaflet.aldi.ie/{slug}/spreads.json").json()
    except Exception as exc:
        logger.warning("Failed to fetch spreads.json for %s: %s", slug, exc)
        return None
    return data if isinstance(data, list) else None
