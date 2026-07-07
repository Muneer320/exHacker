"""Application configuration via Pydantic Settings.

All configuration is loaded from environment variables.
No hardcoded values. No magic numbers.
"""

import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://exhacker-frontend.vercel.app",
        "https://exhacker-backend.vercel.app",
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./exhacker.db"

    # AI Providers — use litellm model names
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # SDPD model tiers (opencode-go provider — litellm-compatible API)
    AI_DEFAULT_PROVIDER: str = "opencode-go"
    AI_MODEL_TIER_1: str = "deepseek-v4-flash"  # Cheap tier
    AI_MODEL_TIER_2: str = "glm-5.2"  # Medium tier
    AI_MODEL_TIER_3: str = "glm-5.2"  # Expensive (upgrade to opus later)

    # AI retry / timeout configuration
    MAX_RETRIES: int = 2
    RETRY_BASE_DELAY: float = 1.0
    AI_TIMEOUT_SECONDS: int = 60

    # Cost tracking
    TRACK_COSTS: bool = True
    COST_LIMIT_PER_PROJECT: float = 0.50        # $0.50 max AI spend per project

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
    MAX_COST_PER_PROJECT: float = 0.50  # Legacy alias

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
