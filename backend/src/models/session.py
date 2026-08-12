"""Session state and dependency injection models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.tools.hotpepper import HotPepperClient
    from src.tools.movie import MovieClient


@dataclass
class SessionState:
    """Mutable state that persists across turns within a conversation."""

    session_id: str
    user_id: str | None = None

    # Conversation
    turn_count: int = 0

    # Domain context
    current_topic: str | None = None
    active_plan: dict[str, Any] | None = None
    last_search_results: list[dict[str, Any]] = field(default_factory=list)
    selected_restaurant: dict[str, Any] | None = None
    selected_area: str | None = None

    # User preferences (learned over time)
    preferred_area: str | None = None
    preferred_cuisines: list[str] = field(default_factory=list)
    budget_preference: str | None = None

    def apply_context_update(self, update: dict[str, Any]) -> None:
        """Apply a context_update from VoiceBotOutput to the session state."""
        if "current_topic" in update and update["current_topic"] is not None:
            self.current_topic = update["current_topic"]
        if "selected_restaurant_id" in update and update["selected_restaurant_id"] is not None:
            self.selected_restaurant = {"id": update["selected_restaurant_id"]}
        if "selected_area" in update and update["selected_area"] is not None:
            self.selected_area = update["selected_area"]
        if "active_plan_id" in update and update["active_plan_id"] is not None:
            if self.active_plan is None:
                self.active_plan = {}
            self.active_plan["id"] = update["active_plan_id"]
        if "user_preferences" in update:
            for k, v in update["user_preferences"].items():
                if k == "preferred_area":
                    self.preferred_area = v
                elif k == "budget":
                    self.budget_preference = v


@dataclass
class SessionDependencies:
    """Injected into every agent run via Pydantic AI's dependency system."""

    state: SessionState
    hotpepper_client: HotPepperClient
    movie_client: MovieClient | None = None
