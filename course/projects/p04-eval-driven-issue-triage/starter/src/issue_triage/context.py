from __future__ import annotations

import json
from pathlib import Path

from issue_triage.models import Issue, KnownIssue, RetrievedCandidate
from issue_triage.ownership import resolve_owner


def build_context(
    issue: Issue,
    corpus: list[KnownIssue],
    candidates: list[RetrievedCandidate],
    ownership_rules: str | Path,
    mode: str,
) -> str:
    owner = resolve_owner(issue.repo, issue.component, ownership_rules)
    if mode == "none":
        return ""
    if mode == "structured":
        return json.dumps({"resolved_owner": owner.value})
    if mode == "full":
        selected = corpus
    elif mode == "retrieval":
        ids = {item.issue_id for item in candidates}
        selected = [item for item in corpus if item.issue_id in ids]
    else:
        raise ValueError(f"unknown context mode: {mode}")
    return json.dumps(
        {
            "resolved_owner": owner.value,
            "historical_issues": [item.model_dump(mode="json") for item in selected],
        },
        sort_keys=True,
    )
