import httpx
from app.llm.base import LLMProvider, Message
from app.config import settings
from typing import Dict, Any, List


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4o", base_url: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.base_url = base_url or settings.OPENAI_BASE_URL
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=120.0)

    async def complete(self, messages: List[Message], **kwargs) -> str:
        response = self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [msg.to_dict() for msg in messages],
                "temperature": kwargs.get("temperature", 0.3),
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def complete_json(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        response = self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [msg.to_dict() for msg in messages],
                "response_format": {"type": "json_object"},
                "temperature": kwargs.get("temperature", 0.3),
            },
        )
        response.raise_for_status()
        import json
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        return json.loads(content)
