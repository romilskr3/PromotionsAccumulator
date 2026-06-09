"""Default keywords for the Favourites filter on each produce tab.

Baked into site-config.json on publish. Users can override per tab in the site
UI (saved in the browser). Edit these lists to change defaults for new visitors.
"""

from __future__ import annotations

VEGETABLE_FAVOURITE_KEYWORDS: list[str] = [
    "onions",
    "carrots",
    "cucumbers",
    "tomatoes",
]

FRUIT_FAVOURITE_KEYWORDS: list[str] = [
    "bananas",
    "apples",
]

# Backward compatibility for older site-config consumers.
FREQUENT_BUY_KEYWORDS: list[str] = VEGETABLE_FAVOURITE_KEYWORDS

DEFAULT_FAVOURITE_KEYWORDS: dict[str, list[str]] = {
    "vegetable": VEGETABLE_FAVOURITE_KEYWORDS,
    "fruit": FRUIT_FAVOURITE_KEYWORDS,
}
