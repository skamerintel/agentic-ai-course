from collections import defaultdict

from job_service.progress import InMemoryProgressStore, RedisProgressStore


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, list[str]] = defaultdict(list)
        self.counters: dict[str, int] = defaultdict(int)
        self.expirations: dict[str, int] = {}
        self.closed = False

    async def incr(self, key: str) -> int:
        self.counters[key] += 1
        return self.counters[key]

    async def llen(self, key: str) -> int:
        return len(self.values[key])

    async def rpush(self, key: str, value: str) -> int:
        self.values[key].append(value)
        return len(self.values[key])

    async def ltrim(self, key: str, start: int, end: int) -> None:
        values = self.values[key]
        start = max(len(values) + start, 0) if start < 0 else start
        end = len(values) + end if end < 0 else end
        self.values[key] = values[start : end + 1]

    async def expire(self, key: str, seconds: int) -> None:
        self.expirations[key] = seconds

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        values = self.values[key]
        end = len(values) + end if end < 0 else end
        return values[start : end + 1]

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        self.closed = True


class UnavailableRedis(FakeRedis):
    async def ping(self) -> bool:
        raise ConnectionError("redis unavailable")


async def test_in_memory_progress_is_ordered() -> None:
    store = InMemoryProgressStore()
    await store.publish("job-1", "queued", "Accepted")
    await store.publish("job-1", "running", "Provider started")

    events = await store.recent("job-1")

    assert [event.sequence for event in events] == [1, 2]


async def test_redis_progress_is_bounded_and_expiring() -> None:
    client = FakeRedis()
    store = RedisProgressStore(client, ttl_seconds=60, limit=2)
    await store.publish("job-1", "queued", "Accepted")
    await store.publish("job-1", "running", "Started")
    await store.publish("job-1", "provider_finished", "Finished")

    events = await store.recent("job-1")

    assert [event.sequence for event in events] == [2, 3]
    assert client.expirations["job:job-1:progress"] == 60


async def test_redis_readiness_failure_is_reported_without_raising() -> None:
    store = RedisProgressStore(UnavailableRedis(), ttl_seconds=60)

    assert await store.ready() is False
