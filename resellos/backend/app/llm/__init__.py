from app.llm.base import LLMProvider, Message
from app.config import settings
import os

_providers = {}

try:
    from app.llm.minimax_provider import MiniMaxProvider

    _providers["minimax"] = MiniMaxProvider
except Exception:
    MiniMaxProvider = None  # type: ignore[assignment]

try:
    from app.llm.openai_provider import OpenAIProvider

    _providers["openai"] = OpenAIProvider
except Exception:
    OpenAIProvider = None  # type: ignore[assignment]

try:
    from app.llm.ollama_provider import OllamaProvider

    _providers["ollama"] = OllamaProvider
except Exception:
    OllamaProvider = None  # type: ignore[assignment]


def get_text_llm_provider() -> LLMProvider:
    provider_name = os.getenv("TEXT_LLM_PROVIDER", os.getenv("LLM_PROVIDER", settings.TEXT_LLM_PROVIDER)).lower()
    provider_cls = _providers.get(provider_name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown TEXT_LLM_PROVIDER '{provider_name}'. Available: {list(_providers.keys())}"
        )
    if provider_name == "openai":
        return provider_cls(api_key=settings.OPENAI_API_KEY, model=os.getenv("TEXT_LLM_MODEL", settings.OPENAI_MODEL))
    if provider_name == "ollama":
        return provider_cls(base_url=settings.OLLAMA_BASE_URL, model=os.getenv("TEXT_LLM_MODEL", settings.OLLAMA_MODEL))
    return provider_cls(
        api_key=settings.MINIMAX_API_KEY,
        model=os.getenv("TEXT_LLM_MODEL", settings.TEXT_LLM_MODEL or settings.MINIMAX_MODEL),
        base_url=settings.MINIMAX_BASE_URL,
    )


def get_llm_provider() -> LLMProvider:
    return get_text_llm_provider()


__all__ = [
    "LLMProvider",
    "Message",
    "MiniMaxProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "get_text_llm_provider",
    "get_llm_provider",
]
