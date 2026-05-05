import httpx
from app.llm.base import LLMProvider, Message
from typing import Dict, Any, List


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    async def complete(self, messages: List[Message], **kwargs) -> str:
        # Build prompt from messages
        prompt_parts = []
        for msg in messages:
            prompt_parts.append(f"{msg.role}: {msg.content}")
        prompt = "\n\n".join(prompt_parts)

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")

    async def complete_json(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        prompt_parts = []
        for msg in messages:
            prompt_parts.append(f"{msg.role}: {msg.content}")
        prompt = "\n\n".join(prompt_parts) + "\n\nRespond ONLY with valid JSON."

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            import json
            content = response.json().get("response", "{}")
            return json.loads(content)