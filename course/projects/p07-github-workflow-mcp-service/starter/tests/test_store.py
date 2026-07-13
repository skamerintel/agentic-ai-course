from datetime import timedelta

import pytest

from github_workflow_mcp.errors import (
    ApprovalRequired,
    DeliveryConflict,
    ProposalStale,
)
from github_workflow_mcp.models import DeliveryStatus, GitHubComment
from github_workflow_mcp.store import StateStore


def test_proposal_requires_out_of_band_approval(tmp_path) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    proposal = store.create_proposal(
        "acme", "payments-service", 41, "Investigating this issue.", "Triage followup"
    )

    with pytest.raises(ApprovalRequired):
        store.require_approved(proposal.proposal_id)
    approved = store.approve(proposal.proposal_id, "mentor@example.com")

    assert approved.approved_by == "mentor@example.com"
    assert (
        store.require_approved(proposal.proposal_id).proposal_id == proposal.proposal_id
    )


def test_stale_proposal_cannot_be_approved(tmp_path) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    proposal = store.create_proposal(
        "acme",
        "payments-service",
        41,
        "Too late",
        "Expired fixture",
        ttl=timedelta(seconds=-1),
    )

    with pytest.raises(ProposalStale):
        store.approve(proposal.proposal_id, "mentor@example.com")


def test_execution_receipt_replays(tmp_path) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    proposal = store.create_proposal(
        "acme", "payments-service", 41, "Approved", "Fixture"
    )
    store.approve(proposal.proposal_id, "mentor@example.com")
    comment = GitHubComment(comment_id=500, url="https://github.test/comment/500")

    first = store.record_execution(proposal.proposal_id, comment)
    second = store.record_execution(proposal.proposal_id, comment)

    assert first.replayed is False
    assert second.replayed is True
    assert first.comment_id == second.comment_id


def test_webhook_delivery_is_durable_and_conflict_checked(tmp_path) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    first = store.record_delivery(
        "delivery-1",
        b'{"action":"opened"}',
        "pull_request",
        action="opened",
        repository="acme/payments-service",
        pull_request_number=90,
    )
    duplicate = store.record_delivery(
        "delivery-1",
        b'{"action":"opened"}',
        "pull_request",
        action="opened",
        repository="acme/payments-service",
        pull_request_number=90,
    )

    assert first.status is DeliveryStatus.ACCEPTED
    assert duplicate.status is DeliveryStatus.DUPLICATE
    with pytest.raises(DeliveryConflict):
        store.record_delivery(
            "delivery-1",
            b'{"action":"closed"}',
            "pull_request",
            action="closed",
            repository="acme/payments-service",
            pull_request_number=90,
        )
