"""Logging configuration.

Structured JSON logging for production.
Human-readable in development.
"""

import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import settings


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

        return json.dumps(log_entry, default=str)


def setup_logging() -> None:
    """Configure logging for the application."""
    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
