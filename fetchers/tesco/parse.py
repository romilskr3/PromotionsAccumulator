from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from fetchers._shared.leaflet_cache import list_week_dirs, read_meta, read_publication
from fetchers._shared.models import Promotion
from fetchers.tesco.constants import MIN_FRESH_4_ITEMS, FRESH_4_URL

logger = logging.getLogger(__name__)

ITEM_RE = re.compile(
    r"(?P<name>Tesco[^\n]+?)\s*"
    r"(?:\n\n\d+\.\d+ \(\d+\)\s*)?"
    r"Write a review\s+More like this\s+"
    r"(?P<price>\d+c|€[\d.]+)\s+(?:Half Price\s+)?Clubcard Price\s+"
    r".*?"
    r"Offer valid for delivery from (?P<from>\d{2}/\d{2}/\d{4}) "
    r"until (?P<until>\d{2}/\d{2}/\d{4})",
    re.IGNORECASE | re.DOTALL,
)

LEGACY_ITEM_RE = re.compile(
    r"(?P<name>[A-Z][^\n]+?)\s+Write a review\s+More like this\s+"
    r"(?:Half Price\s+)?Clubcard Price\s+(?P<price>\d+c|€[\d.]+)\s+"
    r"(?:Half Price\s+)?Clubcard Price\s+.*?"
    r"Offer valid for delivery from (?P<from>\d{2}/\d{2}/\d{4}) "
    r"until (?P<until>\d{2}/\d{2}/\d{4})",
    re.IGNORECASE | re.DOTALL,
)

LEGACY_SIMPLE_ITEM_RE = re.compile(
    r"(?P<name>[A-Z][^\n]+?)\s+Write a review\s+More like this\s+"
    r"Clubcard Price\s+(?P<price>\d+c|€[\d.]+)\s+Clubcard Price\s+.*?"
    r"Offer valid for delivery from (?P<from>\d{2}/\d{2}/\d{4}) "
    r"until (?P<until>\d{2}/\d{2}/\d{4})",
    re.IGNORECASE | re.DOTALL,
)

QTY_SUFFIX_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\s+(\d+)\s*pack\s*$", re.IGNORECASE), "pack"),
    (re.compile(r"\s+(\d+)\s*(g|kg)\s*$", re.IGNORECASE), "weight_spaced"),
    (re.compile(r"\s+(\d+)(g|kg)\s*$", re.IGNORECASE), "weight_compact"),
    (re.compile(r"\s+each\s*$", re.IGNORECASE), "each"),
)


def parse_cached() -> list[Promotion]:
    promotions: list[Promotion] = []
    for week_path in list_week_dirs("tesco"):
        try:
            meta = read_meta(week_path)
            default_from = date.fromisoformat(meta["promo_from"])
            default_until = date.fromisoformat(meta["promo_until"])
            source_url = meta.get("source_url", FRESH_4_URL)
            publication = read_publication(week_path)
            for item in _products_from_publication(publication):
                product, quantity = _normalize_product(item["name"])
                quantity = quantity or item.get("quantity")
                promo_from = (
                    _parse_tesco_date(item["promotion_from"])
                    if item.get("promotion_from")
                    else default_from
                )
                promo_until = (
                    _parse_tesco_date(item["promotion_until"])
                    if item.get("promotion_until")
                    else default_until
                )
                promotions.append(
                    Promotion(
                        supermarket="Tesco",
                        product=product,
                        promotional_price=item["price"],
                        promotion_from=promo_from,
                        promotion_until=promo_until,
                        source="fresh_4",
                        url=source_url,
                        quantity=quantity,
                    )
                )
        except Exception as exc:
            logger.error("Failed parsing Tesco cache %s: %s", week_path, exc)
    return promotions


def parse_page_text(page_text: str) -> tuple[date | None, date | None, list[dict[str, str]]]:
    products = _parse_products_from_text(page_text)
    if not products:
        return None, None, []

    from_dates = [_parse_tesco_date(p["promotion_from"]) for p in products]
    until_dates = [_parse_tesco_date(p["promotion_until"]) for p in products]
    return min(from_dates), max(until_dates), products


def _products_from_publication(publication: Any) -> list[dict[str, str]]:
    if isinstance(publication, dict):
        products = publication.get("products")
        if isinstance(products, list) and products:
            return products
        page_text = publication.get("page_text")
        if isinstance(page_text, str):
            _, _, parsed = parse_page_text(page_text)
            return parsed
    return []


def _parse_products_from_text(page_text: str) -> list[dict[str, str]]:
    products: list[dict[str, str]] = []
    for pattern in (ITEM_RE, LEGACY_ITEM_RE, LEGACY_SIMPLE_ITEM_RE):
        for match in pattern.finditer(page_text):
            raw_name = match.group("name")
            name, quantity = _normalize_product(raw_name)
            if not name or any(existing["name"] == name for existing in products):
                continue
            products.append(
                {
                    "name": name,
                    "price": match.group("price").lower(),
                    "quantity": quantity,
                    "promotion_from": match.group("from"),
                    "promotion_until": match.group("until"),
                }
            )
        if products:
            break

    if len(products) < MIN_FRESH_4_ITEMS:
        logger.warning(
            "Expected at least %d Fresh 4 items, parsed %d",
            MIN_FRESH_4_ITEMS,
            len(products),
        )
    return products


def _clean_name(name: str) -> str:
    return " ".join(name.split())


def _normalize_product(raw_name: str) -> tuple[str, str | None]:
    """Strip Tesco own-brand prefix and move pack size out of the product title."""
    name = _clean_name(raw_name)
    quantity = _extract_quantity_suffix(name)
    if quantity:
        for pattern, _ in QTY_SUFFIX_PATTERNS:
            match = pattern.search(name)
            if match:
                name = name[: match.start()].strip()
                break

    name = re.sub(r"^Tesco\s+", "", name, flags=re.IGNORECASE).strip()
    return _clean_name(name), quantity


def _extract_quantity_suffix(name: str) -> str | None:
    for pattern, kind in QTY_SUFFIX_PATTERNS:
        match = pattern.search(name)
        if not match:
            continue
        if kind == "pack":
            return f"{match.group(1)} pack"
        if kind == "each":
            return "each"
        return f"{match.group(1)}{match.group(2).lower()}"
    return None


def _parse_tesco_date(value: str) -> date:
    day, month, year = value.split("/")
    return date(int(year), int(month), int(day))
