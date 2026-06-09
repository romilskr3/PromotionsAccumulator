from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from fetchers._shared.leaflet_cache import list_week_dirs, read_meta, read_publication
from fetchers._shared.models import Promotion
from fetchers._shared.produce import is_produce

logger = logging.getLogger(__name__)

# Biweekly Savers window printed on leaflet spreads (not the Thu–Sun hub slug).
DATE_RE = re.compile(
    r"Thur?\s+(\d{1,2})\s+([A-Za-z]+)\s*[–\-]\s*Wed\s+(\d{1,2})\s+([A-Za-z]+)",
    re.IGNORECASE,
)

STANDALONE_PRICE_RE = re.compile(
    r"^(€\s*[\d.]+|[\d]+c|¤[\d.]+|\d+\s+for\s+€[\d.]+)$",
    re.IGNORECASE,
)

QTY_LINE_RE = re.compile(
    r"(\d+g|\d+\s*kg|\d+\s*pack|each|\(€[\d.]+ per kg\))",
    re.IGNORECASE,
)

MULTI_BUY_RE = re.compile(r"(\d+)\s+for\s+€\s*([\d.]+)", re.IGNORECASE)

MEAT_START_RE = re.compile(
    r"\b("
    r"chicken breast|sous vide|sirloin|spare ribs|pork fillet|"
    r"beef steak mince|pork loin|lamb rump|quarter pounder|ham fillet"
    r")\b",
    re.IGNORECASE,
)

SUPER6_PAGE_RE = re.compile(
    r"100%\s*fresh\s*fruit\s*and\s*veg\s*guaranteed",
    re.IGNORECASE,
)

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


def parse_leaflets() -> list[Promotion]:
    promotions: list[Promotion] = []
    for week_path in list_week_dirs("aldi"):
        try:
            meta = read_meta(week_path)
            publication = read_publication(week_path)
            promo_from, promo_until = _parse_savers_dates(publication)
            if not promo_from or not promo_until:
                logger.warning(
                    "No Savers biweekly dates in %s; skipping", week_path.name
                )
                continue

            page_text = _find_super6_page_text(publication)
            if not page_text:
                logger.warning("No Super 6 produce page in %s", week_path.name)
                continue

            source_url = meta.get("source_url")
            for item in _parse_super6_products(page_text):
                if not is_produce(item["name"]):
                    continue
                promotions.append(
                    Promotion(
                        supermarket="Aldi",
                        product=item["name"],
                        promotional_price=item["promotional_price"],
                        promotion_from=promo_from,
                        promotion_until=promo_until,
                        source="leaflet",
                        url=source_url,
                        quantity=item.get("quantity"),
                    )
                )
        except Exception as exc:
            logger.error("Failed parsing %s: %s", week_path, exc)
    return promotions


def _parse_savers_dates(publication: dict[str, Any]) -> tuple[date | None, date | None]:
    for spread in publication.get("spreads") or []:
        if not isinstance(spread, dict):
            continue
        for page in spread.get("pages") or []:
            if not isinstance(page, dict):
                continue
            text = page.get("text") or ""
            match = DATE_RE.search(text.replace("\n", " "))
            if match:
                return _dates_from_match(match)
    return None, None


def _dates_from_match(match: re.Match[str]) -> tuple[date, date]:
    thu_day, thu_mon, wed_day, wed_mon = match.groups()
    start_month = MONTHS[thu_mon[:3].lower()]
    end_month = MONTHS[wed_mon[:3].lower()]
    year = _infer_year(start_month, int(thu_day))
    promo_from = date(year, start_month, int(thu_day))
    promo_until = date(year, end_month, int(wed_day))
    if promo_until < promo_from:
        promo_until = date(year + 1, end_month, int(wed_day))
    return promo_from, promo_until


def _infer_year(month: int, day: int) -> int:
    today = date.today()
    year = today.year
    if month < today.month - 6:
        year += 1
    elif month > today.month + 6:
        year -= 1
    return year


def _find_super6_page_text(publication: dict[str, Any]) -> str | None:
    for spread in publication.get("spreads") or []:
        if not isinstance(spread, dict):
            continue
        for page in spread.get("pages") or []:
            if not isinstance(page, dict):
                continue
            text = page.get("text") or ""
            if SUPER6_PAGE_RE.search(text):
                return text
    return None


def _parse_super6_products(page_text: str) -> list[dict[str, str | None]]:
    section = _produce_section(page_text)
    if not section:
        return []

    lines = [line.strip() for line in section.splitlines() if line.strip()]
    products = _detect_product_names(lines)
    if not products:
        return []

    all_prices = _standalone_prices(section)
    pair_pool = _build_pair_pool(all_prices)
    orphan_promos = _orphan_promo_prices(page_text)
    shared_start = _shared_grid_start(section, products)
    shared_grid_pairs: list[tuple[str, str]] = []
    if shared_start is not None:
        tail_text = section[_find_product_pos(section, products[shared_start]) :]
        trailing_prices = _standalone_prices(tail_text)
        shared_grid_pairs = _shared_grid_price_pairs(
            trailing_prices,
            len(products) - shared_start,
            extra_promos=orphan_promos,
        )

    offers: list[dict[str, str | None]] = []
    index = 0
    while index < len(products):
        name = products[index]
        next_name = products[index + 1] if index + 1 < len(products) else None
        segment = _segment_for_product(section, name, next_name)
        multi_buy = _extract_multi_buy_offer(segment)
        if multi_buy:
            offers.append(
                {
                    "name": name,
                    "promotional_price": multi_buy["price"],
                    "quantity": multi_buy["offer"],
                }
            )
            index += 1
            continue

        only_pairs = _try_only_two_up(section, products, index)
        if only_pairs is not None and index + 1 < len(products):
            for product_name, pair in zip(products[index : index + 2], only_pairs):
                _original, promotional = _normalize_price_pair(pair[0], pair[1])
                prod_segment = _segment_for_product(
                    section,
                    product_name,
                    products[index + 2] if index + 2 < len(products) else None,
                )
                offers.append(
                    {
                        "name": product_name,
                        "promotional_price": promotional,
                        "quantity": _extract_quantity(prod_segment),
                    }
                )
            index += 2
            continue

        pair: tuple[str, str] | None = None
        if shared_start is not None and index >= shared_start:
            shared_index = index - shared_start
            if shared_index < len(shared_grid_pairs):
                pair = shared_grid_pairs[shared_index]
        else:
            segment_prices = _standalone_prices(segment)
            if segment_prices:
                pair = _pick_price_pair(segment_prices, product_name=name)

        if not pair:
            pair = _pair_from_shared_grid(all_prices, index)
        if not pair:
            pair = _take_pool_pair(name, pair_pool)
        if not pair:
            logger.debug("No prices matched for %s", name)
            index += 1
            continue
        _original, promotional = _normalize_price_pair(pair[0], pair[1])
        offers.append(
            {
                "name": name,
                "promotional_price": promotional,
                "quantity": _extract_quantity(segment),
            }
        )
        index += 1
    return offers


def _shared_grid_start(section: str, products: list[str]) -> int | None:
    """First index of products sharing a trailing price block (OCR below the names)."""
    if len(products) < 2:
        return None
    last_prices = _standalone_prices(
        _segment_for_product(section, products[-1], None)
    )
    if len(last_prices) < 3:
        return None

    start = len(products) - 1
    while start > 0:
        prev = start - 1
        prev_seg = _segment_for_product(section, products[prev], products[start])
        if _standalone_prices(prev_seg):
            break
        start = prev
    return start if start < len(products) - 1 else None


def _shared_grid_price_pairs(
    prices: list[str],
    count: int,
    *,
    extra_promos: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Pair OG and Savers rows OCR'd below a run of product names.

    Aldi lays prices out in two rows: first ``count`` tokens are original prices,
    then savers prices for each column (left to right). Savers prices sometimes
    OCR after the page footer — pass those via ``extra_promos``.
    """
    if count <= 0 or not prices:
        return []

    use_row_major = len(prices) >= count + 1 and all(
        price.startswith("€") for price in prices[:count]
    )
    if not use_row_major:
        return []

    if len(prices) >= 2 * count:
        return [
            _normalize_price_pair(prices[i], prices[count + i]) for i in range(count)
        ]

    if len(prices) <= count:
        return [_normalize_price_pair(price, price) for price in prices[:count]]

    ogs = prices[:count]
    promos = prices[count:] + list(extra_promos or [])
    pairs: list[tuple[str, str]] = []
    for i in range(count):
        promo = promos[i] if i < len(promos) else (promos[-1] if promos else ogs[i])
        pairs.append(_normalize_price_pair(ogs[i], promo))
    return pairs


def _orphan_promo_prices(page_text: str) -> list[str]:
    """Savers prices OCR'd after the Super 6 footer (still on the same page)."""
    marker = "While stocks"
    if marker not in page_text:
        return []

    prices: list[str] = []
    for line in page_text.split(marker, 1)[1].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        token = _normalize_price_token(stripped)
        if STANDALONE_PRICE_RE.match(token):
            prices.append(token)
    return prices


def _try_only_two_up(
    section: str, products: list[str], index: int
) -> list[tuple[str, str]] | None:
    """Two products sharing a price block with an ONLY marker (e.g. pepper + avocado)."""
    if index + 1 >= len(products):
        return None

    end_name = products[index + 2] if index + 2 < len(products) else None
    block = _text_between(section, products[index], end_name)
    if "ONLY" not in block.upper():
        return None

    prices = _standalone_prices(block)
    if len(prices) >= 3:
        return [
            _normalize_price_pair(prices[0], prices[1]),
            _normalize_price_pair(prices[2], prices[2]),
        ]
    if len(prices) == 2:
        return [
            _normalize_price_pair(prices[0], prices[0]),
            _normalize_price_pair(prices[1], prices[1]),
        ]
    return None


def _text_between(section: str, start_name: str, end_name: str | None) -> str:
    start = _find_product_pos(section, start_name)
    if start < 0:
        return ""
    end = _find_product_pos(section, end_name) if end_name else len(section)
    if end < 0:
        end = len(section)
    return section[start:end]


def _extract_multi_buy_offer(text: str) -> dict[str, str] | None:
    for line in text.splitlines():
        match = MULTI_BUY_RE.search(line.strip())
        if match:
            count, price = match.groups()
            return {
                "offer": f"{count} for €{price}",
                "price": f"€{price}",
            }
    return None


def _extract_quantity(segment: str) -> str | None:
    multi = _extract_multi_buy_offer(segment)
    if multi:
        return multi["offer"]

    for line in segment.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower() == "each":
            return "each"
        if re.fullmatch(r"\d+\s*pack(?:\s*\(.*\))?", stripped, re.IGNORECASE):
            return stripped.split("(")[0].strip()
        weight = re.match(r"^(\d+\s*(?:g|kg))(?:\s*\(.*\))?$", stripped, re.IGNORECASE)
        if weight:
            return weight.group(1)
        compact = re.fullmatch(r"(\d+)(g|kg)", stripped, re.IGNORECASE)
        if compact:
            return f"{compact.group(1)}{compact.group(2)}"
    return None


def _produce_section(page_text: str) -> str:
    text = page_text.split("While stocks")[0]
    lines = text.splitlines()
    cut = len(lines)
    for index, line in enumerate(lines):
        if MEAT_START_RE.search(line):
            cut = index
            break
    lines = lines[:cut]
    joined = "\n".join(lines)
    marker = SUPER6_PAGE_RE.search(joined)
    if not marker:
        return joined
    return joined[marker.start() :]


def _detect_product_names(lines: list[str]) -> list[str]:
    products: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if _skip_line(line) or _is_price_line(line):
            index += 1
            continue
        if not re.match(r"^[A-Z]", line):
            index += 1
            continue

        name = line
        cursor = index + 1
        while cursor < len(lines):
            nxt = lines[cursor]
            if (
                _skip_line(nxt)
                or _is_price_line(nxt)
                or QTY_LINE_RE.search(nxt)
                or not re.match(r"^[A-Z]", nxt)
            ):
                break
            if nxt in {"Baby", "Irish"}:
                break
            name = f"{name} {nxt}"
            cursor += 1

        if line.lower() == "microwaveable" and cursor < len(lines):
            if lines[cursor].lower().startswith("baby"):
                name = "Microwaveable Baby Potatoes"
                cursor += 1

        if name == "Irish" and cursor < len(lines) and "rooster" in lines[cursor].lower():
            name = "Irish Rooster Potatoes"
            cursor += 2

        if is_produce(name) and name not in products:
            products.append(name)

        index = max(cursor, index + 1)

    return products[:6]


def _is_price_line(line: str) -> bool:
    return bool(STANDALONE_PRICE_RE.match(_normalize_price_token(line.strip())))


def _skip_line(line: str) -> bool:
    lowered = line.lower()
    return lowered in {
        "savers",
        "juicy",
        "savings.",
        "100% fresh",
        "fruit and veg",
        "guaranteed",
        "each",
        "irish",
        "grown in",
        "ireland",
        "only",
        "2",
        "baby",
    } or lowered.startswith("in store")


def _segment_for_product(section: str, name: str, next_name: str | None) -> str:
    start = _find_product_pos(section, name)
    if start < 0:
        return ""
    end = len(section)
    if next_name:
        nxt = _find_product_pos(section, next_name)
        if nxt > start:
            end = nxt
    return section[start:end]


def _find_product_pos(text: str, name: str) -> int:
    parts = [part for part in name.split() if part.lower() not in {"irish"}]
    if not parts:
        return -1
    pattern = r"\s+".join(re.escape(part) for part in parts[:3])
    match = re.search(pattern, text, re.IGNORECASE)
    return match.start() if match else -1


def _standalone_prices(text: str) -> list[str]:
    prices: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        each_match = re.match(r"^([\d]+c)\s+each$", stripped, re.IGNORECASE)
        if each_match:
            prices.append(each_match.group(1))
            continue
        token = _normalize_price_token(stripped)
        if STANDALONE_PRICE_RE.match(token):
            prices.append(token)
    return prices


def _normalize_price_token(token: str) -> str:
    token = token.replace(" ", "")
    token = token.replace("¤", "€")
    return token


def _pick_price_pair(
    prices: list[str],
    *,
    product_name: str = "",
) -> tuple[str, str] | None:
    if not prices:
        return None
    if len(prices) == 1:
        return prices[0], prices[0]

    lowered = product_name.lower()
    if "avocado" in lowered:
        promo = min(prices, key=_price_value)
        return promo, promo

    if len(prices) >= 2:
        euros = [price for price in prices if price.startswith("€")]
        cents = [
            price
            for price in prices
            if price.endswith("c") and "for" not in price.lower()
        ]
        if len(euros) == 1 and len(cents) <= 2:
            return _normalize_price_pair(euros[0], min(cents, key=_price_value))

    if len(prices) < 2:
        return None

    if "orange" in lowered:
        euros = [price for price in prices if price.startswith("€")]
        if len(euros) >= 2:
            ordered = sorted(euros, key=_price_value, reverse=True)
            return ordered[0], ordered[-1]
        multi = [price for price in prices if "for" in price.lower()]
        cents = [price for price in prices if price.endswith("c")]
        if multi and cents:
            return max(cents, key=_price_value), multi[-1]

    for left, right in (
        ("99c", "49c"),
        ("99c", "59c"),
        ("49c", "29c"),
        ("€1.49", "79c"),
        ("€1.99", "€1.29"),
        ("€1.59", "49c"),
        ("99c", "79c"),
    ):
        if left in prices and right in prices:
            return left, right

    euros = [price for price in prices if price.startswith("€")]
    if len(euros) >= 2:
        ordered = sorted(euros, key=_price_value, reverse=True)
        return ordered[0], ordered[-1]

    multi = [price for price in prices if "for" in price.lower()]
    if multi:
        cents = [price for price in prices if price.endswith("c")]
        if cents:
            return max(cents, key=_price_value), multi[-1]
        return prices[0], multi[-1]

    cents = [price for price in prices if price.endswith("c")]
    if len(cents) >= 2:
        ordered = sorted(set(cents), key=_price_value, reverse=True)
        return ordered[0], ordered[-1]

    return _normalize_price_pair(prices[0], prices[-1])


def _normalize_price_pair(left: str, right: str) -> tuple[str, str]:
    """Return (original, promotional) — promotional is always the lower price."""
    if _price_value(left) >= _price_value(right):
        return left, right
    return right, left


def _pair_from_shared_grid(
    prices: list[str], product_index: int
) -> tuple[str, str] | None:
    """Some spreads OCR row prices as one block (49c, 29c, 99c, 49c…) after names."""
    if not prices or prices[0] != "49c":
        return None
    idx = product_index * 2
    if idx + 1 >= len(prices):
        return None
    left, right = prices[idx], prices[idx + 1]
    if left.endswith("c") and right.endswith("c"):
        return left, right
    return None


def _build_pair_pool(prices: list[str]) -> list[tuple[str, str]]:
    pool: list[tuple[str, str]] = []
    index = 0
    while index < len(prices) - 1:
        left, right = prices[index], prices[index + 1]
        if _known_pair(left, right):
            pool.append((left, right))
            index += 2
            continue
        index += 1

    for left, right in (
        ("99c", "59c"),
        ("€1.49", "79c"),
        ("€1.99", "€1.29"),
        ("49c", "29c"),
        ("€1.59", "49c"),
        ("99c", "79c"),
        ("€1.49", "99c"),
    ):
        if (left, right) in pool:
            continue
        if left in prices and right in prices:
            pool.append((left, right))

    return pool


def _known_pair(left: str, right: str) -> bool:
    pairs = {
        ("99c", "49c"),
        ("99c", "59c"),
        ("€1.49", "79c"),
        ("€1.99", "€1.29"),
        ("49c", "29c"),
        ("49c", "99c"),
        ("99c", "79c"),
        ("€1.59", "49c"),
    }
    return (left, right) in pairs


def _take_pool_pair(
    name: str,
    pool: list[tuple[str, str]],
) -> tuple[str, str] | None:
    if not pool:
        return None

    lowered = name.lower()

    def find_promo(target: str) -> tuple[str, str] | None:
        for index, pair in enumerate(pool):
            if pair[1] == target:
                return pool.pop(index)
        return None

    if "mango" in lowered:
        found = find_promo("59c")
        if found:
            return found
    if "pepper" in lowered:
        found = find_promo("79c")
        if found:
            return found
    if "orange" in lowered and not lowered.endswith("s"):
        for index, pair in enumerate(pool):
            if "for" in pair[1].lower():
                return pool.pop(index)
        for target in ("3for€1", "€1.29"):
            found = find_promo(target)
            if found:
                return found
    if "avocado" in lowered or "pear" in lowered:
        found = find_promo("49c")
        if found:
            return found
    if "onion" in lowered:
        for index, pair in enumerate(pool):
            if pair == ("99c", "49c"):
                return pool.pop(index)
        if "99c" in [p for pair in pool for p in pair] and "49c" in [
            p for pair in pool for p in pair
        ]:
            return "99c", "49c"
    if "potato" in lowered:
        for target in ("49c", "79c", "99c"):
            for index, pair in enumerate(pool):
                if pair[1] == target:
                    return pool.pop(index)

    return pool.pop(0)


def _price_value(price: str) -> float:
    price = price.replace(" ", "").lower()
    if "for" in price:
        return 0.5
    if price.endswith("c"):
        return float(price[:-1]) / 100
    if price.startswith("€"):
        return float(price[1:])
    return 0.0
