from issue_triage.models import Team
from issue_triage.ownership import resolve_owner


def test_component_rule_precedes_repo_default() -> None:
    assert (
        resolve_owner("acme/devportal", "docs", "data/ownership-rules.json")
        is Team.DOCS
    )
    assert (
        resolve_owner("acme/devportal", "ui", "data/ownership-rules.json")
        is Team.DEVELOPER_EXPERIENCE
    )


def test_unknown_repo_returns_unknown_team() -> None:
    owner = resolve_owner("acme/unknown", None, "data/ownership-rules.json")

    assert owner is Team.UNKNOWN
