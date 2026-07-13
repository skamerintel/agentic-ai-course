from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class FactCheck:
    label: str
    any_of: tuple[str, ...]


@dataclass(frozen=True)
class Incident:
    id: str
    report: str
    reference_summary: str
    fact_checks: tuple[FactCheck, ...]
    forbidden_claims: tuple[str, ...]
    tags: tuple[str, ...]


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    api: str
    model: str
    text: str
    latency_ms: float
    response_id: str | None
    input_tokens: int | None
    output_tokens: int | None
    output_types: tuple[str, ...]


@dataclass(frozen=True)
class Score:
    facts_found: tuple[str, ...]
    facts_missed: tuple[str, ...]
    forbidden_claims_found: tuple[str, ...]
    word_count: int

    @property
    def fact_recall(self) -> float:
        total = len(self.facts_found) + len(self.facts_missed)
        return len(self.facts_found) / total if total else 1.0


@dataclass(frozen=True)
class ExperimentRecord:
    incident_id: str
    result: ProviderResult
    score: Score

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["score"]["fact_recall"] = self.score.fact_recall
        return value
