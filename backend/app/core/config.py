from enum import StrEnum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str:
    """Search for .env in CWD, the dir of this file's grandparent*4, or the
    project root so that pydantic-settings always finds it regardless of CWD."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",  # <project>/.env
        Path(__file__).resolve().parent.parent.parent / ".env",         # backend/.env
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return ".env"


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
        env_file=_find_env_file(),
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

    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    llm_provider: str = "auto"

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
