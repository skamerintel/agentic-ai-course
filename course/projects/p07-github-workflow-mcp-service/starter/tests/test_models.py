import pytest
from pydantic import ValidationError

from github_workflow_mcp.models import RepositoryName


def test_repository_name_rejects_path_segments() -> None:
    with pytest.raises(ValidationError):
        RepositoryName(owner="acme", repo="..")


def test_repository_name_accepts_normal_github_slug() -> None:
    repository = RepositoryName(owner="acme-inc", repo="payments_service")

    assert repository.owner == "acme-inc"
