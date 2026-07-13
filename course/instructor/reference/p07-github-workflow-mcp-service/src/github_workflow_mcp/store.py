from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from github_workflow_mcp.errors import (
    ApprovalRequired,
    DeliveryConflict,
    ProposalNotFound,
    ProposalStale,
)
from github_workflow_mcp.models import (
    ApprovalRequest,
    CommentProposal,
    CommentReceipt,
    DeliveryStatus,
    GitHubComment,
    ProposalStatus,
    WebhookReceipt,
)


def _now() -> datetime:
    return datetime.now(UTC)


def _proposal(row: sqlite3.Row) -> CommentProposal:
    return CommentProposal(
        proposal_id=row["proposal_id"],
        owner=row["owner"],
        repo=row["repo"],
        issue_number=row["issue_number"],
        body=row["body"],
        reason=row["reason"],
        status=ProposalStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        expires_at=datetime.fromisoformat(row["expires_at"]),
        approved_by=row["approved_by"],
    )


class StateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self.setup()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def setup(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id TEXT PRIMARY KEY,
                    owner TEXT NOT NULL,
                    repo TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    body TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    approved_by TEXT,
                    approved_at TEXT
                );
                CREATE TABLE IF NOT EXISTS executions (
                    proposal_id TEXT PRIMARY KEY,
                    comment_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    executed_at TEXT NOT NULL,
                    FOREIGN KEY (proposal_id) REFERENCES proposals(proposal_id)
                );
                CREATE TABLE IF NOT EXISTS deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    payload_hash TEXT NOT NULL,
                    event TEXT NOT NULL,
                    action TEXT,
                    repository TEXT,
                    pull_request_number INTEGER,
                    received_at TEXT NOT NULL
                );
                """
            )

    def create_proposal(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        reason: str,
        *,
        ttl: timedelta = timedelta(hours=1),
    ) -> CommentProposal:
        now = _now()
        proposal = CommentProposal(
            proposal_id=str(uuid4()),
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            body=body,
            reason=reason,
            status=ProposalStatus.PENDING,
            created_at=now,
            expires_at=now + ttl,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO proposals (
                    proposal_id, owner, repo, issue_number, body, reason, status,
                    created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal.proposal_id,
                    proposal.owner,
                    proposal.repo,
                    proposal.issue_number,
                    proposal.body,
                    proposal.reason,
                    proposal.status.value,
                    proposal.created_at.isoformat(),
                    proposal.expires_at.isoformat(),
                ),
            )
        return proposal

    def _get_proposal(
        self, connection: sqlite3.Connection, proposal_id: str
    ) -> CommentProposal:
        row = connection.execute(
            "SELECT * FROM proposals WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()
        if row is None:
            raise ProposalNotFound(proposal_id)
        return _proposal(row)

    def approve(self, proposal_id: str, actor: str) -> CommentProposal:
        validated = ApprovalRequest(proposal_id=proposal_id, actor=actor)
        with self._connect() as connection:
            proposal = self._get_proposal(connection, validated.proposal_id)
            if proposal.expires_at <= _now():
                raise ProposalStale(proposal_id)
            if proposal.status is ProposalStatus.EXECUTED:
                return proposal
            connection.execute(
                """
                UPDATE proposals
                SET status = ?, approved_by = ?, approved_at = ?
                WHERE proposal_id = ?
                """,
                (
                    ProposalStatus.APPROVED.value,
                    validated.actor,
                    _now().isoformat(),
                    proposal_id,
                ),
            )
            return self._get_proposal(connection, proposal_id)

    def require_approved(self, proposal_id: str) -> CommentProposal:
        with self._connect() as connection:
            proposal = self._get_proposal(connection, proposal_id)
        if proposal.expires_at <= _now():
            raise ProposalStale(proposal_id)
        if proposal.status is not ProposalStatus.APPROVED:
            raise ApprovalRequired(proposal_id)
        return proposal

    def get_execution(self, proposal_id: str) -> CommentReceipt | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM executions WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
        if row is None:
            return None
        return CommentReceipt(
            proposal_id=proposal_id,
            comment_id=row["comment_id"],
            url=row["url"],
            replayed=False,
        )

    def record_execution(
        self, proposal_id: str, comment: GitHubComment
    ) -> CommentReceipt:
        existing = self.get_execution(proposal_id)
        if existing is not None:
            return existing.model_copy(update={"replayed": True})
        with self._connect() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO executions (
                        proposal_id, comment_id, url, executed_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (proposal_id, comment.comment_id, comment.url, _now().isoformat()),
                )
            except sqlite3.IntegrityError:
                replay = self.get_execution(proposal_id)
                if replay is None:
                    raise
                return replay.model_copy(update={"replayed": True})
            connection.execute(
                "UPDATE proposals SET status = ? WHERE proposal_id = ?",
                (ProposalStatus.EXECUTED.value, proposal_id),
            )
        return CommentReceipt(
            proposal_id=proposal_id,
            comment_id=comment.comment_id,
            url=comment.url,
            replayed=False,
        )

    def record_delivery(
        self,
        delivery_id: str,
        payload: bytes,
        event: str,
        *,
        action: str | None,
        repository: str | None,
        pull_request_number: int | None,
    ) -> WebhookReceipt:
        payload_hash = hashlib.sha256(payload).hexdigest()
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT * FROM deliveries WHERE delivery_id = ?", (delivery_id,)
            ).fetchone()
            if existing is not None:
                if existing["payload_hash"] != payload_hash:
                    raise DeliveryConflict(delivery_id)
                return WebhookReceipt(
                    delivery_id=delivery_id,
                    event=existing["event"],
                    action=existing["action"],
                    repository=existing["repository"],
                    pull_request_number=existing["pull_request_number"],
                    status=DeliveryStatus.DUPLICATE,
                )
            connection.execute(
                """
                INSERT INTO deliveries (
                    delivery_id, payload_hash, event, action, repository,
                    pull_request_number, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    delivery_id,
                    payload_hash,
                    event,
                    action,
                    repository,
                    pull_request_number,
                    _now().isoformat(),
                ),
            )
        return WebhookReceipt(
            delivery_id=delivery_id,
            event=event,
            action=action,
            repository=repository,
            pull_request_number=pull_request_number,
            status=DeliveryStatus.ACCEPTED,
        )
