from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.llm.base import LLMProvider


class BaseAgent(ABC):
    def __init__(self, llm_provider: LLMProvider, agent_name: str):
        self.llm = llm_provider
        self.agent_name = agent_name

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with given context and return results."""
        pass

    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from file."""
        try:
            with open(f"app/prompts/{filename}", "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format prompt with given variables."""
        return template.format(**kwargs)