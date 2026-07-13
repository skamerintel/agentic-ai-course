from __future__ import annotations

import copy

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from release_workflow.data import load_snapshots
from release_workflow.sink import SimulatedCrash, SqliteDecisionSink
from release_workflow.workflow import (
    build_workflow,
    graph_config,
    initial_state,
)


def resume_payload(
    action: str,
    *,
    edited_decision: str | None = None,
    conditions: list[str] | None = None,
) -> dict:
    return {
        "action": action,
        "rationale": f"Mentor selected {action}",
        "edited_decision": edited_decision,
        "conditions": conditions or [],
    }


def test_ready_workflow_pauses_before_publication(dependencies) -> None:
    graph = build_workflow(dependencies, checkpointer=InMemorySaver())
    config = graph_config("workflow-ready")

    paused = graph.invoke(initial_state("workflow-ready", "REL-100"), config)

    assert paused["proposal"]["decision"] == "ready"
    assert "__interrupt__" in paused
    assert graph.get_state(config).next == ("approval",)
    assert dependencies.sink.count() == 0


@pytest.mark.parametrize(
    ("release_id", "approval", "expected"),
    [
        ("REL-100", resume_payload("approve"), "ready"),
        ("REL-101", resume_payload("reject"), "rejected"),
        (
            "REL-102",
            resume_payload(
                "edit",
                edited_decision="ready_with_conditions",
                conditions=["Merge PR-812"],
            ),
            "ready_with_conditions",
        ),
    ],
)
def test_approval_paths_publish_one_final_decision(
    dependencies, release_id, approval, expected
) -> None:
    graph = build_workflow(dependencies, checkpointer=InMemorySaver())
    workflow_id = f"workflow-{release_id}"
    config = graph_config(workflow_id)
    graph.invoke(initial_state(workflow_id, release_id), config)

    finished = graph.invoke(Command(resume=approval), config)

    assert finished["final_decision"]["decision"] == expected
    assert finished["publication"]["workflow_id"] == workflow_id
    assert dependencies.sink.count() == 1


def test_stream_exposes_named_node_updates(dependencies) -> None:
    graph = build_workflow(dependencies, checkpointer=InMemorySaver())

    updates = list(
        graph.stream(
            initial_state("workflow-stream", "REL-100"),
            graph_config("workflow-stream"),
            stream_mode="updates",
        )
    )
    node_names = {name for update in updates for name in update}

    assert {
        "load_manifest",
        "check_repository",
        "review_notes",
        "derive_blockers",
        "propose_ready",
    } <= node_names


def test_resume_uses_checkpointed_repository_evidence(dependencies) -> None:
    graph = build_workflow(dependencies, checkpointer=InMemorySaver())
    config = graph_config("workflow-mutable")
    paused = graph.invoke(initial_state("workflow-mutable", "REL-103"), config)
    checkpointed_repository = copy.deepcopy(paused["repository"])
    changed = load_snapshots("data/repository-snapshots.json")
    dependencies.snapshots["REL-103"] = changed["REL-103_CHANGED_AFTER_PAUSE"]

    finished = graph.invoke(Command(resume=resume_payload("approve")), config)

    assert finished["repository"] == checkpointed_repository
    assert finished["final_decision"]["decision"] == "ready"


def test_sqlite_checkpoint_survives_graph_reconstruction(
    dependencies, tmp_path
) -> None:
    checkpoint_path = tmp_path / "checkpoints.sqlite"
    config = graph_config("workflow-restart")
    with SqliteSaver.from_conn_string(str(checkpoint_path)) as checkpointer:
        checkpointer.setup()
        graph = build_workflow(dependencies, checkpointer=checkpointer)
        graph.invoke(initial_state("workflow-restart", "REL-100"), config)

    with SqliteSaver.from_conn_string(str(checkpoint_path)) as checkpointer:
        checkpointer.setup()
        recreated = build_workflow(dependencies, checkpointer=checkpointer)
        finished = recreated.invoke(Command(resume=resume_payload("approve")), config)

    assert finished["final_decision"]["decision"] == "ready"
    assert dependencies.sink.count() == 1


def test_crash_after_write_replays_without_duplicate(dependencies, tmp_path) -> None:
    sink = SqliteDecisionSink(
        tmp_path / "crash-decisions.sqlite",
        crash_after_commit_once=True,
    )
    dependencies.sink = sink
    graph = build_workflow(dependencies, checkpointer=InMemorySaver())
    config = graph_config("workflow-crash")
    graph.invoke(initial_state("workflow-crash", "REL-100"), config)

    with pytest.raises(SimulatedCrash):
        graph.invoke(Command(resume=resume_payload("approve")), config)
    recovered = graph.invoke(None, config)

    assert recovered["publication"]["replayed"] is True
    assert sink.publish_attempts == 2
    assert sink.count() == 1
