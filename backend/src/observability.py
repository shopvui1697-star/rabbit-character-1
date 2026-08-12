"""Observability setup using Pydantic Logfire.

Call `setup_observability()` once at startup to instrument all agents and HTTP calls.
If LOGFIRE_TOKEN is not set, observability is silently disabled.
"""

from __future__ import annotations

import logging

from src.config import settings

logger = logging.getLogger(__name__)


def setup_observability() -> None:
    """Initialize Logfire tracing for Pydantic AI agents and HTTP clients."""
    if not settings.logfire_token:
        logger.info("LOGFIRE_TOKEN not set — observability disabled.")
        return

    try:
        import logfire

        logfire.configure(token=settings.logfire_token)
        logfire.instrument_pydantic_ai()
        logfire.instrument_httpx()
        logger.info("Logfire observability enabled.")
    except ImportError:
        logger.warning("logfire package not installed — observability disabled.")
    except Exception as e:
        logger.warning("Failed to configure Logfire: %s", e)
