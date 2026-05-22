from __future__ import annotations

import time

import requests

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "PromotionsAccumulator/0.1 (personal grocery tool; "
            "+https://github.com/local/promotions-accumulator)"
        ),
        "Accept-Language": "en-IE,en;q=0.9",
    }
)

REQUEST_DELAY_SEC = 1.5
_last_request_at = 0.0


def get(url: str, **kwargs) -> requests.Response:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < REQUEST_DELAY_SEC:
        time.sleep(REQUEST_DELAY_SEC - elapsed)
    response = SESSION.get(url, timeout=30, **kwargs)
    _last_request_at = time.monotonic()
    response.raise_for_status()
    return response


def get_optional(url: str, **kwargs) -> requests.Response | None:
    """GET that returns None on 404 instead of raising (for leaflet ID probing)."""
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < REQUEST_DELAY_SEC:
        time.sleep(REQUEST_DELAY_SEC - elapsed)
    response = SESSION.get(url, timeout=30, **kwargs)
    _last_request_at = time.monotonic()
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response
