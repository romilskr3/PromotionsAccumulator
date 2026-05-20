from __future__ import annotations

from fetchers._shared.models import Promotion

COLUMNS = [
    "Supermarket",
    "Product",
    "Quantity",
    "Price",
    "From Date",
    "Until Date",
    "Active today",
]

# Extra fields for sorting/filtering in the web UI (not shown in the table).
CSV_EXTRA_COLUMNS = ["from_sort", "until_sort"]


def sort_key(p: Promotion) -> tuple:
    return (
        p.supermarket,
        0 if p.active_today() else 1,
        p.promotion_from,
        p.product.lower(),
    )
