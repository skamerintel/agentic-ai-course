from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

from operations_agent.agent import AgentConfig, run_agent
from operations_agent.data import OperationsStore, load_scenarios
from operations_agent.model import OpenAIResponsesSession, ScriptedModelSession
from operations_agent.tools import build_registry


def _scenario_config(value: dict[str, int]) -> AgentConfig:
    return AgentConfig(**value)


def _run_scenario(scenario, data_dir: str = "data"):
    registry = build_registry(OperationsStore(data_dir))
    session = ScriptedModelSession(scenario)
    return run_agent(session, registry, _scenario_config(scenario.config))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="operations-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    offline = subparsers.add_parser("offline")
    offline.add_argument("--scenarios", default="fixtures/scenarios.json")
    offline.add_argument("--data", default="data")
    offline.add_argument("--output", default="reports/offline-results.jsonl")

    scenario = subparsers.add_parser("scenario")
    scenario.add_argument("scenario_id")
    scenario.add_argument("--scenarios", default="fixtures/scenarios.json")
    scenario.add_argument("--data", default="data")

    live = subparsers.add_parser("live")
    live.add_argument("user_request")
    live.add_argument("--data", default="data")
    live.add_argument("--timeout", type=float, default=60.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "offline":
        results = [
            _run_scenario(scenario, args.data)
            for scenario in load_scenarios(args.scenarios)
        ]
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            json.dumps(item.model_dump(mode="json"), sort_keys=True) for item in results
        ]
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        counts = Counter(item.stop_reason.value for item in results)
        print(json.dumps(counts, indent=2))
        return 0

    if args.command == "scenario":
        scenario = next(
            item
            for item in load_scenarios(args.scenarios)
            if item.id == args.scenario_id
        )
        print(_run_scenario(scenario, args.data).model_dump_json(indent=2))
        return 0

    registry = build_registry(OperationsStore(args.data))
    session = OpenAIResponsesSession(
        args.user_request,
        os.environ["OPENAI_MODEL"],
        registry.schemas(),
        args.timeout,
    )
    print(run_agent(session, registry).model_dump_json(indent=2))
    return 0
