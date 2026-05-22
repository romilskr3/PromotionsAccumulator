from __future__ import annotations

import logging

from fetchers._shared.dedupe import dedupe_by_product_week
from fetchers._shared.leaflet_cache import list_week_dirs
from fetchers._shared.models import Promotion
from fetchers.supervalu import download, parse

logger = logging.getLogger(__name__)

STORE_NAME = "SuperValu"


def fetch_promotions(
    *,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> list[Promotion]:
    if not skip_download:
        try:
            download.download_leaflet(refresh=refresh_leaflets)
        except Exception as exc:
            logger.error("SuperValu download error (will try cached PDFs): %s", exc)

    if not list_week_dirs("supervalu"):
        logger.warning(
            "No SuperValu leaflet cache under leaflets/supervalu/ — "
            "run with network access or copy a cached week folder"
        )
        return []

    promotions = dedupe_by_product_week(parse.parse_leaflets())
    if not promotions:
        logger.warning("No SuperValu produce promotions parsed from cached leaflet(s)")
    return promotions
