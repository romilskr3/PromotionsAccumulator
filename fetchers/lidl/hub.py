from __future__ import annotations

import re
from datetime import date

from bs4 import BeautifulSoup

from fetchers._shared.http import get
from fetchers._shared.models import WeekWindow

HUB_URL = "https://www.lidl.ie/c/online-leaflets/s10020358"

# From Thu 14/05 to Wed 20/05 May
LABEL_RE = re.compile(
    r"From\s+Thu\s+(\d{1,2})/(\d{1,2})\s+to\s+Wed\s+(\d{1,2})/(\d{1,2})\s+(\w+)",
    re.IGNORECASE,
)
LEAFLET_PATH_RE = re.compile(r"/l/en/leaflet/[^\"'\s]+", re.IGNORECASE)

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _infer_year(thu_month: int, wed_month: int, thu_day: int, wed_day: int) -> int:
    today = date.today()
    year = today.year
    # Week spanning year boundary
    if thu_month == 12 and wed_month == 1:
        return year
    if thu_month < today.month - 6:
        year += 1
    elif thu_month > today.month + 6:
        year -= 1
    return year


def _parse_label(label: str) -> tuple[date, date] | None:
    match = LABEL_RE.search(label)
    if not match:
        return None
    thu_d, thu_m, wed_d, wed_m, month_word = match.groups()
    end_month = MONTHS.get(month_word.lower(), int(wed_m))
    start_month = int(thu_m)
    year = _infer_year(start_month, end_month, int(thu_d), int(wed_d))
    promo_from = date(year, start_month, int(thu_d))
    promo_until = date(year, end_month, int(wed_d))
    if promo_until < promo_from:
        promo_until = date(year + 1, end_month, int(wed_d))
    return promo_from, promo_until


def discover_weeks() -> list[WeekWindow]:
    response = get(HUB_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    weeks: list[WeekWindow] = []
    seen_urls: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/l/en/leaflet/" not in href:
            continue
        if not href.startswith("http"):
            href = f"https://www.lidl.ie{href}"
        if href in seen_urls:
            continue
        label = anchor.get_text(" ", strip=True)
        dates = _parse_label(label)
        if not dates:
            continue
        seen_urls.add(href)
        promo_from, promo_until = dates
        weeks.append(
            WeekWindow(
                promo_from=promo_from,
                promo_until=promo_until,
                label=label,
                source_url=href,
            )
        )

    if not weeks:
        # Fallback: scan raw HTML for leaflet links + nearby text
        for match in LEAFLET_PATH_RE.finditer(response.text):
            path = match.group(0)
            href = f"https://www.lidl.ie{path}"
            if href in seen_urls:
                continue
            seen_urls.add(href)
            slug = path.split("/leaflet/")[-1].split("/")[0]
            dates = _parse_slug_dates(slug)
            if dates:
                promo_from, promo_until = dates
                weeks.append(
                    WeekWindow(
                        promo_from=promo_from,
                        promo_until=promo_until,
                        label=slug,
                        source_url=href,
                    )
                )

    weeks.sort(key=lambda w: w.promo_from)
    return weeks[:2]


def _parse_slug_dates(slug: str) -> tuple[date, date] | None:
    # from-thu-14-05-to-wed-20-05-may
    match = re.search(
        r"from-thu-(\d{1,2})-(\d{1,2})-to-wed-(\d{1,2})-(\d{1,2})-(\w+)",
        slug,
        re.IGNORECASE,
    )
    if not match:
        return None
    thu_d, thu_m, wed_d, wed_m, month_word = match.groups()
    end_month = MONTHS.get(month_word.lower(), int(wed_m))
    start_month = int(thu_m)
    year = _infer_year(start_month, end_month, int(thu_d), int(wed_d))
    promo_from = date(year, start_month, int(thu_d))
    promo_until = date(year, end_month, int(wed_d))
    if promo_until < promo_from:
        promo_until = date(year + 1, end_month, int(wed_d))
    return promo_from, promo_until
