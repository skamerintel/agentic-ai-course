from release_workflow.data import (
    load_manifests,
    load_notes_reviews,
    load_policy,
    load_snapshots,
)
from release_workflow.policy import derive_blockers, route_for_blockers


def test_ready_release_has_no_blockers() -> None:
    manifests = load_manifests("data/release-manifests.jsonl")
    snapshots = load_snapshots("data/repository-snapshots.json")
    reviews = load_notes_reviews("fixtures/notes-reviews.json")

    blockers = derive_blockers(
        manifests["REL-100"],
        snapshots["REL-100"],
        reviews["REL-100"],
        load_policy("data/policy-rules.json"),
    )

    assert blockers == []
    assert route_for_blockers(blockers) == "ready"


def test_security_release_exposes_multiple_blocker_categories() -> None:
    manifests = load_manifests("data/release-manifests.jsonl")
    snapshots = load_snapshots("data/repository-snapshots.json")
    reviews = load_notes_reviews("fixtures/notes-reviews.json")

    blockers = derive_blockers(
        manifests["REL-101"],
        snapshots["REL-101"],
        reviews["REL-101"],
        load_policy("data/policy-rules.json"),
    )

    assert {item.code for item in blockers} == {
        "blocking_issue",
        "failed_check",
        "incomplete_notes",
    }
    assert route_for_blockers(blockers) == "hold"
