from app.llm.base import LLMProvider, Message
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


def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "minimax").lower()
    provider_cls = _providers.get(provider_name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider_name}'. Available: {list(_providers.keys())}"
        )
    return provider_cls()


__all__ = [
    "LLMProvider",
    "Message",
    "MiniMaxProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "get_llm_provider",
]
