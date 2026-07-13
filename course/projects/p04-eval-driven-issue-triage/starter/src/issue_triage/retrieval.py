from __future__ import annotations

from typing import Any

from issue_triage.models import Issue, KnownIssue, RetrievalQuery, RetrievedCandidate


def retrieve_candidates(
    issue: Issue,
    corpus: list[KnownIssue],
    *,
    limit: int = 3,
    same_repo_only: bool = True,
) -> list[RetrievedCandidate]:
    raise NotImplementedError("implement inspectable lexical retrieval")


def evaluate_retrieval(
    issues: list[Issue],
    corpus: list[KnownIssue],
    queries: list[RetrievalQuery],
    *,
    limit: int = 3,
) -> dict[str, Any]:
    raise NotImplementedError("implement hit rate, MRR, and context-size reporting")
