from __future__ import annotations

from typing import Any, Protocol

import httpx

from github_workflow_mcp.errors import RepositoryNotFound
from github_workflow_mcp.models import (
    GitHubComment,
    IssueListResult,
    IssueSummary,
    PullRequestListResult,
    PullRequestSummary,
    RepositoryName,
    RepositoryOverview,
)


class GitHubGateway(Protocol):
    def get_repository(self, owner: str, repo: str) -> RepositoryOverview: ...

    def list_issues(self, owner: str, repo: str, limit: int) -> IssueListResult: ...

    def list_pull_requests(
        self, owner: str, repo: str, limit: int
    ) -> PullRequestListResult: ...

    def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        *,
        idempotency_key: str,
    ) -> GitHubComment: ...


class FixtureGitHubGateway:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.repositories = payload["repositories"]
        self.comments: dict[str, GitHubComment] = {}
        self.comment_calls = 0

    def _repository(self, owner: str, repo: str) -> dict[str, Any]:
        RepositoryName(owner=owner, repo=repo)
        value = self.repositories.get(f"{owner}/{repo}")
        if value is None:
            raise RepositoryNotFound(f"{owner}/{repo}")
        return value

    def get_repository(self, owner: str, repo: str) -> RepositoryOverview:
        return RepositoryOverview.model_validate(
            self._repository(owner, repo)["repository"], strict=True
        )

    def list_issues(self, owner: str, repo: str, limit: int) -> IssueListResult:
        values = self._repository(owner, repo)["issues"]
        return IssueListResult(
            items=[
                IssueSummary.model_validate(item, strict=True)
                for item in values[:limit]
            ],
            truncated=len(values) > limit,
        )

    def list_pull_requests(
        self, owner: str, repo: str, limit: int
    ) -> PullRequestListResult:
        values = self._repository(owner, repo)["pull_requests"]
        return PullRequestListResult(
            items=[
                PullRequestSummary.model_validate(item, strict=True)
                for item in values[:limit]
            ],
            truncated=len(values) > limit,
        )

    def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        *,
        idempotency_key: str,
    ) -> GitHubComment:
        self._repository(owner, repo)
        existing = self.comments.get(idempotency_key)
        if existing is not None:
            return existing
        self.comment_calls += 1
        comment = GitHubComment(
            comment_id=10_000 + self.comment_calls,
            url=f"https://github.test/{owner}/{repo}/issues/{issue_number}#comment-{self.comment_calls}",
        )
        self.comments[idempotency_key] = comment
        return comment


class HttpGitHubGateway:
    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://api.github.com",
        timeout_seconds: float = 10.0,
        max_pages: int = 5,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.max_pages = max_pages
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout_seconds,
            transport=transport,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "github-workflow-mcp/0.1",
            },
        )

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        raise NotImplementedError("implement GitHub failure classification")

    def _paged(self, url: str, limit: int) -> tuple[list[dict[str, Any]], bool]:
        raise NotImplementedError("implement bounded Link-header pagination")

    def get_repository(self, owner: str, repo: str) -> RepositoryOverview:
        raise NotImplementedError("implement repository response normalization")

    def list_issues(self, owner: str, repo: str, limit: int) -> IssueListResult:
        raise NotImplementedError("implement issue pagination and PR filtering")

    def list_pull_requests(
        self, owner: str, repo: str, limit: int
    ) -> PullRequestListResult:
        raise NotImplementedError("implement pull-request pagination")

    def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        *,
        idempotency_key: str,
    ) -> GitHubComment:
        raise NotImplementedError("implement marker-based idempotent comment write")
