import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "exHacker"
    DATABASE_URL: str = "sqlite+aiosqlite:///./exhacker.db"

    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_HOST: str = "http://localhost:11434"

    MOCK_RESEARCH: bool = True
    SEARCH_API_KEY: str = ""

    @property
    def groq_api_keys(self) -> List[str]:
        """Returns a list of parsed Groq API keys (split by comma if multiple key rotation is set)."""
        if not self.GROQ_API_KEY:
            return []
        return [key.strip() for key in self.GROQ_API_KEY.split(",") if key.strip()]


settings = Settings()
