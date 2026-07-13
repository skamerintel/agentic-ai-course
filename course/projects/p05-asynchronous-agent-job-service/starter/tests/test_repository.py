import asyncio

import pytest
from sqlalchemy import select

from job_service.database import AttemptRow
from job_service.domain import IssueInput, JobStatus, JobSubmission, TriageResult
from job_service.errors import IdempotencyConflict


def submission(issue_id: str = "ISS-1", key: str = "idem-key-0001") -> JobSubmission:
    return JobSubmission(
        idempotency_key=key,
        issue=IssueInput(
            issue_id=issue_id,
            repo="acme/service",
            title="Service failure",
            body="The service returned an error.",
        ),
    )


async def test_create_is_durably_idempotent(repository) -> None:
    first, created = await repository.create_job(submission(), "corr-1")
    second, duplicate_created = await repository.create_job(submission(), "corr-2")

    assert created is True
    assert duplicate_created is False
    assert second.job_id == first.job_id
    assert second.correlation_id == "corr-1"


async def test_reused_key_with_different_request_conflicts(repository) -> None:
    await repository.create_job(submission(), "corr-1")

    with pytest.raises(IdempotencyConflict):
        await repository.create_job(submission(issue_id="ISS-OTHER"), "corr-2")


async def test_concurrent_retry_creates_one_job(repository) -> None:
    first, second = await asyncio.gather(
        repository.create_job(submission(), "corr-first"),
        repository.create_job(submission(), "corr-second"),
    )

    assert first[0].job_id == second[0].job_id
    assert sorted((first[1], second[1])) == [False, True]


async def test_completion_and_audit_commit_together(repository) -> None:
    job, _ = await repository.create_job(submission(), "corr-1")
    claimed = await repository.claim_job(job.job_id)
    assert claimed is not None
    assert claimed.status is JobStatus.RUNNING

    completed = await repository.complete_job(
        job.job_id,
        TriageResult(
            category="bug",
            urgency="normal",
            summary="Service failure",
            evidence=["issue:ISS-1"],
        ),
    )
    events = await repository.list_audit_events(job.job_id)
    async with repository.database.sessions() as session:
        attempts = (
            await session.scalars(
                select(AttemptRow).where(AttemptRow.job_id == job.job_id)
            )
        ).all()

    assert completed.status is JobStatus.SUCCEEDED
    assert completed.result is not None
    assert [event.event for event in events] == ["queued", "running", "succeeded"]
    assert len(attempts) == 1
    assert attempts[0].status == "succeeded"


async def test_cancellation_committed_before_completion_wins(repository) -> None:
    job, _ = await repository.create_job(submission(), "corr-1")
    await repository.claim_job(job.job_id)
    cancel_requested = await repository.request_cancel(job.job_id)
    completed = await repository.complete_job(
        job.job_id,
        TriageResult(
            category="bug",
            urgency="normal",
            summary="Should be discarded",
            evidence=["issue:ISS-1"],
        ),
    )

    assert cancel_requested.status is JobStatus.CANCEL_REQUESTED
    assert completed.status is JobStatus.CANCELLED
    assert completed.result is None
