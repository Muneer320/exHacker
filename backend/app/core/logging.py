"""Logging configuration.

Structured JSON logging for production.
Human-readable in development.
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone

from app.core.config import settings


def redact(text):
    from app.studio.credentials import leases

    for entry in tuple(leases._entries.values()):
        secret = entry.secret.get_secret_value()
        if secret:
            text = text.replace(secret, "[REDACTED]")
    for secret in (
        settings.AI_API_KEY,
        settings.OPENAI_API_KEY,
        settings.ANTHROPIC_API_KEY,
        settings.TAVILY_API_KEY,
    ):
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return re.sub(
        r"\b(?:sk-[A-Za-z0-9_-]{12,}|gsk_[A-Za-z0-9_-]{12,}|xai-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{20,})",
        "[REDACTED]",
        text,
    )


class PrivateFormatter(logging.Formatter):
    def format(self, record):
        return redact(super().format(record))


class StructuredFormatter(logging.Formatter):
    """Format logs as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "props"):
            log_entry["props"] = record.props  # type: ignore[attr-defined]

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return redact(json.dumps(log_entry, default=str))


def setup_logging() -> None:
    """Configure logging for the application."""
    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            PrivateFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
