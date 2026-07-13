from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from issue_triage.models import Team


def resolve_owner(repo: str, component: str | None, rules_path: str | Path) -> Team:
    payload: dict[str, Any] = json.loads(Path(rules_path).read_text(encoding="utf-8"))
    rules = payload.get("rules", [])

    for rule in rules:
        if rule["repo"] == repo and rule["component"] == component:
            return Team(rule["team"])
    for rule in rules:
        if rule["repo"] == repo and rule["component"] == "*":
            return Team(rule["team"])
    return Team.UNKNOWN
