from __future__ import annotations

from fetchers._shared.models import Promotion

COLUMNS = [
    "Supermarket",
    "Product",
    "Quantity",
    "Price",
    "From Date",
    "Until Date",
    "Status",
    "Active today",
]

# Extra fields for sorting/filtering in the web UI (not shown in the table).
CSV_EXTRA_COLUMNS = ["category", "from_sort", "until_sort"]


def sort_key(p: Promotion) -> tuple:
    status_order = {"live": 0, "upcoming": 1, "ended": 2}
    return (
        p.supermarket,
        status_order.get(p.promotion_status(), 2),
        p.promotion_from,
        p.product.lower(),
    )
