from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings
from app.vision.base import VisionProvider, image_bytes_to_data_url, response_schema_instruction


class OpenAIVisionProvider(VisionProvider):
    provider_name = "openai_vision"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY or "local"
        self.model = model or settings.VISION_LLM_MODEL or settings.OPENAI_MODEL
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.timeout_seconds = timeout_seconds or settings.VISION_LLM_TIMEOUT_SECONDS
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=self.timeout_seconds)

    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        response_schema: dict | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        data_url = image_bytes_to_data_url(image_bytes, content_type=(metadata or {}).get("content_type"))
        user_prompt = prompt.strip()
        user_prompt = "\n\n".join(
            part for part in [user_prompt, response_schema_instruction(response_schema, metadata)] if part
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a product-research vision assistant. "
                    "Extract structured data from screenshots and photos. "
                    "Return only JSON."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        try:
            response = self.client.post("/chat/completions", json=payload)
        except Exception:
            payload.pop("response_format", None)
            response = self.client.post("/chat/completions", json=payload)

        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON response",
                "raw": content,
            }
