from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from release_workflow.models import (
    NotesReview,
    PolicyRules,
    ReleaseManifest,
    RepositorySnapshot,
)


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_jsonl[ModelT: BaseModel](
    path: str | Path, model: type[ModelT]
) -> list[ModelT]:
    return [
        model.model_validate_json(line, strict=True)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_manifests(path: str | Path) -> dict[str, ReleaseManifest]:
    return {item.release_id: item for item in load_jsonl(path, ReleaseManifest)}


def load_snapshots(path: str | Path) -> dict[str, RepositorySnapshot]:
    payload = load_json(path)
    return {
        key: RepositorySnapshot.model_validate(value, strict=True)
        for key, value in payload.items()
    }


def load_policy(path: str | Path) -> PolicyRules:
    return PolicyRules.model_validate(load_json(path), strict=True)


def load_notes_reviews(path: str | Path) -> dict[str, NotesReview]:
    payload = load_json(path)
    return {
        key: NotesReview.model_validate(value, strict=True)
        for key, value in payload.items()
    }
