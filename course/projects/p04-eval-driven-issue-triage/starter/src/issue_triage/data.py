from __future__ import annotations

import hashlib
from pathlib import Path

from pydantic import BaseModel

from issue_triage.models import (
    GroundTruth,
    Issue,
    KnownIssue,
    RetrievalQuery,
    TriagePrediction,
)


def load_jsonl[ModelT: BaseModel](
    path: str | Path, model: type[ModelT]
) -> list[ModelT]:
    source = Path(path)
    return [
        model.model_validate_json(line, strict=True)
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_issues(path: str | Path) -> list[Issue]:
    return load_jsonl(path, Issue)


def load_truth(path: str | Path) -> list[GroundTruth]:
    return load_jsonl(path, GroundTruth)


def load_predictions(path: str | Path) -> list[TriagePrediction]:
    return load_jsonl(path, TriagePrediction)


def load_known_issues(path: str | Path) -> list[KnownIssue]:
    return load_jsonl(path, KnownIssue)


def load_retrieval_queries(path: str | Path) -> list[RetrievalQuery]:
    return load_jsonl(path, RetrievalQuery)


def fingerprint_files(*paths: str | Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((Path(value) for value in paths), key=lambda item: str(item)):
        digest.update(str(path.name).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
