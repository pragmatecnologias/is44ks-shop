from __future__ import annotations

from typing import Any

from app.connectors.dataforseo.client import DataForSEOClient


class DataForSEOMerchantClient:
    def __init__(self, client: DataForSEOClient) -> None:
        self.client = client

    def submit_google_shopping_products_task(
        self,
        *,
        keyword: str,
        location_code: int,
        language_code: str,
        depth: int = 10,
        priority: int = 1,
        tag: str | None = None,
    ) -> dict[str, Any]:
        payload = [
            {
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "depth": depth,
                "device": "desktop",
                "os": "windows",
                "priority": priority,
            }
        ]
        if tag:
            payload[0]["tag"] = tag
        return self.client.post_json("/merchant/google/products/task_post", payload)

    def get_google_shopping_products_result(self, task_id: str) -> dict[str, Any]:
        return self.client.get_json(f"/merchant/google/products/task_get/advanced/{task_id}")
