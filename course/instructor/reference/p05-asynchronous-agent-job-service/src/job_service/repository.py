from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from job_service.database import AttemptRow, AuditEventRow, Database, JobRow, utc_now
from job_service.domain import (
    AuditEvent,
    IssueInput,
    JobSnapshot,
    JobStatus,
    JobSubmission,
    TriageResult,
)
from job_service.errors import IdempotencyConflict, JobNotFound


def _fingerprint(submission: JobSubmission) -> str:
    payload = json.dumps(
        submission.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _snapshot(row: JobRow) -> JobSnapshot:
    result = (
        TriageResult.model_validate(row.result, strict=True) if row.result else None
    )
    return JobSnapshot(
        job_id=row.job_id,
        idempotency_key=row.idempotency_key,
        correlation_id=row.correlation_id,
        issue=IssueInput(
            issue_id=row.issue_id,
            repo=row.repo,
            title=row.title,
            body=row.body,
        ),
        status=JobStatus(row.status),
        result=result,
        error_code=row.error_code,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def _job(session: AsyncSession, job_id: str, *, lock: bool = False) -> JobRow:
    query = select(JobRow).where(JobRow.job_id == job_id)
    if lock:
        query = query.with_for_update()
    row = await session.scalar(query)
    if row is None:
        raise JobNotFound(job_id)
    return row


def _audit(session: AsyncSession, job_id: str, event: str, detail: str) -> None:
    session.add(AuditEventRow(job_id=job_id, event=event, detail=detail))


async def _running_attempt(session: AsyncSession, job_id: str) -> AttemptRow | None:
    return await session.scalar(
        select(AttemptRow)
        .where(AttemptRow.job_id == job_id, AttemptRow.status == "running")
        .order_by(AttemptRow.attempt_number.desc())
        .limit(1)
    )


class JobRepository:
    def __init__(self, database: Database, *, provider_name: str) -> None:
        self.database = database
        self.provider_name = provider_name

    async def create_job(
        self, submission: JobSubmission, correlation_id: str
    ) -> tuple[JobSnapshot, bool]:
        fingerprint = _fingerprint(submission)
        async with self.database.sessions() as session:
            existing = await session.scalar(
                select(JobRow).where(
                    JobRow.idempotency_key == submission.idempotency_key
                )
            )
            if existing is not None:
                if existing.request_fingerprint != fingerprint:
                    raise IdempotencyConflict(submission.idempotency_key)
                return _snapshot(existing), False

            row = JobRow(
                job_id=str(uuid4()),
                idempotency_key=submission.idempotency_key,
                request_fingerprint=fingerprint,
                correlation_id=correlation_id,
                issue_id=submission.issue.issue_id,
                repo=submission.issue.repo,
                title=submission.issue.title,
                body=submission.issue.body,
                status=JobStatus.QUEUED.value,
            )
            session.add(row)
            _audit(session, row.job_id, "queued", "Job accepted")
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                existing = await session.scalar(
                    select(JobRow).where(
                        JobRow.idempotency_key == submission.idempotency_key
                    )
                )
                if existing is None:
                    raise
                if existing.request_fingerprint != fingerprint:
                    raise IdempotencyConflict(submission.idempotency_key) from None
                return _snapshot(existing), False
            await session.refresh(row)
            return _snapshot(row), True

    async def get_job(self, job_id: str) -> JobSnapshot:
        async with self.database.sessions() as session:
            return _snapshot(await _job(session, job_id))

    async def claim_job(self, job_id: str) -> JobSnapshot | None:
        async with self.database.sessions() as session, session.begin():
            row = await _job(session, job_id, lock=True)
            if JobStatus(row.status) is not JobStatus.QUEUED:
                return None
            attempt_count = await session.scalar(
                select(func.count(AttemptRow.attempt_id)).where(
                    AttemptRow.job_id == job_id
                )
            )
            row.status = JobStatus.RUNNING.value
            session.add(
                AttemptRow(
                    job_id=job_id,
                    attempt_number=int(attempt_count or 0) + 1,
                    provider=self.provider_name,
                    status="running",
                )
            )
            _audit(session, job_id, "running", "Provider attempt started")
            await session.flush()
            return _snapshot(row)

    async def request_cancel(self, job_id: str) -> JobSnapshot:
        async with self.database.sessions() as session, session.begin():
            row = await _job(session, job_id, lock=True)
            status = JobStatus(row.status)
            if status.terminal or status is JobStatus.CANCEL_REQUESTED:
                return _snapshot(row)
            row.cancel_requested = True
            if status is JobStatus.QUEUED:
                row.status = JobStatus.CANCELLED.value
                _audit(session, job_id, "cancelled", "Cancelled before execution")
            else:
                row.status = JobStatus.CANCEL_REQUESTED.value
                _audit(session, job_id, "cancel_requested", "Cancellation requested")
            await session.flush()
            return _snapshot(row)

    async def complete_job(self, job_id: str, result: TriageResult) -> JobSnapshot:
        async with self.database.sessions() as session, session.begin():
            row = await _job(session, job_id, lock=True)
            status = JobStatus(row.status)
            attempt = await _running_attempt(session, job_id)
            if status is JobStatus.CANCEL_REQUESTED:
                row.status = JobStatus.CANCELLED.value
                row.result = None
                if attempt:
                    attempt.status = "cancelled"
                    attempt.completed_at = utc_now()
                _audit(
                    session,
                    job_id,
                    "cancelled",
                    "Cancellation won before completion committed",
                )
            elif status is JobStatus.RUNNING:
                row.status = JobStatus.SUCCEEDED.value
                row.result = result.model_dump(mode="json")
                if attempt:
                    attempt.status = "succeeded"
                    attempt.completed_at = utc_now()
                _audit(session, job_id, "succeeded", "Result committed")
            await session.flush()
            return _snapshot(row)

    async def fail_job(
        self, job_id: str, error_code: str, error_detail: str
    ) -> JobSnapshot:
        async with self.database.sessions() as session, session.begin():
            row = await _job(session, job_id, lock=True)
            status = JobStatus(row.status)
            attempt = await _running_attempt(session, job_id)
            if status is JobStatus.CANCEL_REQUESTED:
                row.status = JobStatus.CANCELLED.value
                if attempt:
                    attempt.status = "cancelled"
                    attempt.completed_at = utc_now()
                _audit(
                    session,
                    job_id,
                    "cancelled",
                    "Cancellation won before failure committed",
                )
            elif status is JobStatus.RUNNING:
                row.status = JobStatus.FAILED.value
                row.error_code = error_code
                row.error_detail = error_detail[:500]
                if attempt:
                    attempt.status = "failed"
                    attempt.error_code = error_code
                    attempt.completed_at = utc_now()
                _audit(session, job_id, "failed", f"Failure category: {error_code}")
            await session.flush()
            return _snapshot(row)

    async def list_audit_events(self, job_id: str) -> list[AuditEvent]:
        async with self.database.sessions() as session:
            await _job(session, job_id)
            rows = (
                await session.scalars(
                    select(AuditEventRow)
                    .where(AuditEventRow.job_id == job_id)
                    .order_by(AuditEventRow.event_id)
                )
            ).all()
            return [
                AuditEvent(
                    event_id=row.event_id,
                    job_id=row.job_id,
                    event=row.event,
                    detail=row.detail,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    async def ready(self) -> bool:
        try:
            async with self.database.sessions() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
