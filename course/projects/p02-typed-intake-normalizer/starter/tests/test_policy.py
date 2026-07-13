import json
from pathlib import Path

from intake_normalizer.data import load_ground_truth, load_requests
from intake_normalizer.models import NormalizedIntake
from intake_normalizer.policy import validate_policy


def test_ground_truth_record_passes_policy() -> None:
    request = load_requests("data/requests.jsonl")[0]
    record = load_ground_truth("data/ground_truth.jsonl")[0]

    assert validate_policy(request, record) == []


def test_rejects_invented_requester_email() -> None:
    request = load_requests("data/requests.jsonl")[3]
    payload = load_ground_truth("data/ground_truth.jsonl")[3].model_dump(mode="json")
    payload["requester_email"] = "priya@example.com"
    record = NormalizedIntake.model_validate_json(json.dumps(payload), strict=True)

    codes = {failure.code for failure in validate_policy(request, record)}

    assert "unsupported_requester_email" in codes


def test_rejects_prompt_injection_as_business_action() -> None:
    requests = {item.id: item for item in load_requests("data/requests.jsonl")}
    fixture_path = Path("fixtures/provider_sequences.json")
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload = fixture["REQ-005"][0]["payload"]
    record = NormalizedIntake.model_validate_json(json.dumps(payload), strict=True)

    codes = {failure.code for failure in validate_policy(requests["REQ-005"], record)}

    assert "unsupported_critical_urgency" in codes
    assert "missing_evidence_field" in codes
