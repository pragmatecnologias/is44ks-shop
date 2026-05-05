from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: List[Message], **kwargs) -> str:
        pass

    @abstractmethod
    async def complete_json(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model

    async def complete(self, messages: List[Message], **kwargs) -> str:
        # Placeholder - actual implementation uses openai SDK
        return ""

    async def complete_json(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        # Placeholder - actual implementation uses openai SDK
        return {}
