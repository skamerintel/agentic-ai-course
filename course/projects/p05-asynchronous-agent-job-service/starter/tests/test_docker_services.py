from __future__ import annotations

import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from job_service.database import Database
from job_service.domain import IssueInput, JobSubmission
from job_service.progress import RedisProgressStore
from job_service.repository import JobRepository

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.docker,
    pytest.mark.skipif(
        os.getenv("JOB_SERVICE_RUN_DOCKER_TESTS") != "1",
        reason="set JOB_SERVICE_RUN_DOCKER_TESTS=1 to use Docker services",
    ),
]


async def test_postgres_and_redis_smoke() -> None:
    database = Database(
        os.getenv(
            "JOB_SERVICE_TEST_DATABASE_URL",
            "postgresql+asyncpg://job_service:job_service@localhost:5432/job_service",
        )
    )
    redis_client = Redis.from_url(
        os.getenv("JOB_SERVICE_TEST_REDIS_URL", "redis://localhost:6379/15")
    )
    progress = RedisProgressStore(redis_client, ttl_seconds=60)
    repository = JobRepository(database, provider_name="docker-smoke")
    suffix = uuid4().hex
    job_id: str | None = None
    try:
        await database.create_schema()
        job, created = await repository.create_job(
            JobSubmission(
                idempotency_key=f"docker-{suffix}",
                issue=IssueInput(
                    issue_id=f"DOCKER-{suffix[:8]}",
                    repo="acme/smoke",
                    title="Docker smoke test",
                    body="Verify real PostgreSQL and Redis adapters.",
                ),
            ),
            f"corr-{suffix}",
        )
        job_id = job.job_id
        await progress.publish(job.job_id, "queued", "Docker smoke event")

        assert created is True
        assert (await repository.get_job(job.job_id)).job_id == job.job_id
        assert (await progress.recent(job.job_id))[0].event == "queued"
    finally:
        if job_id is not None:
            await redis_client.delete(
                f"job:{job_id}:progress",
                f"job:{job_id}:progress-sequence",
            )
        await progress.close()
        await database.dispose()
