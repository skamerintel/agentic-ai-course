from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intake_normalizer.models import ServiceRequest


@dataclass(frozen=True)
class ProviderSuccess:
    payload: dict[str, Any]
    response_id: str | None
    model: str
    input_tokens: int | None
    output_tokens: int | None


@dataclass(frozen=True)
class ProviderRefusal:
    reason: str
    response_id: str | None
    model: str


ProviderResponse = ProviderSuccess | ProviderRefusal
ProviderCall = Callable[[ServiceRequest], ProviderResponse]


class ProviderFailure(Exception):
    def __init__(self, code: str, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


class FixtureGateway:
    def __init__(self, fixture_path: str | Path) -> None:
        self._sequences: dict[str, list[dict[str, Any]]] = json.loads(
            Path(fixture_path).read_text(encoding="utf-8")
        )
        self._positions: dict[str, int] = {}

    def __call__(self, request: ServiceRequest) -> ProviderResponse:
        sequence = self._sequences[request.id]
        position = self._positions.get(request.id, 0)
        if position >= len(sequence):
            raise ProviderFailure(
                "fixture_exhausted",
                f"no fixture step remains for {request.id}",
                retryable=False,
            )
        self._positions[request.id] = position + 1
        step = sequence[position]
        kind = step["kind"]
        if kind == "failure":
            raise ProviderFailure(
                str(step["code"]),
                str(step["message"]),
                retryable=bool(step["retryable"]),
            )
        if kind == "refusal":
            return ProviderRefusal(
                reason=str(step["reason"]),
                response_id=str(step["response_id"]),
                model=str(step["model"]),
            )
        if kind != "success":
            raise ProviderFailure(
                "invalid_fixture",
                f"unknown fixture kind: {kind}",
                retryable=False,
            )
        return ProviderSuccess(
            payload=dict(step["payload"]),
            response_id=str(step["response_id"]),
            model=str(step["model"]),
            input_tokens=int(step["input_tokens"]),
            output_tokens=int(step["output_tokens"]),
        )


class OpenAIResponsesGateway:
    def __init__(self, model: str, timeout_seconds: float = 60.0) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds

    def __call__(self, request: ServiceRequest) -> ProviderResponse:
        raise NotImplementedError("implement the live structured-output adapter")
