"""Application configuration via Pydantic Settings.

All configuration is loaded from environment variables.
No hardcoded values. No magic numbers.
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "exHacker"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./exhacker.db"

    # AI Providers — use litellm model names
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_MODEL_TIER_1: str = "gpt-4o-mini"       # Cheap — research queries, explanations
    AI_MODEL_TIER_2: str = "gpt-4o"            # Medium — directions, architecture reasoning
    AI_MODEL_TIER_3: str = "o3-mini"            # Expensive — complex analysis

    # Mock modes — no API keys needed for development
    MOCK_AI: bool = False                       # Use fake AI responses (no cost)
    MOCK_RESEARCH: bool = True                  # Use fake research data (no API calls)

    # Research
    TAVILY_API_KEY: str = ""
    SERPAPI_API_KEY: str = ""
    RESEARCH_CACHE_TTL_SECONDS: int = 86400  # 24 hours

    # Limits
    FREE_TIER_PROJECTS_PER_DAY: int = 3
    PRO_TIER_PROJECTS_PER_DAY: int = 50
    MAX_PROJECTS_PER_USER: int = 50
    MAX_COST_PER_PROJECT: float = 0.50       # $0.50 max AI spend per project

    # Caching
    CACHE_BACKEND: str = "memory"  # memory or redis
    REDIS_URL: str = ""

    # Auth (v2)
    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_GITHUB_CLIENT_ID: str = ""
    OAUTH_GITHUB_CLIENT_SECRET: str = ""
    SECRET_KEY: str = "change-me-in-production"

    # Feature flags
    FEATURE_PITCH_GENERATION: bool = False
    FEATURE_TEAM_COLLABORATION: bool = False
    FEATURE_EXPORT_PDF: bool = False

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"

    @property
    def database_url_async(self) -> str:
        """Return the async database URL.
        For SQLite, ensures aiosqlite driver is used.
        """
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        # For PostgreSQL, swap async driver
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
