from __future__ import annotations

from intake_normalizer.models import FailureDetail, NormalizedIntake, ServiceRequest


def validate_policy(
    request: ServiceRequest, record: NormalizedIntake
) -> list[FailureDetail]:
    """Compare a schema-valid record to source data and business rules."""
    raise NotImplementedError("implement business-policy validation")
