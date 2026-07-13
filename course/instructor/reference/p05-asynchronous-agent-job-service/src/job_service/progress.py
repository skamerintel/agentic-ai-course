from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any, Protocol

from job_service.domain import ProgressEvent


class ProgressStore(Protocol):
    async def publish(self, job_id: str, event: str, detail: str) -> ProgressEvent: ...

    async def recent(self, job_id: str) -> list[ProgressEvent]: ...

    async def ready(self) -> bool: ...

    async def close(self) -> None: ...


class InMemoryProgressStore:
    def __init__(self) -> None:
        self._events: dict[str, list[ProgressEvent]] = defaultdict(list)

    async def publish(self, job_id: str, event: str, detail: str) -> ProgressEvent:
        progress = ProgressEvent(
            job_id=job_id,
            sequence=len(self._events[job_id]) + 1,
            event=event,
            detail=detail,
            created_at=datetime.now(UTC),
        )
        self._events[job_id].append(progress)
        return progress

    async def recent(self, job_id: str) -> list[ProgressEvent]:
        return list(self._events[job_id])

    async def ready(self) -> bool:
        return True

    async def close(self) -> None:
        return None


class RedisProgressStore:
    def __init__(self, client: Any, *, ttl_seconds: int, limit: int = 50) -> None:
        self.client = client
        self.ttl_seconds = ttl_seconds
        self.limit = limit

    def _key(self, job_id: str) -> str:
        return f"job:{job_id}:progress"

    def _sequence_key(self, job_id: str) -> str:
        return f"job:{job_id}:progress-sequence"

    async def publish(self, job_id: str, event: str, detail: str) -> ProgressEvent:
        key = self._key(job_id)
        sequence_key = self._sequence_key(job_id)
        sequence = int(await self.client.incr(sequence_key))
        progress = ProgressEvent(
            job_id=job_id,
            sequence=sequence,
            event=event,
            detail=detail,
            created_at=datetime.now(UTC),
        )
        await self.client.rpush(key, progress.model_dump_json())
        await self.client.ltrim(key, -self.limit, -1)
        await self.client.expire(key, self.ttl_seconds)
        await self.client.expire(sequence_key, self.ttl_seconds)
        return progress

    async def recent(self, job_id: str) -> list[ProgressEvent]:
        values = await self.client.lrange(self._key(job_id), 0, -1)
        return [
            ProgressEvent.model_validate_json(value, strict=True) for value in values
        ]

    async def ready(self) -> bool:
        try:
            return bool(await self.client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        await self.client.aclose()
