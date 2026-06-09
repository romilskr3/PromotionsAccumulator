from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import date
from pathlib import Path

from fetchers._shared.columns import COLUMNS, CSV_EXTRA_COLUMNS
from fetchers._shared.csv_export import CSV_OUTPUT_PATH
from fetchers._shared.models import Promotion


def read_promotions_csv(path: Path | None = None) -> list[Promotion]:
    """Load promotions from the last generated CSV (if present)."""
    path = path or CSV_OUTPUT_PATH
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    data_lines = [line for line in lines if line.strip() and not line.startswith("#")]
    if len(data_lines) < 2:
        return []

    reader = csv.DictReader(data_lines)
    fieldnames = list(reader.fieldnames or [])
    expected = set(COLUMNS + CSV_EXTRA_COLUMNS)
    if not expected.intersection(fieldnames):
        return []

    promotions: list[Promotion] = []
    for row in reader:
        promo = _row_to_promotion(row)
        if promo:
            promotions.append(promo)
    return promotions


def _row_to_promotion(row: dict[str, str]) -> Promotion | None:
    try:
        promo_from = date.fromisoformat((row.get("from_sort") or "").strip())
        promo_until = date.fromisoformat((row.get("until_sort") or "").strip())
    except ValueError:
        return None

    supermarket = (row.get("Supermarket") or "").strip()
    product = (row.get("Product") or "").strip()
    if not supermarket or not product:
        return None

    quantity = (row.get("Quantity") or "").strip()
    if quantity in ("", "—"):
        quantity = None

    return Promotion(
        supermarket=supermarket,
        product=product,
        promotional_price=(row.get("Price") or "").strip(),
        promotion_from=promo_from,
        promotion_until=promo_until,
        source="csv-cache",
        quantity=quantity,
    ).with_normalized_dates()


def promotions_by_supermarket(
    promotions: Iterable[Promotion],
) -> dict[str, list[Promotion]]:
    grouped: dict[str, list[Promotion]] = {}
    for promo in promotions:
        grouped.setdefault(promo.supermarket, []).append(promo)
    return grouped
