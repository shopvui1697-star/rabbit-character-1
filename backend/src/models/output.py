"""Structured output models for the voice assistant.

Every agent response conforms to VoiceBotOutput. Pydantic AI validates the LLM
output against this schema and retries on validation failure.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UIActionType(str, Enum):
    """Types of UI components the agent can command the frontend to render."""

    SHOW_MAP = "SHOW_MAP"
    SHOW_RESTAURANT_LIST = "SHOW_RESTAURANT_LIST"
    SHOW_RESTAURANT_DETAIL = "SHOW_RESTAURANT_DETAIL"
    SHOW_MUSIC_PLAYER = "SHOW_MUSIC_PLAYER"
    SHOW_PLAN_EDITOR = "SHOW_PLAN_EDITOR"
    SHOW_CONFIRMATION = "SHOW_CONFIRMATION"
    SHOW_REVIEWS = "SHOW_REVIEWS"
    SHOW_MOVIE_LIST = "SHOW_MOVIE_LIST"
    SHOW_MOVIE_DETAIL = "SHOW_MOVIE_DETAIL"
    SHOW_SUGGESTION_CHIPS = "SHOW_SUGGESTION_CHIPS"
    CLEAR_UI = "CLEAR_UI"
    SPLIT_VIEW = "SPLIT_VIEW"


class UIPriority(str, Enum):
    """Priority determines how the frontend lays out overlapping panels."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    OVERLAY = "overlay"


class UIAction(BaseModel):
    """A single UI command sent to the frontend."""

    action: UIActionType = Field(description="Which UI component to render.")
    priority: UIPriority = Field(
        default=UIPriority.PRIMARY,
        description="Layout priority: primary fills main area, secondary is sidebar, overlay floats.",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Payload for the UI component (markers, restaurant list, track info, etc.).",
    )


class ContextUpdate(BaseModel):
    """State changes the agent wants persisted in the session."""

    current_topic: str | None = Field(
        default=None, description="Active domain: gourmet, music, planning, reservation."
    )
    active_plan_id: str | None = Field(
        default=None, description="ID of the plan currently being built."
    )
    selected_restaurant_id: str | None = Field(
        default=None, description="ID of the restaurant the user is focused on."
    )
    selected_area: str | None = Field(
        default=None, description="Area the user is currently searching in."
    )
    user_preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Learned preferences (e.g. preferred cuisine, budget).",
    )


class VoiceBotOutput(BaseModel):
    """The unified output schema for all agent responses.

    The LLM MUST return JSON conforming to this schema. Pydantic AI validates
    and retries up to 3 times on failure.
    """

    voice_response: str = Field(
        description=(
            "Text for TTS to speak to the user. "
            "Keep concise — aim for 1-3 sentences. Use natural, conversational English."
        ),
    )
    ui_actions: list[UIAction] = Field(
        default_factory=list,
        description="UI components to render on the frontend. Can be empty for voice-only responses.",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Follow-up suggestion chips shown to the user. Max 4 items.",
    )
    follow_up_prompt: str | None = Field(
        default=None,
        description="Optional question to guide the conversation forward.",
    )
    context_update: ContextUpdate | None = Field(
        default=None,
        description="State changes to persist in the session for future turns.",
    )
