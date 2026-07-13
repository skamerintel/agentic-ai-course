from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette

from github_workflow_mcp.store import StateStore


def validate_signature(body: bytes, signature: str | None, secret: str) -> None:
    raise NotImplementedError("validate X-Hub-Signature-256 over the raw body")


def create_http_app(
    server: FastMCP,
    store: StateStore,
    *,
    webhook_secret: str,
) -> Starlette:
    raise NotImplementedError("mount MCP, health, and signed webhook routes")
