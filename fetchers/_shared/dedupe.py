from __future__ import annotations

from fetchers._shared.models import Promotion


def dedupe_by_product_week(promotions: list[Promotion]) -> list[Promotion]:
    by_key: dict[str, Promotion] = {}
    for promo in promotions:
        key = (
            f"{promo.product.lower()}|{promo.promotion_from}|{promo.promotion_until}"
        )
        by_key[key] = promo
    return list(by_key.values())
