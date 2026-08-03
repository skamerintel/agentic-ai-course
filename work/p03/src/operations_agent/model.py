from __future__ import annotations

import json
import os
from collections.abc import Iterable
from typing import Any, Protocol, cast

import anthropic
from anthropic.lib.bedrock import AnthropicBedrock

from operations_agent.models import ModelTurn, Scenario, ToolCall, ToolResult


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


def _build_client(
    timeout_seconds: float,
) -> anthropic.Anthropic | AnthropicBedrock:
    """Direct Anthropic API if ANTHROPIC_API_KEY is set, else Bedrock.

    Lets a learner switch providers by setting env vars only, with no code
    change: ANTHROPIC_API_KEY for the direct API, or
    AWS_BEARER_TOKEN_BEDROCK/AWS_REGION (read natively by AnthropicBedrock)
    for Bedrock.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic(timeout=timeout_seconds)
    return AnthropicBedrock(timeout=timeout_seconds)


def _to_claude_tools(tool_schemas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "name": schema["name"],
            "description": schema["description"],
            "input_schema": schema["parameters"],
        }
        for schema in tool_schemas
    ]


class ClaudeSession:
    def __init__(
        self,
        user_request: str,
        model: str,
        tool_schemas: list[dict[str, Any]],
        timeout_seconds: float = 60.0,
        max_tokens: int = 1024,
    ) -> None:
        self.model = model
        self.tools = _to_claude_tools(tool_schemas)
        self.max_tokens = max_tokens
        self._client = _build_client(timeout_seconds)
        self._messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_request}
        ]

    def respond(self, tool_outputs: list[ToolResult] | None = None) -> ModelTurn:
        if tool_outputs:
            self._messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": result.call_id,
                            "content": result.model_output(),
                        }
                        for result in tool_outputs
                    ],
                }
            )

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=cast(Iterable[anthropic.types.ToolUnionParam], self.tools),
                messages=cast(Iterable[anthropic.types.MessageParam], self._messages),
            )
        except anthropic.APIError as error:
            raise ModelGatewayError(str(error)) from error

        self._messages.append({"role": "assistant", "content": response.content})

        tool_calls = [
            ToolCall(
                call_id=block.id,
                name=block.name,
                arguments=json.dumps(block.input, sort_keys=True),
            )
            for block in response.content
            if block.type == "tool_use"
        ]
        final_text = None
        if not tool_calls:
            text_blocks = [
                block.text for block in response.content if block.type == "text"
            ]
            final_text = "".join(text_blocks) or None

        return ModelTurn(
            response_id=response.id,
            tool_calls=tool_calls,
            final_text=final_text,
        )
