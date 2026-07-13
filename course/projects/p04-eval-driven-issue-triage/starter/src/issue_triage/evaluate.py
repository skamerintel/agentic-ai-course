from __future__ import annotations

from typing import Any

from issue_triage.models import GroundTruth, TriagePrediction


def evaluate_predictions(
    truth: list[GroundTruth],
    predictions: list[TriagePrediction],
    *,
    dataset_fingerprint: str | None = None,
    prediction_fingerprint: str | None = None,
) -> dict[str, Any]:
    raise NotImplementedError("implement multi-metric and slice evaluation")


def compare_reports(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    raise NotImplementedError("implement metric and slice comparison")
