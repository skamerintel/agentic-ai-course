from __future__ import annotations

from issue_triage.models import Issue, TriagePrediction


def predict_openai(
    issue: Issue,
    context: str,
    model: str,
    *,
    timeout_seconds: float = 60.0,
) -> TriagePrediction:
    raise NotImplementedError("implement live Responses structured-output triage")
