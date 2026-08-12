"""Shared LLM model factory — 9Router (OpenAI-compatible) or AWS Bedrock."""

from __future__ import annotations

import os

from pydantic_ai.models import Model
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_ai.providers.openai import OpenAIProvider

from src.config import settings


def get_chat_model() -> Model:
    """Return the configured chat model for all agents."""
    if settings.llm_provider == "bedrock":
        os.environ.setdefault("AWS_ACCESS_KEY_ID", settings.aws_access_key_id)
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", settings.aws_secret_access_key)
        os.environ.setdefault("AWS_REGION", settings.aws_region)

        model_name = settings.default_model.removeprefix("bedrock:")
        return BedrockConverseModel(
            model_name=model_name,
            provider=BedrockProvider(region_name=settings.aws_region),
        )

    model_name = settings.default_model.removeprefix("openai:")
    return OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
        ),
    )


chat_model = get_chat_model()
