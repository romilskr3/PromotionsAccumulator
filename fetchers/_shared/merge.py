from __future__ import annotations

import logging
from dataclasses import dataclass

from fetchers._shared.csv_import import promotions_by_supermarket
from fetchers._shared.dedupe import dedupe_by_product_week
from fetchers._shared.models import Promotion

logger = logging.getLogger(__name__)


@dataclass
class StoreFetchResult:
    store_key: str
    store_name: str
    promotions: list[Promotion]
    failed: bool = False
    error_message: str | None = None


@dataclass
class FetchReport:
    results: list[StoreFetchResult]

    @property
    def promotions(self) -> list[Promotion]:
        return [p for r in self.results for p in r.promotions]


def merge_with_previous_csv(
    report: FetchReport,
    previous: list[Promotion],
) -> list[Promotion]:
    """Merge fresh fetches into the previous CSV, per supermarket.

    Successful fetch: keep previous rows for that store and add new ones; duplicate
    product+week keys prefer the freshly fetched row. Ended promos stay until their
    dates pass (Status is recomputed on export). Failed/empty fetch: keep previous only.
    """
    previous_by_store = promotions_by_supermarket(previous)
    refreshed_stores = {r.store_name for r in report.results}
    merged: list[Promotion] = []

    for result in report.results:
        previous_rows = previous_by_store.get(result.store_name, [])
        if result.promotions:
            # Previous rows first so dedupe keeps the newer fetch on the same key.
            combined = previous_rows + result.promotions
            merged.extend(dedupe_by_product_week(combined))
            continue
        if previous_rows and (result.failed or not result.promotions):
            reason = (
                f"failed ({result.error_message})"
                if result.failed
                else "returned no promotions"
            )
            logger.warning(
                "%s fetch %s — keeping %d row(s) from previous CSV",
                result.store_name,
                reason,
                len(previous_rows),
            )
            merged.extend(previous_rows)

    for store_name, rows in previous_by_store.items():
        if store_name not in refreshed_stores:
            merged.extend(rows)

    return [p.with_normalized_dates() for p in merged]
