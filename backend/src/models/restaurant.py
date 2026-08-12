"""Restaurant-related models for the Gourmet domain."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    """A restaurant result from the HotPepper API."""

    id: str = Field(description="HotPepper store ID (e.g. J001234567)")
    name: str
    address: str = ""
    lat: float | None = None
    lng: float | None = None
    genre: str = ""
    sub_genre: str = ""
    budget: str = ""
    budget_average: str = ""
    open_hours: str = ""
    close: str = ""
    access: str = ""
    photo_url: str = ""
    url: str = ""
    private_room: bool = False
    card_accepted: bool = False
    wifi: bool = False
    parking: bool = False
    pet_friendly: bool = False
    child_friendly: bool = False


class Genre(BaseModel):
    """A genre/cuisine category from HotPepper."""

    code: str
    name: str


class Area(BaseModel):
    """An area/location from HotPepper."""

    code: str
    name: str
