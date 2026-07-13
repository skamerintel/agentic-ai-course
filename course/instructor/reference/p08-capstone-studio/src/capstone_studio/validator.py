from __future__ import annotations

from collections import Counter

from capstone_studio.models import (
    ArtifactManifest,
    ArtifactStatus,
    CapstoneProposal,
    FindingSeverity,
    IntegrationKind,
    RequiredArtifact,
    StepMode,
    ValidationFinding,
    ValidationReport,
)


def _finding(
    code: str,
    message: str,
    severity: FindingSeverity = FindingSeverity.BLOCKING,
) -> ValidationFinding:
    return ValidationFinding(code=code, severity=severity, message=message)


def validate_proposal(proposal: CapstoneProposal) -> ValidationReport:
    findings: list[ValidationFinding] = []

    if proposal.primary_interface.value == "chat":
        findings.append(
            _finding(
                "primary-interface",
                "The capstone must primarily operate a workflow, event, or batch API.",
            )
        )
    if len(proposal.success_metrics) < 2 or len(proposal.non_goals) < 2:
        findings.append(
            _finding(
                "outcome-scope",
                "Define at least two success metrics and two explicit non-goals.",
            )
        )

    modes = {step.mode for step in proposal.workflow_steps}
    if len(proposal.workflow_steps) < 5 or not set(StepMode) <= modes:
        findings.append(
            _finding(
                "workflow-modes",
                "Map at least five steps covering deterministic, model, tool, "
                "and human responsibility.",
            )
        )
    if len({step.id for step in proposal.workflow_steps}) != len(
        proposal.workflow_steps
    ):
        findings.append(_finding("workflow-ids", "Workflow step IDs must be unique."))

    kinds = {integration.kind for integration in proposal.integrations}
    if IntegrationKind.GITHUB not in kinds or IntegrationKind.EXTERNAL not in kinds:
        findings.append(
            _finding(
                "integrations",
                "Use GitHub and at least one additional outcome-relevant external API.",
            )
        )
    if any(len(integration.failure_modes) < 2 for integration in proposal.integrations):
        findings.append(
            _finding(
                "integration-failures",
                "Each API boundary needs at least two explicit failure modes "
                "and fixtures.",
            )
        )

    if "openai" not in proposal.model_boundary.provider.lower():
        findings.append(_finding("openai-boundary", "Use an OpenAI provider boundary."))
    if proposal.model_boundary.api.lower() != "responses":
        findings.append(
            _finding("responses-api", "The primary OpenAI path must use Responses API.")
        )
    if not proposal.model_boundary.structured_output:
        findings.append(
            _finding(
                "structured-output", "Model output must use a validated structure."
            )
        )

    if (
        proposal.orchestration.framework.lower() != "langgraph"
        or len(proposal.orchestration.justification.split()) < 12
    ):
        findings.append(
            _finding(
                "langgraph",
                "Justify LangGraph using concrete state, interrupt, replay, "
                "or recovery needs.",
            )
        )

    postgres = [
        state for state in proposal.state_choices if state.name.lower() == "postgresql"
    ]
    if not postgres or not any(state.source_of_truth for state in postgres):
        findings.append(
            _finding("postgres", "PostgreSQL must own justified durable product state.")
        )
    redis = proposal.optional_capabilities.redis
    if redis.enabled:
        redis_state = [
            state for state in proposal.state_choices if state.name.lower() == "redis"
        ]
        if not redis_state or any(state.source_of_truth for state in redis_state):
            findings.append(
                _finding(
                    "redis-semantics",
                    "Enabled Redis needs an explicit transient role and loss "
                    "behavior; it must not be the durable source of truth.",
                )
            )

    if not proposal.approval_points or not any(
        "outside" in point.enforcement_boundary.lower()
        and "model" in point.enforcement_boundary.lower()
        for point in proposal.approval_points
    ):
        findings.append(
            _finding(
                "approval",
                "Define durable human approval enforced outside the "
                "model-callable surface.",
            )
        )

    evaluation = proposal.evaluation
    if evaluation.dataset_size < 30:
        findings.append(
            _finding(
                "ground-truth-size",
                "Plan at least 30 labeled cases unless the mentor approves a "
                "defended alternative.",
            )
        )
    holdout = evaluation.holdout_policy.lower()
    if not any(word in holdout for word in ("untouched", "blind", "frozen")):
        findings.append(
            _finding("holdout", "Define an untouched, blind, or frozen holdout policy.")
        )
    if evaluation.iteration_budget < 2:
        findings.append(
            _finding(
                "iterations", "Budget at least two measured improvement iterations."
            )
        )
    if (
        len(evaluation.metrics) < 3
        or len(evaluation.slices) < 3
        or len(evaluation.failure_taxonomy) < 3
    ):
        findings.append(
            _finding(
                "failure-slices",
                "Define at least three metrics, three failure slices, and three "
                "failure classes.",
            )
        )

    delivery = proposal.delivery
    if delivery.package_manager.lower() != "uv":
        findings.append(_finding("uv", "Use uv for the capstone project workflow."))
    if delivery.build_backend.lower() != "hatchling":
        findings.append(_finding("hatchling", "Build the package with Hatchling."))
    required_tests = {"unit", "integration", "contract", "recovery"}
    if not required_tests <= {item.lower() for item in delivery.test_types}:
        findings.append(
            _finding(
                "test-strategy",
                "Plan unit, integration, contract, and recovery-oriented tests.",
            )
        )
    if len(delivery.milestones) < 5 or any(
        len(milestone.acceptance_evidence) < 2 for milestone in delivery.milestones
    ):
        findings.append(
            _finding(
                "milestones",
                "Plan five vertical milestones with at least two acceptance "
                "artifacts each.",
            )
        )

    fastmcp = proposal.optional_capabilities.fastmcp
    dangerous = {"approve", "approval", "shell", "arbitrary-http", "admin"}
    if fastmcp.enabled and (
        not fastmcp.clients
        or dangerous & {action.lower() for action in fastmcp.exposed_actions}
    ):
        findings.append(
            _finding(
                "mcp-authority",
                "FastMCP needs a named client and cannot expose approval, shell, "
                "admin, or arbitrary HTTP authority.",
            )
        )
    elif not fastmcp.enabled:
        findings.append(
            _finding(
                "mcp-omitted",
                "FastMCP is omitted; preserve the rationale in the architecture "
                "decision.",
                FindingSeverity.WARNING,
            )
        )

    if len(proposal.risks) < 5:
        findings.append(
            _finding("risk-register", "Own at least five concrete capstone risks.")
        )
    if not any(integration.write for integration in proposal.integrations):
        findings.append(
            _finding(
                "write-demonstration",
                "No external write is proposed; defend an equivalent "
                "consequential approval demonstration.",
                FindingSeverity.WARNING,
            )
        )

    return ValidationReport(subject=proposal.title, findings=findings)


def validate_artifact_manifest(
    manifest: ArtifactManifest,
    requirements: list[RequiredArtifact],
) -> ValidationReport:
    findings: list[ValidationFinding] = []
    counts = Counter(record.id for record in manifest.artifacts)
    required_ids = {requirement.id for requirement in requirements}
    records = {record.id: record for record in manifest.artifacts}

    for artifact_id, count in sorted(counts.items()):
        if count > 1:
            findings.append(
                _finding(
                    "duplicate-artifact",
                    f"Artifact {artifact_id!r} appears {count} times.",
                )
            )
    for artifact_id in sorted(required_ids - records.keys()):
        findings.append(
            _finding(
                "missing-artifact", f"Required artifact {artifact_id!r} is absent."
            )
        )
    for artifact_id in sorted(required_ids & records.keys()):
        record = records[artifact_id]
        if record.status is not ArtifactStatus.COMPLETE:
            findings.append(
                _finding(
                    "incomplete-artifact",
                    f"Required artifact {artifact_id!r} is {record.status.value}.",
                )
            )
        if len(record.evidence.split()) < 3:
            findings.append(
                _finding(
                    "weak-artifact-evidence",
                    f"Artifact {artifact_id!r} needs specific review or "
                    "reproduction evidence.",
                    FindingSeverity.WARNING,
                )
            )
    for artifact_id in sorted(records.keys() - required_ids):
        findings.append(
            _finding(
                "extra-artifact",
                f"Artifact {artifact_id!r} is not required; keep it only if it "
                "strengthens the narrative.",
                FindingSeverity.WARNING,
            )
        )

    return ValidationReport(subject=manifest.project_slug, findings=findings)
