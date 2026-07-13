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
    blockers: list[Blocker] = []
    blocking_labels = set(policy.block_on_issue_labels)
    blocking_severities = set(policy.block_on_issue_severities)
    allowed_pr_labels = set(policy.allowed_open_pr_labels)

    for issue in repository.open_issues:
        if issue.label in blocking_labels or issue.severity in blocking_severities:
            blockers.append(
                Blocker(
                    code="blocking_issue",
                    detail=f"Issue {issue.id} blocks release",
                    evidence=f"issue:{issue.id}",
                )
            )

    for pull_request in repository.open_pull_requests:
        if not set(pull_request.labels) <= allowed_pr_labels:
            blockers.append(
                Blocker(
                    code="open_pull_request",
                    detail=f"Pull request {pull_request.id} is not exempt",
                    evidence=f"pull_request:{pull_request.id}",
                )
            )

    for check in manifest.required_checks:
        actual = repository.checks.get(check, "missing")
        if actual != policy.required_check_status:
            blockers.append(
                Blocker(
                    code="failed_check",
                    detail=f"Required check {check} is {actual}",
                    evidence=f"check:{check}:{actual}",
                )
            )

    if notes_review.score < policy.notes_minimum_score:
        blockers.append(
            Blocker(
                code="incomplete_notes",
                detail="Release notes do not meet the completeness threshold",
                evidence=f"notes_score:{notes_review.score}",
            )
        )
    return blockers


def route_for_blockers(blockers: list[Blocker]) -> RouteName:
    return "hold" if blockers else "ready"
