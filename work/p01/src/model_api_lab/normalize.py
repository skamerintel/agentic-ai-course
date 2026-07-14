from __future__ import annotations

from typing import Any

from model_api_lab.models import ProviderResult


def normalize_openai_responses(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    """Normalize an OpenAI Responses payload.

    Inspect typed output items. Do not assume output[0] is a text message.
    """
    output = payload["output"]
    output_types = tuple(item["type"] for item in output)

    texts = [
        block["text"]
        for item in output
        if item["type"] == "message"
        for block in item["content"]
        if block["type"] == "output_text"
    ]
    if not texts:
        raise ValueError("no text found in Responses output")

    usage = payload.get("usage", {})
    return ProviderResult(
        provider="openai",
        api="responses",
        model=payload["model"],
        text="".join(texts),
        latency_ms=latency_ms,
        response_id=payload["id"],
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        output_types=output_types,
    )


def normalize_openai_chat(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    """Normalize an OpenAI Chat Completions payload."""
    choices = payload["choices"]
    if not choices:
        raise ValueError("no text found in Chat Completions choices")

    text = choices[0]["message"]["content"]
    usage = payload.get("usage", {})
    return ProviderResult(
        provider="openai",
        api="chat_completions",
        model=payload["model"],
        text=text,
        latency_ms=latency_ms,
        response_id=payload["id"],
        input_tokens=usage.get("prompt_tokens"),
        output_tokens=usage.get("completion_tokens"),
        output_types=(),
    )


def normalize_anthropic_messages(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    """Normalize an Anthropic Messages payload by content-block type."""
    content = payload["content"]
    output_types = tuple(block["type"] for block in content)

    texts = [block["text"] for block in content if block["type"] == "text"]
    if not texts:
        raise ValueError("no text found in Messages content")

    usage = payload.get("usage", {})
    return ProviderResult(
        provider="anthropic",
        api="messages",
        model=payload["model"],
        text="".join(texts),
        latency_ms=latency_ms,
        response_id=payload["id"],
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        output_types=output_types,
    )
