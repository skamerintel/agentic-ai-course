from __future__ import annotations

from job_service.database import Database
from job_service.domain import AuditEvent, JobSnapshot, JobSubmission, TriageResult


class JobRepository:
    def __init__(self, database: Database, *, provider_name: str) -> None:
        self.database = database
        self.provider_name = provider_name

    async def create_job(
        self, submission: JobSubmission, correlation_id: str
    ) -> tuple[JobSnapshot, bool]:
        raise NotImplementedError("implement durable idempotent job creation")

    async def get_job(self, job_id: str) -> JobSnapshot:
        raise NotImplementedError("implement job lookup")

    async def claim_job(self, job_id: str) -> JobSnapshot | None:
        raise NotImplementedError("implement atomic queued-to-running transition")

    async def request_cancel(self, job_id: str) -> JobSnapshot:
        raise NotImplementedError("implement cancellation transition policy")

    async def complete_job(self, job_id: str, result: TriageResult) -> JobSnapshot:
        raise NotImplementedError("implement cancellation-safe completion")

    async def fail_job(
        self, job_id: str, error_code: str, error_detail: str
    ) -> JobSnapshot:
        raise NotImplementedError("implement classified failure transition")

    async def list_audit_events(self, job_id: str) -> list[AuditEvent]:
        raise NotImplementedError("implement ordered durable audit lookup")

    async def ready(self) -> bool:
        raise NotImplementedError("implement a minimal database readiness check")
