from __future__ import annotations

from typing import Any

from model_api_lab.models import ProviderResult


def normalize_openai_responses(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    """Normalize an OpenAI Responses payload.

    Inspect typed output items. Do not assume output[0] is a text message.
    """
    raise NotImplementedError("implement Responses normalization")


def normalize_openai_chat(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    """Normalize an OpenAI Chat Completions payload."""
    raise NotImplementedError("implement Chat Completions normalization")


def normalize_anthropic_messages(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    """Normalize an Anthropic Messages payload by content-block type."""
    raise NotImplementedError("implement Messages normalization")
