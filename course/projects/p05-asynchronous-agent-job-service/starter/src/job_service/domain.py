from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    CANCEL_REQUESTED = "cancel_requested"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def terminal(self) -> bool:
        return self in {self.SUCCEEDED, self.FAILED, self.CANCELLED}


class IssueInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    issue_id: str = Field(min_length=1, max_length=80)
    repo: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=20_000)


class JobSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    idempotency_key: str = Field(
        min_length=8,
        max_length=120,
        pattern=r"^[A-Za-z0-9._:-]+$",
    )
    issue: IssueInput


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    category: str
    urgency: str
    summary: str
    evidence: list[str] = Field(min_length=1, max_length=8)


class JobSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    job_id: str
    idempotency_key: str
    correlation_id: str
    issue: IssueInput
    status: JobStatus
    result: TriageResult | None = None
    error_code: str | None = None
    created_at: datetime
    updated_at: datetime


class ProgressEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    job_id: str
    sequence: int = Field(ge=1)
    event: str
    detail: str
    created_at: datetime


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    event_id: int
    job_id: str
    event: str
    detail: str
    created_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
