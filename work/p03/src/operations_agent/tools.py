from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

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
                message=f"unknown tool: {call.name}",
            )

        try:
            raw_arguments = json.loads(call.arguments)
            arguments = definition.arguments_model.model_validate(raw_arguments)
        except (json.JSONDecodeError, ValidationError) as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.INVALID_ARGUMENTS,
                message=str(error),
            )

        try:
            data = definition.handler(arguments)
        except ToolNotFoundError as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.NOT_FOUND,
                message=str(error),
            )
        except RetryableToolError as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.RETRYABLE_ERROR,
                message=str(error),
            )
        except TerminalToolError as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.name,
                status=ToolStatus.TERMINAL_ERROR,
                message=str(error),
            )

        return ToolResult(
            call_id=call.call_id,
            tool_name=call.name,
            status=ToolStatus.SUCCESS,
            data=data,
        )


def build_registry(store: OperationsStore) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="get_service_status",
            description=(
                "Get the current status of one named service by exact name. "
                "Returns operational state, region, and a short status detail "
                "as of the last update. Use this for 'is X up / healthy / "
                "degraded' questions."
            ),
            arguments_model=GetServiceStatusArgs,
            handler=lambda args: store.get_service_status(
                cast(GetServiceStatusArgs, args).service_name
            ),
        )
    )
    registry.register(
        ToolDefinition(
            name="search_incidents",
            description=(
                "Search historical incidents for one named service, most "
                "recent first, up to a caller-supplied limit. Use this to "
                "explain why a service is degraded or to show recent "
                "incident history."
            ),
            arguments_model=SearchIncidentsArgs,
            handler=lambda args: store.search_incidents(
                cast(SearchIncidentsArgs, args).service_name,
                cast(SearchIncidentsArgs, args).limit,
            ),
        )
    )
    registry.register(
        ToolDefinition(
            name="get_asset",
            description=(
                "Get one managed asset by its exact asset ID (pattern like "
                "LAP-204). Returns kind, owner, location, and status. Use "
                "this only when the user supplies or implies a specific "
                "asset identifier."
            ),
            arguments_model=GetAssetArgs,
            handler=lambda args: store.get_asset(cast(GetAssetArgs, args).asset_id),
        )
    )
    return registry
