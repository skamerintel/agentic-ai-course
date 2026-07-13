from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from model_api_lab.models import ExperimentRecord, Incident, Score


def score_summary(incident: Incident, text: str) -> Score:
    """Apply the supplied coarse lexical checks.

    This score is intentionally incomplete and must not replace human review.
    """
    raise NotImplementedError("implement automatic scoring")


def aggregate(records: Iterable[ExperimentRecord]) -> dict[str, dict[str, Any]]:
    """Aggregate count, recall, violations, words, and latency by API."""
    raise NotImplementedError("implement aggregation")
