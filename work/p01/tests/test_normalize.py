import json
from pathlib import Path

import pytest

from model_api_lab.normalize import normalize_anthropic_messages


def load_fixture(name: str, incident_id: str) -> dict:
    payloads = json.loads(Path("fixtures", name).read_text(encoding="utf-8"))
    return payloads[incident_id]


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
        (
            normalize_anthropic_messages,
            {"id": "x", "model": "m", "content": []},
        ),
    ],
)
def test_missing_text_is_explicit(normalizer, payload) -> None:
    with pytest.raises(ValueError, match="text"):
        normalizer(payload)
