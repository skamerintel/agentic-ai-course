from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from job_service.config import Settings
from job_service.database import Database
from job_service.domain import (
    AuditEvent,
    ErrorDetail,
    ErrorEnvelope,
    JobSnapshot,
    JobSubmission,
    ProgressEvent,
    TriageResult,
)
from job_service.errors import (
    IdempotencyConflict,
    JobNotFound,
    JobServiceError,
    ResultNotReady,
)
from job_service.progress import InMemoryProgressStore, RedisProgressStore
from job_service.provider import (
    DeterministicTriageProvider,
    OpenAITriageProvider,
    TriageProvider,
)
from job_service.repository import JobRepository
from job_service.runner import InProcessJobRunner
from job_service.service import JobService


def get_service(request: Request) -> JobService:
    return request.app.state.service


ServiceDependency = Annotated[JobService, Depends(get_service)]


def _error_status(exc: JobServiceError) -> int:
    if isinstance(exc, JobNotFound):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, (IdempotencyConflict, ResultNotReady)):
        return status.HTTP_409_CONFLICT
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _provider(settings: Settings) -> TriageProvider:
    if settings.provider == "fake":
        return DeterministicTriageProvider()
    if settings.provider == "openai" and settings.openai_model:
        return OpenAITriageProvider(
            settings.openai_model,
            base_url=settings.openai_base_url,
        )
    raise ValueError("provider configuration is incomplete")


def create_app(
    settings: Settings | None = None,
    *,
    provider: TriageProvider | None = None,
) -> FastAPI:
    configured = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(configured.database_url)
        await database.create_schema()
        if configured.redis_url:
            from redis.asyncio import Redis

            progress = RedisProgressStore(
                Redis.from_url(configured.redis_url),
                ttl_seconds=configured.progress_ttl_seconds,
            )
        else:
            progress = InMemoryProgressStore()
        selected_provider = provider or _provider(configured)
        repository = JobRepository(database, provider_name=selected_provider.name)
        service = JobService(
            repository,
            progress,
            selected_provider,
            auto_run=configured.auto_run_jobs,
        )
        runner = InProcessJobRunner(service.run_job)
        service.attach_scheduler(runner)
        app.state.database = database
        app.state.progress = progress
        app.state.provider = selected_provider
        app.state.service = service
        app.state.runner = runner
        yield
        await runner.close()
        await progress.close()
        close = getattr(selected_provider, "close", None)
        if close is not None:
            await close()
        await database.dispose()

    app = FastAPI(title="Asynchronous Agent Job Service", lifespan=lifespan)

    @app.exception_handler(JobServiceError)
    async def job_service_error(
        _request: Request, exc: JobServiceError
    ) -> JSONResponse:
        body = ErrorEnvelope(
            error=ErrorDetail(code=exc.code, message=exc.public_message)
        )
        return JSONResponse(
            status_code=_error_status(exc),
            content=body.model_dump(mode="json"),
        )

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def ready(service: ServiceDependency) -> JSONResponse:
        is_ready = await service.ready()
        return JSONResponse(
            status_code=200 if is_ready else 503,
            content={"status": "ready" if is_ready else "unavailable"},
        )

    @app.post(
        "/v1/jobs",
        response_model=JobSnapshot,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def submit_job(
        submission: JobSubmission,
        request: Request,
        response: Response,
        service: ServiceDependency,
    ) -> JobSnapshot:
        correlation_id = request.headers.get("x-correlation-id") or str(uuid4())
        snapshot, created = await service.submit(submission, correlation_id)
        response.status_code = 202 if created else 200
        return snapshot

    @app.get("/v1/jobs/{job_id}", response_model=JobSnapshot)
    async def get_job(job_id: str, service: ServiceDependency) -> JobSnapshot:
        return await service.get_job(job_id)

    @app.delete(
        "/v1/jobs/{job_id}",
        response_model=JobSnapshot,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def cancel_job(job_id: str, service: ServiceDependency) -> JobSnapshot:
        return await service.cancel(job_id)

    @app.get("/v1/jobs/{job_id}/result", response_model=TriageResult)
    async def get_result(job_id: str, service: ServiceDependency) -> TriageResult:
        return await service.get_result(job_id)

    @app.get("/v1/jobs/{job_id}/progress", response_model=list[ProgressEvent])
    async def get_progress(
        job_id: str, service: ServiceDependency
    ) -> list[ProgressEvent]:
        return await service.recent_progress(job_id)

    @app.get("/v1/jobs/{job_id}/audit", response_model=list[AuditEvent])
    async def get_audit(job_id: str, service: ServiceDependency) -> list[AuditEvent]:
        return await service.audit_events(job_id)

    return app
