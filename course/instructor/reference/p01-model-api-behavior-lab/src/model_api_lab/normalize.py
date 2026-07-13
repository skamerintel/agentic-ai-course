from __future__ import annotations

from typing import Any

from model_api_lab.models import ProviderResult


def _integer(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def _text_or_error(parts: list[str], api: str) -> str:
    text = "\n".join(part.strip() for part in parts if part.strip()).strip()
    if not text:
        raise ValueError(f"{api} payload contains no supported text output")
    return text


def normalize_openai_responses(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    output = payload.get("output")
    items = output if isinstance(output, list) else []
    output_types: list[str] = []
    text_parts: list[str] = []

    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type", "unknown"))
        output_types.append(item_type)
        if item_type != "message":
            continue
        content = item.get("content")
        blocks = content if isinstance(content, list) else []
        for block in blocks:
            if not isinstance(block, dict) or block.get("type") != "output_text":
                continue
            text = block.get("text")
            if isinstance(text, str):
                text_parts.append(text)

    usage = payload.get("usage")
    usage_data = usage if isinstance(usage, dict) else {}
    return ProviderResult(
        provider="openai",
        api="responses",
        model=str(payload.get("model", "unknown")),
        text=_text_or_error(text_parts, "Responses"),
        latency_ms=latency_ms,
        response_id=str(payload["id"]) if payload.get("id") is not None else None,
        input_tokens=_integer(usage_data.get("input_tokens")),
        output_tokens=_integer(usage_data.get("output_tokens")),
        output_types=tuple(output_types),
    )


def normalize_openai_chat(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    choices = payload.get("choices")
    choice_items = choices if isinstance(choices, list) else []
    text_parts: list[str] = []

    for choice in choice_items:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, str):
            text_parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "text":
                    continue
                text = block.get("text")
                if isinstance(text, str):
                    text_parts.append(text)

    usage = payload.get("usage")
    usage_data = usage if isinstance(usage, dict) else {}
    return ProviderResult(
        provider="openai",
        api="chat_completions",
        model=str(payload.get("model", "unknown")),
        text=_text_or_error(text_parts, "Chat Completions"),
        latency_ms=latency_ms,
        response_id=str(payload["id"]) if payload.get("id") is not None else None,
        input_tokens=_integer(usage_data.get("prompt_tokens")),
        output_tokens=_integer(usage_data.get("completion_tokens")),
        output_types=("message",) if text_parts else (),
    )


def normalize_anthropic_messages(
    payload: dict[str, Any], latency_ms: float = 0.0
) -> ProviderResult:
    content = payload.get("content")
    blocks = content if isinstance(content, list) else []
    text_parts: list[str] = []
    output_types: list[str] = []

    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = str(block.get("type", "unknown"))
        output_types.append(block_type)
        if block_type != "text":
            continue
        text = block.get("text")
        if isinstance(text, str):
            text_parts.append(text)

    usage = payload.get("usage")
    usage_data = usage if isinstance(usage, dict) else {}
    return ProviderResult(
        provider="anthropic",
        api="messages",
        model=str(payload.get("model", "unknown")),
        text=_text_or_error(text_parts, "Messages"),
        latency_ms=latency_ms,
        response_id=str(payload["id"]) if payload.get("id") is not None else None,
        input_tokens=_integer(usage_data.get("input_tokens")),
        output_tokens=_integer(usage_data.get("output_tokens")),
        output_types=tuple(output_types),
    )
