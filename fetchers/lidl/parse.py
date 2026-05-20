from __future__ import annotations

import logging
from datetime import date
from typing import Any

from fetchers._shared.leaflet_cache import list_week_dirs, read_meta, read_publication
from fetchers._shared.models import Promotion
from fetchers._shared.produce import is_produce

logger = logging.getLogger(__name__)


def parse_leaflets() -> list[Promotion]:
    promotions: list[Promotion] = []
    for week_path in list_week_dirs("lidl"):
        try:
            meta = read_meta(week_path)
            promo_from = date.fromisoformat(meta["promo_from"])
            promo_until = date.fromisoformat(meta["promo_until"])
            publication = read_publication(week_path)
            for item in _extract_flyer_products(publication):
                category = item.get("category", "")
                if not _is_leaflet_produce(item["name"], category):
                    continue
                promotions.append(
                    Promotion(
                        supermarket="Lidl",
                        product=item["name"],
                        promotional_price=item["promotional_price"],
                        promotion_from=promo_from,
                        promotion_until=promo_until,
                        source="leaflet",
                        url=item.get("url"),
                        quantity=item.get("quantity") or item.get("unit"),
                    )
                )
        except Exception as exc:
            logger.error("Failed parsing %s: %s", week_path, exc)
    return promotions


def _extract_flyer_products(publication: Any) -> list[dict[str, Any]]:
    flyers = _collect_flyers(publication)
    offers: list[dict[str, Any]] = []
    seen: set[str] = set()

    for flyer in flyers:
        products = flyer.get("products") or {}
        if not isinstance(products, dict):
            continue
        for product in products.values():
            if not isinstance(product, dict):
                continue
            parsed = _normalize_flyer_product(product)
            if not parsed:
                continue
            key = f"{parsed['name']}|{parsed['promotional_price']}"
            if key in seen:
                continue
            seen.add(key)
            offers.append(parsed)

    return offers


def _collect_flyers(publication: Any) -> list[dict[str, Any]]:
    flyers: list[dict[str, Any]] = []
    if isinstance(publication, list):
        for entry in publication:
            data = entry.get("data") if isinstance(entry, dict) else None
            if isinstance(data, dict) and isinstance(data.get("flyer"), dict):
                flyers.append(data["flyer"])
    elif isinstance(publication, dict):
        if isinstance(publication.get("flyer"), dict):
            flyers.append(publication["flyer"])
    return flyers


def _normalize_flyer_product(product: dict[str, Any]) -> dict[str, Any] | None:
    name = product.get("title") or product.get("name")
    if not name or not isinstance(name, str):
        return None

    promo = product.get("price")
    if promo is None:
        return None
    promotional_price = str(promo).replace(",", ".")

    original = product.get("oldPrice") or product.get("strikePrice")
    original_price = str(original) if original is not None else None

    unit = product.get("description") or product.get("unit")
    url = product.get("url")
    if isinstance(url, str) and url.startswith("/"):
        url = f"https://www.lidl.ie{url}"

    category = product.get("wonCategoryPrimary") or product.get("categoryPrimary") or ""

    return {
        "name": name.strip(),
        "promotional_price": promotional_price,
        "original_price": original_price,
        "unit": unit if isinstance(unit, str) else None,
        "url": url if isinstance(url, str) else None,
        "category": category,
    }


def _is_leaflet_produce(name: str, category: str) -> bool:
    from fetchers._shared.produce import BLOCKLIST, PRODUCE_CATEGORY, is_produce

    if BLOCKLIST.search(name):
        return False
    if PRODUCE_CATEGORY.search(category):
        return True
    if "food and near food" in category.lower():
        return is_produce(name, category)
    return is_produce(name, category)
