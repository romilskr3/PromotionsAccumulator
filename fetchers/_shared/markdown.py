from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fetchers._shared.models import DUBLIN, Promotion

OUTPUT_PATH = Path(__file__).resolve().parents[2] / "output" / "promotions.md"

COLUMNS = [
    "Supermarket",
    "Product",
    "Quantity",
    "Price",
    "From Date",
    "Until Date",
    "Active today",
]


def _sort_key(p: Promotion) -> tuple:
    return (
        p.supermarket,
        0 if p.active_today() else 1,
        p.promotion_from,
        p.product.lower(),
    )


def render_promotions(promotions: list[Promotion]) -> str:
    now = datetime.now(DUBLIN).strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Fruit & Vegetable Promotions — Dublin",
        "",
        f"Generated: {now} Europe/Dublin",
        "",
        "## All promotions",
        "",
        "| " + " | ".join(COLUMNS) + " |",
        "| " + " | ".join(["---"] * len(COLUMNS)) + " |",
    ]

    sorted_promos = sorted(promotions, key=_sort_key)
    if not sorted_promos:
        lines.append("| _No promotions found this run._ | | | | | | |")
    else:
        for p in sorted_promos:
            lines.append(
                "| "
                + " | ".join(
                    [
                        p.supermarket,
                        _escape_cell(p.product),
                        _escape_cell(p.format_quantity()),
                        _escape_cell(p.format_price(p.promotional_price)),
                        _format_promo_date(p.promotion_from),
                        _format_promo_date(p.promotion_until),
                        "True" if p.active_today() else "False",
                    ]
                )
                + " |"
            )

    lines.append("")
    return "\n".join(lines)


def write_promotions(promotions: list[Promotion], path: Path | None = None) -> Path:
    path = path or OUTPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_promotions(promotions), encoding="utf-8")
    return path


def _format_promo_date(value: date) -> str:
    return value.strftime("%d/%m")


def _escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
