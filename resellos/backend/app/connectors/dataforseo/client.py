from __future__ import annotations

from typing import Any

import httpx


class DataForSEOClient:
    def __init__(
        self,
        login: str,
        password: str,
        base_url: str = "https://api.dataforseo.com/v3",
        timeout_seconds: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=httpx.BasicAuth(login, password),
            headers={"Content-Type": "application/json"},
            timeout=timeout_seconds,
        )

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post(path, json=payload)
        response.raise_for_status()
        return response.json()

    def get_json(self, path: str) -> dict[str, Any]:
        response = self.client.get(path)
        response.raise_for_status()
        return response.json()

