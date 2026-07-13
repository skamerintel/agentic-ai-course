from __future__ import annotations

from release_workflow.models import (
    Blocker,
    NotesReview,
    PolicyRules,
    ReleaseManifest,
    RepositorySnapshot,
    RouteName,
)


def derive_blockers(
    manifest: ReleaseManifest,
    repository: RepositorySnapshot,
    notes_review: NotesReview,
    policy: PolicyRules,
) -> list[Blocker]:
    raise NotImplementedError("implement deterministic release blocker policy")


def route_for_blockers(blockers: list[Blocker]) -> RouteName:
    raise NotImplementedError("route to ready or hold")
