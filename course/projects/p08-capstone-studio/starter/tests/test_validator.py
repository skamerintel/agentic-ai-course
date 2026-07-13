from __future__ import annotations

from capstone_studio.models import (
    ArtifactStatus,
    CapstoneProposal,
    FindingSeverity,
)
from capstone_studio.validator import validate_artifact_manifest, validate_proposal


def blocking_codes(report) -> set[str]:
    return {
        finding.code
        for finding in report.findings
        if finding.severity is FindingSeverity.BLOCKING
    }


def test_weak_proposal_rejects_chatbot_scope(weak_proposal: CapstoneProposal) -> None:
    assert "primary-interface" in blocking_codes(validate_proposal(weak_proposal))


def test_weak_proposal_rejects_decorative_architecture(
    weak_proposal: CapstoneProposal,
) -> None:
    codes = blocking_codes(validate_proposal(weak_proposal))
    assert {"workflow-modes", "responses-api", "langgraph", "postgres"} <= codes


def test_weak_proposal_rejects_shallow_evaluation(
    weak_proposal: CapstoneProposal,
) -> None:
    codes = blocking_codes(validate_proposal(weak_proposal))
    assert {"ground-truth-size", "holdout", "iterations", "failure-slices"} <= codes


def test_weak_proposal_rejects_model_controlled_authority(
    weak_proposal: CapstoneProposal,
) -> None:
    codes = blocking_codes(validate_proposal(weak_proposal))
    assert {"approval", "mcp-authority"} <= codes


def test_complete_manifest_passes(complete_manifest, requirements) -> None:
    assert validate_artifact_manifest(complete_manifest, requirements).passed


def test_manifest_reports_missing_and_incomplete(
    complete_manifest, requirements
) -> None:
    complete_manifest.artifacts.pop()
    complete_manifest.artifacts[0].status = ArtifactStatus.DEFERRED

    codes = blocking_codes(validate_artifact_manifest(complete_manifest, requirements))
    assert {"missing-artifact", "incomplete-artifact"} <= codes


def test_manifest_reports_duplicates(complete_manifest, requirements) -> None:
    complete_manifest.artifacts.append(complete_manifest.artifacts[0].model_copy())

    assert "duplicate-artifact" in blocking_codes(
        validate_artifact_manifest(complete_manifest, requirements)
    )
