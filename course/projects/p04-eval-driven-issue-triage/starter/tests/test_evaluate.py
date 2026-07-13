from issue_triage.data import load_predictions, load_truth
from issue_triage.evaluate import compare_reports, evaluate_predictions


def report(path: str):
    return evaluate_predictions(
        load_truth("data/ground-truth-dev.jsonl"), load_predictions(path)
    )


def test_baseline_metrics_are_dimension_specific() -> None:
    baseline = report("fixtures/baseline-predictions.jsonl")

    assert baseline["overall"]["count"] == 10
    assert baseline["overall"]["category_accuracy"] == 0.7
    assert baseline["overall"]["urgency_accuracy"] == 0.4
    assert baseline["overall"]["owner_accuracy"] == 0.8
    assert baseline["slices"]["docs"]["category_accuracy"] == 0.0


def test_candidate_improves_overall_but_regresses_feature_slice() -> None:
    baseline = report("fixtures/baseline-predictions.jsonl")
    candidate = report("fixtures/improved-predictions.jsonl")
    comparison = compare_reports(baseline, candidate)

    assert candidate["overall"]["category_accuracy"] == 0.9
    assert comparison["overall_delta"]["category_accuracy"] == 0.2
    assert comparison["slice_delta"]["feature"]["category_accuracy"] == -1.0


def test_duplicate_ranking_metrics_are_separate() -> None:
    baseline = report("fixtures/baseline-predictions.jsonl")

    assert "duplicate_hit_at_3" in baseline["overall"]
    assert "duplicate_mrr" in baseline["overall"]
    assert "duplicate_decision_accuracy" in baseline["overall"]
