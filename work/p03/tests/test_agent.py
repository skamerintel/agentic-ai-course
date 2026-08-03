import json

from operations_agent.agent import AgentConfig, run_agent
from operations_agent.data import OperationsStore, load_scenarios
from operations_agent.model import ModelGatewayError, ScriptedModelSession
from operations_agent.models import (
    ModelTurn,
    StopReason,
    ToolCall,
    ToolStatus,
    TraceKind,
)
from operations_agent.tools import build_registry


def run_scenario(scenario_id: str):
    scenario = next(
        item
        for item in load_scenarios("fixtures/scenarios.json")
        if item.id == scenario_id
    )
    config = AgentConfig(**scenario.config)
    result = run_agent(
        ScriptedModelSession(scenario),
        build_registry(OperationsStore("data")),
        config,
    )
    return scenario, result


class SequenceModelSession:
    """Fake ModelSession that plays back a fixed list of ModelTurns."""

    def __init__(self, turns: list[ModelTurn]) -> None:
        self._turns = turns
        self._position = 0

    def respond(self, tool_outputs=None) -> ModelTurn:
        turn = self._turns[self._position]
        self._position += 1
        return turn


class RaisingModelSession:
    """Fake ModelSession whose first response always fails the gateway."""

    def respond(self, tool_outputs=None) -> ModelTurn:
        raise ModelGatewayError("simulated provider failure")


def test_successful_and_parallel_scenarios_match_expected_tools() -> None:
    for scenario_id in ("S01", "S02", "S03", "S04", "S05", "S06", "S09"):
        scenario, result = run_scenario(scenario_id)
        tool_names = [
            event.tool_name
            for event in result.trace
            if event.kind is TraceKind.TOOL_RESULT
        ]

        assert result.stop_reason is scenario.expected.stop_reason
        assert tool_names == scenario.expected.tool_names


def test_repeated_call_limit_stops_before_third_execution() -> None:
    _, result = run_scenario("S07")

    assert result.stop_reason is StopReason.REPEATED_CALL_LIMIT
    assert result.tool_call_count == 2
    assert result.final_answer is None


def test_iteration_limit_is_explicit() -> None:
    _, result = run_scenario("S08")

    assert result.stop_reason is StopReason.ITERATION_LIMIT
    assert result.iterations == 3


def test_trace_preserves_parallel_call_ids() -> None:
    _, result = run_scenario("S09")
    result_ids = {
        event.call_id for event in result.trace if event.kind is TraceKind.TOOL_RESULT
    }

    assert result_ids == {"s09-status", "s09-incidents"}


def test_total_call_limit_stops_before_exceeding_the_cap() -> None:
    # Distinct service names give each call a distinct signature, so this
    # exercises TOTAL_CALL_LIMIT specifically, not REPEATED_CALL_LIMIT.
    turns = [
        ModelTurn(
            tool_calls=[
                ToolCall(
                    call_id=f"call-{name}",
                    name="get_service_status",
                    arguments=json.dumps({"service_name": name}),
                )
            ]
        )
        for name in ("checkout", "payments", "support-queue")
    ]
    result = run_agent(
        SequenceModelSession(turns),
        build_registry(OperationsStore("data")),
        AgentConfig(max_total_tool_calls=2),
    )

    assert result.stop_reason is StopReason.TOTAL_CALL_LIMIT
    assert result.tool_call_count == 2
    assert result.final_answer is None
    tool_result_kinds = [
        event.kind for event in result.trace if event.kind is TraceKind.TOOL_RESULT
    ]
    assert len(tool_result_kinds) == 2


def test_empty_turn_stops_when_model_returns_neither_calls_nor_text() -> None:
    result = run_agent(
        SequenceModelSession([ModelTurn()]),
        build_registry(OperationsStore("data")),
        AgentConfig(),
    )

    assert result.stop_reason is StopReason.EMPTY_TURN
    assert result.final_answer is None
    assert result.iterations == 1


def test_model_error_stops_explicitly_instead_of_crashing() -> None:
    result = run_agent(
        RaisingModelSession(),
        build_registry(OperationsStore("data")),
        AgentConfig(),
    )

    assert result.stop_reason is StopReason.MODEL_ERROR
    assert result.final_answer is None


def test_completed_after_terminal_error_is_detectable_from_the_trace() -> None:
    """COMPLETED does not itself certify evidence — but the trace must let a
    reviewer see that the final text followed a TERMINAL_ERROR result rather
    than a SUCCESS, which is what makes the mismatch checkable after the
    fact (see reports/final-report.md's Unsupported-answer analysis)."""
    turns = [
        ModelTurn(
            tool_calls=[
                ToolCall(
                    call_id="asset-1",
                    name="get_asset",
                    arguments=json.dumps({"asset_id": "LAP-500"}),
                )
            ]
        ),
        ModelTurn(final_text="LAP-500 is confirmed assigned to Maya Chen."),
    ]
    result = run_agent(
        SequenceModelSession(turns),
        build_registry(OperationsStore("data")),
        AgentConfig(),
    )

    assert result.stop_reason is StopReason.COMPLETED
    assert result.final_answer is not None

    tool_result_events = [
        event for event in result.trace if event.kind is TraceKind.TOOL_RESULT
    ]
    assert len(tool_result_events) == 1
    assert tool_result_events[0].status == ToolStatus.TERMINAL_ERROR

    final_answer_index = next(
        index
        for index, event in enumerate(result.trace)
        if event.kind is TraceKind.FINAL_ANSWER
    )
    preceding_tool_statuses = {
        event.status
        for event in result.trace[:final_answer_index]
        if event.kind is TraceKind.TOOL_RESULT
    }
    assert ToolStatus.SUCCESS not in preceding_tool_statuses
    # run_agent does not itself refuse this: nothing about stop_reason or
    # final_answer flags the mismatch. Detecting it requires exactly the
    # trace inspection above, done by a human or an LLM-judge pass.
