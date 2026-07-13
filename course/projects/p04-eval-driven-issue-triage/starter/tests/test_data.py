from pathlib import Path

from issue_triage.data import (
    fingerprint_files,
    load_issues,
    load_predictions,
    load_truth,
)


def test_loads_development_assets() -> None:
    assert len(load_issues("data/issues-dev.jsonl")) == 10
    assert len(load_truth("data/ground-truth-dev.jsonl")) == 10
    assert len(load_predictions("fixtures/baseline-predictions.jsonl")) == 10


def test_fingerprint_changes_with_content(tmp_path: Path) -> None:
    first = tmp_path / "first.jsonl"
    first.write_text('{"value":1}\n', encoding="utf-8")
    before = fingerprint_files(first)
    first.write_text('{"value":2}\n', encoding="utf-8")

    assert fingerprint_files(first) != before
