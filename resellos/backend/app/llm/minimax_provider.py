import httpx
from app.llm.base import LLMProvider, Message
from app.config import settings
from typing import Dict, Any, List


class MiniMaxProvider(LLMProvider):
    """MiniMax Text API provider - default for ResellOS."""

    def __init__(
        self,
        api_key: str = None,
        model: str = "MiniMax-Text-01",
        base_url: str = "https://api.minimax.chat/v1",
    ):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.model = model
        self.base_url = base_url
        self._client = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._client

    async def complete(self, messages: List[Message], **kwargs) -> str:
        client = self._get_client()
        payload = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": kwargs.get("temperature", 0.3),
        }
        response = client.post("/text/chatcompletion_v2", json=payload)
        response.raise_for_status()
        data = response.json()
        # MiniMax returns choices[0].message.content similar to OpenAI
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def complete_json(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        client = self._get_client()
        # Add instruction to respond with JSON
        json_messages = list(messages)
        json_messages.append(Message("user", "Respond ONLY with valid JSON. No markdown, no explanation."))
        payload = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in json_messages],
            "temperature": kwargs.get("temperature", 0.1),
        }
        response = client.post("/text/chatcompletion_v2", json=payload)
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw": content}
