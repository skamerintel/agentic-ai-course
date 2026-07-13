from __future__ import annotations

from capstone_studio.models import (
    ArtifactManifest,
    CapstoneProposal,
    RequiredArtifact,
    ValidationReport,
)


def validate_proposal(proposal: CapstoneProposal) -> ValidationReport:
    """Return all capstone proposal gate findings in one report."""
    raise NotImplementedError("implement the cross-field proposal gate")


def validate_artifact_manifest(
    manifest: ArtifactManifest,
    requirements: list[RequiredArtifact],
) -> ValidationReport:
    """Return missing, incomplete, duplicate, and weak artifact findings."""
    raise NotImplementedError("implement final portfolio artifact validation")
