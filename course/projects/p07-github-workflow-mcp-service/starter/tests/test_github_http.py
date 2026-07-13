import json

import httpx
import pytest

from github_workflow_mcp.errors import PermissionDenied, RateLimited
from github_workflow_mcp.github import HttpGitHubGateway


def test_issue_pagination_filters_pull_requests() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if len(requests) == 1:
            return httpx.Response(
                200,
                json=[
                    {
                        "number": 1,
                        "title": "Issue one",
                        "body": "Body",
                        "labels": [{"name": "bug"}],
                        "user": {"login": "alice"},
                    },
                    {
                        "number": 2,
                        "title": "PR in issues API",
                        "body": "Body",
                        "labels": [],
                        "user": {"login": "bob"},
                        "pull_request": {"url": "https://api.github.test/pr/2"},
                    },
                ],
                headers={"link": '<https://api.github.test/page2>; rel="next"'},
            )
        return httpx.Response(
            200,
            json=[
                {
                    "number": 3,
                    "title": "Issue three",
                    "body": "Body",
                    "labels": [{"name": "docs"}],
                    "user": {"login": "carol"},
                }
            ],
        )

    gateway = HttpGitHubGateway(
        "token",
        base_url="https://api.github.test",
        transport=httpx.MockTransport(handler),
    )
    result = gateway.list_issues("acme", "repo", limit=10)

    assert [item.number for item in result.items] == [1, 3]
    assert len(requests) == 2


@pytest.mark.parametrize(
    ("headers", "error"),
    [
        ({"x-ratelimit-remaining": "0", "x-ratelimit-reset": "123"}, RateLimited),
        ({"x-ratelimit-remaining": "99"}, PermissionDenied),
    ],
)
def test_403_is_classified_from_rate_headers(headers, error) -> None:
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            403, headers=headers, json={"message": "denied"}
        )
    )
    gateway = HttpGitHubGateway(
        "token", base_url="https://api.github.test", transport=transport
    )

    with pytest.raises(error):
        gateway.get_repository("acme", "repo")


def test_comment_replay_finds_existing_marker() -> None:
    posts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal posts
        if request.method == "GET":
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 700,
                        "html_url": "https://github.test/comment/700",
                        "body": "Done\n\n<!-- github-workflow-mcp:proposal-7 -->",
                    }
                ],
            )
        posts += 1
        return httpx.Response(201, json=json.loads(request.content))

    gateway = HttpGitHubGateway(
        "token",
        base_url="https://api.github.test",
        transport=httpx.MockTransport(handler),
    )
    comment = gateway.create_issue_comment(
        "acme", "repo", 7, "Done", idempotency_key="proposal-7"
    )

    assert comment.comment_id == 700
    assert posts == 0
