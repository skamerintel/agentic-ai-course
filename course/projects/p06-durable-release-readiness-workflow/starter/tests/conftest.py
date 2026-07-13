from __future__ import annotations

import pytest

from release_workflow.data import (
    load_manifests,
    load_notes_reviews,
    load_policy,
    load_snapshots,
)
from release_workflow.models import DecisionRecord, PublicationReceipt
from release_workflow.reviewer import FixtureNotesReviewer
from release_workflow.workflow import WorkflowDependencies


class RecordingSink:
    def __init__(self) -> None:
        self.records: dict[str, PublicationReceipt] = {}

    def publish(self, workflow_id: str, decision: DecisionRecord) -> PublicationReceipt:
        receipt = PublicationReceipt(
            workflow_id=workflow_id,
            receipt_id=f"receipt-{workflow_id}",
            payload_fingerprint=decision.decision.value,
            replayed=workflow_id in self.records,
        )
        self.records.setdefault(workflow_id, receipt)
        return receipt

    def count(self) -> int:
        return len(self.records)


@pytest.fixture
def dependencies() -> WorkflowDependencies:
    reviews = load_notes_reviews("fixtures/notes-reviews.json")
    return WorkflowDependencies(
        manifests=load_manifests("data/release-manifests.jsonl"),
        snapshots=load_snapshots("data/repository-snapshots.json"),
        policy=load_policy("data/policy-rules.json"),
        reviewer=FixtureNotesReviewer(reviews),
        sink=RecordingSink(),
    )
