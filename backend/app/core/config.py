from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = True

    app_name: str = "exHacker"
    app_version: str = "2.0.0"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://exhacker:exhacker@localhost:5432/exhacker"
    database_sync_url: str = "postgresql+psycopg2://exhacker:exhacker@localhost:5432/exhacker"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20

    llm_provider: str = "auto"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4096

    cors_origins: str = '["http://localhost:3000"]'

    agent_timeout_seconds: int = 120
    agent_max_retries: int = 2

    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


settings = Settings()
