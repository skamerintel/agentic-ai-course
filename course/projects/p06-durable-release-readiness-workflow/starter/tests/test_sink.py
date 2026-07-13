import pytest

from release_workflow.models import Decision, DecisionRecord
from release_workflow.sink import PublicationConflict, SqliteDecisionSink


def decision(value: Decision = Decision.READY) -> DecisionRecord:
    return DecisionRecord(decision=value, rationale="Policy evidence is clear")


def test_replay_returns_existing_receipt(tmp_path) -> None:
    sink = SqliteDecisionSink(tmp_path / "decisions.sqlite")
    first = sink.publish("workflow-1", decision())
    second = sink.publish("workflow-1", decision())

    assert first.receipt_id == second.receipt_id
    assert first.replayed is False
    assert second.replayed is True
    assert sink.count() == 1


def test_same_workflow_cannot_publish_different_payload(tmp_path) -> None:
    sink = SqliteDecisionSink(tmp_path / "decisions.sqlite")
    sink.publish("workflow-1", decision())

    with pytest.raises(PublicationConflict):
        sink.publish("workflow-1", decision(Decision.HOLD))
