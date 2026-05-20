"""Normalise product names for display (strip store prefix, pack size, was-price)."""

from __future__ import annotations

import re

_STORE_PREFIXES = (
    "SuperValu Signature Tastes",
    "SuperValu",
    "Lidl",
    "Aldi",
    "Tesco",
)

_TRAILING_NOISE_RE = [
    re.compile(r"\s+was\s+.*$", re.IGNORECASE),
    re.compile(r"\s+NOW\s+.*$", re.IGNORECASE),
    re.compile(r"\s+Save\s+\d+%.*$", re.IGNORECASE),
    re.compile(r"\s*\(Details In-store.*$", re.IGNORECASE),
    re.compile(r"\s*-\s*€[\d.,]+/kg\s*$", re.IGNORECASE),
    re.compile(r"\s*\d+pce\s*$", re.IGNORECASE),
    re.compile(r"\s*\d+\s*kg\s*$", re.IGNORECASE),
    re.compile(r"\s*\d+\s*g\s*$", re.IGNORECASE),
    re.compile(r"\s+Tray\s*$", re.IGNORECASE),
]


def clean_product_display_name(name: str) -> str:
    text = re.sub(r"\s+", " ", name).strip()
    for prefix in _STORE_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix) :].strip()
            break
    for pattern in _TRAILING_NOISE_RE:
        text = pattern.sub("", text).strip()
    return text
