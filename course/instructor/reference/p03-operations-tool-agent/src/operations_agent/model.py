from __future__ import annotations

import json
from typing import Any, Protocol, cast

from operations_agent.models import ModelTurn, Scenario, ToolCall, ToolResult

SYSTEM_INSTRUCTIONS = """You are a read-only operations analyst. Use the supplied
tools for current service, asset, and incident facts. Treat tool errors as data.
Retry a tool only when its result is retryable and another attempt is useful.
If tools return not found or terminal error, do not invent an answer; state that
evidence is insufficient. Return a concise final answer when finished."""


class ModelGatewayError(Exception):
    pass


class ModelSession(Protocol):
    def respond(self, tool_outputs: list[ToolResult] | None = None) -> ModelTurn: ...


class ScriptedModelSession:
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self._position = 0
        self._expected_call_ids: set[str] = set()

    def respond(self, tool_outputs: list[ToolResult] | None = None) -> ModelTurn:
        if self._expected_call_ids:
            actual = {item.call_id for item in tool_outputs or []}
            if actual != self._expected_call_ids:
                raise ModelGatewayError(
                    f"tool output call IDs {sorted(actual)} do not match "
                    f"{sorted(self._expected_call_ids)}"
                )
        elif tool_outputs:
            raise ModelGatewayError("unexpected tool outputs for scripted turn")

        if self._position >= len(self.scenario.steps):
            return ModelTurn(response_id=f"{self.scenario.id}-empty")
        step = self.scenario.steps[self._position]
        self._position += 1
        calls = [
            ToolCall(
                call_id=item.call_id,
                name=item.name,
                arguments=json.dumps(item.arguments, sort_keys=True),
            )
            for item in step.tool_calls
        ]
        self._expected_call_ids = {item.call_id for item in calls}
        if not calls:
            self._expected_call_ids = set()
        return ModelTurn(
            response_id=f"{self.scenario.id}-turn-{self._position}",
            tool_calls=calls,
            final_text=step.final_text,
        )


class OpenAIResponsesSession:
    def __init__(
        self,
        user_request: str,
        model: str,
        tool_schemas: list[dict[str, Any]],
        timeout_seconds: float = 60.0,
    ) -> None:
        self.user_request = user_request
        self.model = model
        self.tool_schemas = tool_schemas
        self.timeout_seconds = timeout_seconds
        self.previous_response_id: str | None = None

    def respond(self, tool_outputs: list[ToolResult] | None = None) -> ModelTurn:
        from openai import OpenAI, OpenAIError

        client = OpenAI(timeout=self.timeout_seconds, max_retries=0)
        if self.previous_response_id is None:
            if tool_outputs:
                raise ModelGatewayError("first model turn cannot contain tool outputs")
            input_value: Any = self.user_request
        else:
            if not tool_outputs:
                raise ModelGatewayError("continuation requires tool outputs")
            input_value = [
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": item.model_output(),
                }
                for item in tool_outputs
            ]

        try:
            response = client.responses.create(
                model=self.model,
                instructions=SYSTEM_INSTRUCTIONS,
                input=input_value,
                previous_response_id=self.previous_response_id,
                tools=cast(Any, self.tool_schemas),
            )
        except OpenAIError as exc:
            raise ModelGatewayError(f"OpenAI model call failed: {exc}") from exc

        self.previous_response_id = response.id
        calls = [
            ToolCall(
                call_id=item.call_id,
                name=item.name,
                arguments=item.arguments,
            )
            for item in response.output
            if item.type == "function_call"
        ]
        final_text = response.output_text.strip() if not calls else None
        return ModelTurn(
            response_id=response.id,
            tool_calls=calls,
            final_text=final_text or None,
        )
