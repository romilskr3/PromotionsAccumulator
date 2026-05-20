from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from typing import Any

import fitz

from fetchers._shared.leaflet_cache import list_week_dirs, read_meta, read_publication
from fetchers._shared.models import Promotion
from fetchers._shared.produce import is_produce
from fetchers._shared.product_display import clean_product_display_name
from fetchers.supervalu.constants import STORE_NAME

logger = logging.getLogger(__name__)

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

DATE_RANGE_RE = re.compile(
    r"Offers valid from Thursday\s+(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"([A-Za-z]+)\s*-\s*Wednesday\s+(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"([A-Za-z]+)\s+(\d{4})",
    re.IGNORECASE,
)

UNTIL_ONLY_RE = re.compile(
    r"Offers Valid until Wednesday\s+(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"([A-Za-z]+)\s+(\d{4})",
    re.IGNORECASE,
)

FRESH_PAGE_MARKERS = (
    "save up to 50% on fresh favourites",
    "super fresh5",
    "super fresh 5",
    "irish strawberries",
    "fruit & berries mix",
)

PROCESSED_SKIP = re.compile(
    r"\b(ketchup|mayonnaise|sauce|pasta|pesto|chopped|peeled|plum tomatoes|"
    r"feasts|classics|stir in|finely chopped|pizza|meal|ice cream|yogurt|"
    r"kefir|coleslaw|burger|wedges|dippers|splits|lollies)\b",
    re.IGNORECASE,
)

SAVE_HEADER_RE = re.compile(r"^Save\s+(\d+)%\s*$", re.IGNORECASE)
NOW_HEADER_RE = re.compile(r"^NOW\s*$", re.IGNORECASE)
PRICE_LINE_RE = re.compile(r"^([\d.]+c|€[\d.]+)\s*$", re.IGNORECASE)
PRODUCT_START_RE = re.compile(r"^SuperValu\b", re.IGNORECASE)
STRAWBERRY_BLOCK_RE = re.compile(
    r"SuperValu Signature Tastes\s+Super Sweet Irish Strawberries",
    re.IGNORECASE,
)
STRAWBERRY_PRICE_RE = re.compile(r"€([\d.]+)\s+Each", re.IGNORECASE)
PRODUCT_LINE_STOP_RE = re.compile(
    r"^(Caramico|Clean Cut|Prices correct|Fresh Picks|\d+$|2 FOR|MIX & MATCH|"
    r"TASTE THE|SUPER\s*$|FRESH5|REAL REWARDS)",
    re.IGNORECASE,
)

QTY_IN_NAME_RE = re.compile(
    r"\b(\d+pce|\d+\s*pack|\d+g|\d+\s*kg|each)\b",
    re.IGNORECASE,
)


def parse_leaflets() -> list[Promotion]:
    promotions: list[Promotion] = []
    for week_path in list_week_dirs("supervalu"):
        try:
            meta = read_meta(week_path)
            publication = read_publication(week_path)
            pdf_path = week_path / "leaflet.pdf"
            if not pdf_path.exists():
                logger.warning("Missing PDF in %s", week_path.name)
                continue

            promo_from = date.fromisoformat(meta["promo_from"])
            promo_until = date.fromisoformat(meta["promo_until"])
            source_url = meta.get("source_url", "")

            doc = fitz.open(pdf_path)
            for item in parse_promotions_from_pdf(
                doc,
                promo_from=promo_from,
                promo_until=promo_until,
            ):
                product = item["product"]
                if not is_produce(product) or PROCESSED_SKIP.search(product):
                    continue
                promotions.append(
                    Promotion(
                        supermarket=STORE_NAME,
                        product=product,
                        promotional_price=item["price"],
                        promotion_from=item.get("promotion_from", promo_from),
                        promotion_until=item.get("promotion_until", promo_until),
                        source="leaflet",
                        url=source_url,
                        quantity=item.get("quantity"),
                    )
                )
            doc.close()
            week_count = sum(
                1
                for p in promotions
                if p.supermarket == STORE_NAME
                and p.promotion_from == promo_from
            )
            logger.info(
                "SuperValu %s: %d produce offer(s) from leaflet %s",
                week_path.name,
                week_count,
                publication.get("leaflet_id", "?"),
            )
        except Exception as exc:
            logger.error("Failed parsing SuperValu %s: %s", week_path, exc)
    return promotions


def parse_dates_from_pdf(doc: fitz.Document) -> tuple[date | None, date | None]:
    combined = "\n".join(page.get_text() for page in doc)
    match = DATE_RANGE_RE.search(combined.replace("\n", " "))
    if match:
        return _dates_from_range_match(match)
    match = UNTIL_ONLY_RE.search(combined.replace("\n", " "))
    if match:
        return _dates_from_until_only(match)
    return None, None


def parse_promotions_from_pdf(
    doc: fitz.Document,
    *,
    promo_from: date,
    promo_until: date,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for page in doc:
        text = page.get_text()
        if not _is_fresh_produce_page(text):
            continue
        week_from, week_until = _page_week_window(text, promo_from, promo_until)
        for raw in _extract_products(text):
            raw_name = raw.get("raw_name") or _clean_product_name(raw["product"])
            product = clean_product_display_name(raw_name)
            if not product or product.lower() in seen:
                continue
            seen.add(product.lower())
            items.append(
                {
                    "product": product,
                    "price": raw["price"],
                    "quantity": raw.get("quantity") or _quantity_from_name(raw_name),
                    "promotion_from": week_from,
                    "promotion_until": week_until,
                }
            )
    return items


def _is_fresh_produce_page(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in FRESH_PAGE_MARKERS)


def _page_week_window(
    text: str, default_from: date, default_until: date
) -> tuple[date, date]:
    match = re.search(
        r"1 Week Only\s+(\d{1,2})(?:st|nd|rd|th)?\s*-\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return default_from, default_until
    start_day, end_day, month_name = match.groups()
    month = MONTHS.get(month_name[:3].lower())
    if not month:
        return default_from, default_until
    year = default_from.year
    try:
        return (
            date(year, month, int(start_day)),
            date(year, month, int(end_day)),
        )
    except ValueError:
        return default_from, default_until


def _extract_products(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    lowered = text.lower()
    if (
        "save up to 50% on fresh favourites" in lowered
        and "fresh picks" in lowered
    ):
        start = lowered.index("save up to 50% on fresh favourites")
        items.extend(_parse_super_fresh_block(text[start:]))
    if "irish strawberries" in lowered and STRAWBERRY_BLOCK_RE.search(text):
        items.extend(_parse_strawberry_block(text))
    return items


def _parse_super_fresh_block(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    items: list[dict[str, str]] = []
    pending_price: str | None = None
    product_lines: list[str] = []
    i = 0

    def flush_product(*, price: str | None) -> None:
        nonlocal product_lines, pending_price
        if not product_lines:
            return
        use_price = price or pending_price
        if use_price:
            items.append({"product": " ".join(product_lines), "price": use_price})
            pending_price = None
        product_lines = []

    while i < len(lines):
        line = lines[i]
        if NOW_HEADER_RE.match(line):
            price = _price_after_now(lines, i)
            if product_lines and price:
                flush_product(price=price)
            elif price:
                pending_price = price
            i += 1
            continue
        if SAVE_HEADER_RE.match(line):
            flush_product(price=_find_inline_now_price(lines, i))
            i += 1
            product_lines = []
            continue
        if PRODUCT_START_RE.match(line):
            flush_product(price=_find_inline_now_price(lines, i))
            product_lines = [line]
        elif product_lines and not line.lower().startswith("was "):
            if line.lower().startswith("save ") or PRODUCT_LINE_STOP_RE.match(line):
                flush_product(price=None)
                product_lines = []
                if line.lower().startswith("save "):
                    continue
                i += 1
                continue
            product_lines.append(line)
        i += 1
    flush_product(price=None)
    items.extend(_backfill_orphan_prices(lines, items))
    return items


def _backfill_orphan_prices(
    lines: list[str], items: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Pair trailing NOW prices with products that were parsed without a price."""
    extra: list[dict[str, str]] = []
    priced_names = {item["product"].lower() for item in items}
    orphan_prices: list[str] = []
    orphan_products: list[str] = []

    i = 0
    while i < len(lines):
        if NOW_HEADER_RE.match(lines[i]):
            price = _price_after_now(lines, i)
            if price:
                orphan_prices.append(price)
        if PRODUCT_START_RE.match(lines[i]) and "orange" in lines[i].lower():
            name = lines[i]
            j = i + 1
            while j < len(lines) and not PRODUCT_START_RE.match(lines[j]):
                if PRODUCT_LINE_STOP_RE.match(lines[j]) or SAVE_HEADER_RE.match(lines[j]):
                    break
                if not lines[j].lower().startswith("was "):
                    name += " " + lines[j]
                j += 1
            raw_name = _clean_product_name(name)
            clean = clean_product_display_name(raw_name)
            if clean.lower() not in priced_names and "orange" in clean.lower():
                orphan_products.append({"product": clean, "raw_name": raw_name})
        i += 1

    for entry, price in zip(orphan_products, orphan_prices[-len(orphan_products) :]):
        extra.append(
            {
                "product": entry["product"],
                "raw_name": entry["raw_name"],
                "price": price,
            }
        )
    return extra


def _price_after_now(lines: list[str], now_index: int) -> str | None:
    for j in range(now_index + 1, min(now_index + 4, len(lines))):
        if PRICE_LINE_RE.match(lines[j]):
            return lines[j]
        if SAVE_HEADER_RE.match(lines[j]) or PRODUCT_START_RE.match(lines[j]):
            break
    return None


def _find_inline_now_price(lines: list[str], product_index: int) -> str | None:
    for j in range(product_index, min(product_index + 6, len(lines))):
        if NOW_HEADER_RE.match(lines[j]):
            return _price_after_now(lines, j)
    return None


def _parse_strawberry_block(text: str) -> list[dict[str, str]]:
    if not STRAWBERRY_BLOCK_RE.search(text):
        return []
    price_match = STRAWBERRY_PRICE_RE.search(text)
    if not price_match:
        return []
    raw_name = "SuperValu Signature Tastes Super Sweet Irish Strawberries 325g"
    return [
        {
            "product": clean_product_display_name(raw_name),
            "raw_name": raw_name,
            "price": f"€{price_match.group(1)}",
            "quantity": "325 g",
        }
    ]


def _clean_product_name(name: str) -> str:
    """Strip PDF layout noise before display-name cleaning."""
    text = re.sub(r"\s+", " ", name).strip()
    text = re.sub(r"\s+was\s+.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+NOW\s+.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Save\s+\d+%.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\(Details In-store.*$", "", text, flags=re.IGNORECASE)
    return text.strip()


def _quantity_from_name(product: str) -> str | None:
    """Infer pack size from leaflet wording (raw product line, before display cleaning)."""
    lowered = product.lower()

    if re.search(r"\bloose\b", lowered):
        return "Each"

    pce_match = re.search(r"(\d+)\s*pce", lowered)
    if pce_match:
        count = pce_match.group(1)
        if re.search(r"\btwinpack\b", lowered):
            return f"{count} pce"
        return f"{count} pack"

    kg_match = re.search(r"(\d+)\s*kg", lowered)
    if kg_match:
        return f"{kg_match.group(1)} kg"

    g_match = re.search(r"(\d+)\s*g", lowered)
    if g_match:
        return f"{g_match.group(1)} g"

    if re.search(r"\beach\b", lowered):
        return "Each"

    return None


def _dates_from_range_match(match: re.Match[str]) -> tuple[date, date]:
    thu_day, thu_mon, wed_day, wed_mon, year = match.groups()
    start_month = MONTHS[thu_mon[:3].lower()]
    end_month = MONTHS[wed_mon[:3].lower()]
    promo_from = date(int(year), start_month, int(thu_day))
    promo_until = date(int(year), end_month, int(wed_day))
    if promo_until < promo_from:
        promo_until = date(int(year) + 1, end_month, int(wed_day))
    return promo_from, promo_until


def _dates_from_until_only(match: re.Match[str]) -> tuple[date, date]:
    wed_day, wed_mon, year = match.groups()
    end_month = MONTHS[wed_mon[:3].lower()]
    promo_until = date(int(year), end_month, int(wed_day))
    promo_from = promo_until
    return promo_from, promo_until
