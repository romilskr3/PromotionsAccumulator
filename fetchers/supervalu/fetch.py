from __future__ import annotations

import logging

from fetchers._shared.dedupe import dedupe_by_product_week
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
        download.download_leaflet(refresh=refresh_leaflets)

    promotions = dedupe_by_product_week(parse.parse_leaflets())
    if not promotions:
        logger.warning("No SuperValu produce promotions parsed")
    return promotions
