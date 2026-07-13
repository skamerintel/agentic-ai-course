from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import ValidationError

from release_workflow.data import (
    load_manifests,
    load_notes_reviews,
    load_policy,
    load_snapshots,
)
from release_workflow.reviewer import FixtureNotesReviewer
from release_workflow.sink import SimulatedCrash, SqliteDecisionSink
from release_workflow.workflow import (
    WorkflowDependencies,
    approval_command,
    build_workflow,
    graph_config,
    initial_state,
)


def dependencies(tmp_path, *, crash: bool = False) -> WorkflowDependencies:
    reviews = load_notes_reviews("fixtures/notes-reviews.json")
    return WorkflowDependencies(
        manifests=load_manifests("data/release-manifests.jsonl"),
        snapshots=load_snapshots("data/repository-snapshots.json"),
        policy=load_policy("data/policy-rules.json"),
        reviewer=FixtureNotesReviewer(reviews),
        sink=SqliteDecisionSink(
            tmp_path / "holdout-decisions.sqlite",
            crash_after_commit_once=crash,
        ),
    )


def approval(action: str, **changes) -> dict:
    return {
        "action": action,
        "rationale": f"Holdout action: {action}",
        "edited_decision": changes.get("edited_decision"),
        "conditions": changes.get("conditions", []),
    }


def test_invalid_edit_does_not_publish(tmp_path) -> None:
    deps = dependencies(tmp_path)
    graph = build_workflow(deps, checkpointer=InMemorySaver())
    config = graph_config("holdout-invalid-edit")
    graph.invoke(initial_state("holdout-invalid-edit", "REL-100"), config)

    with pytest.raises(ValidationError):
        graph.invoke(Command(resume=approval("edit")), config)

    assert deps.sink.count() == 0


def test_new_thread_observes_change_but_paused_thread_does_not(tmp_path) -> None:
    deps = dependencies(tmp_path)
    graph = build_workflow(deps, checkpointer=InMemorySaver())
    paused_config = graph_config("holdout-paused")
    graph.invoke(initial_state("holdout-paused", "REL-103"), paused_config)
    deps.snapshots["REL-103"] = deps.snapshots["REL-103_CHANGED_AFTER_PAUSE"]

    resumed = graph.invoke(Command(resume=approval("approve")), paused_config)
    new_run = graph.invoke(
        initial_state("holdout-new", "REL-103"),
        graph_config("holdout-new"),
    )

    assert resumed["final_decision"]["decision"] == "ready"
    assert new_run["proposal"]["decision"] == "hold"


def test_crash_replay_reuses_receipt(tmp_path) -> None:
    deps = dependencies(tmp_path, crash=True)
    graph = build_workflow(deps, checkpointer=InMemorySaver())
    config = graph_config("holdout-crash")
    graph.invoke(initial_state("holdout-crash", "REL-100"), config)

    with pytest.raises(SimulatedCrash):
        graph.invoke(Command(resume=approval("approve")), config)
    durable = deps.sink.get("holdout-crash")
    recovered = graph.invoke(None, config)

    assert durable is not None
    assert recovered["publication"]["receipt_id"] == durable.receipt_id
    assert recovered["publication"]["replayed"] is True
    assert deps.sink.publish_attempts == 2
    assert deps.sink.count() == 1


def test_threads_and_workflow_receipts_are_independent(tmp_path) -> None:
    deps = dependencies(tmp_path)
    graph = build_workflow(deps, checkpointer=InMemorySaver())
    for workflow_id in ("holdout-thread-a", "holdout-thread-b"):
        config = graph_config(workflow_id)
        graph.invoke(initial_state(workflow_id, "REL-100"), config)
        graph.invoke(Command(resume=approval("approve")), config)

    first = deps.sink.get("holdout-thread-a")
    second = deps.sink.get("holdout-thread-b")

    assert first is not None and second is not None
    assert first.receipt_id != second.receipt_id
    assert deps.sink.count() == 2


def test_approval_command_remains_available_to_mentor() -> None:
    command = approval_command("approve", "Reviewed by mentor")

    assert command.action.value == "approve"
