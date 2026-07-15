from model_api_lab.data import load_incidents
from model_api_lab.evaluate import score_summary


def test_scores_found_and_missed_facts() -> None:
    incident = load_incidents("data/incidents.jsonl")[0]

    score = score_summary(
        incident,
        "US checkout had 503 errors after Redis memory exhaustion. Added capacity.",
    )

    assert "affected checkout in US" in score.facts_found
    assert "503 errors" in score.facts_found
    assert "capacity mitigation" in score.facts_found
    assert "no completed order loss" in score.facts_missed
    assert score.fact_recall == 0.8


def test_flags_only_supplied_forbidden_phrases() -> None:
    incident = load_incidents("data/incidents.jsonl")[2]

    score = score_summary(
        incident,
        "Version 4.12 affected all Android users and the root cause was confirmed.",
    )

    assert score.forbidden_claims_found == (
        "root cause was confirmed",
        "all android users",
    )
