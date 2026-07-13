from job_service.domain import IssueInput
from job_service.provider import DeterministicTriageProvider


async def test_deterministic_provider_is_offline_and_structured() -> None:
    provider = DeterministicTriageProvider()
    result = await provider.triage(
        IssueInput(
            issue_id="ISS-1",
            repo="acme/payments",
            title="Payment failure",
            body="A payment request failed after a timeout.",
        ),
        "corr-1",
    )

    assert result.category == "bug"
    assert result.urgency == "high"
    assert "issue:ISS-1" in result.evidence
