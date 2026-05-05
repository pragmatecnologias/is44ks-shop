from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _get_nested(value: Any, *path: str) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def iter_google_shopping_items(payload: Any) -> Iterable[dict[str, Any]]:
    if isinstance(payload, dict):
        item_type = payload.get("type")
        if (
            item_type in {"google_shopping_serp", "google_shopping_paid"}
            or payload.get("shopping_url")
            or payload.get("price") is not None
            or payload.get("title")
            or payload.get("product_images")
        ):
            yield payload
        for value in payload.values():
            yield from iter_google_shopping_items(value)
    elif isinstance(payload, list):
        for value in payload:
            yield from iter_google_shopping_items(value)


def map_google_shopping_item_to_candidate(item: dict[str, Any], *, source_job: dict[str, Any]) -> dict[str, Any]:
    delivery_price = _get_nested(item, "delivery_info", "delivery_price", "current")
    if delivery_price is None:
        delivery_price = _get_nested(item, "delivery_price", "current")

    product_rating = item.get("product_rating") or {}
    shop_rating = item.get("shop_rating") or {}
    rating_value = (
        product_rating.get("value")
        if isinstance(product_rating, dict)
        else None
    ) or (shop_rating.get("value") if isinstance(shop_rating, dict) else None)
    reviews_count = item.get("reviews_count")
    if reviews_count is None and isinstance(product_rating, dict):
        reviews_count = product_rating.get("votes_count")
    if reviews_count is None and isinstance(shop_rating, dict):
        reviews_count = shop_rating.get("votes_count")

    image_url = None
    product_images = item.get("product_images")
    if isinstance(product_images, list) and product_images:
        image_url = product_images[0]
    if not image_url:
        image_url = item.get("image_url")

    seller = item.get("seller") or item.get("domain")
    url = item.get("shopping_url") or item.get("url")

    return {
        "source": "DATAFORSEO",
        "candidate_type": "MARKETPLACE_EVIDENCE",
        "marketplace": "Google Shopping",
        "evidence_type": "ACTIVE_LISTING",
        "title": item.get("title") or item.get("description"),
        "url": url,
        "price": _as_float(item.get("price")),
        "shipping_price": _as_float(delivery_price),
        "seller": seller,
        "rating": _as_float(rating_value),
        "review_count": _as_int(reviews_count),
        "image_url": image_url,
        "confidence": "MEDIUM" if item.get("title") else "LOW",
        "review_status": "PENDING",
        "raw_json": item,
    }
