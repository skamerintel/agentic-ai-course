from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class InterfaceKind(StrEnum):
    WORKFLOW_API = "workflow_api"
    EVENT_DRIVEN = "event_driven"
    BATCH = "batch"
    CHAT = "chat"


class StepMode(StrEnum):
    DETERMINISTIC = "deterministic"
    MODEL = "model"
    TOOL = "tool"
    HUMAN = "human"


class IntegrationKind(StrEnum):
    GITHUB = "github"
    EXTERNAL = "external"


class WorkflowStep(StrictModel):
    id: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=3, max_length=100)
    mode: StepMode
    purpose: str = Field(min_length=10, max_length=500)
    output_contract: str = Field(min_length=3, max_length=300)
    failure_behavior: str = Field(min_length=5, max_length=500)


class IntegrationSpec(StrictModel):
    name: str = Field(min_length=2, max_length=100)
    kind: IntegrationKind
    purpose: str = Field(min_length=10, max_length=500)
    read: bool
    write: bool
    fixture_strategy: str = Field(min_length=5, max_length=500)
    failure_modes: list[str]


class ModelBoundary(StrictModel):
    provider: str = Field(min_length=2, max_length=100)
    api: str = Field(min_length=2, max_length=100)
    structured_output: bool
    configuration_policy: str = Field(min_length=10, max_length=500)


class OrchestrationDecision(StrictModel):
    framework: str = Field(min_length=2, max_length=100)
    justification: str = Field(min_length=10, max_length=1000)


class StateChoice(StrictModel):
    name: str = Field(min_length=2, max_length=100)
    purpose: str = Field(min_length=10, max_length=500)
    source_of_truth: bool
    loss_behavior: str = Field(min_length=10, max_length=500)


class ApprovalPoint(StrictModel):
    action: str = Field(min_length=3, max_length=200)
    approver: str = Field(min_length=3, max_length=200)
    enforcement_boundary: str = Field(min_length=10, max_length=500)
    replay_strategy: str = Field(min_length=10, max_length=500)


class EvaluationPlan(StrictModel):
    ground_truth_source: str = Field(min_length=10, max_length=1000)
    dataset_size: int = Field(ge=1)
    holdout_policy: str = Field(min_length=10, max_length=1000)
    metrics: list[str]
    slices: list[str]
    failure_taxonomy: list[str]
    baseline: str = Field(min_length=3, max_length=1000)
    iteration_budget: int = Field(ge=0)


class Milestone(StrictModel):
    name: str = Field(min_length=3, max_length=100)
    demo: str = Field(min_length=5, max_length=500)
    acceptance_evidence: list[str]


class DeliveryPlan(StrictModel):
    package_manager: str = Field(min_length=2, max_length=100)
    build_backend: str = Field(min_length=2, max_length=100)
    docker_smoke_test: str = Field(min_length=5, max_length=500)
    test_types: list[str]
    milestones: list[Milestone]


class OptionalCapability(StrictModel):
    enabled: bool
    rationale: str = Field(min_length=3, max_length=500)
    clients: list[str]
    exposed_actions: list[str]


class OptionalCapabilities(StrictModel):
    redis: OptionalCapability
    fastmcp: OptionalCapability


class Risk(StrictModel):
    id: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=10, max_length=500)
    trigger: str = Field(min_length=5, max_length=500)
    mitigation: str = Field(min_length=10, max_length=500)
    owner: str = Field(min_length=3, max_length=100)


class CapstoneProposal(StrictModel):
    title: str = Field(min_length=5, max_length=150)
    domain: str = Field(min_length=3, max_length=100)
    primary_interface: InterfaceKind
    business_user: str = Field(min_length=3, max_length=200)
    business_outcome: str = Field(min_length=15, max_length=1000)
    success_metrics: list[str]
    non_goals: list[str]
    llm_justification: str = Field(min_length=10, max_length=1000)
    workflow_steps: list[WorkflowStep]
    integrations: list[IntegrationSpec]
    model_boundary: ModelBoundary
    orchestration: OrchestrationDecision
    state_choices: list[StateChoice]
    approval_points: list[ApprovalPoint]
    evaluation: EvaluationPlan
    delivery: DeliveryPlan
    optional_capabilities: OptionalCapabilities
    risks: list[Risk]


class ArtifactStatus(StrEnum):
    COMPLETE = "complete"
    DEFERRED = "deferred"
    MISSING = "missing"


class ArtifactRecord(StrictModel):
    id: str = Field(min_length=2, max_length=100)
    path: str = Field(min_length=1, max_length=500)
    status: ArtifactStatus
    evidence: str = Field(min_length=3, max_length=1000)


class ArtifactManifest(StrictModel):
    project_slug: str = Field(pattern=r"^[a-z0-9-]+$")
    repository_url: str = Field(min_length=10, max_length=500)
    artifacts: list[ArtifactRecord]


class RequiredArtifact(StrictModel):
    id: str
    phase: str
    description: str


class FindingSeverity(StrEnum):
    BLOCKING = "blocking"
    WARNING = "warning"


class ValidationFinding(StrictModel):
    code: str
    severity: FindingSeverity
    message: str


class ValidationReport(StrictModel):
    subject: str
    findings: list[ValidationFinding]

    @property
    def passed(self) -> bool:
        return not any(
            finding.severity is FindingSeverity.BLOCKING for finding in self.findings
        )
