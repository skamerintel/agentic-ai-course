from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from operations_agent.models import Scenario


class RetryableToolError(Exception):
    pass


class TerminalToolError(Exception):
    pass


class ToolNotFoundError(Exception):
    pass


class OperationsStore:
    def __init__(self, data_dir: str | Path) -> None:
        root = Path(data_dir)
        self.services: list[dict[str, Any]] = json.loads(
            (root / "services.json").read_text(encoding="utf-8")
        )
        self.assets: list[dict[str, Any]] = json.loads(
            (root / "assets.json").read_text(encoding="utf-8")
        )
        self.incidents: list[dict[str, Any]] = json.loads(
            (root / "incidents.json").read_text(encoding="utf-8")
        )
        self.failure_plan: dict[str, list[str]] = json.loads(
            (root / "failure_plan.json").read_text(encoding="utf-8")
        )

    def _planned_failure(self, tool_name: str, key: str) -> None:
        plan = self.failure_plan.get(f"{tool_name}:{key}", [])
        if not plan:
            return
        failure = plan.pop(0)
        if failure == "retryable":
            raise RetryableToolError(f"temporary failure for {tool_name}")
        if failure == "terminal":
            raise TerminalToolError(f"terminal failure for {tool_name}")

    def get_service_status(self, service_name: str) -> dict[str, Any]:
        normalized = service_name.casefold()
        self._planned_failure("get_service_status", normalized)
        for service in self.services:
            if str(service["name"]).casefold() == normalized:
                return service
        raise ToolNotFoundError(f"service not found: {service_name}")

    def get_asset(self, asset_id: str) -> dict[str, Any]:
        normalized = asset_id.upper()
        self._planned_failure("get_asset", normalized)
        for asset in self.assets:
            if str(asset["asset_id"]).upper() == normalized:
                return asset
        raise ToolNotFoundError(f"asset not found: {asset_id}")

    def search_incidents(self, service_name: str, limit: int) -> list[dict[str, Any]]:
        normalized = service_name.casefold()
        self._planned_failure("search_incidents", normalized)
        matches = [
            incident
            for incident in self.incidents
            if str(incident["service"]).casefold() == normalized
        ]
        matches.sort(key=lambda item: str(item["started_at"]), reverse=True)
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for incident in matches:
            incident_id = str(incident["incident_id"])
            if incident_id in seen:
                continue
            seen.add(incident_id)
            unique.append(incident)
        if not unique:
            raise ToolNotFoundError(f"incidents not found for: {service_name}")
        return unique[:limit]


def load_scenarios(path: str | Path) -> list[Scenario]:
    source = Path(path).read_text(encoding="utf-8")
    return TypeAdapter(list[Scenario]).validate_json(source, strict=True)
