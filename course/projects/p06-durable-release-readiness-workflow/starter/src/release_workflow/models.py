from __future__ import annotations

import operator
from enum import StrEnum
from typing import Annotated, Any, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReleaseManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    release_id: str
    version: str
    commit_sha: str
    release_notes: str
    required_checks: list[str]
    slices: list[str] = Field(default_factory=list)


class RepositoryIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str
    severity: str
    label: str


class PullRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str
    labels: list[str]


class RepositorySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    open_issues: list[RepositoryIssue]
    open_pull_requests: list[PullRequest]
    checks: dict[str, str]


class PolicyRules(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    block_on_issue_labels: list[str]
    block_on_issue_severities: list[str]
    allowed_open_pr_labels: list[str]
    required_check_status: str
    notes_minimum_score: float = Field(ge=0, le=1)
    ready_decision: str
    blocked_decision: str


class NotesReview(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    score: float = Field(ge=0, le=1)
    summary: str
    missing_sections: list[str]


class Blocker(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    code: str
    detail: str
    evidence: str


class Decision(StrEnum):
    READY = "ready"
    HOLD = "hold"
    READY_WITH_CONDITIONS = "ready_with_conditions"
    REJECTED = "rejected"


class DecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    decision: Decision
    rationale: str
    conditions: list[str] = Field(default_factory=list)


class ApprovalAction(StrEnum):
    APPROVE = "approve"
    EDIT = "edit"
    REJECT = "reject"


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    action: ApprovalAction
    rationale: str = Field(min_length=1)
    edited_decision: Decision | None = None
    conditions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_edit(self) -> ApprovalResponse:
        if self.action is ApprovalAction.EDIT and self.edited_decision is None:
            raise ValueError("edited_decision is required for edit")
        if self.action is not ApprovalAction.EDIT and self.edited_decision is not None:
            raise ValueError("edited_decision is allowed only for edit")
        return self


class PublicationReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    workflow_id: str
    receipt_id: str
    payload_fingerprint: str
    replayed: bool


class ProgressUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    stage: str
    detail: str


class ReleaseState(TypedDict, total=False):
    workflow_id: str
    release_id: str
    manifest: dict[str, Any]
    repository: dict[str, Any]
    notes_review: dict[str, Any]
    blockers: list[dict[str, Any]]
    proposal: dict[str, Any]
    approval: dict[str, Any]
    final_decision: dict[str, Any]
    publication: dict[str, Any]
    progress: Annotated[list[dict[str, str]], operator.add]


ApprovalPayload = dict[str, Any]
RouteName = Literal["ready", "hold"]
