from __future__ import annotations

import logging

from fetchers._shared.models import Promotion

logger = logging.getLogger(__name__)

STORE_NAME = "SuperValu"


def fetch_promotions(
    *,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> list[Promotion]:
    logger.info("Skipping SuperValu: not implemented yet")
    return []
