"""Movie specialist agent — movie search and discovery via Lovvit API.

This agent handles all movie-related queries: searching for movies by title,
genre, keyword, etc.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent, RunContext

from src.agents.llm import chat_model
from src.models.output import VoiceBotOutput
from src.models.session import SessionDependencies

# Load system prompt from markdown file
_instructions_path = Path(__file__).parent / "instructions" / "movie.md"
_instructions = _instructions_path.read_text(encoding="utf-8")

movie_agent: Agent[SessionDependencies, VoiceBotOutput] = Agent(
    chat_model,
    output_type=VoiceBotOutput,
    deps_type=SessionDependencies,
    instructions=_instructions,
    retries=3,
)


# ─── Dynamic instructions ────────────────────────────────────────────────────


@movie_agent.instructions
def add_session_context(ctx: RunContext[SessionDependencies]) -> str:
    """Inject current session state into the system prompt."""
    state = ctx.deps.state
    parts: list[str] = []

    if state.current_topic:
        parts.append(f"Current topic: {state.current_topic}")
    if state.last_search_results:
        titles = [r.get("title", "?") for r in state.last_search_results[:5]]
        parts.append(f"Previous search results: {', '.join(titles)}")

    if parts:
        return "\n## Current Session Context\n" + "\n".join(f"- {p}" for p in parts)
    return ""


# ─── Tools ────────────────────────────────────────────────────────────────────


@movie_agent.tool
async def find_movies(
    ctx: RunContext[SessionDependencies],
    query: str,
    count: int = 5,
    page: int = 1,
) -> list[dict]:
    """Search for movies in the movie database (data_archive_movie_master).

    Call this tool ONCE per search. Combine keywords for best results.

    Args:
        query: Natural language search (e.g. "tokyo action", "comedy 2024",
               "horror japanese", "スタジオジブリ", "marvel"). Mix language freely.
        count: Number of results to return (1-10, default 5).
        page: Page number for pagination (default 1).
    """
    client = ctx.deps.movie_client
    movies = await client.search_movies(
        query=query,
        count=min(count, 10),
        page=page,
    )

    result_dicts = [m.model_dump() for m in movies]
    ctx.deps.state.last_search_results = result_dicts
    ctx.deps.state.current_topic = "movie"
    return result_dicts
