"""Explicit runtime settings; real providers by default, opt-in offline fixtures."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = Field(default=False, validation_alias="EXHACKER_DEBUG")
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite+aiosqlite:///./exhacker.db"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    STUDIO_DEMO_MODE: bool = False
    STUDIO_WORKER_ENABLED: bool = True
    STUDIO_JOB_LEASE_SECONDS: int = Field(default=300, ge=15, le=3600)
    STUDIO_IDEA_ROUNDS: int = Field(default=2, ge=1, le=3)
    STUDIO_CONTEXT_CHAR_LIMIT: int = Field(default=180000, ge=10000, le=500000)
    STUDIO_COST_LIMIT: float = Field(default=5.0, gt=0, le=100)
    STUDIO_SEARCH_LIMIT: int = Field(default=100, ge=1, le=1000)
    MAX_PROJECTS_PER_USER: int = Field(default=50, ge=1, le=1000)
    FREE_TIER_PROJECTS_PER_DAY: int = Field(default=3, ge=1, le=100)

    AI_MODEL: str = "openai/gpt-4o-mini"
    AI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_BASE_URL: str | None = None
    LITELLM_LOCAL_MODEL_COST_MAP: bool = True
    AI_TIMEOUT_SECONDS: int = Field(default=120, ge=10, le=300)
    AI_MAX_OUTPUT_TOKENS: int = Field(default=12000, ge=1000, le=32000)
    # Set these to rates for your configured provider/model. They include the
    # conservative reservation used to enforce per-project spending limits.
    AI_INPUT_USD_PER_MILLION: float = Field(default=3.0, gt=0)
    AI_OUTPUT_USD_PER_MILLION: float = Field(default=15.0, gt=0)
    TAVILY_API_KEY: str = ""

    @property
    def is_production(self):
        return self.ENV == "production"

    @property
    def database_url_async(self):
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        if self.DATABASE_URL.startswith("sqlite://"):
            return self.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return self.DATABASE_URL


settings = Settings()
