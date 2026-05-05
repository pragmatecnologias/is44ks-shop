from __future__ import annotations

from app.config import settings
from app.vision.openai_vision_provider import OpenAIVisionProvider


class QwenVLProvider(OpenAIVisionProvider):
    provider_name = "qwen_vl"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key or settings.VISION_LLM_API_KEY or "local",
            model=model or settings.VISION_LLM_MODEL,
            base_url=base_url or settings.VISION_LLM_BASE_URL,
            timeout_seconds=timeout_seconds or settings.VISION_LLM_TIMEOUT_SECONDS,
        )
