from __future__ import annotations

from intake_normalizer.models import (
    EvidenceField,
    FailureDetail,
    MissingInformation,
    NormalizedIntake,
    ServiceRequest,
    Urgency,
)

CRITICAL_INDICATORS = (
    "production checkout is down",
    "down for all",
    "revenue is blocked",
    "customer responses are blocked",
    "security breach",
    "data exposure",
    "safety risk",
)


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def _failure(code: str, message: str) -> FailureDetail:
    return FailureDetail(code=code, message=message, retryable=False)


def validate_policy(
    request: ServiceRequest, record: NormalizedIntake
) -> list[FailureDetail]:
    failures: list[FailureDetail] = []
    source = _normalized(request.text)

    if record.source_id != request.id:
        failures.append(
            _failure("source_id_mismatch", "source_id does not match input")
        )

    if record.requester_email and _normalized(record.requester_email) not in source:
        failures.append(
            _failure(
                "unsupported_requester_email",
                "requester email is not supported by source text",
            )
        )

    evidence_fields = {item.field for item in record.evidence}
    for item in record.evidence:
        if _normalized(item.quote) not in source:
            failures.append(
                _failure(
                    "unsupported_evidence",
                    f"evidence for {item.field.value} is not an exact source excerpt",
                )
            )

    required_evidence: set[EvidenceField] = set()
    if record.requester_name or record.requester_email:
        required_evidence.add(EvidenceField.REQUESTER)
    if record.affected_system:
        required_evidence.add(EvidenceField.AFFECTED_SYSTEM)
    if record.requested_action:
        required_evidence.add(EvidenceField.REQUESTED_ACTION)
    if record.due_date:
        required_evidence.add(EvidenceField.DUE_DATE)
    if record.urgency is Urgency.CRITICAL:
        required_evidence.add(EvidenceField.URGENCY)

    for field in sorted(
        required_evidence - evidence_fields, key=lambda item: item.value
    ):
        failures.append(
            _failure(
                "missing_evidence_field",
                f"accepted {field.value} lacks a matching evidence item",
            )
        )

    missing = set(record.missing_information)
    required_missing: set[MissingInformation] = set()
    if not (record.requester_name or record.requester_email):
        required_missing.add(MissingInformation.REQUESTER_IDENTITY)
    if not record.affected_system:
        required_missing.add(MissingInformation.AFFECTED_SYSTEM)
    if not record.requested_action:
        required_missing.add(MissingInformation.REQUESTED_ACTION)

    for marker in sorted(required_missing - missing, key=lambda item: item.value):
        failures.append(
            _failure(
                "missing_information_marker",
                f"absent field requires {marker.value}",
            )
        )

    contradictory = {
        MissingInformation.REQUESTER_IDENTITY: bool(
            record.requester_name or record.requester_email
        ),
        MissingInformation.AFFECTED_SYSTEM: bool(record.affected_system),
        MissingInformation.REQUESTED_ACTION: bool(record.requested_action),
    }
    for marker, is_present in contradictory.items():
        if marker in missing and is_present:
            failures.append(
                _failure(
                    "contradictory_missing_information",
                    f"{marker.value} is marked missing but a value is present",
                )
            )

    if missing and not record.requires_follow_up:
        failures.append(
            _failure("follow_up_required", "missing information requires follow-up")
        )
    if not missing and record.requires_follow_up:
        failures.append(
            _failure(
                "follow_up_without_missing_information",
                "follow-up is true but no missing information is identified",
            )
        )

    if record.due_date and record.due_date < request.received_at.date():
        failures.append(_failure("past_due_date", "due date precedes request receipt"))

    if record.urgency is Urgency.CRITICAL and not any(
        indicator in source for indicator in CRITICAL_INDICATORS
    ):
        failures.append(
            _failure(
                "unsupported_critical_urgency",
                "critical urgency lacks a supported severe-impact indicator",
            )
        )
    return failures
