from __future__ import annotations

import logging

from fetchers._shared.dedupe import dedupe_by_product_week
from fetchers._shared.models import Promotion
from fetchers.aldi import download, parse

logger = logging.getLogger(__name__)

STORE_NAME = "Aldi"


def fetch_promotions(
    *,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> list[Promotion]:
    if not skip_download:
        download.download_leaflets(refresh=refresh_leaflets)

    return dedupe_by_product_week(parse.parse_leaflets())
