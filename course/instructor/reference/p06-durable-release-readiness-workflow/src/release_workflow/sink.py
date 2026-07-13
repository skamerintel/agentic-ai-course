from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from release_workflow.models import DecisionRecord, PublicationReceipt


class SimulatedCrash(RuntimeError):
    pass


class PublicationConflict(RuntimeError):
    pass


class DecisionSink(Protocol):
    def publish(
        self, workflow_id: str, decision: DecisionRecord
    ) -> PublicationReceipt: ...


def _payload(decision: DecisionRecord) -> tuple[str, str]:
    payload = json.dumps(
        decision.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    return payload, hashlib.sha256(payload.encode()).hexdigest()


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
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    workflow_id TEXT PRIMARY KEY,
                    receipt_id TEXT NOT NULL,
                    payload_fingerprint TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def publish(self, workflow_id: str, decision: DecisionRecord) -> PublicationReceipt:
        self.publish_attempts += 1
        payload, fingerprint = _payload(decision)
        with sqlite3.connect(self.path) as connection:
            existing = connection.execute(
                """
                SELECT receipt_id, payload_fingerprint
                FROM decisions WHERE workflow_id = ?
                """,
                (workflow_id,),
            ).fetchone()
            if existing is not None:
                receipt_id, existing_fingerprint = existing
                if existing_fingerprint != fingerprint:
                    raise PublicationConflict(
                        "workflow already published a different decision"
                    )
                return PublicationReceipt(
                    workflow_id=workflow_id,
                    receipt_id=receipt_id,
                    payload_fingerprint=fingerprint,
                    replayed=True,
                )

            receipt_id = str(uuid4())
            connection.execute(
                """
                INSERT INTO decisions (
                    workflow_id, receipt_id, payload_fingerprint, payload_json
                ) VALUES (?, ?, ?, ?)
                """,
                (workflow_id, receipt_id, fingerprint, payload),
            )
            connection.commit()

        if self.crash_after_commit_once and not self._crashed:
            self._crashed = True
            raise SimulatedCrash("process crashed after publication commit")
        return PublicationReceipt(
            workflow_id=workflow_id,
            receipt_id=receipt_id,
            payload_fingerprint=fingerprint,
            replayed=False,
        )

    def count(self) -> int:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute("SELECT COUNT(*) FROM decisions").fetchone()
        return int(row[0]) if row else 0

    def get(self, workflow_id: str) -> PublicationReceipt | None:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                """
                SELECT receipt_id, payload_fingerprint
                FROM decisions WHERE workflow_id = ?
                """,
                (workflow_id,),
            ).fetchone()
        if row is None:
            return None
        return PublicationReceipt(
            workflow_id=workflow_id,
            receipt_id=row[0],
            payload_fingerprint=row[1],
            replayed=False,
        )
