from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from capstone_studio.models import ArtifactManifest, CapstoneProposal, RequiredArtifact


@pytest.fixture
def weak_proposal() -> CapstoneProposal:
    return CapstoneProposal.model_validate_json(
        Path("fixtures/weak-proposal.json").read_text()
    )


@pytest.fixture
def complete_manifest() -> ArtifactManifest:
    requirements = json.loads(Path("data/required-artifacts.json").read_text())
    return ArtifactManifest.model_validate_json(
        json.dumps(
            {
                "project_slug": "support-escalation-investigator",
                "repository_url": "https://github.example/acme/support-investigator",
                "artifacts": [
                    {
                        "id": item["id"],
                        "path": f"reports/{item['id']}.md",
                        "status": "complete",
                        "evidence": f"Reviewed evidence for {item['id']}",
                    }
                    for item in requirements
                ],
            }
        )
    )


@pytest.fixture
def requirements() -> list[RequiredArtifact]:
    return TypeAdapter(list[RequiredArtifact]).validate_json(
        Path("data/required-artifacts.json").read_text()
    )
