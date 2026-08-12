"""Movie-related models for the Movie domain."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Movie(BaseModel):
    """A movie result from the Lovvit OpenSearch API."""

    id: int = Field(description="Lovvit movie ID")
    title: str = ""
    original_title: str = ""
    overview: str = ""
    release_date: str = ""
    poster_url: str = ""
    backdrop_url: str = ""
    source_url: str = ""
    vote_average: float | None = None
    vote_count: int = 0
    genre_ids: str = ""
    product_type: str = ""
    runtime: int | None = None
