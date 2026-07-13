from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from capstone_studio.models import ArtifactManifest, CapstoneProposal


def test_weak_proposal_is_structurally_valid(weak_proposal: CapstoneProposal) -> None:
    assert weak_proposal.title == "Universal Engineering Copilot"


def test_models_reject_unknown_fields(weak_proposal: CapstoneProposal) -> None:
    payload = weak_proposal.model_dump(mode="json")
    payload["framework_stars"] = 100_000

    with pytest.raises(ValidationError):
        CapstoneProposal.model_validate(payload)


def test_manifest_requires_slug() -> None:
    with pytest.raises(ValidationError):
        ArtifactManifest.model_validate_json(
            json.dumps(
                {
                    "project_slug": "Not A Slug",
                    "repository_url": "https://example.test/x",
                    "artifacts": [],
                }
            )
        )
