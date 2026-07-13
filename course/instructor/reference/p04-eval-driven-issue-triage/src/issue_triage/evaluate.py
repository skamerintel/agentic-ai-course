from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from issue_triage.models import GroundTruth, TriagePrediction


def _safe_div(numerator: int | float, denominator: int | float) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _prediction_index(
    predictions: Iterable[TriagePrediction],
) -> dict[str, TriagePrediction]:
    result: dict[str, TriagePrediction] = {}
    for prediction in predictions:
        if prediction.issue_id in result:
            raise ValueError(f"duplicate prediction: {prediction.issue_id}")
        result[prediction.issue_id] = prediction
    return result


def _score_subset(
    truth: list[GroundTruth], predictions: dict[str, TriagePrediction]
) -> dict[str, Any]:
    category_correct = 0
    urgency_correct = 0
    owner_correct = 0
    followup_correct = 0
    duplicate_decision_correct = 0
    exact_correct = 0
    label_true_positive = 0
    label_false_positive = 0
    label_false_negative = 0
    duplicate_positive_count = 0
    duplicate_hits = 0
    reciprocal_rank_total = 0.0

    for expected in truth:
        prediction = predictions.get(expected.issue_id)
        if prediction is None:
            label_false_negative += len(set(expected.required_labels))
            if expected.acceptable_duplicate_ids:
                duplicate_positive_count += 1
            continue

        category_match = prediction.category is expected.category
        urgency_match = prediction.urgency is expected.urgency
        owner_match = prediction.owner in expected.acceptable_owners
        followup_match = (
            bool(prediction.missing_information_questions)
            is expected.ask_for_information
        )
        category_correct += category_match
        urgency_correct += urgency_match
        owner_correct += owner_match
        followup_correct += followup_match

        expected_labels = set(expected.required_labels)
        predicted_labels = set(prediction.labels)
        label_true_positive += len(expected_labels & predicted_labels)
        label_false_positive += len(predicted_labels - expected_labels)
        label_false_negative += len(expected_labels - predicted_labels)

        expected_duplicates = set(expected.acceptable_duplicate_ids)
        predicted_duplicates = prediction.duplicate_candidates[:3]
        duplicate_decision_correct += bool(predicted_duplicates) is bool(
            expected_duplicates
        )
        if expected_duplicates:
            duplicate_positive_count += 1
            rank = next(
                (
                    index
                    for index, candidate in enumerate(predicted_duplicates, start=1)
                    if candidate in expected_duplicates
                ),
                None,
            )
            if rank is not None:
                duplicate_hits += 1
                reciprocal_rank_total += 1 / rank

        exact_correct += (
            category_match
            and urgency_match
            and owner_match
            and predicted_labels == expected_labels
            and followup_match
        )

    count = len(truth)
    label_precision = _safe_div(
        label_true_positive, label_true_positive + label_false_positive
    )
    label_recall = _safe_div(
        label_true_positive, label_true_positive + label_false_negative
    )
    label_f1 = (
        round(2 * label_precision * label_recall / (label_precision + label_recall), 4)
        if label_precision + label_recall
        else 0.0
    )
    return {
        "count": count,
        "category_accuracy": _safe_div(category_correct, count),
        "urgency_accuracy": _safe_div(urgency_correct, count),
        "owner_accuracy": _safe_div(owner_correct, count),
        "followup_accuracy": _safe_div(followup_correct, count),
        "label_precision": label_precision,
        "label_recall": label_recall,
        "label_f1": label_f1,
        "duplicate_decision_accuracy": _safe_div(duplicate_decision_correct, count),
        "duplicate_hit_at_3": _safe_div(duplicate_hits, duplicate_positive_count),
        "duplicate_mrr": round(reciprocal_rank_total / duplicate_positive_count, 4)
        if duplicate_positive_count
        else 0.0,
        "exact_triage_accuracy": _safe_div(exact_correct, count),
    }


def evaluate_predictions(
    truth: list[GroundTruth],
    predictions: list[TriagePrediction],
    *,
    dataset_fingerprint: str | None = None,
    prediction_fingerprint: str | None = None,
) -> dict[str, Any]:
    truth_ids = {item.issue_id for item in truth}
    prediction_index = _prediction_index(predictions)
    prediction_ids = set(prediction_index)
    slices = sorted({slice_name for item in truth for slice_name in item.slices})

    return {
        "dataset_fingerprint": dataset_fingerprint,
        "prediction_fingerprint": prediction_fingerprint,
        "coverage": {
            "expected_count": len(truth_ids),
            "prediction_count": len(prediction_ids),
            "missing_ids": sorted(truth_ids - prediction_ids),
            "extra_ids": sorted(prediction_ids - truth_ids),
        },
        "overall": _score_subset(truth, prediction_index),
        "slices": {
            slice_name: _score_subset(
                [item for item in truth if slice_name in item.slices],
                prediction_index,
            )
            for slice_name in slices
        },
    }


def _numeric_delta(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, float]:
    return {
        key: round(float(candidate[key]) - float(value), 4)
        for key, value in baseline.items()
        if key != "count"
        and isinstance(value, int | float)
        and isinstance(candidate.get(key), int | float)
    }


def compare_reports(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    baseline_fingerprint = baseline.get("dataset_fingerprint")
    candidate_fingerprint = candidate.get("dataset_fingerprint")
    if (
        baseline_fingerprint
        and candidate_fingerprint
        and baseline_fingerprint != candidate_fingerprint
    ):
        raise ValueError("cannot compare reports with different dataset fingerprints")

    slice_names = sorted(set(baseline["slices"]) | set(candidate["slices"]))
    slice_delta = {
        name: _numeric_delta(
            baseline["slices"].get(name, {}), candidate["slices"].get(name, {})
        )
        for name in slice_names
    }
    regressions = [
        {"slice": name, "metric": metric, "delta": delta}
        for name, metrics in slice_delta.items()
        for metric, delta in metrics.items()
        if delta < 0
    ]
    return {
        "dataset_fingerprint": candidate_fingerprint or baseline_fingerprint,
        "overall_delta": _numeric_delta(baseline["overall"], candidate["overall"]),
        "slice_delta": slice_delta,
        "regressions": regressions,
    }
