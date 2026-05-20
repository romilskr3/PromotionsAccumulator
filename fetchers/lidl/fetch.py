from __future__ import annotations

import logging
from collections import defaultdict

from fetchers._shared.models import Promotion
from fetchers.lidl import super_savers

logger = logging.getLogger(__name__)

STORE_NAME = "Lidl"
SUPER_SAVERS_PER_WEEK = 6


def fetch_promotions(
    *,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> list[Promotion]:
    del refresh_leaflets  # leaflet not used for Lidl promotions

    promotions = super_savers.fetch_super_savers(skip_download=skip_download)
    _log_week_counts(promotions)
    return promotions


def _log_week_counts(promotions: list[Promotion]) -> None:
    by_week: dict[tuple, list[str]] = defaultdict(list)
    for promo in promotions:
        key = (promo.promotion_from, promo.promotion_until)
        by_week[key].append(promo.product)

    for (start, end), products in sorted(by_week.items()):
        count = len(products)
        if count != SUPER_SAVERS_PER_WEEK:
            logger.warning(
                "Expected %d Super Savers for %s–%s, got %d: %s",
                SUPER_SAVERS_PER_WEEK,
                start,
                end,
                count,
                ", ".join(products),
            )
        else:
            logger.info(
                "Super Savers %s–%s: %d products",
                start,
                end,
                count,
            )
