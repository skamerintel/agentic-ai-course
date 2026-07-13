from __future__ import annotations

from typing import Protocol

from job_service.domain import (
    AuditEvent,
    JobSnapshot,
    JobSubmission,
    ProgressEvent,
    TriageResult,
)
from job_service.progress import ProgressStore
from job_service.provider import TriageProvider
from job_service.repository import JobRepository


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
        raise NotImplementedError("implement submission and scheduling")

    async def run_job(self, job_id: str) -> None:
        raise NotImplementedError("implement classified provider execution")

    async def cancel(self, job_id: str) -> JobSnapshot:
        raise NotImplementedError("implement cancellation and progress")

    async def get_job(self, job_id: str) -> JobSnapshot:
        return await self.repository.get_job(job_id)

    async def get_result(self, job_id: str) -> TriageResult:
        raise NotImplementedError("implement terminal result policy")

    async def recent_progress(self, job_id: str) -> list[ProgressEvent]:
        await self.repository.get_job(job_id)
        return await self.progress.recent(job_id)

    async def audit_events(self, job_id: str) -> list[AuditEvent]:
        return await self.repository.list_audit_events(job_id)

    async def ready(self) -> bool:
        return await self.repository.ready() and await self.progress.ready()
