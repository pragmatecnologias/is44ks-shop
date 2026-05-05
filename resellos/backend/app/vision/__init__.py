from app.config import settings
from app.vision.base import VisionProvider
from app.vision.openai_vision_provider import OpenAIVisionProvider
from app.vision.qwen_vl_provider import QwenVLProvider


def get_vision_provider() -> VisionProvider:
    provider_name = settings.VISION_LLM_PROVIDER.lower()
    if provider_name in {"qwen_vl", "qwen", "qwen-vl"}:
        return QwenVLProvider()
    if provider_name in {"openai", "openai_vision", "openai-vision"}:
        return OpenAIVisionProvider(api_key=settings.OPENAI_API_KEY, model=settings.VISION_LLM_MODEL)
    raise ValueError(
        f"Unknown VISION_LLM_PROVIDER '{provider_name}'. Available: ['qwen_vl', 'openai']"
    )


__all__ = [
    "VisionProvider",
    "OpenAIVisionProvider",
    "QwenVLProvider",
    "get_vision_provider",
]
