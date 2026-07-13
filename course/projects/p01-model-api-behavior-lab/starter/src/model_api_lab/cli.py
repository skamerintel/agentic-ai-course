from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from model_api_lab.data import load_incidents
from model_api_lab.evaluate import score_summary
from model_api_lab.experiment import run_offline, summarize, write_jsonl
from model_api_lab.models import ExperimentRecord
from model_api_lab.providers import (
    call_anthropic_messages,
    call_openai_chat,
    call_openai_responses,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="model-api-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    offline = subparsers.add_parser("offline", help="run deterministic fixtures")
    offline.add_argument("--data", default="data/incidents.jsonl")
    offline.add_argument("--fixtures", default="fixtures")
    offline.add_argument("--output", default="reports/offline-results.jsonl")

    live = subparsers.add_parser("live", help="run one live provider call")
    live.add_argument("provider", choices=("responses", "chat", "anthropic"))
    live.add_argument("incident_id")
    live.add_argument("--data", default="data/incidents.jsonl")
    live.add_argument("--output", default="reports/live-result.json")
    live.add_argument("--timeout", type=float, default=60.0)
    return parser


def _live(args: argparse.Namespace) -> int:
    incidents = {item.id: item for item in load_incidents(args.data)}
    incident = incidents[args.incident_id]

    if args.provider == "responses":
        model = os.environ["OPENAI_MODEL"]
        result = call_openai_responses(incident, model, args.timeout)
    elif args.provider == "chat":
        model = os.environ["OPENAI_MODEL"]
        result = call_openai_chat(incident, model, args.timeout)
    else:
        model = os.environ["ANTHROPIC_MODEL"]
        result = call_anthropic_messages(incident, model, args.timeout)

    record = ExperimentRecord(
        incident_id=incident.id,
        result=result,
        score=score_summary(incident, result.text),
    )
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record.as_dict(), indent=2), encoding="utf-8")
    print(json.dumps(record.as_dict(), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "offline":
        records = run_offline(args.data, args.fixtures)
        write_jsonl(records, args.output)
        print(summarize(records))
        return 0
    return _live(args)
