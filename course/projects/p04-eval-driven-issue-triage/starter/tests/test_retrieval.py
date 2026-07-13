from issue_triage.data import (
    load_issues,
    load_known_issues,
    load_retrieval_queries,
)
from issue_triage.retrieval import evaluate_retrieval, retrieve_candidates


def test_retrieves_expected_duplicate_for_payments_issue() -> None:
    issue = load_issues("data/issues-dev.jsonl")[0]
    corpus = load_known_issues("data/known-issues.jsonl")
    candidates = retrieve_candidates(issue, corpus)

    assert candidates[0].issue_id == "K001"


def test_retrieval_report_separates_hit_rate_and_context_size() -> None:
    report = evaluate_retrieval(
        load_issues("data/issues-dev.jsonl"),
        load_known_issues("data/known-issues.jsonl"),
        load_retrieval_queries("data/retrieval-queries.jsonl"),
    )

    assert report["query_count"] == 6
    assert report["hit_at_3"] >= 0.8
    assert report["mean_reciprocal_rank"] >= 0.8
    assert report["full_context_characters"] > report["mean_retrieved_characters"]
