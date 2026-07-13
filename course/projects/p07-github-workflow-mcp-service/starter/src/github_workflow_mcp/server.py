from __future__ import annotations

from fastmcp import FastMCP

from github_workflow_mcp.github import GitHubGateway
from github_workflow_mcp.models import CapabilityPolicy
from github_workflow_mcp.store import StateStore


def create_server(
    gateway: GitHubGateway,
    store: StateStore,
    policy: CapabilityPolicy,
) -> FastMCP:
    raise NotImplementedError("implement the bounded MCP capability surface")
