"""Filter offers to fruit and vegetables."""

from __future__ import annotations

import re

PRODUCE_KEYWORDS = re.compile(
    r"\b("
    r"fruit|vegetable|veg\b|salad|herb|berry|berries|apple|banana|orange|"
    r"lemon|lime|grape|melon|watermelon|pineapple|mango|peach|pear|plum|"
    r"cherry|strawberr|blueberr|raspberr|blackberr|avocado|tomatoes?|"
    r"potatoes?|carrots?|onions?|garlic|peppers?|cucumber|courgette|zucchini|"
    r"pears?|apples?|oranges?|shallots?|mushrooms?|"
    r"aubergine|eggplant|broccoli|cauliflower|cabbage|lettuce|spinach|"
    r"kale|celery|beetroot|beet|radish|turnip|parsnip|swede|leek|"
    r"mushroom|ginger|spring\s+onion|scallion|shallot|beans|peas|"
    r"sweetcorn|corn\s+on|asparagus|artichoke|rhubarb|fig|kiwi|"
    r"pomegranate|nectarine|apricot|coconut|grapefruit|satsuma|"
    r"clementine|mandarin|organic\s+produce|fresh\s+produce"
    r")\b",
    re.IGNORECASE,
)

BLOCKLIST = re.compile(
    r"\b("
    r"plant\b|flower|bouquet|seed\s+packet|grill|bbq|meat|chicken|"
    r"beef|pork|fish|salmon|ham\b|sausage|bacon|cheese|milk\b|yoghurt|"
    r"yogurt|butter|egg\b|bread|napp|diaper|wine|beer|"
    r"salt/pepper\s+mill|pepper\s+mill|electric\s+mill|crisp|crisps|"
    r"dumpling|schnitzel|wings|nectar|cashew|nut\b|frozen\s+fruit|"
    r"pickles?\b|plants\b|chilli\s+plants|dumplings?"
    r")\b",
    re.IGNORECASE,
)

PRODUCE_CATEGORY = re.compile(
    r"\b(fresh\s+fruit|fruit|vegetable|veg\b|salad|potato|tomato|herb|berry)\b",
    re.IGNORECASE,
)

PRODUCE_SECTIONS = re.compile(
    r"\b(fruit|vegetable|veg|salad|produce|organic)\b",
    re.IGNORECASE,
)


def is_produce(product_name: str, section: str = "") -> bool:
    text = f"{product_name} {section}".strip()
    if BLOCKLIST.search(product_name):
        return False
    if PRODUCE_CATEGORY.search(section):
        return True
    if PRODUCE_SECTIONS.search(section):
        return True
    return bool(PRODUCE_KEYWORDS.search(product_name))
