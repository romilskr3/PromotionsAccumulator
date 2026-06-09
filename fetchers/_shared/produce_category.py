"""Classify promotion products as fruit or vegetable (for site tabs).

Edit FRUIT_TERMS / VEGETABLE_TERMS to add products; VEGETABLE_FIRST avoids misclassifying
e.g. Cherry Tomatoes and Plum Tomatoes as fruit.
"""

from __future__ import annotations

import re
from typing import Literal

ProduceType = Literal["fruit", "vegetable"]

# Checked before fruit patterns (tomato, pepper, etc.).
VEGETABLE_FIRST = re.compile(
    r"\b("
    r"tomato|potato|onion|shallot|pepper|cucumber(?:s)?|broccoli|mushroom|radish|"
    r"salad|courgette|zucchini|carrot|cabbage|lettuce|spinach|kale|celery|"
    r"beetroot|beet|turnip|parsnip|swede|leek|garlic|cauliflower|aubergine|"
    r"eggplant|asparagus|artichoke|ginger|scallion|spring\s+onion|"
    r"sweetcorn|corn\s+on|beans?\b|peas?\b|chard|fennel|okra"
    r")\b",
    re.IGNORECASE,
)

FRUIT = re.compile(
    r"\b("
    r"mango|oranges?|pears?|apples?|easypeelers|satsuma|clementine|mandarin|"
    r"grapefruit|lemon|lime|grape|melon|watermelon|pineapple|peach(?:es)?|"
    r"strawberr(?:y|ies)?|blueberr(?:y|ies)?|raspberr(?:y|ies)?|"
    r"blackberr(?:y|ies)?|gooseberr(?:y|ies)?|cranberr(?:y|ies)?|"
    r"banana(?:s)?|kiwi|fig\b|apricot(?:s)?|nectarine(?:s)?|avocado|coconut|pomegranate|"
    r"rhubarb|damson|greengage|passion\s*fruit|physalis|lychee|papaya|"
    r"guava|persimmon|dragon\s*fruit|starfruit|currant"
    r")\b",
    re.IGNORECASE,
)

# Optional exact overrides (lowercase substring in product name).
EXTRA_VEGETABLE = ("salad trio",)
EXTRA_FRUIT = ()


def produce_type(product_name: str) -> ProduceType:
    text = product_name.strip().lower()
    for phrase in EXTRA_VEGETABLE:
        if phrase in text:
            return "vegetable"
    for phrase in EXTRA_FRUIT:
        if phrase in text:
            return "fruit"
    if VEGETABLE_FIRST.search(product_name):
        return "vegetable"
    if FRUIT.search(product_name):
        return "fruit"
    # Default: most unmatched fresh-produce promos in this project are vegetables.
    return "vegetable"
