from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Channel(StrEnum):
    EMAIL = "email"
    FORM = "form"
    CHAT = "chat"


class Category(StrEnum):
    ACCESS = "access"
    INCIDENT = "incident"
    DATA_REQUEST = "data_request"
    BILLING = "billing"
    HARDWARE = "hardware"
    CONFIGURATION = "configuration"
    OTHER = "other"


class Urgency(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MissingInformation(StrEnum):
    REQUESTER_IDENTITY = "requester_identity"
    REQUESTER_CONTACT = "requester_contact"
    AFFECTED_SYSTEM = "affected_system"
    REQUESTED_ACTION = "requested_action"
    DUE_DATE_CLARIFICATION = "due_date_clarification"


class EvidenceField(StrEnum):
    CATEGORY = "category"
    URGENCY = "urgency"
    REQUESTER = "requester"
    AFFECTED_SYSTEM = "affected_system"
    REQUESTED_ACTION = "requested_action"
    DUE_DATE = "due_date"


class ServiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str = Field(pattern=r"^REQ-\d{3}$")
    channel: Channel
    received_at: datetime
    text: str = Field(min_length=5)


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    field: EvidenceField
    quote: str


class NormalizedIntake(BaseModel):
    """Intentionally permissive starter model for the learner to harden."""

    model_config = ConfigDict(extra="ignore")

    source_id: str
    category: Category
    urgency: Urgency
    requester_name: str | None = None
    requester_email: str | None = None
    affected_system: str | None = None
    requested_action: str | None = None
    due_date: date | None = None
    requires_follow_up: bool = False
    missing_information: list[MissingInformation] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class OutcomeKind(StrEnum):
    SUCCESS = "success"
    REFUSAL = "refusal"
    PROVIDER_ERROR = "provider_error"
    SCHEMA_ERROR = "schema_error"
    POLICY_ERROR = "policy_error"


class ProgressKind(StrEnum):
    STARTED = "started"
    ATTEMPT = "attempt"
    RETRYING = "retrying"
    COMPLETED = "completed"


class FailureDetail(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    code: str
    message: str
    retryable: bool = False


class ProcessingResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    source_id: str
    correlation_id: str
    outcome: OutcomeKind
    attempts: int = Field(ge=1)
    record: NormalizedIntake | None = None
    failures: list[FailureDetail] = Field(default_factory=list)
    response_id: str | None = None
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class ProgressEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    source_id: str
    correlation_id: str
    kind: ProgressKind
    attempt: int = Field(ge=0)
    detail: str | None = None
