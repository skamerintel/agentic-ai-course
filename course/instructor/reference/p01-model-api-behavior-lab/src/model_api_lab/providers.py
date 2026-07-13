from __future__ import annotations

from time import perf_counter
from typing import Any

from model_api_lab.models import Incident, ProviderResult
from model_api_lab.normalize import (
    normalize_anthropic_messages,
    normalize_openai_chat,
    normalize_openai_responses,
)
from model_api_lab.prompting import SYSTEM_INSTRUCTIONS, user_prompt


def _payload(value: Any) -> dict[str, Any]:
    dumped = value.model_dump(mode="json")
    if not isinstance(dumped, dict):
        raise TypeError("provider response did not serialize to an object")
    return dumped


def call_openai_responses(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    from openai import OpenAI

    client = OpenAI(timeout=timeout_seconds)
    started = perf_counter()
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=user_prompt(incident),
    )
    latency_ms = (perf_counter() - started) * 1000
    return normalize_openai_responses(_payload(response), latency_ms)


def call_openai_chat(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    from openai import OpenAI

    client = OpenAI(timeout=timeout_seconds)
    started = perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_prompt(incident)},
        ],
    )
    latency_ms = (perf_counter() - started) * 1000
    return normalize_openai_chat(_payload(response), latency_ms)


def call_anthropic_messages(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    from anthropic import Anthropic

    client = Anthropic(timeout=timeout_seconds)
    started = perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=240,
        system=SYSTEM_INSTRUCTIONS,
        messages=[{"role": "user", "content": user_prompt(incident)}],
    )
    latency_ms = (perf_counter() - started) * 1000
    return normalize_anthropic_messages(_payload(response), latency_ms)
