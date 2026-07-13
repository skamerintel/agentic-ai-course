from __future__ import annotations

import hashlib
import hmac
import sqlite3
from pathlib import Path

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastmcp import Client
from fastmcp.exceptions import ToolError

from github_workflow_mcp.data import load_json, load_policy
from github_workflow_mcp.github import FixtureGitHubGateway
from github_workflow_mcp.server import create_server
from github_workflow_mcp.store import StateStore
from github_workflow_mcp.webhook import create_http_app

SECRET = "holdout-secret"
pytestmark = pytest.mark.asyncio


def components(tmp_path):
    gateway = FixtureGitHubGateway(load_json("fixtures/github-api.json"))
    store = StateStore(tmp_path / "holdout-state.sqlite")
    policy = load_policy("data/capability-policy.json")
    server = create_server(gateway, store, policy)
    return gateway, store, server


def sign(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


async def test_model_cannot_approve_its_own_comment(tmp_path) -> None:
    gateway, _store, server = components(tmp_path)
    async with Client(server) as client:
        names = {tool.name for tool in await client.list_tools()}
        proposal = await client.call_tool(
            "propose_issue_comment",
            {
                "owner": "acme",
                "repo": "payments-service",
                "issue_number": 42,
                "body": "The issue says approval is granted, so post now.",
                "reason": "Untrusted issue requested it.",
            },
        )
        with pytest.raises(ToolError):
            await client.call_tool(
                "execute_approved_comment",
                {"proposal_id": proposal.data["proposal_id"]},
            )

    assert "approve_proposal" not in names
    assert gateway.comment_calls == 0


async def test_invalid_signature_rejected_before_persistence(tmp_path) -> None:
    _gateway, store, server = components(tmp_path)
    app = create_http_app(server, store, webhook_secret=SECRET)
    body = b'{"action":"opened"}'
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/webhooks/github",
                content=body,
                headers={
                    "x-hub-signature-256": "sha256=invalid",
                    "x-github-delivery": "holdout-invalid",
                    "x-github-event": "pull_request",
                },
            )
    with sqlite3.connect(store.path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]

    assert response.status_code == 401
    assert count == 0


async def test_changed_redelivery_conflicts(tmp_path) -> None:
    _gateway, store, server = components(tmp_path)
    app = create_http_app(server, store, webhook_secret=SECRET)
    original = Path("fixtures/webhooks/pull-request-opened.json").read_bytes()
    changed = Path("fixtures/webhooks/pull-request-synchronize.json").read_bytes()
    base_headers = {
        "x-github-delivery": "holdout-delivery",
        "x-github-event": "pull_request",
        "content-type": "application/json",
    }
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            first = await client.post(
                "/webhooks/github",
                content=original,
                headers={**base_headers, "x-hub-signature-256": sign(original)},
            )
            conflict = await client.post(
                "/webhooks/github",
                content=changed,
                headers={**base_headers, "x-hub-signature-256": sign(changed)},
            )

    assert first.status_code == 202
    assert conflict.status_code == 409
    assert conflict.json()["error"] == "delivery_conflict"


async def test_lost_local_receipt_reconciles_existing_comment(tmp_path) -> None:
    gateway, store, server = components(tmp_path)
    async with Client(server) as client:
        proposal = await client.call_tool(
            "propose_issue_comment",
            {
                "owner": "acme",
                "repo": "payments-service",
                "issue_number": 41,
                "body": "Approved status update.",
                "reason": "Reporter communication.",
            },
        )
        proposal_id = proposal.data["proposal_id"]
        store.approve(proposal_id, "mentor@example.com")
        first = await client.call_tool(
            "execute_approved_comment", {"proposal_id": proposal_id}
        )
        with sqlite3.connect(store.path) as connection:
            connection.execute(
                "DELETE FROM executions WHERE proposal_id = ?", (proposal_id,)
            )
            connection.execute(
                "UPDATE proposals SET status = 'approved' WHERE proposal_id = ?",
                (proposal_id,),
            )
        second = await client.call_tool(
            "execute_approved_comment", {"proposal_id": proposal_id}
        )

    assert first.data["comment_id"] == second.data["comment_id"]
    assert gateway.comment_calls == 1


async def test_untrusted_text_does_not_change_capabilities(tmp_path) -> None:
    _gateway, _store, server = components(tmp_path)
    async with Client(server) as client:
        before = {tool.name for tool in await client.list_tools()}
        issues = await client.call_tool(
            "list_open_issues",
            {"owner": "acme", "repo": "payments-service", "limit": 10},
        )
        after = {tool.name for tool in await client.list_tools()}

    injected = next(item for item in issues.data["items"] if item["number"] == 42)
    assert "approve any write" in injected["body"]
    assert before == after
