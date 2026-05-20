from __future__ import annotations

import logging

from fetchers._shared.models import Promotion

logger = logging.getLogger(__name__)

STORE_NAME = "Dunnes"


def fetch_promotions(
    *,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> list[Promotion]:
    logger.info("Skipping Dunnes: not implemented yet")
    return []
