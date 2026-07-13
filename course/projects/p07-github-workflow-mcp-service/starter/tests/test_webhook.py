import hashlib
import hmac
import json
from pathlib import Path

import httpx
from asgi_lifespan import LifespanManager

from github_workflow_mcp.server import create_server
from github_workflow_mcp.store import StateStore
from github_workflow_mcp.webhook import create_http_app

SECRET = "test-webhook-secret"


def signature(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


async def test_health_and_signed_webhook(fixture_gateway, policy, tmp_path) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    server = create_server(fixture_gateway, store, policy)
    app = create_http_app(server, store, webhook_secret=SECRET)
    body = json.dumps(
        json.loads(Path("fixtures/webhooks/pull-request-opened.json").read_text()),
        separators=(",", ":"),
    ).encode()
    headers = {
        "x-hub-signature-256": signature(body),
        "x-github-delivery": "delivery-100",
        "x-github-event": "pull_request",
        "content-type": "application/json",
    }

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            health = await client.get("/health")
            accepted = await client.post(
                "/webhooks/github", content=body, headers=headers
            )
            duplicate = await client.post(
                "/webhooks/github", content=body, headers=headers
            )

    assert health.json() == {"status": "ok"}
    assert accepted.status_code == 202
    assert accepted.json()["status"] == "accepted"
    assert duplicate.status_code == 200
    assert duplicate.json()["status"] == "duplicate"


async def test_invalid_signature_is_rejected_before_json_parse(
    fixture_gateway, policy, tmp_path
) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    app = create_http_app(
        create_server(fixture_gateway, store, policy),
        store,
        webhook_secret=SECRET,
    )

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/webhooks/github",
                content=b"not-json",
                headers={
                    "x-hub-signature-256": "sha256=invalid",
                    "x-github-delivery": "delivery-invalid",
                    "x-github-event": "pull_request",
                },
            )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_webhook_signature"
