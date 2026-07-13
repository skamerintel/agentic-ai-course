import json

import pytest
from pydantic import ValidationError

from intake_normalizer.models import NormalizedIntake


def valid_payload() -> dict:
    return {
        "source_id": "REQ-001",
        "category": "access",
        "urgency": "normal",
        "requester_name": "Maya Chen",
        "requester_email": "maya.chen@example.com",
        "affected_system": "Atlas Billing",
        "requested_action": "Grant read-only access",
        "due_date": "2026-07-17",
        "requires_follow_up": False,
        "missing_information": [],
        "evidence": [
            {"field": "affected_system", "quote": "Atlas Billing"},
            {"field": "requested_action", "quote": "grant me read-only access"},
        ],
    }


def validate(payload: dict) -> NormalizedIntake:
    return NormalizedIntake.model_validate_json(json.dumps(payload), strict=True)


def test_rejects_unknown_fields() -> None:
    payload = valid_payload() | {"recommended_team": "billing-admins"}

    with pytest.raises(ValidationError, match="extra"):
        validate(payload)


def test_rejects_wrong_boolean_type() -> None:
    payload = valid_payload() | {"requires_follow_up": "false"}

    with pytest.raises(ValidationError):
        validate(payload)


def test_rejects_duplicate_missing_information() -> None:
    payload = valid_payload() | {
        "requires_follow_up": True,
        "missing_information": ["affected_system", "affected_system"],
    }

    with pytest.raises(ValidationError, match="duplicate"):
        validate(payload)


def test_rejects_blank_evidence_quote() -> None:
    payload = valid_payload() | {
        "evidence": [{"field": "affected_system", "quote": " "}]
    }

    with pytest.raises(ValidationError):
        validate(payload)
