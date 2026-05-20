from __future__ import annotations

import re
from datetime import date

from bs4 import BeautifulSoup

from fetchers._shared.http import get
from fetchers._shared.models import WeekWindow

HUB_URL = "https://www.aldi.ie/leaflet"

# aldi-ie-thur-14may-sun-17-may
SLUG_RE = re.compile(
    r"aldi-ie-thur-(\d{1,2})-?([a-z]{3})-sun-(\d{1,2})-?([a-z]{3})",
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


def _infer_year(month: int, day: int) -> int:
    today = date.today()
    year = today.year
    if month < today.month - 6:
        year += 1
    elif month > today.month + 6:
        year -= 1
    return year


def _parse_slug(slug: str) -> tuple[date, date] | None:
    match = SLUG_RE.search(slug)
    if not match:
        return None
    thu_day, thu_mon, sun_day, sun_mon = match.groups()
    start_month = MONTHS.get(thu_mon.lower())
    end_month = MONTHS.get(sun_mon.lower())
    if not start_month or not end_month:
        return None
    year = _infer_year(start_month, int(thu_day))
    promo_from = date(year, start_month, int(thu_day))
    promo_until = date(year, end_month, int(sun_day))
    if promo_until < promo_from:
        promo_until = date(year + 1, end_month, int(sun_day))
    return promo_from, promo_until


def discover_weeks() -> list[WeekWindow]:
    response = get(HUB_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    weeks: list[WeekWindow] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "leaflet.aldi.ie" not in href:
            continue
        slug = href.rstrip("/").split("/")[-1]
        if slug in seen:
            continue
        dates = _parse_slug(slug)
        if not dates:
            continue
        seen.add(slug)
        promo_from, promo_until = dates
        title = anchor.get_text(" ", strip=True) or slug
        weeks.append(
            WeekWindow(
                promo_from=promo_from,
                promo_until=promo_until,
                label=f"Thu {promo_from:%d %b} – Sun {promo_until:%d %b}",
                source_url=href if href.startswith("http") else f"https://leaflet.aldi.ie/{slug}",
            )
        )

    weeks.sort(key=lambda w: w.promo_from)
    return weeks[:2]
