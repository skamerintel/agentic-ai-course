from collections import Counter

from intake_normalizer.data import load_requests
from intake_normalizer.models import OutcomeKind
from intake_normalizer.pipeline import process_batch
from intake_normalizer.provider import FixtureGateway


def test_offline_batch_exercises_all_outcome_classes() -> None:
    results = process_batch(
        load_requests("data/requests.jsonl"),
        FixtureGateway("fixtures/provider_sequences.json"),
        sleeper=lambda _: None,
    )
    counts = Counter(result.outcome for result in results)

    assert len(results) == 10
    assert counts == {
        OutcomeKind.SUCCESS: 6,
        OutcomeKind.POLICY_ERROR: 1,
        OutcomeKind.SCHEMA_ERROR: 1,
        OutcomeKind.REFUSAL: 1,
        OutcomeKind.PROVIDER_ERROR: 1,
    }
