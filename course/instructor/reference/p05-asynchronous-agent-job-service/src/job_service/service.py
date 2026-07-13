from __future__ import annotations

import logging
from typing import Protocol

from job_service.domain import (
    AuditEvent,
    JobSnapshot,
    JobSubmission,
    ProgressEvent,
    TriageResult,
)
from job_service.errors import ResultNotReady
from job_service.progress import ProgressStore
from job_service.provider import ProviderFailure, TriageProvider
from job_service.repository import JobRepository

LOGGER = logging.getLogger(__name__)


class Scheduler(Protocol):
    def schedule(self, job_id: str) -> None: ...


class JobService:
    def __init__(
        self,
        repository: JobRepository,
        progress: ProgressStore,
        provider: TriageProvider,
        *,
        auto_run: bool,
    ) -> None:
        self.repository = repository
        self.progress = progress
        self.provider = provider
        self.auto_run = auto_run
        self.scheduler: Scheduler | None = None

    def attach_scheduler(self, scheduler: Scheduler) -> None:
        self.scheduler = scheduler

    async def submit(
        self, submission: JobSubmission, correlation_id: str
    ) -> tuple[JobSnapshot, bool]:
        snapshot, created = await self.repository.create_job(submission, correlation_id)
        if created:
            await self.progress.publish(snapshot.job_id, "queued", "Job accepted")
            LOGGER.info(
                "job accepted job_id=%s correlation_id=%s",
                snapshot.job_id,
                snapshot.correlation_id,
            )
            if self.auto_run and self.scheduler is not None:
                self.scheduler.schedule(snapshot.job_id)
        return snapshot, created

    async def run_job(self, job_id: str) -> None:
        claimed = await self.repository.claim_job(job_id)
        if claimed is None:
            return
        await self.progress.publish(job_id, "running", "Job execution started")
        await self.progress.publish(
            job_id, "provider_started", "Model provider attempt started"
        )
        try:
            result = await self.provider.triage(claimed.issue, claimed.correlation_id)
        except ProviderFailure as exc:
            final = await self.repository.fail_job(job_id, exc.code, exc.public_message)
            LOGGER.warning(
                "provider failure job_id=%s correlation_id=%s code=%s",
                job_id,
                claimed.correlation_id,
                exc.code,
            )
        except Exception as exc:
            final = await self.repository.fail_job(
                job_id,
                "provider_internal_error",
                "The provider boundary failed unexpectedly.",
            )
            LOGGER.error(
                "unexpected provider failure job_id=%s correlation_id=%s "
                "exception_type=%s",
                job_id,
                claimed.correlation_id,
                type(exc).__name__,
            )
        else:
            final = await self.repository.complete_job(job_id, result)
        await self.progress.publish(
            job_id,
            final.status.value,
            f"Job reached {final.status.value}",
        )

    async def cancel(self, job_id: str) -> JobSnapshot:
        snapshot = await self.repository.request_cancel(job_id)
        await self.progress.publish(
            job_id,
            snapshot.status.value,
            f"Job reached {snapshot.status.value}",
        )
        return snapshot

    async def get_job(self, job_id: str) -> JobSnapshot:
        return await self.repository.get_job(job_id)

    async def get_result(self, job_id: str) -> TriageResult:
        snapshot = await self.repository.get_job(job_id)
        if snapshot.result is None:
            raise ResultNotReady(job_id)
        return snapshot.result

    async def recent_progress(self, job_id: str) -> list[ProgressEvent]:
        await self.repository.get_job(job_id)
        return await self.progress.recent(job_id)

    async def audit_events(self, job_id: str) -> list[AuditEvent]:
        return await self.repository.list_audit_events(job_id)

    async def ready(self) -> bool:
        return await self.repository.ready() and await self.progress.ready()
