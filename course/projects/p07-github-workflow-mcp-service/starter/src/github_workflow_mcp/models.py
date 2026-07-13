from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepositoryOverview(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    owner: str
    name: str
    default_branch: str
    private: bool
    archived: bool


class IssueSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    number: int = Field(gt=0)
    title: str
    body: str
    labels: list[str]
    author: str


class PullRequestSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    number: int = Field(gt=0)
    title: str
    head_sha: str
    draft: bool
    labels: list[str]
    author: str


class IssueListResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    items: list[IssueSummary]
    truncated: bool


class PullRequestListResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    items: list[PullRequestSummary]
    truncated: bool


class ProposalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"


class CommentProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    proposal_id: str
    owner: str
    repo: str
    issue_number: int = Field(gt=0)
    body: str = Field(min_length=1, max_length=1000)
    reason: str = Field(min_length=1, max_length=500)
    status: ProposalStatus
    created_at: datetime
    expires_at: datetime
    approved_by: str | None = None


class CommentReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    proposal_id: str
    comment_id: int = Field(gt=0)
    url: str
    replayed: bool


class DeliveryStatus(StrEnum):
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"
    IGNORED = "ignored"


class WebhookReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    delivery_id: str
    event: str
    action: str | None
    repository: str | None
    pull_request_number: int | None
    status: DeliveryStatus


class CapabilityPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    server_name: str
    max_list_items: int = Field(ge=1, le=100)
    max_comment_characters: int = Field(ge=1, le=5000)
    read_tools: list[str]
    proposal_tools: list[str]
    guarded_write_tools: list[str]
    administrative_actions_not_exposed_as_tools: list[str]
    webhook_events: list[str]
    approval_required: bool


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    proposal_id: str
    actor: str = Field(min_length=3, max_length=200)


class GitHubComment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    comment_id: int = Field(gt=0)
    url: str


class WebhookPullRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    number: int = Field(gt=0)


class WebhookRepository(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    full_name: str


class PullRequestWebhook(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    action: str
    repository: WebhookRepository
    pull_request: WebhookPullRequest


class HttpPage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    items: list[dict]
    next_url: str | None = None


class RepositoryName(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    owner: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")
    repo: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")

    @model_validator(mode="after")
    def reject_dot_segments(self) -> RepositoryName:
        if self.owner in {".", ".."} or self.repo in {".", ".."}:
            raise ValueError("repository segments cannot be dot paths")
        return self
