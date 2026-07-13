import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from github_workflow_mcp.server import create_server


async def test_capability_catalog_excludes_human_approval(
    fixture_gateway, memory_store, policy
) -> None:
    server = create_server(fixture_gateway, memory_store, policy)
    async with Client(server) as client:
        names = {tool.name for tool in await client.list_tools()}

    assert names == {
        "get_repository_overview",
        "list_open_issues",
        "list_open_pull_requests",
        "propose_issue_comment",
        "execute_approved_comment",
    }
    assert "approve_proposal" not in names


async def test_read_tool_and_policy_resource(
    fixture_gateway, memory_store, policy
) -> None:
    server = create_server(fixture_gateway, memory_store, policy)
    async with Client(server) as client:
        issues = await client.call_tool(
            "list_open_issues",
            {"owner": "acme", "repo": "payments-service", "limit": 2},
        )
        resource = await client.read_resource("github://acme/payments-service/policy")

    assert issues.data["truncated"] is True
    assert len(issues.data["items"]) == 2
    assert "approval_required" in resource[0].text


async def test_comment_requires_external_approval_and_replays(
    fixture_gateway, memory_store, policy
) -> None:
    server = create_server(fixture_gateway, memory_store, policy)
    async with Client(server) as client:
        proposed = await client.call_tool(
            "propose_issue_comment",
            {
                "owner": "acme",
                "repo": "payments-service",
                "issue_number": 41,
                "body": "We are investigating this retry behavior.",
                "reason": "Provide bounded status to the reporter.",
            },
        )
        proposal_id = proposed.data["proposal_id"]
        with pytest.raises(ToolError):
            await client.call_tool(
                "execute_approved_comment", {"proposal_id": proposal_id}
            )
        memory_store.approve(proposal_id, "mentor@example.com")
        first = await client.call_tool(
            "execute_approved_comment", {"proposal_id": proposal_id}
        )
        second = await client.call_tool(
            "execute_approved_comment", {"proposal_id": proposal_id}
        )

    assert first.data["replayed"] is False
    assert second.data["replayed"] is True
    assert fixture_gateway.comment_calls == 1
