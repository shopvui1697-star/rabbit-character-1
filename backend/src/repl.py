"""Interactive text REPL for testing the Rabbit3 agent.

Usage:
    cd backend
    python -m src.repl

This provides a terminal-based conversation loop with the gourmet agent.
The agent returns structured VoiceBotOutput JSON, which the REPL renders
in a human-readable format.
"""

from __future__ import annotations

import asyncio
import json
import sys
import uuid

from src.agents.coordinator import route_and_run
from src.models.output import VoiceBotOutput
from src.models.session import SessionDependencies, SessionState
from src.observability import setup_observability
from src.tools.hotpepper import HotPepperClient
from src.tools.movie import MovieClient

# ANSI colors for terminal output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_output(output: VoiceBotOutput) -> None:
    """Pretty-print a VoiceBotOutput to the terminal."""
    # Voice response
    print(f"\n{GREEN}{BOLD}Voice:{RESET} {GREEN}\"{output.voice_response}\"{RESET}")

    # UI Actions
    if output.ui_actions:
        print(f"\n{YELLOW}UI Actions:{RESET}")
        for i, action in enumerate(output.ui_actions, 1):
            data_summary = _summarize_data(action.action.value, action.data)
            print(f"  {YELLOW}[{i}]{RESET} {action.action.value}: {data_summary}")

    # Suggestions
    if output.suggestions:
        chips = " | ".join(f"[{s}]" for s in output.suggestions)
        print(f"\n{CYAN}Suggestions:{RESET} {chips}")

    # Follow-up prompt
    if output.follow_up_prompt:
        print(f"\n{DIM}Follow-up: {output.follow_up_prompt}{RESET}")

    # Context update (debug)
    if output.context_update:
        update_dict = output.context_update.model_dump(exclude_none=True)
        if update_dict:
            print(f"\n{DIM}Context update: {json.dumps(update_dict, ensure_ascii=False)}{RESET}")


def _summarize_data(action_type: str, data: dict) -> str:
    """Create a brief summary of UI action data."""
    if action_type == "SHOW_RESTAURANT_LIST":
        restaurants = data.get("restaurants", [])
        if restaurants:
            names = [r.get("name", "?") for r in restaurants[:3]]
            total = len(restaurants)
            suffix = f" (+{total - 3} more)" if total > 3 else ""
            return f"{total} restaurants: {', '.join(names)}{suffix}"
        return "empty list"

    if action_type == "SHOW_MOVIE_LIST":
        movies = data.get("movies", [])
        if movies:
            titles = [m.get("title", "?") for m in movies[:3]]
            total = len(movies)
            suffix = f" (+{total - 3} more)" if total > 3 else ""
            return f"{total} movies: {', '.join(titles)}{suffix}"
        return "empty list"

    if action_type == "SHOW_MOVIE_DETAIL":
        return data.get("title", data.get("id", "details"))

    if action_type == "SHOW_MAP":
        markers = data.get("markers", [])
        return f"{len(markers)} markers"

    if action_type == "SHOW_RESTAURANT_DETAIL":
        return data.get("name", data.get("id", "details"))

    # Generic fallback
    if data:
        keys = list(data.keys())[:3]
        return f"{{ {', '.join(keys)} }}"
    return "{}"


async def run_repl() -> None:
    """Main REPL loop."""
    setup_observability()
    print(f"\n{BOLD}🐇 Rabbit3 Text Agent (Phase 1){RESET}")
    print(f"{DIM}Type 'quit' or 'exit' to leave. Type 'state' to see session state.{RESET}")
    print(f"{DIM}Type 'clear' to reset session.{RESET}\n")

    session_id = str(uuid.uuid4())[:8]
    state = SessionState(session_id=session_id)
    hotpepper_client = HotPepperClient()
    movie_client = MovieClient()

    # Conversation history for multi-turn
    message_history: list[dict[str, str]] = []

    try:
        while True:
            try:
                user_input = input(f"{BOLD}You:{RESET} ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGoodbye! 👋")
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit"):
                print("\nGoodbye! 👋")
                break

            if user_input.lower() == "state":
                _print_state(state)
                continue

            if user_input.lower() == "clear":
                state = SessionState(session_id=str(uuid.uuid4())[:8])
                message_history.clear()
                print(f"{DIM}Session cleared.{RESET}\n")
                continue

            # Build dependencies
            deps = SessionDependencies(
                state=state,
                hotpepper_client=hotpepper_client,
                movie_client=movie_client,
            )

            print(f"\n{DIM}Agent thinking...{RESET}")

            try:
                output, message_history, domain = await route_and_run(  # type: ignore[assignment]
                    user_input,
                    deps=deps,
                    message_history=message_history,  # type: ignore[arg-type]
                )
                print(f"{DIM}[routed → {domain}]{RESET}")
                print_output(output)

                # Apply context update to session state
                if output.context_update:
                    state.apply_context_update(
                        output.context_update.model_dump(exclude_none=True)
                    )

                state.turn_count += 1

            except Exception as e:
                print(f"\n{BOLD}\033[91mError:{RESET} {e}")
                if "--debug" in sys.argv:
                    import traceback

                    traceback.print_exc()

            print()  # Blank line between turns

    finally:
        await hotpepper_client.close()
        await movie_client.close()


def _print_state(state: SessionState) -> None:
    """Print current session state for debugging."""
    print(f"\n{DIM}━━━ Session State ━━━")
    print(f"  session_id: {state.session_id}")
    print(f"  turn_count: {state.turn_count}")
    print(f"  current_topic: {state.current_topic}")
    print(f"  selected_area: {state.selected_area}")
    print(f"  selected_restaurant: {state.selected_restaurant}")
    print(f"  last_search_results: {len(state.last_search_results)} items")
    print(f"  preferred_cuisines: {state.preferred_cuisines}")
    print(f"  budget_preference: {state.budget_preference}")
    print(f"━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def main() -> None:
    asyncio.run(run_repl())


if __name__ == "__main__":
    main()
