from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database_url: str = "sqlite+aiosqlite:///./job-service.db"
    redis_url: str | None = None
    progress_ttl_seconds: int = Field(default=300, ge=10, le=86_400)
    auto_run_jobs: bool = True
    provider: str = "fake"
    openai_model: str | None = None
    openai_base_url: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        redis_url = os.getenv("JOB_SERVICE_REDIS_URL") or None
        model = os.getenv("OPENAI_MODEL") or None
        base_url = os.getenv("OPENAI_BASE_URL") or None
        return cls(
            database_url=os.getenv(
                "JOB_SERVICE_DATABASE_URL",
                "sqlite+aiosqlite:///./job-service.db",
            ),
            redis_url=redis_url,
            progress_ttl_seconds=int(
                os.getenv("JOB_SERVICE_PROGRESS_TTL_SECONDS", "300")
            ),
            auto_run_jobs=os.getenv("JOB_SERVICE_AUTO_RUN_JOBS", "true").lower()
            in {"1", "true", "yes"},
            provider=os.getenv("JOB_SERVICE_PROVIDER", "fake"),
            openai_model=model,
            openai_base_url=base_url,
        )
