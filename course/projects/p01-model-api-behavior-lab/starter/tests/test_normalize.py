import json
from pathlib import Path

import pytest

from model_api_lab.normalize import (
    normalize_anthropic_messages,
    normalize_openai_chat,
    normalize_openai_responses,
)


def load_fixture(name: str, incident_id: str) -> dict:
    payloads = json.loads(Path("fixtures", name).read_text(encoding="utf-8"))
    return payloads[incident_id]


def test_responses_skips_non_message_items_and_preserves_usage() -> None:
    result = normalize_openai_responses(
        load_fixture("openai_responses.json", "INC-001"), 12.5
    )

    assert result.provider == "openai"
    assert result.api == "responses"
    assert result.response_id == "resp_fixture_001"
    assert result.input_tokens == 126
    assert result.output_tokens == 52
    assert result.output_types == ("reasoning", "message")
    assert "Redis memory exhaustion" in result.text
    assert result.latency_ms == 12.5


def test_chat_extracts_message_content() -> None:
    result = normalize_openai_chat(load_fixture("openai_chat.json", "INC-002"))

    assert result.provider == "openai"
    assert result.api == "chat_completions"
    assert result.response_id == "chatcmpl_fixture_002"
    assert result.input_tokens == 114
    assert "06:18 CT" in result.text


def test_anthropic_joins_all_text_blocks() -> None:
    result = normalize_anthropic_messages(
        load_fixture("anthropic_messages.json", "INC-003")
    )

    assert result.provider == "anthropic"
    assert result.api == "messages"
    assert result.output_types == ("text", "text")
    assert "root cause remains unconfirmed" in result.text
    assert "iOS" in result.text


@pytest.mark.parametrize(
    ("normalizer", "payload"),
    [
        (normalize_openai_responses, {"id": "x", "model": "m", "output": []}),
        (
            normalize_openai_chat,
            {"id": "x", "model": "m", "choices": []},
        ),
        (
            normalize_anthropic_messages,
            {"id": "x", "model": "m", "content": []},
        ),
    ],
)
def test_missing_text_is_explicit(normalizer, payload) -> None:
    with pytest.raises(ValueError, match="text"):
        normalizer(payload)
