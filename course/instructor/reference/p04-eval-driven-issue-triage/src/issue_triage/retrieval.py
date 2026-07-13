from __future__ import annotations

import re
from statistics import mean
from typing import Any

from issue_triage.models import Issue, KnownIssue, RetrievalQuery, RetrievedCandidate

TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "after",
    "all",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "when",
    "with",
}


def _tokens(value: str) -> set[str]:
    tokens = TOKEN.findall(value.casefold())
    return {token for token in tokens if token not in STOPWORDS}


def retrieve_candidates(
    issue: Issue,
    corpus: list[KnownIssue],
    *,
    limit: int = 3,
    same_repo_only: bool = True,
) -> list[RetrievedCandidate]:
    if limit < 1:
        raise ValueError("limit must be at least one")
    query_tokens = _tokens(issue.text)
    scored: list[RetrievedCandidate] = []

    for candidate in corpus:
        if same_repo_only and candidate.repo != issue.repo:
            continue
        document_tokens = _tokens(candidate.text)
        overlap = query_tokens & document_tokens
        if not overlap:
            continue
        score = len(overlap) / max(len(query_tokens), 1)
        if issue.component and candidate.component == issue.component:
            score += 0.25
        scored.append(
            RetrievedCandidate(issue_id=candidate.issue_id, score=round(score, 6))
        )
    scored.sort(key=lambda item: (-item.score, item.issue_id))
    return scored[:limit]


def evaluate_retrieval(
    issues: list[Issue],
    corpus: list[KnownIssue],
    queries: list[RetrievalQuery],
    *,
    limit: int = 3,
) -> dict[str, Any]:
    issue_index = {item.issue_id: item for item in issues}
    corpus_index = {item.issue_id: item for item in corpus}
    hits = 0
    reciprocal_rank = 0.0
    retrieved_sizes: list[int] = []
    details: list[dict[str, Any]] = []

    for query in queries:
        issue = issue_index[query.issue_id]
        candidates = retrieve_candidates(issue, corpus, limit=limit)
        ids = [item.issue_id for item in candidates]
        rank = next(
            (
                index
                for index, candidate_id in enumerate(ids, start=1)
                if candidate_id in set(query.expected_ids)
            ),
            None,
        )
        if rank is not None:
            hits += 1
            reciprocal_rank += 1 / rank
        context_characters = sum(len(corpus_index[item].text) for item in ids)
        retrieved_sizes.append(context_characters)
        details.append(
            {
                "issue_id": issue.issue_id,
                "expected_ids": query.expected_ids,
                "retrieved_ids": ids,
                "rank": rank,
                "context_characters": context_characters,
            }
        )

    full_context_characters = sum(len(item.text) for item in corpus)
    count = len(queries)
    return {
        "query_count": count,
        "limit": limit,
        "hit_at_3": round(hits / count, 4) if count else 0.0,
        "mean_reciprocal_rank": round(reciprocal_rank / count, 4) if count else 0.0,
        "full_context_characters": full_context_characters,
        "mean_retrieved_characters": round(mean(retrieved_sizes), 2)
        if retrieved_sizes
        else 0.0,
        "details": details,
    }
