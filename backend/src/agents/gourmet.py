"""Gourmet specialist agent — restaurant search and discovery.

Phase 1: Single agent that handles all gourmet queries using HotPepper API.
Phase 2: This becomes a specialist agent called by the coordinator.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent, RunContext

from src.agents.llm import chat_model
from src.models.output import VoiceBotOutput
from src.models.session import SessionDependencies

# Load system prompt from markdown file
_instructions_path = Path(__file__).parent / "instructions" / "gourmet.md"
_instructions = _instructions_path.read_text(encoding="utf-8")

gourmet_agent: Agent[SessionDependencies, VoiceBotOutput] = Agent(
    chat_model,
    output_type=VoiceBotOutput,
    deps_type=SessionDependencies,
    instructions=_instructions,
    retries=3,
)


# ─── Dynamic instructions ────────────────────────────────────────────────────


@gourmet_agent.instructions
def add_session_context(ctx: RunContext[SessionDependencies]) -> str:
    """Inject current session state into the system prompt."""
    state = ctx.deps.state
    parts: list[str] = []

    if state.selected_area:
        parts.append(f"The user is currently searching in area: {state.selected_area}")
    if state.preferred_cuisines:
        parts.append(f"User's preferred cuisines: {', '.join(state.preferred_cuisines)}")
    if state.budget_preference:
        parts.append(f"User's budget preference: {state.budget_preference}")
    if state.last_search_results:
        names = [r.get("name", "?") for r in state.last_search_results[:5]]
        parts.append(f"Previous search results (for reference): {', '.join(names)}")
    if state.selected_restaurant:
        parts.append(
            f"Currently selected restaurant: {state.selected_restaurant.get('name', state.selected_restaurant.get('id', '?'))}"
        )

    if parts:
        return "\n## Current Session Context\n" + "\n".join(f"- {p}" for p in parts)
    return ""


# ─── Tools ────────────────────────────────────────────────────────────────────


@gourmet_agent.tool
async def find_restaurants(
    ctx: RunContext[SessionDependencies],
    area_keyword: str | None = None,
    genre_keyword: str | None = None,
    budget_keyword: str | None = None,
    private_room: bool = False,
    card: bool = False,
    wifi: bool = False,
    count: int = 5,
) -> list[dict[str, str | float | bool | None]]:
    """Find restaurants in one call. Use natural language for area, genre, and budget.

    This tool does lookup + search internally — call it ONCE per search. Do NOT call
    lookup_genre, lookup_area, or search_restaurants separately for a search.

    Args:
        area_keyword: Area name (e.g. "渋谷", "新宿", "銀座", "Shibuya"). Use session
            selected_area if user said "here" or "same area". Default "渋谷" if omitted.
        genre_keyword: Cuisine/genre (e.g. "ラーメン", "寿司", "イタリアン", "ramen")
        budget_keyword: Budget hint (e.g. "3000", "安い", "〜5000円") or None
        private_room: Filter for private rooms.
        card: Filter for credit card accepted.
        wifi: Filter for WiFi.
        count: Number of results (1-10, default 5).
    """
    client = ctx.deps.hotpepper_client

    # Resolve area — use session, argument, or default
    area_to_use = area_keyword or ctx.deps.state.selected_area or "Shibuya"
    areas = await client.search_middle_areas(keyword=area_to_use)
    area_code = areas[0].code if areas else None

    # Lookup genre code (optional)
    genre_code = None
    if genre_keyword:
        genres = await client.search_genres(keyword=genre_keyword)
        genre_code = genres[0].code if genres else None

    # Lookup budget code (optional)
    budget_code = None
    if budget_keyword:
        budgets = await client.get_budget_master()
        kw = budget_keyword.lower()
        for b in budgets:
            if kw in (b.get("name", "") or "").lower() or kw in (b.get("average", "") or "").lower():
                budget_code = b.get("code")
                break
        if not budget_code and budgets:
            budget_code = budgets[0].get("code")

    # Single search call (pass keywords for Lovvit, codes for HotPepper/dummy)
    restaurants = await client.search_restaurants(
        middle_area=area_code,
        genre=genre_code,
        area_keyword=area_to_use,
        genre_keyword=genre_keyword,
        budget=budget_code,
        private_room=private_room,
        card=card,
        wifi=wifi,
        count=min(count, 10),
    )

    result_dicts = [r.model_dump() for r in restaurants]
    ctx.deps.state.last_search_results = result_dicts
    ctx.deps.state.selected_area = area_to_use
    return result_dicts


@gourmet_agent.tool
async def search_restaurants(
    ctx: RunContext[SessionDependencies],
    keyword: str | None = None,
    genre_code: str | None = None,
    area_code: str | None = None,
    budget_code: str | None = None,
    private_room: bool = False,
    card: bool = False,
    wifi: bool = False,
    lunch: bool = False,
    pet: bool = False,
    child: bool = False,
    parking: bool = False,
    free_drink: bool = False,
    free_food: bool = False,
    count: int = 5,
) -> list[dict[str, str | float | bool | None]]:
    """Low-level search by HotPepper codes. Prefer find_restaurants for user searches.

    Args:
        keyword: Free text search across restaurant names and descriptions (e.g. "sushi", "birthday")
        genre_code: HotPepper genre code (e.g. "G001"). Use lookup_genre to find codes.
        area_code: HotPepper area code (large/middle/small). Use lookup_area to find codes.
        budget_code: HotPepper budget code (e.g. "B003"). Use lookup_budget to find codes.
        private_room: Filter for restaurants with private rooms.
        card: Filter for restaurants accepting credit cards.
        wifi: Filter for WiFi availability.
        lunch: Filter for lunch service.
        pet: Filter for pet-friendly restaurants.
        child: Filter for child-friendly restaurants.
        parking: Filter for parking availability.
        free_drink: Filter for all-you-can-drink option.
        free_food: Filter for all-you-can-eat option.
        count: Number of results (1-10, default 5).
    """
    client = ctx.deps.hotpepper_client
    restaurants = await client.search_restaurants(
        keyword=keyword,
        genre=genre_code,
        middle_area=area_code,
        budget=budget_code,
        private_room=private_room,
        card=card,
        wifi=wifi,
        lunch=lunch,
        pet=pet,
        child=child,
        parking=parking,
        free_drink=free_drink,
        free_food=free_food,
        count=min(count, 10),
    )

    # Store results in session for follow-up references
    result_dicts = [r.model_dump() for r in restaurants]
    ctx.deps.state.last_search_results = result_dicts

    return result_dicts


@gourmet_agent.tool
async def get_restaurant_detail(
    ctx: RunContext[SessionDependencies],
    restaurant_id: str,
) -> dict[str, str | float | bool | None] | str:
    """Get detailed information about a specific restaurant by its HotPepper ID.

    Args:
        restaurant_id: The HotPepper store ID (e.g. "J001234567").
    """
    client = ctx.deps.hotpepper_client
    restaurant = await client.get_restaurant_by_id(restaurant_id)
    if restaurant is None:
        return f"No restaurant found with ID: {restaurant_id}"
    result = restaurant.model_dump()
    ctx.deps.state.selected_restaurant = result
    return result


@gourmet_agent.tool
async def search_by_location(
    ctx: RunContext[SessionDependencies],
    latitude: float,
    longitude: float,
    range_level: int = 3,
    genre_code: str | None = None,
    keyword: str | None = None,
    count: int = 5,
) -> list[dict[str, str | float | bool | None]]:
    """Search for restaurants near a geographic location.

    Args:
        latitude: Latitude of the search center point.
        longitude: Longitude of the search center point.
        range_level: Search radius: 1=300m, 2=500m, 3=1km, 4=2km, 5=3km.
        genre_code: Optional genre filter code (use lookup_genre to find codes).
        keyword: Optional keyword filter.
        count: Number of results (1-10, default 5).
    """
    client = ctx.deps.hotpepper_client
    restaurants = await client.search_restaurants(
        lat=latitude,
        lng=longitude,
        range_level=range_level,
        genre=genre_code,
        keyword=keyword,
        count=min(count, 10),
    )
    result_dicts = [r.model_dump() for r in restaurants]
    ctx.deps.state.last_search_results = result_dicts
    return result_dicts


@gourmet_agent.tool
async def lookup_genre(
    ctx: RunContext[SessionDependencies],
    keyword: str,
) -> list[dict[str, str]]:
    """Look up HotPepper genre codes by keyword.

    Always call this before searching by genre to get the correct code.

    Args:
        keyword: Genre/cuisine keyword (e.g. "イタリアン", "居酒屋", "寿司", "バー", "焼肉")
    """
    client = ctx.deps.hotpepper_client
    genres = await client.search_genres(keyword=keyword)
    return [{"code": g.code, "name": g.name} for g in genres]


@gourmet_agent.tool
async def lookup_area(
    ctx: RunContext[SessionDependencies],
    keyword: str,
) -> list[dict[str, str]]:
    """Look up HotPepper area codes by keyword.

    Always call this before searching by area to get the correct code.
    Returns middle-area codes which are the most useful for restaurant search.

    Args:
        keyword: Area name (e.g. "渋谷", "新宿", "銀座", "梅田", "博多")
    """
    client = ctx.deps.hotpepper_client
    areas = await client.search_middle_areas(keyword=keyword)
    return [{"code": a.code, "name": a.name} for a in areas]


@gourmet_agent.tool
async def lookup_budget(
    ctx: RunContext[SessionDependencies],
) -> list[dict[str, str]]:
    """Get the list of dinner budget codes and their ranges.

    Call this when the user mentions a budget preference to find the right code.
    """
    client = ctx.deps.hotpepper_client
    budgets = await client.get_budget_master()
    return [{"code": b.get("code", ""), "name": b.get("name", "")} for b in budgets]
