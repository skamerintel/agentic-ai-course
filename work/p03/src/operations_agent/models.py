from __future__ import annotations

import json
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ToolStatus(StrEnum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    INVALID_ARGUMENTS = "invalid_arguments"
    RETRYABLE_ERROR = "retryable_error"
    TERMINAL_ERROR = "terminal_error"
    UNKNOWN_TOOL = "unknown_tool"


class StopReason(StrEnum):
    COMPLETED = "completed"
    ITERATION_LIMIT = "iteration_limit"
    TOTAL_CALL_LIMIT = "total_call_limit"
    REPEATED_CALL_LIMIT = "repeated_call_limit"
    MODEL_ERROR = "model_error"
    EMPTY_TURN = "empty_turn"


class TraceKind(StrEnum):
    MODEL_TURN = "model_turn"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FINAL_ANSWER = "final_answer"
    STOP = "stop"


class GetServiceStatusArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    service_name: str = Field(min_length=1, max_length=80)


class SearchIncidentsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    service_name: str = Field(min_length=1, max_length=80)
    limit: int = Field(ge=1, le=5)


class GetAssetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    asset_id: str = Field(pattern=r"^[A-Z]+-[A-Z0-9]+$")


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    call_id: str
    name: str
    arguments: str

    def signature(self) -> str:
        try:
            parsed = json.loads(self.arguments)
            arguments = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        except json.JSONDecodeError:
            arguments = self.arguments
        return f"{self.name}:{arguments}"


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    call_id: str
    tool_name: str
    status: ToolStatus
    data: Any = None
    error_code: str | None = None
    message: str | None = None

    def model_output(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True)


class ModelTurn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    response_id: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    final_text: str | None = None

    @model_validator(mode="after")
    def has_calls_or_text(self) -> Self:
        if self.tool_calls and self.final_text:
            raise ValueError("model turn cannot contain calls and final_text")
        return self


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    sequence: int = Field(ge=1)
    kind: TraceKind
    iteration: int = Field(ge=0)
    response_id: str | None = None
    call_id: str | None = None
    tool_name: str | None = None
    status: str | None = None
    detail: str | None = None


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    stop_reason: StopReason
    iterations: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    final_answer: str | None = None
    trace: list[TraceEvent]


class ScenarioCall(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    call_id: str
    name: str
    arguments: dict[str, Any]


class ScenarioStep(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    tool_calls: list[ScenarioCall] = Field(default_factory=list)
    final_text: str | None = None


class ScenarioExpected(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    stop_reason: StopReason
    tool_names: list[str]


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    user_request: str
    config: dict[str, int] = Field(default_factory=dict)
    steps: list[ScenarioStep]
    expected: ScenarioExpected
