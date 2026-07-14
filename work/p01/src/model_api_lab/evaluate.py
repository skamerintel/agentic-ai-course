from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from model_api_lab.models import ExperimentRecord, Incident, Score


def score_summary(incident: Incident, text: str) -> Score:
    """Apply the supplied coarse lexical checks.

    This score is intentionally incomplete and must not replace human review.
    """
    lowered = text.lower()

    facts_found = tuple(
        check.label
        for check in incident.fact_checks
        if any(phrase.lower() in lowered for phrase in check.any_of)
    )
    facts_missed = tuple(
        check.label for check in incident.fact_checks if check.label not in facts_found
    )
    forbidden_claims_found = tuple(
        claim for claim in incident.forbidden_claims if claim.lower() in lowered
    )

    return Score(
        facts_found=facts_found,
        facts_missed=facts_missed,
        forbidden_claims_found=forbidden_claims_found,
        word_count=len(text.split()),
    )


def aggregate(records: Iterable[ExperimentRecord]) -> dict[str, dict[str, Any]]:
    """Aggregate count, recall, violations, words, and latency by API."""
    by_api: dict[str, list[ExperimentRecord]] = {}
    for record in records:
        by_api.setdefault(record.result.api, []).append(record)

    summary: dict[str, dict[str, Any]] = {}
    for api, api_records in by_api.items():
        count = len(api_records)
        summary[api] = {
            "count": count,
            "avg_fact_recall": sum(r.score.fact_recall for r in api_records) / count,
            "forbidden_claim_violations": sum(
                len(r.score.forbidden_claims_found) for r in api_records
            ),
            "avg_word_count": sum(r.score.word_count for r in api_records) / count,
            "avg_latency_ms": sum(r.result.latency_ms for r in api_records) / count,
        }
    return summary
