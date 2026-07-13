from __future__ import annotations

import hashlib
import hmac
import json
from typing import cast

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from github_workflow_mcp.errors import (
    DeliveryConflict,
    InvalidWebhookSignature,
)
from github_workflow_mcp.models import (
    DeliveryStatus,
    PullRequestWebhook,
)
from github_workflow_mcp.store import StateStore


def validate_signature(body: bytes, signature: str | None, secret: str) -> None:
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if signature is None or not hmac.compare_digest(expected, signature):
        raise InvalidWebhookSignature("signature mismatch")


def create_http_app(
    server: FastMCP,
    store: StateStore,
    *,
    webhook_secret: str,
) -> Starlette:
    app = cast(
        Starlette,
        server.http_app(path="/mcp", stateless_http=True, json_response=True),
    )

    async def health(_request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def webhook(request: Request) -> JSONResponse:
        body = await request.body()
        try:
            validate_signature(
                body,
                request.headers.get("x-hub-signature-256"),
                webhook_secret,
            )
        except InvalidWebhookSignature as exc:
            return JSONResponse({"error": exc.code}, status_code=401)

        delivery_id = request.headers.get("x-github-delivery")
        event = request.headers.get("x-github-event")
        if not delivery_id or not event:
            return JSONResponse({"error": "missing_webhook_headers"}, status_code=400)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return JSONResponse({"error": "invalid_json"}, status_code=400)

        action: str | None = None
        repository: str | None = None
        pull_request_number: int | None = None
        if event == "pull_request":
            parsed = PullRequestWebhook.model_validate(payload, strict=True)
            action = parsed.action
            repository = parsed.repository.full_name
            pull_request_number = parsed.pull_request.number
        try:
            receipt = store.record_delivery(
                delivery_id,
                body,
                event,
                action=action,
                repository=repository,
                pull_request_number=pull_request_number,
            )
        except DeliveryConflict as exc:
            return JSONResponse({"error": exc.code}, status_code=409)
        status_code = 202 if receipt.status is DeliveryStatus.ACCEPTED else 200
        return JSONResponse(receipt.model_dump(mode="json"), status_code=status_code)

    app.routes.append(Route("/health", health, methods=["GET"]))
    app.routes.append(Route("/webhooks/github", webhook, methods=["POST"]))
    return app
