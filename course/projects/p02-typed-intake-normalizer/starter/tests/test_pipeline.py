from intake_normalizer.data import load_requests
from intake_normalizer.models import OutcomeKind, ProgressKind
from intake_normalizer.pipeline import RetryPolicy, process_request
from intake_normalizer.provider import FixtureGateway


def request_by_id(request_id: str):
    requests = load_requests("data/requests.jsonl")
    return next(item for item in requests if item.id == request_id)


def test_retries_transient_failure_then_succeeds() -> None:
    events = []
    result = process_request(
        request_by_id("REQ-002"),
        FixtureGateway("fixtures/provider_sequences.json"),
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0),
        emit=events.append,
        sleeper=lambda _: None,
        correlation_id="corr-002",
    )

    assert result.outcome is OutcomeKind.SUCCESS
    assert result.attempts == 2
    assert {event.correlation_id for event in events} == {"corr-002"}
    assert [event.kind for event in events] == [
        ProgressKind.STARTED,
        ProgressKind.ATTEMPT,
        ProgressKind.RETRYING,
        ProgressKind.ATTEMPT,
        ProgressKind.COMPLETED,
    ]


def test_schema_policy_refusal_and_terminal_failures_do_not_retry() -> None:
    expected = {
        "REQ-005": OutcomeKind.POLICY_ERROR,
        "REQ-007": OutcomeKind.SCHEMA_ERROR,
        "REQ-008": OutcomeKind.REFUSAL,
        "REQ-009": OutcomeKind.PROVIDER_ERROR,
    }

    for request_id, outcome in expected.items():
        result = process_request(
            request_by_id(request_id),
            FixtureGateway("fixtures/provider_sequences.json"),
            sleeper=lambda _: None,
        )
        assert result.outcome is outcome
        assert result.attempts == 1


def test_multiple_transient_failures_are_bounded() -> None:
    result = process_request(
        request_by_id("REQ-010"),
        FixtureGateway("fixtures/provider_sequences.json"),
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0),
        sleeper=lambda _: None,
    )

    assert result.outcome is OutcomeKind.SUCCESS
    assert result.attempts == 3
