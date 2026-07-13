from __future__ import annotations

import os
from pathlib import Path

from github_workflow_mcp.data import load_json, load_policy
from github_workflow_mcp.github import FixtureGitHubGateway, HttpGitHubGateway
from github_workflow_mcp.server import create_server
from github_workflow_mcp.store import StateStore
from github_workflow_mcp.webhook import create_http_app


def build_components():
    mode = os.getenv("GITHUB_MCP_MODE", "fixture")
    policy = load_policy(
        os.getenv("GITHUB_MCP_POLICY_PATH", "data/capability-policy.json")
    )
    store = StateStore(os.getenv("GITHUB_MCP_STATE_PATH", "github-workflow-mcp.sqlite"))
    if mode == "fixture":
        gateway = FixtureGitHubGateway(
            load_json(os.getenv("GITHUB_MCP_FIXTURE_PATH", "fixtures/github-api.json"))
        )
    elif mode == "github":
        gateway = HttpGitHubGateway(
            os.environ["GITHUB_TOKEN"],
            base_url=os.getenv("GITHUB_API_URL", "https://api.github.com"),
        )
    else:
        raise ValueError(f"unsupported GITHUB_MCP_MODE: {mode}")
    server = create_server(gateway, store, policy)
    return server, store


def build_http_app():
    server, store = build_components()
    return create_http_app(
        server,
        store,
        webhook_secret=os.environ["GITHUB_MCP_WEBHOOK_SECRET"],
    )


def ensure_state_parent() -> None:
    path = Path(os.getenv("GITHUB_MCP_STATE_PATH", "github-workflow-mcp.sqlite"))
    path.parent.mkdir(parents=True, exist_ok=True)
