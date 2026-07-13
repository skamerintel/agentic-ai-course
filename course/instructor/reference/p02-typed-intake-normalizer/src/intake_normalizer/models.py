from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    model_config = ConfigDict(extra="forbid", strict=True)

    field: EvidenceField
    quote: str = Field(min_length=2, max_length=400)

    @field_validator("quote")
    @classmethod
    def strip_quote(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("evidence quote must not be blank")
        return stripped


class NormalizedIntake(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    source_id: str = Field(pattern=r"^REQ-\d{3}$")
    category: Category
    urgency: Urgency
    requester_name: str | None = None
    requester_email: str | None = None
    affected_system: str | None = None
    requested_action: str | None = Field(default=None, min_length=5)
    due_date: date | None = None
    requires_follow_up: bool
    missing_information: list[MissingInformation] = Field(
        default_factory=list, max_length=5
    )
    evidence: list[EvidenceItem] = Field(min_length=1, max_length=8)

    @field_validator(
        "requester_name", "requester_email", "affected_system", "requested_action"
    )
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("optional text must be null rather than blank")
        return stripped

    @field_validator("requester_email")
    @classmethod
    def validate_email_shape(cls, value: str | None) -> str | None:
        if value is None:
            return None
        local, separator, domain = value.partition("@")
        if not separator or not local or "." not in domain:
            raise ValueError("requester_email must have a basic email shape")
        return value

    @model_validator(mode="after")
    def reject_duplicate_missing_information(self) -> Self:
        if len(self.missing_information) != len(set(self.missing_information)):
            raise ValueError("duplicate missing_information values are not allowed")
        return self


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
