from __future__ import annotations

from pathlib import Path
from typing import Protocol

from release_workflow.models import DecisionRecord, PublicationReceipt


class SimulatedCrash(RuntimeError):
    pass


class PublicationConflict(RuntimeError):
    pass


class DecisionSink(Protocol):
    def publish(
        self, workflow_id: str, decision: DecisionRecord
    ) -> PublicationReceipt: ...


class SqliteDecisionSink:
    def __init__(
        self,
        path: str | Path,
        *,
        crash_after_commit_once: bool = False,
    ) -> None:
        self.path = str(path)
        self.crash_after_commit_once = crash_after_commit_once
        self.publish_attempts = 0
        self._crashed = False
        self.setup()

    def setup(self) -> None:
        raise NotImplementedError("create the durable publication table")

    def publish(self, workflow_id: str, decision: DecisionRecord) -> PublicationReceipt:
        raise NotImplementedError("implement durable idempotent publication")

    def count(self) -> int:
        raise NotImplementedError("return durable publication count")

    def get(self, workflow_id: str) -> PublicationReceipt | None:
        raise NotImplementedError("return the durable publication receipt")
