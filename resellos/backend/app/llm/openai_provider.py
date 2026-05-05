from openai import OpenAI
from app.llm.base import LLMProvider, Message
from app.config import settings
from typing import Dict, Any, List


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    async def complete(self, messages: List[Message], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            temperature=kwargs.get("temperature", 0.3),
        )
        return response.choices[0].message.content or ""

    async def complete_json(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            response_format={"type": "json_object"},
            temperature=kwargs.get("temperature", 0.3),
        )
        import json
        content = response.choices[0].message.content or "{}"
        return json.loads(content)