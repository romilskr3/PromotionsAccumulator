from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from fetchers._shared.columns import COLUMNS, CSV_EXTRA_COLUMNS, sort_key
from fetchers._shared.models import DUBLIN, Promotion

CSV_OUTPUT_PATH = Path(__file__).resolve().parents[2] / "output" / "promotions.csv"


def promotion_row(p: Promotion) -> dict[str, str]:
    return {
        "Supermarket": p.supermarket,
        "Product": p.product,
        "Quantity": p.format_quantity(),
        "Price": p.format_price(p.promotional_price),
        "From Date": p.promotion_from.strftime("%d/%m"),
        "Until Date": p.promotion_until.strftime("%d/%m"),
        "Active today": "True" if p.active_today() else "False",
        "from_sort": p.promotion_from.isoformat(),
        "until_sort": p.promotion_until.isoformat(),
    }


def write_promotions_csv(
    promotions: list[Promotion], path: Path | None = None
) -> Path:
    path = path or CSV_OUTPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(DUBLIN).strftime("%Y-%m-%d %H:%M")
    fieldnames = COLUMNS + CSV_EXTRA_COLUMNS
    sorted_promos = sorted(promotions, key=sort_key)

    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(f"# Generated: {generated} Europe/Dublin\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for p in sorted_promos:
            writer.writerow(promotion_row(p))

    return path
