from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from operations_agent.data import (
    OperationsStore,
    RetryableToolError,
    TerminalToolError,
    ToolNotFoundError,
)
from operations_agent.models import (
    GetAssetArgs,
    GetServiceStatusArgs,
    SearchIncidentsArgs,
    ToolCall,
    ToolResult,
    ToolStatus,
)

ToolHandler = Callable[[BaseModel], Any]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    arguments_model: type[BaseModel]
    handler: ToolHandler


def _validation_message(error: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(item) for item in entry['loc'])}:{entry['type']}"
        for entry in error.errors(include_input=False)
    )


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ValueError(f"duplicate tool: {definition.name}")
        self._tools[definition.name] = definition

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": definition.name,
                "description": definition.description,
                "parameters": definition.arguments_model.model_json_schema(),
                "strict": True,
            }
            for definition in self._tools.values()
        ]

    def execute(self, call: ToolCall) -> ToolResult:
        definition = self._tools.get(call.name)
        if definition is None:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.UNKNOWN_TOOL,
                error_code="unknown_tool",
                message="requested tool is not available",
            )
        try:
            arguments = definition.arguments_model.model_validate_json(
                call.arguments, strict=True
            )
        except ValidationError as exc:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.INVALID_ARGUMENTS,
                error_code="invalid_arguments",
                message=_validation_message(exc),
            )

        try:
            data = definition.handler(arguments)
        except ToolNotFoundError as exc:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.NOT_FOUND,
                error_code="not_found",
                message=str(exc),
            )
        except RetryableToolError as exc:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.RETRYABLE_ERROR,
                error_code="retryable_tool_error",
                message=str(exc),
            )
        except TerminalToolError as exc:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.TERMINAL_ERROR,
                error_code="terminal_tool_error",
                message=str(exc),
            )

        if len(json.dumps(data, sort_keys=True)) > 4_000:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.TERMINAL_ERROR,
                error_code="result_too_large",
                message="tool result exceeded the application size limit",
            )
        return ToolResult(
            call_id=call.call_id,
            tool_name=call.name,
            status=ToolStatus.SUCCESS,
            data=data,
        )


def build_registry(store: OperationsStore) -> ToolRegistry:
    registry = ToolRegistry()

    def service_status(arguments: BaseModel) -> dict[str, Any]:
        assert isinstance(arguments, GetServiceStatusArgs)
        return store.get_service_status(arguments.service_name)

    def incident_search(arguments: BaseModel) -> list[dict[str, Any]]:
        assert isinstance(arguments, SearchIncidentsArgs)
        return store.search_incidents(arguments.service_name, arguments.limit)

    def asset_lookup(arguments: BaseModel) -> dict[str, Any]:
        assert isinstance(arguments, GetAssetArgs)
        return store.get_asset(arguments.asset_id)

    registry.register(
        ToolDefinition(
            name="get_service_status",
            description=(
                "Get the current operational status of one named service. "
                "Use for present health, not incident history."
            ),
            arguments_model=GetServiceStatusArgs,
            handler=service_status,
        )
    )
    registry.register(
        ToolDefinition(
            name="search_incidents",
            description=(
                "Return up to five recent historical incidents for one service. "
                "Use for past events, not current service health."
            ),
            arguments_model=SearchIncidentsArgs,
            handler=incident_search,
        )
    )
    registry.register(
        ToolDefinition(
            name="get_asset",
            description="Look up one managed asset by its exact asset identifier.",
            arguments_model=GetAssetArgs,
            handler=asset_lookup,
        )
    )
    return registry
