from __future__ import annotations

from pathlib import Path

from intake_normalizer.models import NormalizedIntake, ServiceRequest


def load_requests(path: str | Path) -> list[ServiceRequest]:
    source = Path(path)
    return [
        ServiceRequest.model_validate_json(line, strict=True)
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_ground_truth(path: str | Path) -> list[NormalizedIntake]:
    source = Path(path)
    return [
        NormalizedIntake.model_validate_json(line, strict=True)
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
