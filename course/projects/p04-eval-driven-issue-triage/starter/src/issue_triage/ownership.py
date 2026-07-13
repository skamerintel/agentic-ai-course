from __future__ import annotations

from pathlib import Path

from issue_triage.models import Team


def resolve_owner(repo: str, component: str | None, rules_path: str | Path) -> Team:
    raise NotImplementedError("implement deterministic ownership lookup")
