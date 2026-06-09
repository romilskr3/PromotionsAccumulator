from __future__ import annotations

import logging

from fetchers._shared.dedupe import dedupe_by_product_week
from fetchers._shared.models import Promotion
from fetchers.tesco import fresh_4, parse
from fetchers.tesco.constants import MIN_FRESH_4_ITEMS

logger = logging.getLogger(__name__)

STORE_NAME = "Tesco"


def fetch_promotions(
    *,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> list[Promotion]:
    if not skip_download:
        fresh_4.download_fresh_4(refresh=refresh_leaflets)

    promotions = parse.parse_cached()
    if not promotions:
        logger.warning(
            "No Tesco promotions in cache. Run: "
            "python scripts/update_promotions.py --store tesco --refresh-leaflets"
        )
    elif len(promotions) < MIN_FRESH_4_ITEMS:
        logger.warning(
            "Expected at least %d Tesco Fresh 4 items, got %d",
            MIN_FRESH_4_ITEMS,
            len(promotions),
        )

    return dedupe_by_product_week(promotions)
