from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from github_workflow_mcp.data import load_json, load_policy
from github_workflow_mcp.errors import ApprovalRequired, ProposalNotFound
from github_workflow_mcp.github import FixtureGitHubGateway
from github_workflow_mcp.models import (
    CommentProposal,
    CommentReceipt,
    GitHubComment,
    ProposalStatus,
)


class MemoryStore:
    def __init__(self) -> None:
        self.proposals: dict[str, CommentProposal] = {}
        self.executions: dict[str, CommentReceipt] = {}

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
        now = datetime.now(UTC)
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
        self.proposals[proposal.proposal_id] = proposal
        return proposal

    def approve(self, proposal_id: str, actor: str) -> CommentProposal:
        proposal = self.proposals[proposal_id]
        approved = proposal.model_copy(
            update={"status": ProposalStatus.APPROVED, "approved_by": actor}
        )
        self.proposals[proposal_id] = approved
        return approved

    def require_approved(self, proposal_id: str) -> CommentProposal:
        proposal = self.proposals.get(proposal_id)
        if proposal is None:
            raise ProposalNotFound(proposal_id)
        if proposal.status is not ProposalStatus.APPROVED:
            raise ApprovalRequired(proposal_id)
        return proposal

    def get_execution(self, proposal_id: str) -> CommentReceipt | None:
        return self.executions.get(proposal_id)

    def record_execution(
        self, proposal_id: str, comment: GitHubComment
    ) -> CommentReceipt:
        existing = self.executions.get(proposal_id)
        if existing:
            return existing.model_copy(update={"replayed": True})
        receipt = CommentReceipt(
            proposal_id=proposal_id,
            comment_id=comment.comment_id,
            url=comment.url,
            replayed=False,
        )
        self.executions[proposal_id] = receipt
        return receipt


@pytest.fixture
def fixture_gateway() -> FixtureGitHubGateway:
    return FixtureGitHubGateway(load_json("fixtures/github-api.json"))


@pytest.fixture
def policy():
    return load_policy("data/capability-policy.json")


@pytest.fixture
def memory_store() -> MemoryStore:
    return MemoryStore()
