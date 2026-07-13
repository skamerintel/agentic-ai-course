from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from job_service.database import Database
from job_service.repository import JobRepository


@pytest.fixture
async def repository(tmp_path) -> AsyncIterator[JobRepository]:
    database = Database(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    await database.create_schema()
    yield JobRepository(database, provider_name="test-provider")
    await database.dispose()
