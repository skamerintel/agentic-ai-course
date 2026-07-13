from __future__ import annotations

from typing import Any, Protocol

import httpx

from github_workflow_mcp.errors import (
    PermissionDenied,
    RateLimited,
    RepositoryNotFound,
)
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
            url=(
                f"https://github.test/{owner}/{repo}/issues/{issue_number}"
                f"#comment-{self.comment_calls}"
            ),
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
        response = self.client.request(method, url, **kwargs)
        if response.status_code == 404:
            raise RepositoryNotFound(url)
        if response.status_code in {403, 429}:
            remaining = response.headers.get("x-ratelimit-remaining")
            if response.status_code == 429 or remaining == "0":
                raise RateLimited(
                    response.headers.get("retry-after")
                    or response.headers.get("x-ratelimit-reset")
                )
            raise PermissionDenied(url)
        if response.status_code in {401, 404}:
            raise PermissionDenied(url)
        response.raise_for_status()
        return response

    def _paged(self, url: str, limit: int) -> tuple[list[dict[str, Any]], bool]:
        items: list[dict[str, Any]] = []
        next_url: str | None = url
        pages = 0
        while next_url and pages < self.max_pages and len(items) < limit:
            response = self._request("GET", next_url)
            payload = response.json()
            if not isinstance(payload, list):
                raise ValueError("GitHub list endpoint returned a non-list payload")
            items.extend(item for item in payload if isinstance(item, dict))
            pages += 1
            next_link = response.links.get("next")
            next_url = next_link["url"] if next_link else None
        truncated = bool(next_url) or len(items) > limit
        return items[:limit], truncated

    def get_repository(self, owner: str, repo: str) -> RepositoryOverview:
        RepositoryName(owner=owner, repo=repo)
        payload = self._request("GET", f"/repos/{owner}/{repo}").json()
        return RepositoryOverview.model_validate(
            {
                "owner": payload["owner"]["login"],
                "name": payload["name"],
                "default_branch": payload["default_branch"],
                "private": payload["private"],
                "archived": payload["archived"],
            },
            strict=True,
        )

    def list_issues(self, owner: str, repo: str, limit: int) -> IssueListResult:
        RepositoryName(owner=owner, repo=repo)
        payload, truncated = self._paged(
            f"/repos/{owner}/{repo}/issues?state=open&per_page=100",
            min(max(limit * 2, limit), 100),
        )
        issues = [item for item in payload if "pull_request" not in item]
        normalized = [
            IssueSummary(
                number=item["number"],
                title=item["title"],
                body=item.get("body") or "",
                labels=[label["name"] for label in item.get("labels", [])],
                author=item["user"]["login"],
            )
            for item in issues[:limit]
        ]
        return IssueListResult(
            items=normalized,
            truncated=truncated or len(issues) > limit,
        )

    def list_pull_requests(
        self, owner: str, repo: str, limit: int
    ) -> PullRequestListResult:
        RepositoryName(owner=owner, repo=repo)
        payload, truncated = self._paged(
            f"/repos/{owner}/{repo}/pulls?state=open&per_page=100", limit
        )
        items = [
            PullRequestSummary(
                number=item["number"],
                title=item["title"],
                head_sha=item["head"]["sha"],
                draft=bool(item.get("draft", False)),
                labels=[label["name"] for label in item.get("labels", [])],
                author=item["user"]["login"],
            )
            for item in payload
        ]
        return PullRequestListResult(items=items, truncated=truncated)

    def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        *,
        idempotency_key: str,
    ) -> GitHubComment:
        RepositoryName(owner=owner, repo=repo)
        marker = f"<!-- github-workflow-mcp:{idempotency_key} -->"
        comments, _truncated = self._paged(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments?per_page=100",
            500,
        )
        for comment in comments:
            if marker in (comment.get("body") or ""):
                return GitHubComment(comment_id=comment["id"], url=comment["html_url"])
        response = self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": f"{body}\n\n{marker}"},
        ).json()
        return GitHubComment(comment_id=response["id"], url=response["html_url"])
