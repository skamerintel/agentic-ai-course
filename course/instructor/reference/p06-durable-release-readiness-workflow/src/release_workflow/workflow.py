from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from release_workflow.models import (
    ApprovalAction,
    ApprovalResponse,
    Blocker,
    Decision,
    DecisionRecord,
    NotesReview,
    PolicyRules,
    ReleaseManifest,
    ReleaseState,
    RepositorySnapshot,
)
from release_workflow.policy import derive_blockers, route_for_blockers
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


def _progress(stage: str, detail: str) -> list[dict[str, str]]:
    return [{"stage": stage, "detail": detail}]


def _values(state: ReleaseState) -> dict[str, Any]:
    """Expose staged values after graph ordering guarantees their presence."""
    return cast(dict[str, Any], state)


def build_workflow(
    dependencies: WorkflowDependencies,
    *,
    checkpointer: Any,
) -> Any:
    def load_manifest(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        manifest = dependencies.manifests[values["release_id"]]
        return {
            "manifest": manifest.model_dump(mode="json"),
            "progress": _progress("manifest_loaded", manifest.release_id),
        }

    def check_repository(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        snapshot = dependencies.snapshots[values["release_id"]]
        return {
            "repository": snapshot.model_dump(mode="json"),
            "progress": _progress("repository_checked", values["release_id"]),
        }

    def review_notes(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        manifest = ReleaseManifest.model_validate(values["manifest"], strict=True)
        review = dependencies.reviewer.review(manifest)
        return {
            "notes_review": review.model_dump(mode="json"),
            "progress": _progress("notes_reviewed", review.summary),
        }

    def blocker_node(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        manifest = ReleaseManifest.model_validate(values["manifest"], strict=True)
        repository = RepositorySnapshot.model_validate(
            values["repository"], strict=True
        )
        notes_review = NotesReview.model_validate(values["notes_review"], strict=True)
        blockers = derive_blockers(
            manifest, repository, notes_review, dependencies.policy
        )
        return {
            "blockers": [item.model_dump(mode="json") for item in blockers],
            "progress": _progress("blockers_derived", f"{len(blockers)} blocker(s)"),
        }

    def blocker_route(state: ReleaseState) -> str:
        values = _values(state)
        blockers = [
            Blocker.model_validate(item, strict=True)
            for item in values.get("blockers", [])
        ]
        return route_for_blockers(blockers)

    def propose_ready(state: ReleaseState) -> dict[str, Any]:
        proposal = DecisionRecord(
            decision=Decision.READY,
            rationale="All deterministic checks and notes requirements passed",
        )
        return {
            "proposal": proposal.model_dump(mode="json"),
            "progress": _progress("proposal_created", "ready"),
        }

    def propose_hold(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        blockers = [
            Blocker.model_validate(item, strict=True) for item in values["blockers"]
        ]
        proposal = DecisionRecord(
            decision=Decision.HOLD,
            rationale="; ".join(item.detail for item in blockers),
        )
        return {
            "proposal": proposal.model_dump(mode="json"),
            "progress": _progress("proposal_created", "hold"),
        }

    def approval(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        response = interrupt(
            {
                "workflow_id": values["workflow_id"],
                "release_id": values["release_id"],
                "proposal": values["proposal"],
                "blockers": values.get("blockers", []),
                "allowed_actions": ["approve", "edit", "reject"],
            }
        )
        validated = ApprovalResponse.model_validate(response, strict=False)
        return {
            "approval": validated.model_dump(mode="json"),
            "progress": _progress("approval_received", validated.action.value),
        }

    def finalize(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        approval_response = ApprovalResponse.model_validate(
            values["approval"], strict=False
        )
        proposal = DecisionRecord.model_validate(values["proposal"], strict=False)
        if approval_response.action is ApprovalAction.APPROVE:
            final = proposal
        elif approval_response.action is ApprovalAction.REJECT:
            final = DecisionRecord(
                decision=Decision.REJECTED,
                rationale=approval_response.rationale,
            )
        else:
            if approval_response.edited_decision is None:
                raise ValueError("validated edit is missing edited_decision")
            final = DecisionRecord(
                decision=approval_response.edited_decision,
                rationale=approval_response.rationale,
                conditions=approval_response.conditions,
            )
        return {
            "final_decision": final.model_dump(mode="json"),
            "progress": _progress("decision_finalized", final.decision.value),
        }

    def publish(state: ReleaseState) -> dict[str, Any]:
        values = _values(state)
        decision = DecisionRecord.model_validate(values["final_decision"], strict=False)
        receipt = dependencies.sink.publish(values["workflow_id"], decision)
        return {
            "publication": receipt.model_dump(mode="json"),
            "progress": _progress("decision_published", receipt.receipt_id),
        }

    builder = StateGraph(ReleaseState)
    builder.add_node("load_manifest", load_manifest)
    builder.add_node("check_repository", check_repository)
    builder.add_node("review_notes", review_notes)
    builder.add_node("derive_blockers", blocker_node)
    builder.add_node("propose_ready", propose_ready)
    builder.add_node("propose_hold", propose_hold)
    builder.add_node("approval", approval)
    builder.add_node("finalize", finalize)
    builder.add_node("publish", publish)
    builder.add_edge(START, "load_manifest")
    builder.add_edge("load_manifest", "check_repository")
    builder.add_edge("check_repository", "review_notes")
    builder.add_edge("review_notes", "derive_blockers")
    builder.add_conditional_edges(
        "derive_blockers",
        blocker_route,
        {"ready": "propose_ready", "hold": "propose_hold"},
    )
    builder.add_edge("propose_ready", "approval")
    builder.add_edge("propose_hold", "approval")
    builder.add_edge("approval", "finalize")
    builder.add_edge("finalize", "publish")
    builder.add_edge("publish", END)
    return builder.compile(checkpointer=checkpointer)
