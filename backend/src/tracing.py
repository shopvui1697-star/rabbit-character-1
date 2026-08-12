"""Step execution timing — writes to logs/ when LOG_LEVEL=debug.

Usage:
    with trace_step("route_and_run", session_id="abc"):
        await route_and_run(...)

When LOG_LEVEL is "debug", each completed step is logged to
logs/trace_YYYYMMDD.log with duration in milliseconds.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path

from src.config import settings

logger = logging.getLogger(__name__)

_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def _is_debug() -> bool:
    return settings.log_level.lower() == "debug"


def _ensure_logs_dir() -> Path:
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return _LOGS_DIR


def log_input(step: str, input_text: str) -> None:
    """Append input marker: ======{input}======= for each process (when LOG_LEVEL=debug)."""
    if not _is_debug():
        return
    try:
        logs_dir = _ensure_logs_dir()
        today = datetime.utcnow().strftime("%Y%m%d")
        path = logs_dir / f"trace_{today}.log"
        sanitized = str(input_text).replace("\n", " ").strip()[:500]
        line = f"======[{step}] {sanitized}=======\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.warning("Failed to write trace input: %s", e)


def log_step(step: str, duration_ms: float, **extra: str) -> None:
    """Write one trace line to the daily log file (when LOG_LEVEL=debug)."""
    if not _is_debug():
        return
    try:
        logs_dir = _ensure_logs_dir()
        today = datetime.utcnow().strftime("%Y%m%d")
        path = logs_dir / f"trace_{today}.log"
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        extra_str = ""
        if extra:
            parts = [f"{k}={v}" for k, v in extra.items()]
            extra_str = " " + " ".join(parts)
        line = f"{ts} [{step}] {duration_ms:.2f}ms{extra_str}\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.warning("Failed to write trace log: %s", e)


@asynccontextmanager
async def trace_step(step: str, **extra: str):
    """Context manager that logs step duration when debug mode is on.

    Example:
        async with trace_step("route_and_run", session_id="abc", domain="gourmet"):
            output, _, domain = await route_and_run(...)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_step(step, elapsed_ms, **extra)


@contextmanager
def trace_step_sync(step: str, **extra: str):
    """Sync context manager for non-async steps."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_step(step, elapsed_ms, **extra)
