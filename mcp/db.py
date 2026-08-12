"""PostgreSQL connection pool for rabbit3 database."""

from __future__ import annotations

import os
import logging

import asyncpg

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


def _dsn() -> str:
    return os.environ.get(
        "MOVIE_DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/rabbit3",
    )


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None or _pool._closed:
        logger.info("Connecting to %s", _dsn())
        _pool = await asyncpg.create_pool(_dsn(), min_size=1, max_size=5)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
