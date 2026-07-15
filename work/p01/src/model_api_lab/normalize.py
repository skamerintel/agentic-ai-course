from __future__ import annotations

from typing import Any

from model_api_lab.models import ProviderResult


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
