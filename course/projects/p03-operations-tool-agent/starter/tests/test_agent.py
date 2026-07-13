from operations_agent.agent import AgentConfig, run_agent
from operations_agent.data import OperationsStore, load_scenarios
from operations_agent.model import ScriptedModelSession
from operations_agent.models import StopReason, TraceKind
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
