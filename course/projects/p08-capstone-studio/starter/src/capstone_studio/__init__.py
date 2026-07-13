"""Capstone proposal and evidence validation."""

from capstone_studio.models import ArtifactManifest, CapstoneProposal
from capstone_studio.validator import validate_artifact_manifest, validate_proposal

__all__ = [
    "ArtifactManifest",
    "CapstoneProposal",
    "validate_artifact_manifest",
    "validate_proposal",
]
