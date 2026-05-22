from __future__ import annotations

import importlib
import logging
from typing import Callable

from fetchers._shared.merge import FetchReport, StoreFetchResult
from fetchers._shared.models import Promotion

logger = logging.getLogger(__name__)

FetchFn = Callable[..., list[Promotion]]

STORES: dict[str, tuple[str, str]] = {
    "lidl": ("Lidl", "fetchers.lidl.fetch"),
    "aldi": ("Aldi", "fetchers.aldi.fetch"),
    "tesco": ("Tesco", "fetchers.tesco.fetch"),
    "supervalu": ("SuperValu", "fetchers.supervalu.fetch"),
    "dunnes": ("Dunnes", "fetchers.dunnes.fetch"),
}


def _load_fetcher(module_path: str) -> FetchFn:
    module = importlib.import_module(module_path)
    return module.fetch_promotions


def fetch_all(
    *,
    stores: list[str] | None = None,
    skip_download: bool = False,
    refresh_leaflets: bool = False,
) -> FetchReport:
    selected = stores or list(STORES.keys())
    results: list[StoreFetchResult] = []
    errors = 0

    for store_key in selected:
        if store_key not in STORES:
            logger.warning("Unknown store: %s", store_key)
            continue
        name, module_path = STORES[store_key]
        try:
            fetcher = _load_fetcher(module_path)
            promos = fetcher(
                skip_download=skip_download,
                refresh_leaflets=refresh_leaflets,
            )
            logger.info("%s: %d promotion(s)", name, len(promos))
            results.append(
                StoreFetchResult(
                    store_key=store_key,
                    store_name=name,
                    promotions=promos,
                )
            )
        except Exception as exc:
            errors += 1
            logger.error("%s fetch failed: %s", name, exc)
            results.append(
                StoreFetchResult(
                    store_key=store_key,
                    store_name=name,
                    promotions=[],
                    failed=True,
                    error_message=str(exc),
                )
            )

    if errors == len(selected):
        raise RuntimeError("All store fetchers failed")

    return FetchReport(results=results)
