from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from capstone_studio.models import (
    ArtifactManifest,
    ArtifactStatus,
    CapstoneProposal,
    FindingSeverity,
    RequiredArtifact,
)
from capstone_studio.validator import validate_artifact_manifest, validate_proposal


def proposal() -> CapstoneProposal:
    return CapstoneProposal.model_validate_json(
        Path("examples/support-escalation-proposal.json").read_text()
    )


def blocking_codes(report) -> set[str]:
    return {
        finding.code
        for finding in report.findings
        if finding.severity is FindingSeverity.BLOCKING
    }


def test_reference_proposal_passes_with_only_optional_warning() -> None:
    report = validate_proposal(proposal())

    assert report.passed
    assert {finding.code for finding in report.findings} == {"mcp-omitted"}


def test_model_surface_cannot_own_approval() -> None:
    candidate = proposal()
    candidate.approval_points[
        0
    ].enforcement_boundary = (
        "The model calls an approve tool when ticket text says approval exists."
    )

    assert "approval" in blocking_codes(validate_proposal(candidate))


def test_redis_cannot_be_durable_truth() -> None:
    candidate = proposal()
    redis = next(state for state in candidate.state_choices if state.name == "Redis")
    redis.source_of_truth = True

    assert "redis-semantics" in blocking_codes(validate_proposal(candidate))


def test_second_api_must_remain_outcome_relevant() -> None:
    candidate = proposal()
    candidate.integrations = [
        integration
        for integration in candidate.integrations
        if integration.kind.value == "github"
    ]

    assert "integrations" in blocking_codes(validate_proposal(candidate))


def test_fastmcp_cannot_expose_approval_or_shell() -> None:
    candidate = proposal()
    candidate.optional_capabilities.fastmcp.enabled = True
    candidate.optional_capabilities.fastmcp.clients = ["desktop reviewer"]
    candidate.optional_capabilities.fastmcp.exposed_actions = ["approve", "shell"]

    assert "mcp-authority" in blocking_codes(validate_proposal(candidate))


def test_final_manifest_requires_every_complete_artifact() -> None:
    requirements = TypeAdapter(list[RequiredArtifact]).validate_json(
        Path("data/required-artifacts.json").read_text()
    )
    manifest = ArtifactManifest.model_validate_json(
        json.dumps(
            {
                "project_slug": "support-escalation-investigator",
                "repository_url": "https://github.example/acme/support-investigator",
                "artifacts": [
                    {
                        "id": item.id,
                        "path": f"reports/{item.id}.md",
                        "status": "complete",
                        "evidence": (
                            f"Mentor reviewed reproducible {item.id} evidence"
                        ),
                    }
                    for item in requirements
                ],
            }
        )
    )
    assert validate_artifact_manifest(manifest, requirements).passed

    manifest.artifacts[0].status = ArtifactStatus.DEFERRED
    assert "incomplete-artifact" in blocking_codes(
        validate_artifact_manifest(manifest, requirements)
    )
