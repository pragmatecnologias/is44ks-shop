from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resellos"
    LLM_PROVIDER: Literal["minimax", "openai", "ollama"] = "minimax"
    MINIMAX_API_KEY: str = ""
    MINIMAX_MODEL: str = "MiniMax-Text-01"
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    DEFAULT_MARKETPLACE_FEE_PERCENT: float = 13.0
    DEFAULT_PACKAGING_COST: float = 0.50
    DEFAULT_RETURN_ALLOWANCE: float = 0.50
    MIN_ACCEPTABLE_PROFIT: float = 3.0
    MIN_ACCEPTABLE_MARGIN: float = 20.0
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
