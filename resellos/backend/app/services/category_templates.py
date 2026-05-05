from __future__ import annotations

from typing import Any


CATEGORY_TEMPLATES: dict[str, dict[str, Any]] = {
    "car accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["car seat gap organizer", "car side pocket storage"],
            "ebay_active": ["car seat gap organizer", "car storage accessory"],
            "mercari": ["car organizer", "car accessory"],
            "supplier": ["car seat gap storage box", "auto side organizer"],
        },
    },
    "desk accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["desk cable clips", "desk organizer"],
            "ebay_active": ["desk organizer", "desk accessory"],
            "mercari": ["desk cable clip", "desktop organizer"],
            "supplier": ["desk accessory", "cable clip organizer"],
        },
    },
    "home organization": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["drawer organizer", "storage solution"],
            "ebay_active": ["home organizer", "drawer divider"],
            "mercari": ["storage organizer", "drawer organizer"],
            "supplier": ["home organizer", "storage solution", "drawer organizer"],
        },
    },
    "pet accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["pet hair remover", "pet grooming glove"],
            "ebay_active": ["pet accessory", "pet grooming tool"],
            "mercari": ["pet accessory", "pet hair remover"],
            "supplier": ["pet accessory", "pet grooming tool"],
        },
    },
    "travel accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["travel organizer", "packing cube"],
            "ebay_active": ["travel accessory", "packing organizer"],
            "mercari": ["travel organizer", "packing cube"],
            "supplier": ["travel accessory", "travel organizer", "packing cube"],
        },
    },
    "creator tools": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["creator tool", "content creator accessory"],
            "ebay_active": ["desk mount", "creator accessory"],
            "mercari": ["creator accessory", "desk mount"],
            "supplier": ["creator tool", "content creator accessory", "desk mount"],
        },
    },
    "small tools": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["small tool", "hand tool"],
            "ebay_active": ["utility tool", "small workshop tool"],
            "mercari": ["hand tool", "utility tool"],
            "supplier": ["small tool", "utility tool", "hand tool"],
        },
    },
}
