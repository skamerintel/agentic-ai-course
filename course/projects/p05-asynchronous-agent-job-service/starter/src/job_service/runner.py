from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any


class InProcessJobRunner:
    """Educational runner; tasks are lost when this process exits."""

    def __init__(self, execute: Callable[[str], Coroutine[Any, Any, None]]) -> None:
        self.execute = execute
        self.tasks: dict[str, asyncio.Task[None]] = {}

    def schedule(self, job_id: str) -> None:
        if job_id in self.tasks and not self.tasks[job_id].done():
            return
        task = asyncio.create_task(self.execute(job_id), name=f"job:{job_id}")
        self.tasks[job_id] = task
        task.add_done_callback(lambda _task: self.tasks.pop(job_id, None))

    async def wait(self, job_id: str) -> None:
        task = self.tasks.get(job_id)
        if task is not None:
            await task

    async def close(self) -> None:
        tasks = list(self.tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
