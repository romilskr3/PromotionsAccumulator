from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

DUBLIN = ZoneInfo("Europe/Dublin")


@dataclass
class Promotion:
    supermarket: str
    product: str
    promotional_price: str
    promotion_from: date
    promotion_until: date
    source: str = "leaflet"
    url: str | None = None
    quantity: str | None = None

    def active_today(self, today: date | None = None) -> bool:
        return self.promotion_status(today) == "live"

    def promotion_status(self, today: date | None = None) -> str:
        """One of live, upcoming, ended (Europe/Dublin calendar day)."""
        today = today or datetime.now(DUBLIN).date()
        if self.promotion_from <= today <= self.promotion_until:
            return "live"
        if today < self.promotion_from:
            return "upcoming"
        return "ended"

    def format_price(self, value: str | None) -> str:
        if value is None or value == "":
            return "—"
        text = value.strip()
        if text.lower().startswith("€"):
            return text.replace(" ", "")
        cent_match = re.fullmatch(r"(\d+)c", text.replace(" ", ""), re.IGNORECASE)
        if cent_match:
            return f"€{int(cent_match.group(1)) / 100:.2f}"
        if re.fullmatch(r"\d+\s+for\s+€\s*[\d.]+", text, re.IGNORECASE):
            return re.sub(r"€\s+", "€", text)
        if "for" in text.lower():
            return text
        return f"€{text}"

    def format_quantity(self, value: str | None = None) -> str:
        text = (value if value is not None else self.quantity) or ""
        text = text.strip()
        if not text:
            return "—"
        lowered = text.lower()
        if lowered == "each":
            return "Each"
        pack_match = re.fullmatch(r"(\d+)\s*pack(?:\s*\(.*\))?", lowered)
        if pack_match:
            return f"{pack_match.group(1)} pack"
        weight_match = re.fullmatch(r"(\d+)\s*(g|kg)(?:\s*\(.*\))?", lowered)
        if weight_match:
            return f"{weight_match.group(1)} {weight_match.group(2)}"
        compact = re.fullmatch(r"(\d+)(g|kg)", lowered)
        if compact:
            return f"{compact.group(1)} {compact.group(2)}"
        multi = re.fullmatch(r"(\d+)\s+for\s+€\s*([\d.]+)", lowered)
        if multi:
            return f"{multi.group(1)} for €{multi.group(2)}"
        return text


@dataclass
class WeekWindow:
    promo_from: date
    promo_until: date
    label: str
    source_url: str
