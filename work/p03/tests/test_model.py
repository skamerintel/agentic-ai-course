import pytest

from operations_agent.data import load_scenarios
from operations_agent.model import ModelGatewayError, ScriptedModelSession
from operations_agent.models import ToolResult, ToolStatus


def test_scripted_session_requires_matching_call_ids() -> None:
    scenario = load_scenarios("fixtures/scenarios.json")[0]
    session = ScriptedModelSession(scenario)
    turn = session.respond()

    assert turn.tool_calls[0].call_id == "s01-status"
    with pytest.raises(ModelGatewayError, match="call IDs"):
        session.respond(
            [
                ToolResult(
                    call_id="wrong",
                    tool_name="get_service_status",
                    status=ToolStatus.SUCCESS,
                    data={},
                )
            ]
        )
