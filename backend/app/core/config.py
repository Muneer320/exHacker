from enum import StrEnum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    debug: bool = True

    app_name: str = "exHacker"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://exhacker:exhacker@localhost:5432/exhacker"
    database_sync_url: str = "postgresql+psycopg2://exhacker:exhacker@localhost:5432/exhacker"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4096

    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    agent_timeout_seconds: int = 120
    agent_max_retries: int = 2
    workflow_progress_poll_interval: float = 0.5

    upload_dir: Path = Path("uploads")
    export_dir: Path = Path("exports")

    sentry_dsn: str | None = None
    otlp_endpoint: str | None = None


settings = Settings()
