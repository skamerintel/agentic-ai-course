from __future__ import annotations

import json
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from time import sleep as default_sleep

from pydantic import ValidationError

from intake_normalizer.models import (
    FailureDetail,
    NormalizedIntake,
    OutcomeKind,
    ProcessingResult,
    ProgressEvent,
    ProgressKind,
    ServiceRequest,
)
from intake_normalizer.policy import validate_policy
from intake_normalizer.provider import (
    ProviderCall,
    ProviderFailure,
    ProviderRefusal,
)

EventSink = Callable[[ProgressEvent], None]
Sleep = Callable[[float], None]


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25

    def delay_for(self, attempt: int) -> float:
        return self.base_delay_seconds * (2 ** (attempt - 1))


DEFAULT_RETRY_POLICY = RetryPolicy()


def _emit(
    sink: EventSink | None,
    request: ServiceRequest,
    correlation_id: str,
    kind: ProgressKind,
    attempt: int,
    detail: str | None = None,
) -> None:
    if sink:
        sink(
            ProgressEvent(
                source_id=request.id,
                correlation_id=correlation_id,
                kind=kind,
                attempt=attempt,
                detail=detail,
            )
        )


def _schema_failure(error: ValidationError) -> FailureDetail:
    parts = [
        f"{'.'.join(str(item) for item in entry['loc'])}:{entry['type']}"
        for entry in error.errors(include_input=False)
    ]
    return FailureDetail(
        code="schema_validation",
        message="; ".join(parts),
        retryable=False,
    )


def _complete(
    result: ProcessingResult,
    request: ServiceRequest,
    emit: EventSink | None,
) -> ProcessingResult:
    _emit(
        emit,
        request,
        result.correlation_id,
        ProgressKind.COMPLETED,
        result.attempts,
        result.outcome.value,
    )
    return result


def process_request(
    request: ServiceRequest,
    provider: ProviderCall,
    *,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    emit: EventSink | None = None,
    sleeper: Sleep = default_sleep,
    correlation_id: str | None = None,
) -> ProcessingResult:
    if retry_policy.max_attempts < 1:
        raise ValueError("max_attempts must be at least one")

    run_id = correlation_id or str(uuid.uuid4())
    provider_failures: list[FailureDetail] = []
    _emit(emit, request, run_id, ProgressKind.STARTED, 0)

    for attempt in range(1, retry_policy.max_attempts + 1):
        _emit(emit, request, run_id, ProgressKind.ATTEMPT, attempt)
        try:
            response = provider(request)
        except ProviderFailure as exc:
            failure = FailureDetail(
                code=exc.code,
                message=exc.message,
                retryable=exc.retryable,
            )
            provider_failures.append(failure)
            if exc.retryable and attempt < retry_policy.max_attempts:
                _emit(
                    emit,
                    request,
                    run_id,
                    ProgressKind.RETRYING,
                    attempt,
                    exc.code,
                )
                sleeper(retry_policy.delay_for(attempt))
                continue
            return _complete(
                ProcessingResult(
                    source_id=request.id,
                    correlation_id=run_id,
                    outcome=OutcomeKind.PROVIDER_ERROR,
                    attempts=attempt,
                    failures=provider_failures,
                ),
                request,
                emit,
            )

        if isinstance(response, ProviderRefusal):
            return _complete(
                ProcessingResult(
                    source_id=request.id,
                    correlation_id=run_id,
                    outcome=OutcomeKind.REFUSAL,
                    attempts=attempt,
                    failures=[
                        FailureDetail(
                            code="provider_refusal",
                            message=response.reason,
                            retryable=False,
                        )
                    ],
                    response_id=response.response_id,
                    model=response.model,
                ),
                request,
                emit,
            )

        try:
            serialized = json.dumps(response.payload)
            record = NormalizedIntake.model_validate_json(serialized, strict=True)
        except ValidationError as exc:
            return _complete(
                ProcessingResult(
                    source_id=request.id,
                    correlation_id=run_id,
                    outcome=OutcomeKind.SCHEMA_ERROR,
                    attempts=attempt,
                    failures=[_schema_failure(exc)],
                    response_id=response.response_id,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                ),
                request,
                emit,
            )

        policy_failures = validate_policy(request, record)
        if policy_failures:
            return _complete(
                ProcessingResult(
                    source_id=request.id,
                    correlation_id=run_id,
                    outcome=OutcomeKind.POLICY_ERROR,
                    attempts=attempt,
                    record=record,
                    failures=policy_failures,
                    response_id=response.response_id,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                ),
                request,
                emit,
            )

        return _complete(
            ProcessingResult(
                source_id=request.id,
                correlation_id=run_id,
                outcome=OutcomeKind.SUCCESS,
                attempts=attempt,
                record=record,
                response_id=response.response_id,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            ),
            request,
            emit,
        )
    raise AssertionError("attempt loop did not return")


def process_batch(
    requests: Iterable[ServiceRequest],
    provider: ProviderCall,
    *,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    emit: EventSink | None = None,
    sleeper: Sleep = default_sleep,
) -> list[ProcessingResult]:
    return [
        process_request(
            request,
            provider,
            retry_policy=retry_policy,
            emit=emit,
            sleeper=sleeper,
        )
        for request in requests
    ]
