from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from model_api_lab.models import FactCheck, Incident


def _incident_from_dict(value: dict[str, Any]) -> Incident:
    return Incident(
        id=str(value["id"]),
        report=str(value["report"]),
        reference_summary=str(value["reference_summary"]),
        fact_checks=tuple(
            FactCheck(
                label=str(check["label"]),
                any_of=tuple(str(phrase) for phrase in check["any_of"]),
            )
            for check in value["fact_checks"]
        ),
        forbidden_claims=tuple(str(item) for item in value["forbidden_claims"]),
        tags=tuple(str(item) for item in value["tags"]),
    )


def load_incidents(path: str | Path) -> list[Incident]:
    source = Path(path)
    incidents: list[Incident] = []
    lines = source.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number} of {source}") from exc
        incidents.append(_incident_from_dict(value))
    return incidents
