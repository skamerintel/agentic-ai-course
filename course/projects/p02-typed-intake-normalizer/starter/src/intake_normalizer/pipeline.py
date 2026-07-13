from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from time import sleep as default_sleep

from intake_normalizer.models import ProcessingResult, ProgressEvent, ServiceRequest
from intake_normalizer.provider import ProviderCall

EventSink = Callable[[ProgressEvent], None]
Sleep = Callable[[float], None]


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25

    def delay_for(self, attempt: int) -> float:
        return self.base_delay_seconds * (2 ** (attempt - 1))


DEFAULT_RETRY_POLICY = RetryPolicy()


def process_request(
    request: ServiceRequest,
    provider: ProviderCall,
    *,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    emit: EventSink | None = None,
    sleeper: Sleep = default_sleep,
    correlation_id: str | None = None,
) -> ProcessingResult:
    raise NotImplementedError("implement classified processing and retries")


def process_batch(
    requests: Iterable[ServiceRequest],
    provider: ProviderCall,
    *,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    emit: EventSink | None = None,
    sleeper: Sleep = default_sleep,
) -> list[ProcessingResult]:
    raise NotImplementedError("implement batch processing")
