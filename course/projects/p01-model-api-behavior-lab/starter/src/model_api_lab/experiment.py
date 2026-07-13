from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from model_api_lab.data import load_incidents
from model_api_lab.evaluate import aggregate, score_summary
from model_api_lab.models import ExperimentRecord, ProviderResult
from model_api_lab.normalize import (
    normalize_anthropic_messages,
    normalize_openai_chat,
    normalize_openai_responses,
)

Normalizer = Callable[[dict[str, Any], float], ProviderResult]

OFFLINE_PROVIDERS: tuple[tuple[str, Normalizer], ...] = (
    ("openai_responses.json", normalize_openai_responses),
    ("openai_chat.json", normalize_openai_chat),
    ("anthropic_messages.json", normalize_anthropic_messages),
)


def run_offline(
    data_path: str | Path, fixtures_dir: str | Path
) -> list[ExperimentRecord]:
    incidents = {item.id: item for item in load_incidents(data_path)}
    fixture_root = Path(fixtures_dir)
    records: list[ExperimentRecord] = []

    for filename, normalizer in OFFLINE_PROVIDERS:
        payloads = json.loads((fixture_root / filename).read_text(encoding="utf-8"))
        for incident_id, payload in payloads.items():
            incident = incidents[incident_id]
            result = normalizer(payload, 0.0)
            records.append(
                ExperimentRecord(
                    incident_id=incident_id,
                    result=result,
                    score=score_summary(incident, result.text),
                )
            )
    return records


def write_jsonl(records: list[ExperimentRecord], output: str | Path) -> None:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(json.dumps(record.as_dict(), sort_keys=True) for record in records)
    target.write_text(f"{body}\n" if body else "", encoding="utf-8")


def summarize(records: list[ExperimentRecord]) -> str:
    return json.dumps(aggregate(records), indent=2, sort_keys=True)
