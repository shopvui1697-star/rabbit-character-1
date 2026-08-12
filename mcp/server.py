"""MCP server for movie search — backed by rabbit3.data_archive_movie_master.

Phase 1: SQL text search (ILIKE / ts_vector full-text when available).
Phase 2: pgvector similarity search on an `embedding` column.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from db import get_pool, close_pool

logger = logging.getLogger(__name__)

mcp = FastMCP("rabbit3-movie")

TABLE = "data_archive_movie_master"

# ── Phase 1: SQL-based search ─────────────────────────────────────────────────


@mcp.tool()
async def search_movies(
    query: str,
    count: int = 10,
    page: int = 1,
) -> list[dict[str, Any]]:
    """Search movies in data_archive_movie_master.

    Args:
        query: Free-text search (matches title, original_title, overview).
        count: Max results per page (1–100).
        page:  Page number (1-based).
    """
    pool = await get_pool()
    count = max(1, min(count, 100))
    offset = (max(1, page) - 1) * count

    keywords = [kw.strip() for kw in query.split() if kw.strip()]
    if not keywords:
        return []

    where_clauses = []
    params: list[Any] = []
    for i, kw in enumerate(keywords, start=1):
        pattern = f"%{kw}%"
        where_clauses.append(
            f"(title ILIKE ${i} OR original_title ILIKE ${i} OR overview ILIKE ${i})"
        )
        params.append(pattern)

    where_sql = " AND ".join(where_clauses)
    next_param = len(params) + 1

    sql = f"""
        SELECT
            id,
            title,
            COALESCE(original_title, '') as original_title,
            COALESCE(overview, '') as overview,
            COALESCE(release_date, '') as release_date,
            COALESCE(poster_path, '') as poster_url,
            COALESCE(backdrop_path, '') as backdrop_url,
            COALESCE(source, '') as source,
            vote_average,
            COALESCE(vote_count, 0) as vote_count,
            COALESCE(genre_ids, '') as genre_ids,
            runtime
        FROM {TABLE}
        WHERE {where_sql}
        ORDER BY vote_count DESC NULLS LAST, id
        LIMIT ${next_param} OFFSET ${next_param + 1}
    """
    params.extend([count, offset])

    try:
        rows = await pool.fetch(sql, *params)
        result = [dict(row) for row in rows]
        logger.info(f"search_movies returning {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Database query error: {e}")
        return []


@mcp.tool()
async def get_movie_by_id(movie_id: int) -> dict[str, Any] | None:
    """Fetch a single movie by its ID.

    Args:
        movie_id: Primary key in data_archive_movie_master.
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        f"""
        SELECT
            id, title, original_title, overview, release_date,
            poster_path, backdrop_path, source,
            vote_average, vote_count, genre_ids, runtime
        FROM {TABLE}
        WHERE id = $1
        """,
        movie_id,
    )
    return dict(row) if row else None


@mcp.tool()
async def list_genres() -> list[dict[str, Any]]:
    """Return distinct genre_ids values used across all movies."""
    pool = await get_pool()
    rows = await pool.fetch(
        f"SELECT DISTINCT genre_ids FROM {TABLE} WHERE genre_ids IS NOT NULL ORDER BY genre_ids"
    )
    return [dict(row) for row in rows]


# ── Phase 2: Vector similarity search (Ollama embeddings) ────────────────────
# Uncomment after running migrations/002_add_vector.sql and populating embeddings
# with generate_embeddings.py
#
@mcp.tool()
async def search_movies_by_vector(
    query_embedding: list[float],
    count: int = 10,
) -> list[dict[str, Any]]:
    """Semantic similarity search using pgvector and Ollama embeddings.

    Args:
        query_embedding: Embedding vector from Ollama (768-dim for nomic-embed-text).
        count: Max results (default 10).

    Returns:
        List of movies sorted by similarity, with similarity score included.
    """
    pool = await get_pool()
    
    try:
        sql = f"""
            SELECT 
                id, title, original_title, overview, release_date,
                poster_url, backdrop_url, source_url,
                vote_average, vote_count, genre_ids, product_type, runtime,
                1 - (embedding <=> $1::vector) AS similarity
            FROM {TABLE}
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """
        rows = await pool.fetch(sql, query_embedding, count)
        result = [dict(row) for row in rows]
        logger.info(f"search_movies_by_vector returning {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []


if __name__ == "__main__":
    logger.info("Starting MCP server")
    mcp.run()
