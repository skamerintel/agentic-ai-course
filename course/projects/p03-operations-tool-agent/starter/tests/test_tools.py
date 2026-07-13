from operations_agent.data import OperationsStore
from operations_agent.models import ToolCall, ToolStatus
from operations_agent.tools import build_registry


def registry():
    return build_registry(OperationsStore("data"))


def test_exposes_three_strict_read_only_schemas() -> None:
    schemas = registry().schemas()

    assert {item["name"] for item in schemas} == {
        "get_service_status",
        "search_incidents",
        "get_asset",
    }
    assert all(item["type"] == "function" for item in schemas)
    assert all(item["strict"] is True for item in schemas)
    assert all(item["parameters"]["additionalProperties"] is False for item in schemas)


def test_validates_arguments_and_preserves_call_id() -> None:
    result = registry().execute(
        ToolCall(call_id="call-1", name="get_asset", arguments='{"asset":"LAP-204"}')
    )

    assert result.call_id == "call-1"
    assert result.status is ToolStatus.INVALID_ARGUMENTS


def test_returns_not_found_unknown_retryable_and_terminal_results() -> None:
    tool_registry = registry()

    not_found = tool_registry.execute(
        ToolCall(
            call_id="not-found",
            name="get_service_status",
            arguments='{"service_name":"lunar"}',
        )
    )
    unknown = tool_registry.execute(
        ToolCall(call_id="unknown", name="delete_asset", arguments="{}")
    )
    retryable = tool_registry.execute(
        ToolCall(
            call_id="retryable",
            name="get_service_status",
            arguments='{"service_name":"payments"}',
        )
    )
    terminal = tool_registry.execute(
        ToolCall(
            call_id="terminal",
            name="get_asset",
            arguments='{"asset_id":"LAP-500"}',
        )
    )

    assert not_found.status is ToolStatus.NOT_FOUND
    assert unknown.status is ToolStatus.UNKNOWN_TOOL
    assert retryable.status is ToolStatus.RETRYABLE_ERROR
    assert terminal.status is ToolStatus.TERMINAL_ERROR
