"""Allowlisted JSON request metadata with no message/payload interpolation."""

import json
import logging


class JsonFormatter(logging.Formatter):
    """Serialize only fixed safe request fields."""

    def format(self, record: logging.LogRecord) -> str:
        """Discard arbitrary messages, exception details and extra fields."""
        fields = {
            key: getattr(record, key, None)
            for key in (
                "request_id",
                "method",
                "route",
                "status",
                "duration_ms",
            )
        }
        return json.dumps(
            {"event": "http_request", "level": record.levelname, **fields}
        )


def configure_logging() -> logging.Logger:
    """Configure the application request logger without duplicate handlers."""
    logger = logging.getLogger("fastapi_app.requests")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
