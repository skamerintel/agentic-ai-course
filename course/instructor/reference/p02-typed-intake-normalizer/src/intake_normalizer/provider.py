from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intake_normalizer.models import NormalizedIntake, ServiceRequest
from intake_normalizer.prompting import SYSTEM_INSTRUCTIONS, render_request


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


def _refusal_reason(response: Any) -> str | None:
    for output in response.output:
        if getattr(output, "type", None) != "message":
            continue
        for content in output.content:
            if getattr(content, "type", None) == "refusal":
                return str(content.refusal)
    return None


class OpenAIResponsesGateway:
    def __init__(self, model: str, timeout_seconds: float = 60.0) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds

    def __call__(self, request: ServiceRequest) -> ProviderResponse:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            AuthenticationError,
            BadRequestError,
            InternalServerError,
            NotFoundError,
            OpenAI,
            OpenAIError,
            PermissionDeniedError,
            RateLimitError,
            UnprocessableEntityError,
        )

        client = OpenAI(timeout=self.timeout_seconds, max_retries=0)
        try:
            response = client.responses.parse(
                model=self.model,
                instructions=SYSTEM_INSTRUCTIONS,
                input=render_request(request),
                text_format=NormalizedIntake,
            )
        except RateLimitError as exc:
            raise ProviderFailure("rate_limit", str(exc), retryable=True) from exc
        except APITimeoutError as exc:
            raise ProviderFailure("timeout", str(exc), retryable=True) from exc
        except APIConnectionError as exc:
            raise ProviderFailure("connection", str(exc), retryable=True) from exc
        except InternalServerError as exc:
            raise ProviderFailure("server_error", str(exc), retryable=True) from exc
        except (AuthenticationError, PermissionDeniedError) as exc:
            raise ProviderFailure("authentication", str(exc), retryable=False) from exc
        except (BadRequestError, NotFoundError, UnprocessableEntityError) as exc:
            raise ProviderFailure("invalid_request", str(exc), retryable=False) from exc
        except APIStatusError as exc:
            retryable = exc.status_code >= 500
            raise ProviderFailure(
                f"http_{exc.status_code}", str(exc), retryable=retryable
            ) from exc
        except OpenAIError as exc:
            raise ProviderFailure("openai_sdk", str(exc), retryable=False) from exc

        parsed = response.output_parsed
        if parsed is None:
            refusal = _refusal_reason(response)
            if refusal:
                return ProviderRefusal(
                    reason=refusal,
                    response_id=response.id,
                    model=response.model,
                )
            raise ProviderFailure(
                "missing_parsed_output",
                "Responses result contained no parsed record or refusal",
                retryable=False,
            )

        usage = response.usage
        return ProviderSuccess(
            payload=parsed.model_dump(mode="json"),
            response_id=response.id,
            model=response.model,
            input_tokens=usage.input_tokens if usage else None,
            output_tokens=usage.output_tokens if usage else None,
        )
