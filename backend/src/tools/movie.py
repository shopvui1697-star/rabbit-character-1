"""Movie search client — backed by the rabbit3-movie MCP server.

Phase 1: SQL text search against data_archive_movie_master.
Phase 2: Vector similarity search (pgvector) via search_movies_by_vector tool.

The backend spawns the MCP server as a subprocess via stdio.
The MCP server owns the database connection — the backend never touches PostgreSQL directly.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.config import settings
from src.models.movie import Movie
from src.tracing import log_input, trace_step

logger = logging.getLogger(__name__)

# ─── Dummy data (fallback when MCP server is unavailable) ─────────────────────

DUMMY_MOVIES: list[Movie] = [
    Movie(
        id=1,
        title="Spirited Away",
        original_title="千と千尋の神隠し",
        overview="A young girl finds herself in a magical world of spirits and must work to free herself and her parents.",
        release_date="2001-07-20",
        poster_url="https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
        source_url="https://www.themoviedb.org/movie/129",
        vote_average=8.5,
        vote_count=14000,
        genre_ids="16,14",
        product_type="movie",
        runtime=125,
    ),
    Movie(
        id=2,
        title="Your Name",
        original_title="君の名は。",
        overview="Two teenagers share a profound, magical connection upon discovering they are swapping bodies.",
        release_date="2016-08-26",
        poster_url="https://image.tmdb.org/t/p/w500/q719jXXEhI1am6qdBIAbpZBecbg.jpg",
        source_url="https://www.themoviedb.org/movie/372058",
        vote_average=8.6,
        vote_count=9700,
        genre_ids="16,18,14",
        product_type="movie",
        runtime=106,
    ),
    Movie(
        id=3,
        title="Tokyo Story",
        original_title="東京物語",
        overview="An elderly couple visit their children and grandchildren in the city, but find them too busy to spend time with them.",
        release_date="1953-11-03",
        poster_url="https://image.tmdb.org/t/p/w500/sNFMpKmJxEOI4fWmfsYkd9laG6M.jpg",
        source_url="https://www.themoviedb.org/movie/18148",
        vote_average=8.2,
        vote_count=1300,
        genre_ids="18",
        product_type="movie",
        runtime=136,
    ),
]


def _row_to_movie(row: dict[str, Any]) -> Movie:
    """Convert a row dict from the MCP server response into a Movie model."""
    return Movie(
        id=row.get("id", 0),
        title=row.get("title", "") or "",
        original_title=row.get("original_title", "") or "",
        overview=row.get("overview", "") or "",
        release_date=str(row.get("release_date", "") or ""),
        poster_url=row.get("poster_url", "") or "",
        backdrop_url=row.get("backdrop_url", "") or "",
        source_url=row.get("source_url", "") or "",
        vote_average=row.get("vote_average"),
        vote_count=row.get("vote_count", 0) or 0,
        genre_ids=str(row.get("genre_ids", "") or ""),
        product_type=row.get("product_type", "") or "",
        runtime=row.get("runtime"),
    )


def _parse_mcp_result(result: Any) -> list[dict[str, Any]]:
    """Extract a list of dicts from MCP tool call result content blocks."""
    for block in result.content:
        if hasattr(block, "text"):
            text = block.text
            if not text or not text.strip():
                logger.warning("MCP returned empty text block")
                continue
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict):
                    return [parsed] if parsed else []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MCP response: {e}, text={text[:200]}")
                continue
    
    # If no text blocks, check if result itself is the data
    if hasattr(result, "content") and isinstance(result.content, list):
        # FastMCP might return the data directly
        return result.content if isinstance(result.content, list) else []
    
    return []


# ─── MCP server parameters ───────────────────────────────────────────────────

_MCP_DIR = str(Path(__file__).resolve().parents[3] / "mcp")

_MCP_SERVER = StdioServerParameters(
    command="python",
    args=["server.py"],
    cwd=_MCP_DIR,
    env={"MOVIE_DATABASE_URL": settings.movie_database_url},
)


class MovieClient:
    """Async client that spawns the rabbit3-movie MCP server as a subprocess."""

    async def search_movies(
        self,
        *,
        query: str,
        count: int = 10,
        page: int = 1,
    ) -> list[Movie]:
        """Search movies via MCP server → data_archive_movie_master.

        Falls back to dummy data if the MCP server is unreachable.
        """
        log_input("tool_search_movies", query)
        async with trace_step("tool_search_movies", source="mcp"):
            try:
                async with stdio_client(_MCP_SERVER) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.call_tool(
                            "search_movies",
                            arguments={
                                "query": query,
                                "count": min(count, 100),
                                "page": page,
                            },
                        )

                # Debug: log the raw result structure
                logger.debug(f"MCP result type: {type(result)}, content: {result.content if hasattr(result, 'content') else 'no content'}")
                
                items = _parse_mcp_result(result)
                if not items:
                    logger.info("MCP search returned 0 results for %r", query)
                    return []

                logger.debug(f"Parsed {len(items)} movies from MCP")
                return [_row_to_movie(item) for item in items[:count]]

            except Exception:
                logger.exception("MCP movie server error — falling back to dummy data")
                q = query.lower()
                matched = [
                    m
                    for m in DUMMY_MOVIES
                    if q in m.title.lower() or q in m.overview.lower()
                ]
                return matched or DUMMY_MOVIES[:count]

    async def get_movie(self, movie_id: int) -> Movie | None:
        """Fetch a single movie by ID via MCP server."""
        try:
            async with stdio_client(_MCP_SERVER) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "get_movie_by_id",
                        arguments={"movie_id": movie_id},
                    )

            items = _parse_mcp_result(result)
            if items:
                return _row_to_movie(items[0])
            return None

        except Exception:
            logger.exception("MCP get_movie error for id=%d", movie_id)
            return None
