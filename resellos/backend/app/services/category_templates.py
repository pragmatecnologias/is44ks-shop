from __future__ import annotations

from typing import Any


CATEGORY_TEMPLATES: dict[str, dict[str, Any]] = {
    "car accessories": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Confirm dimensions",
            "Check universal fit claims",
            "Avoid mechanical or safety-critical parts",
            "Check installation photos",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "What are the exact dimensions?",
            "Does the packaging include any logo?",
            "What is the product weight?",
        ],
        "red_flags": ["airbag", "seatbelt", "brake", "electrical"],
        "listing_angles": ["keeps car organized", "prevents items falling", "easy installation", "universal fit"],
    },
    "desk accessories": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Check bundle potential",
            "Check size and dimensions",
            "Check whether competitors use real photos",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "Can you confirm the material?",
            "What are the exact dimensions?",
            "Can you send real photos?",
        ],
        "red_flags": ["electrical", "fragile", "branded"],
        "listing_angles": ["cleans up desk clutter", "boosts productivity", "small space solution"],
    },
    "home organization": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Check dimensions and material",
            "Check return risk",
            "Check bundle potential",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "What is the material?",
            "What are the exact dimensions?",
            "Can the item be bundled safely?",
        ],
        "red_flags": ["food contact", "child safety", "electrical"],
        "listing_angles": ["saves space", "neat home", "simple storage"],
    },
    "pet accessories": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Check material safety notes",
            "Avoid medicine or supplement claims",
            "Check for ingestible/contact risk",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "What material is used?",
            "Is it safe for generic pet use?",
            "Can you confirm there are no medicinal claims?",
        ],
        "red_flags": ["medicine", "supplement", "prescription", "ingestible"],
        "listing_angles": ["makes pet care easier", "safe generic accessory", "simple cleanup"],
    },
    "travel accessories": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Check compactness and weight",
            "Check bundle potential",
            "Check shipping risk",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "What is the product weight?",
            "Can it ship compactly?",
            "What are the exact dimensions?",
        ],
        "red_flags": ["battery", "electrical", "fragile"],
        "listing_angles": ["travel convenience", "compact storage", "easy packing"],
    },
    "creator tools": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Check photo quality needs",
            "Check feature clarity",
            "Check bundle potential",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "Can you provide real photos?",
            "What are the exact features?",
            "What is the product weight?",
        ],
        "red_flags": ["electronics", "trademarked"],
        "listing_angles": ["content creator utility", "desk-friendly setup", "simple workflow"],
    },
    "small tools": {
        "evidence_thresholds": {
            "sold": 5,
            "active": 5,
            "suppliers": 2,
        },
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
        "research_tasks": [
            "Confirm material and dimensions",
            "Check if the tool is powered or mechanical",
            "Check use case clarity",
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "supplier_questions": [
            "Is the tool powered?",
            "What is the exact material?",
            "What are the exact dimensions?",
        ],
        "red_flags": ["powered", "safety-critical"],
        "listing_angles": ["easy job completion", "small workshop helper"],
    },
}
