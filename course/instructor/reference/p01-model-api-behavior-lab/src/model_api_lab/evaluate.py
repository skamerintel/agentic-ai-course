from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from model_api_lab.models import ExperimentRecord, Incident, Score


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def score_summary(incident: Incident, text: str) -> Score:
    normalized_text = _normalized(text)
    found: list[str] = []
    missed: list[str] = []

    for check in incident.fact_checks:
        phrases = (_normalized(phrase) for phrase in check.any_of)
        matches = any(phrase in normalized_text for phrase in phrases)
        target = found if matches else missed
        target.append(check.label)

    violations = tuple(
        claim
        for claim in incident.forbidden_claims
        if _normalized(claim) in normalized_text
    )
    return Score(
        facts_found=tuple(found),
        facts_missed=tuple(missed),
        forbidden_claims_found=violations,
        word_count=len(text.split()),
    )


def aggregate(records: Iterable[ExperimentRecord]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[ExperimentRecord]] = defaultdict(list)
    for record in records:
        groups[record.result.api].append(record)

    summary: dict[str, dict[str, Any]] = {}
    for api, items in sorted(groups.items()):
        count = len(items)
        summary[api] = {
            "count": count,
            "mean_fact_recall": round(
                sum(item.score.fact_recall for item in items) / count, 4
            ),
            "forbidden_claims_found": sum(
                len(item.score.forbidden_claims_found) for item in items
            ),
            "mean_word_count": round(
                sum(item.score.word_count for item in items) / count, 2
            ),
            "mean_latency_ms": round(
                sum(item.result.latency_ms for item in items) / count, 2
            ),
        }
    return summary
