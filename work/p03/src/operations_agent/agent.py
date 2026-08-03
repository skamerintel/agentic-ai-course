from __future__ import annotations

from dataclasses import dataclass

from operations_agent.model import ModelGatewayError, ModelSession
from operations_agent.models import (
    AgentResult,
    StopReason,
    ToolResult,
    TraceEvent,
    TraceKind,
)
from operations_agent.tools import ToolRegistry


@dataclass(frozen=True)
class AgentConfig:
    max_iterations: int = 6
    max_total_tool_calls: int = 10
    max_repeated_calls_per_signature: int = 2


DEFAULT_AGENT_CONFIG = AgentConfig()


def run_agent(
    session: ModelSession,
    registry: ToolRegistry,
    config: AgentConfig = DEFAULT_AGENT_CONFIG,
) -> AgentResult:
    trace: list[TraceEvent] = []
    sequence = 0
    iteration = 0
    tool_call_count = 0
    signature_counts: dict[str, int] = {}
    pending_outputs: list[ToolResult] | None = None

    def next_sequence() -> int:
        nonlocal sequence
        sequence += 1
        return sequence

    def stop(reason: StopReason) -> AgentResult:
        trace.append(
            TraceEvent(
                sequence=next_sequence(),
                kind=TraceKind.STOP,
                iteration=iteration,
                status=reason,
            )
        )
        return AgentResult(
            stop_reason=reason,
            iterations=iteration,
            tool_call_count=tool_call_count,
            final_answer=None,
            trace=trace,
        )

    while True:
        iteration += 1
        if iteration > config.max_iterations:
            iteration -= 1
            return stop(StopReason.ITERATION_LIMIT)

        try:
            turn = session.respond(pending_outputs)
        except ModelGatewayError:
            return stop(StopReason.MODEL_ERROR)

        trace.append(
            TraceEvent(
                sequence=next_sequence(),
                kind=TraceKind.MODEL_TURN,
                iteration=iteration,
                response_id=turn.response_id,
            )
        )

        if turn.final_text is not None:
            trace.append(
                TraceEvent(
                    sequence=next_sequence(),
                    kind=TraceKind.FINAL_ANSWER,
                    iteration=iteration,
                    detail=turn.final_text,
                )
            )
            trace.append(
                TraceEvent(
                    sequence=next_sequence(),
                    kind=TraceKind.STOP,
                    iteration=iteration,
                    status=StopReason.COMPLETED,
                )
            )
            return AgentResult(
                stop_reason=StopReason.COMPLETED,
                iterations=iteration,
                tool_call_count=tool_call_count,
                final_answer=turn.final_text,
                trace=trace,
            )

        if not turn.tool_calls:
            return stop(StopReason.EMPTY_TURN)

        pending_outputs = []
        for call in turn.tool_calls:
            trace.append(
                TraceEvent(
                    sequence=next_sequence(),
                    kind=TraceKind.TOOL_CALL,
                    iteration=iteration,
                    call_id=call.call_id,
                    tool_name=call.name,
                )
            )

            if tool_call_count >= config.max_total_tool_calls:
                return stop(StopReason.TOTAL_CALL_LIMIT)

            signature = call.signature()
            repeat_limit = config.max_repeated_calls_per_signature
            if signature_counts.get(signature, 0) >= repeat_limit:
                return stop(StopReason.REPEATED_CALL_LIMIT)

            tool_call_count += 1
            signature_counts[signature] = signature_counts.get(signature, 0) + 1
            result = registry.execute(call)
            pending_outputs.append(result)
            trace.append(
                TraceEvent(
                    sequence=next_sequence(),
                    kind=TraceKind.TOOL_RESULT,
                    iteration=iteration,
                    call_id=result.call_id,
                    tool_name=result.tool_name,
                    status=result.status,
                )
            )
