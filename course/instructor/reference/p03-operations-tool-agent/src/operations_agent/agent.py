from __future__ import annotations

from collections import Counter
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
    if (
        min(
            config.max_iterations,
            config.max_total_tool_calls,
            config.max_repeated_calls_per_signature,
        )
        < 1
    ):
        raise ValueError("agent limits must be at least one")

    trace: list[TraceEvent] = []
    repeated: Counter[str] = Counter()
    pending_outputs: list[ToolResult] | None = None
    tool_call_count = 0

    def record(kind: TraceKind, iteration: int, **values: str | None) -> None:
        trace.append(
            TraceEvent(
                sequence=len(trace) + 1,
                kind=kind,
                iteration=iteration,
                **values,
            )
        )

    def stopped(
        reason: StopReason,
        iteration: int,
        detail: str,
    ) -> AgentResult:
        record(TraceKind.STOP, iteration, status=reason.value, detail=detail)
        return AgentResult(
            stop_reason=reason,
            iterations=iteration,
            tool_call_count=tool_call_count,
            trace=trace,
        )

    for iteration in range(1, config.max_iterations + 1):
        try:
            turn = session.respond(pending_outputs)
        except ModelGatewayError as exc:
            return stopped(StopReason.MODEL_ERROR, iteration, str(exc))

        record(
            TraceKind.MODEL_TURN,
            iteration,
            response_id=turn.response_id,
            detail=f"tool_calls={len(turn.tool_calls)}",
        )
        if turn.tool_calls:
            outputs: list[ToolResult] = []
            for call in turn.tool_calls:
                record(
                    TraceKind.TOOL_CALL,
                    iteration,
                    response_id=turn.response_id,
                    call_id=call.call_id,
                    tool_name=call.name,
                )
                if tool_call_count >= config.max_total_tool_calls:
                    return stopped(
                        StopReason.TOTAL_CALL_LIMIT,
                        iteration,
                        "maximum total tool calls reached",
                    )

                signature = call.signature()
                repeated[signature] += 1
                if repeated[signature] > config.max_repeated_calls_per_signature:
                    return stopped(
                        StopReason.REPEATED_CALL_LIMIT,
                        iteration,
                        f"repeated signature blocked: {call.name}",
                    )

                result = registry.execute(call)
                tool_call_count += 1
                outputs.append(result)
                record(
                    TraceKind.TOOL_RESULT,
                    iteration,
                    call_id=result.call_id,
                    tool_name=result.tool_name,
                    status=result.status.value,
                    detail=result.error_code,
                )
            pending_outputs = outputs
            continue

        if turn.final_text and turn.final_text.strip():
            answer = turn.final_text.strip()
            record(
                TraceKind.FINAL_ANSWER,
                iteration,
                response_id=turn.response_id,
                detail=answer,
            )
            record(
                TraceKind.STOP,
                iteration,
                status=StopReason.COMPLETED.value,
                detail="model returned a final answer",
            )
            return AgentResult(
                stop_reason=StopReason.COMPLETED,
                iterations=iteration,
                tool_call_count=tool_call_count,
                final_answer=answer,
                trace=trace,
            )
        return stopped(
            StopReason.EMPTY_TURN,
            iteration,
            "model returned neither tool calls nor final text",
        )

    return stopped(
        StopReason.ITERATION_LIMIT,
        config.max_iterations,
        "maximum model iterations reached",
    )
