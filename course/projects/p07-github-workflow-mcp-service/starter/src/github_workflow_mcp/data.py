from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from github_workflow_mcp.models import CapabilityPolicy


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_policy(path: str | Path) -> CapabilityPolicy:
    return CapabilityPolicy.model_validate(load_json(path), strict=True)
