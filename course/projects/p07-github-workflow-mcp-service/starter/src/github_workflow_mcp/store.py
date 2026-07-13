from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from github_workflow_mcp.models import (
    CommentProposal,
    CommentReceipt,
    GitHubComment,
    WebhookReceipt,
)


class StateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self.setup()

    def setup(self) -> None:
        raise NotImplementedError("create proposal, execution, and delivery tables")

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
        raise NotImplementedError("persist a pending comment proposal")

    def approve(self, proposal_id: str, actor: str) -> CommentProposal:
        raise NotImplementedError("record out-of-band human approval")

    def require_approved(self, proposal_id: str) -> CommentProposal:
        raise NotImplementedError("load a current approved proposal")

    def get_execution(self, proposal_id: str) -> CommentReceipt | None:
        raise NotImplementedError("load an existing write receipt")

    def record_execution(
        self, proposal_id: str, comment: GitHubComment
    ) -> CommentReceipt:
        raise NotImplementedError("persist one idempotent execution receipt")

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
        raise NotImplementedError("persist and deduplicate a webhook delivery")
