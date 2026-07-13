from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from release_workflow.models import (
    ApprovalResponse,
    PolicyRules,
    ReleaseManifest,
    ReleaseState,
    RepositorySnapshot,
)
from release_workflow.reviewer import NotesReviewer
from release_workflow.sink import DecisionSink


@dataclass
class WorkflowDependencies:
    manifests: dict[str, ReleaseManifest]
    snapshots: dict[str, RepositorySnapshot]
    policy: PolicyRules
    reviewer: NotesReviewer
    sink: DecisionSink


def graph_config(thread_id: str) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": thread_id}}


def initial_state(workflow_id: str, release_id: str) -> ReleaseState:
    return {
        "workflow_id": workflow_id,
        "release_id": release_id,
        "progress": [],
    }


def approval_command(
    action: str,
    rationale: str,
    *,
    edited_decision: str | None = None,
    conditions: list[str] | None = None,
) -> ApprovalResponse:
    return ApprovalResponse.model_validate(
        {
            "action": action,
            "rationale": rationale,
            "edited_decision": edited_decision,
            "conditions": conditions or [],
        },
        strict=False,
    )


def build_workflow(
    dependencies: WorkflowDependencies,
    *,
    checkpointer: Any,
) -> Any:
    raise NotImplementedError("implement typed LangGraph nodes, edges, and interrupt")
