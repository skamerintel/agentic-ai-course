from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Category(StrEnum):
    BUG = "bug"
    FEATURE = "feature"
    DOCS = "docs"
    QUESTION = "question"
    SECURITY = "security"


class Urgency(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Team(StrEnum):
    PAYMENTS = "payments"
    IDENTITY = "identity"
    DEVELOPER_EXPERIENCE = "developer_experience"
    DOCS = "docs"
    PLATFORM = "platform"
    SECURITY = "security"
    UNKNOWN = "unknown"


class Issue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    issue_id: str
    repo: str
    component: str | None = None
    title: str
    body: str
    slices: list[str] = Field(default_factory=list)

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.body}"


class GroundTruth(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    issue_id: str
    category: Category
    urgency: Urgency
    acceptable_owners: list[Team] = Field(min_length=1)
    required_labels: list[str]
    acceptable_duplicate_ids: list[str]
    ask_for_information: bool
    slices: list[str]
    adjudication_note: str


class TriagePrediction(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    issue_id: str
    category: Category
    urgency: Urgency
    owner: Team
    labels: list[str]
    duplicate_candidates: list[str] = Field(max_length=3)
    missing_information_questions: list[str] = Field(max_length=3)
    evidence: list[str] = Field(min_length=1, max_length=8)


class KnownIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    issue_id: str
    repo: str
    component: str
    title: str
    summary: str
    status: str

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.summary}"


class RetrievalQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    issue_id: str
    expected_ids: list[str]
    repo: str


class RetrievedCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    issue_id: str
    score: float
