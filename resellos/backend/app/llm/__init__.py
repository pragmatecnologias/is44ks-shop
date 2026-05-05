from app.llm.base import LLMProvider, Message
from app.llm.minimax_provider import MiniMaxProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider
import os

_providers = {
    "minimax": MiniMaxProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


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
