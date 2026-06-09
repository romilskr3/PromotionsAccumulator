from __future__ import annotations

import html
import json
import logging
import re
from datetime import date, datetime
from fetchers._shared.http import SESSION
from fetchers._shared.leaflet_cache import LEAFLETS_ROOT
from fetchers._shared.models import DUBLIN, Promotion, WeekWindow
from fetchers._shared.produce import is_produce
from fetchers.lidl.hub import discover_weeks

logger = logging.getLogger(__name__)

SUPER_SAVERS_PAGE = "https://www.lidl.ie/c/super-savers/a10028883"
GRID_DATA_RE = re.compile(r'data-grid-data="([^"]+)"')
RIBBON_RANGE_RE = re.compile(
    r"(\d{1,2})\.(\d{1,2})\s*-\s*(\d{1,2})\.(\d{1,2})"
)
RIBBON_FROM_RE = re.compile(r"From\s+(\d{1,2})\.(\d{1,2})", re.IGNORECASE)


def fetch_super_savers(
    *,
    skip_download: bool = False,
    weeks: list[WeekWindow] | None = None,
) -> list[Promotion]:
    weeks = weeks or discover_weeks()
    week_by_range = {(w.promo_from, w.promo_until): w for w in weeks}
    this_week = weeks[0] if weeks else None
    next_week = weeks[1] if len(weeks) > 1 else None

    grid_items = _parse_super_savers_page()
    if not grid_items:
        logger.warning("No Super Savers products parsed from campaign page")
        return []

    if not skip_download:
        _save_snapshot(grid_items)

    promotions: list[Promotion] = []
    for gridbox in grid_items:
        item = {"gridbox": {"data": gridbox, "meta": {}}}
        promo = _item_to_promotion(item, weeks, week_by_range, this_week, next_week)
        if promo:
            promotions.append(promo)

    return promotions


def _parse_super_savers_page() -> list[dict]:
    response = SESSION.get(SUPER_SAVERS_PAGE, timeout=30)
    response.raise_for_status()
    page_html = response.text
    items: list[dict] = []
    seen: set[str] = set()

    for match in GRID_DATA_RE.finditer(page_html):
        raw = html.unescape(match.group(1))
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        title = data.get("fullTitle") or data.get("title") or ""
        if not title:
            continue
        key = title.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(data)

    logger.info("Parsed %d Super Savers products from page", len(items))
    return items


def _item_to_promotion(
    item: dict,
    weeks: list[WeekWindow],
    week_by_range: dict[tuple[date, date], WeekWindow],
    this_week: WeekWindow | None,
    next_week: WeekWindow | None,
) -> Promotion | None:
    gridbox = (item.get("gridbox") or {}).get("data") or {}
    meta = (item.get("gridbox") or {}).get("meta") or {}

    name = gridbox.get("fullTitle") or gridbox.get("title") or ""
    if not name:
        return None

    if not gridbox.get("lidlPlus"):
        return None

    if not is_produce(name, _category_hint(gridbox, meta)):
        return None

    if not _has_week_ribbon(gridbox):
        return None

    promo_from, promo_until = _resolve_dates(
        gridbox, weeks, week_by_range, this_week, next_week
    )
    if not promo_from or not promo_until:
        return None

    promotional = _price_from_gridbox(gridbox, lidl_plus=True)
    if not promotional:
        return None

    canonical = gridbox.get("canonicalUrl") or ""
    url = f"https://www.lidl.ie{canonical}" if canonical.startswith("/") else canonical
    packaging = (gridbox.get("lidlPlus") or [{}])[0]
    quantity = (packaging.get("price") or {}).get("packaging", {}).get("text")

    return Promotion(
        supermarket="Lidl",
        product=name,
        promotional_price=promotional,
        promotion_from=promo_from,
        promotion_until=promo_until,
        source="super_savers",
        url=url or None,
        quantity=quantity,
    ).with_normalized_dates()


def _has_week_ribbon(gridbox: dict) -> bool:
    for ribbon in gridbox.get("ribbons") or []:
        text = ribbon.get("text") if isinstance(ribbon, dict) else str(ribbon)
        text = text or ""
        if RIBBON_RANGE_RE.search(text) or RIBBON_FROM_RE.search(text):
            return True
    return False


def _category_hint(gridbox: dict, meta: dict) -> str:
    keyfacts = gridbox.get("keyfacts") or {}
    return keyfacts.get("wonCategoryPrimary") or ""


def _resolve_dates(
    gridbox: dict,
    weeks: list[WeekWindow],
    week_by_range: dict[tuple[date, date], WeekWindow],
    this_week: WeekWindow | None,
    next_week: WeekWindow | None,
) -> tuple[date | None, date | None]:
    # Ribbon text (e.g. "21.05 - 27.05" or "From 04.06") matches the leaflet week.
    for ribbon in gridbox.get("ribbons") or []:
        text = ribbon.get("text") if isinstance(ribbon, dict) else str(ribbon)
        parsed = _ribbon_dates(text, weeks, week_by_range)
        if parsed[0] is not None:
            return parsed

    store_start = gridbox.get("storeStartDate")
    if store_start:
        start = datetime.fromtimestamp(store_start, tz=DUBLIN).date()
        for pf, pu in week_by_range:
            if pf <= start <= pu:
                return pf, pu
        if next_week and start >= next_week.promo_from:
            return next_week.promo_from, next_week.promo_until

    if this_week:
        return this_week.promo_from, this_week.promo_until
    return None, None


def _ribbon_dates(
    text: str,
    weeks: list[WeekWindow],
    week_by_range: dict[tuple[date, date], WeekWindow],
) -> tuple[date | None, date | None]:
    text = text or ""
    match = RIBBON_RANGE_RE.search(text)
    if match:
        return _dates_from_range_ribbon(match, weeks)

    from_match = RIBBON_FROM_RE.search(text)
    if from_match:
        return _dates_from_start_ribbon(from_match, weeks)

    return None, None


def _dates_from_range_ribbon(
    match: re.Match[str],
    weeks: list[WeekWindow],
) -> tuple[date | None, date | None]:
    start_day, start_month, end_day, end_month = (int(x) for x in match.groups())

    for week in weeks:
        if (
            week.promo_from.day == start_day
            and week.promo_from.month == start_month
            and week.promo_until.day == end_day
            and week.promo_until.month == end_month
        ):
            return week.promo_from, week.promo_until

    if not weeks:
        return None, None

    year = weeks[0].promo_from.year
    promo_from = date(year, start_month, start_day)
    promo_until = date(year, end_month, end_day)
    if promo_until < promo_from:
        if start_month == end_month:
            # e.g. 28.05 - 03.05 on the leaflet means 28 May – 3 June.
            next_month = start_month + 1
            if next_month > 12:
                promo_until = date(year + 1, 1, end_day)
            else:
                promo_until = date(year, next_month, end_day)
        else:
            promo_until = date(year + 1, end_month, end_day)

    return _snap_to_catalogue_week(promo_from, promo_until, weeks)


def _dates_from_start_ribbon(
    match: re.Match[str],
    weeks: list[WeekWindow],
) -> tuple[date | None, date | None]:
    """Ribbon like 'From 04.06' — start of a Thu–Wed catalogue week."""
    start_day, start_month = (int(x) for x in match.groups())
    for week in weeks:
        if week.promo_from.day == start_day and week.promo_from.month == start_month:
            return week.promo_from, week.promo_until

    if not weeks:
        return None, None

    year = weeks[0].promo_from.year
    promo_from = date(year, start_month, start_day)
    return _snap_to_catalogue_week(promo_from, promo_from, weeks)


def _snap_to_catalogue_week(
    promo_from: date,
    promo_until: date,
    weeks: list[WeekWindow],
) -> tuple[date, date]:
    """Align ribbon ranges to Thu–Wed catalogue weeks from the leaflet hub."""
    for week in weeks:
        if promo_from >= week.promo_from and promo_until <= week.promo_until:
            return week.promo_from, week.promo_until
        if promo_from <= week.promo_until and promo_until >= week.promo_from:
            return week.promo_from, week.promo_until
    return promo_from, promo_until


def _price_from_gridbox(gridbox: dict, *, lidl_plus: bool) -> str | None:
    if lidl_plus:
        lp = gridbox.get("lidlPlus") or []
        if lp and isinstance(lp, list):
            price = (lp[0].get("price") or {}).get("price")
            if price is not None:
                return str(price)
    price_data = gridbox.get("price") or {}
    price = price_data.get("price")
    if price is not None:
        return str(price)
    return None


def _save_snapshot(items: list) -> None:
    snap_dir = LEAFLETS_ROOT / "lidl" / "super-savers"
    snap_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(DUBLIN).strftime("%Y-%m-%dT%H%M%S")
    path = snap_dir / f"{ts}.json"
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
