from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resellos"
    LLM_PROVIDER: Literal["minimax", "openai", "ollama"] = "minimax"
    TEXT_LLM_PROVIDER: Literal["minimax", "openai", "ollama"] = "minimax"
    TEXT_LLM_MODEL: str = "MiniMax-Text-01"
    MINIMAX_API_KEY: str = ""
    MINIMAX_MODEL: str = "MiniMax-Text-01"
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    VISION_LLM_PROVIDER: Literal["qwen_vl", "openai"] = "qwen_vl"
    VISION_LLM_BASE_URL: str = "http://localhost:8001/v1"
    VISION_LLM_MODEL: str = "Qwen/Qwen3-VL-8B-Instruct"
    VISION_LLM_TIMEOUT_SECONDS: int = 120
    VISION_LLM_API_KEY: str = ""
    DEFAULT_MARKETPLACE_FEE_PERCENT: float = 13.0
    DEFAULT_PACKAGING_COST: float = 0.50
    DEFAULT_OUTBOUND_SHIPPING: float = 4.50
    DEFAULT_RETURN_ALLOWANCE: float = 0.50
    MIN_ACCEPTABLE_PROFIT: float = 3.0
    MIN_ACCEPTABLE_MARGIN: float = 20.0
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
