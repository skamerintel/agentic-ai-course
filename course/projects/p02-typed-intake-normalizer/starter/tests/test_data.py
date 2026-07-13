from intake_normalizer.data import load_ground_truth, load_requests


def test_loads_supplied_requests_and_ground_truth() -> None:
    requests = load_requests("data/requests.jsonl")
    expected = load_ground_truth("data/ground_truth.jsonl")

    assert len(requests) == 10
    assert len(expected) == 10
    assert requests[0].id == expected[0].source_id == "REQ-001"
