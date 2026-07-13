from __future__ import annotations

from model_api_lab.models import Incident, ProviderResult


def call_openai_responses(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    """Call OpenAI Responses. Import the SDK inside this function."""
    raise NotImplementedError("implement the live Responses adapter")


def call_openai_chat(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    """Call OpenAI Chat Completions. Import the SDK inside this function."""
    raise NotImplementedError("implement the live Chat Completions adapter")


def call_anthropic_messages(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    """Call Anthropic Messages. Import the SDK inside this function."""
    raise NotImplementedError("implement the live Messages adapter")
