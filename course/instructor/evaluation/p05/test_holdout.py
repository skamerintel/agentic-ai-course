from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest

from job_service.database import Database
from job_service.domain import IssueInput, JobStatus, JobSubmission, TriageResult
from job_service.errors import IdempotencyConflict
from job_service.progress import InMemoryProgressStore
from job_service.provider import DeterministicTriageProvider
from job_service.repository import JobRepository
from job_service.service import JobService

pytestmark = pytest.mark.asyncio


def submission(body: str = "The payment failed.") -> JobSubmission:
    return JobSubmission(
        idempotency_key="holdout-idem-001",
        issue=IssueInput(
            issue_id="HOLDOUT-1",
            repo="acme/payments",
            title="Payment failure",
            body=body,
        ),
    )


@asynccontextmanager
async def service_context(
    tmp_path, provider
) -> AsyncIterator[tuple[JobService, InMemoryProgressStore]]:
    database = Database(f"sqlite+aiosqlite:///{tmp_path / 'holdout.db'}")
    await database.create_schema()
    progress = InMemoryProgressStore()
    repository = JobRepository(database, provider_name=provider.name)
    yield JobService(repository, progress, provider, auto_run=False), progress
    await database.dispose()


async def test_changed_request_cannot_reuse_idempotency_key(tmp_path) -> None:
    async with service_context(tmp_path, DeterministicTriageProvider()) as (
        service,
        _progress,
    ):
        await service.submit(submission(), "corr-1")
        with pytest.raises(IdempotencyConflict):
            await service.submit(submission("A materially changed body."), "corr-2")


class BlockingProvider:
    name = "blocking-provider"

    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def triage(self, issue, correlation_id):
        self.started.set()
        await self.release.wait()
        return TriageResult(
            category="bug",
            urgency="high",
            summary="Should be discarded after cancellation",
            evidence=[f"issue:{issue.issue_id}"],
        )


async def test_cancellation_wins_before_completion_commit(tmp_path) -> None:
    provider = BlockingProvider()
    async with service_context(tmp_path, provider) as (service, _progress):
        job, _ = await service.submit(submission(), "corr-race")
        task = asyncio.create_task(service.run_job(job.job_id))
        await provider.started.wait()
        requested = await service.cancel(job.job_id)
        provider.release.set()
        await task
        final = await service.get_job(job.job_id)

    assert requested.status is JobStatus.CANCEL_REQUESTED
    assert final.status is JobStatus.CANCELLED
    assert final.result is None


async def test_progress_loss_does_not_erase_durable_result(tmp_path) -> None:
    async with service_context(tmp_path, DeterministicTriageProvider()) as (
        service,
        progress,
    ):
        job, _ = await service.submit(submission(), "corr-expiry")
        await service.run_job(job.job_id)
        progress._events.clear()
        final = await service.get_job(job.job_id)
        events = await service.audit_events(job.job_id)

    assert final.status is JobStatus.SUCCEEDED
    assert final.result is not None
    assert events[-1].event == "succeeded"


class SecretFailureProvider:
    name = "secret-failure-provider"

    async def triage(self, issue, correlation_id):
        raise RuntimeError("secret-token-that-must-not-be-public")


async def test_unexpected_provider_error_is_classified(tmp_path, caplog) -> None:
    async with service_context(tmp_path, SecretFailureProvider()) as (
        service,
        _progress,
    ):
        job, _ = await service.submit(submission(), "corr-safe")
        await service.run_job(job.job_id)
        failed = await service.get_job(job.job_id)

    assert failed.status is JobStatus.FAILED
    assert failed.error_code == "provider_internal_error"
    assert "secret-token-that-must-not-be-public" not in failed.model_dump_json()
    assert "secret-token-that-must-not-be-public" not in caplog.text
