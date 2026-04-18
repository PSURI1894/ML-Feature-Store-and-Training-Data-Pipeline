"""Structured logging via structlog.

JSON in prod (machine-parseable for the log platform), pretty console locally.
Bind ``feature_view`` / ``entity`` / ``request_id`` once and every downstream log
line carries them — essential for debugging point-in-time and serving issues.
"""

from __future__ import annotations

import logging
import sys

import structlog

from feature_platform.common.config import get_settings

_CONFIGURED = False


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    settings = get_settings()

    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=settings.log_level.upper()
    )

    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    processors.append(
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    configure_logging()
    return structlog.get_logger(name)
