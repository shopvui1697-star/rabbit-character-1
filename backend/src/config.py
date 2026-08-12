"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM — 9Router (default) or AWS Bedrock
    llm_provider: str = "9router"  # "9router" | "bedrock"
    openai_base_url: str = "http://localhost:20128/v1"
    openai_api_key: str = "9router"
    default_model: str = "Default"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # Services
    use_dummy_gourmet: bool = True  # If True, return dummy data
    # Lovvit OpenSearch APIs (restaurant only — movie search moved to MCP)
    lovvit_api_key: str = ""
    lovvit_restaurant_search_url: str = "https://stg.opensearch.lovvit.jp/api/v1/restaurant/search"

    # Movie MCP server (database connection — passed to MCP subprocess)
    movie_database_url: str = "postgresql://localhost:5432/rabbit3"

    # Observability
    logfire_token: str = ""

    # App
    environment: str = "development"
    log_level: str = "debug"


settings = Settings()
