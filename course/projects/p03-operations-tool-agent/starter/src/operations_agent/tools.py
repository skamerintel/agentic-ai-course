from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from operations_agent.data import OperationsStore
from operations_agent.models import ToolCall, ToolResult

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
        raise NotImplementedError("implement strict function schemas")

    def execute(self, call: ToolCall) -> ToolResult:
        raise NotImplementedError("implement validated deterministic dispatch")


def build_registry(store: OperationsStore) -> ToolRegistry:
    raise NotImplementedError("register the three read-only tools")
