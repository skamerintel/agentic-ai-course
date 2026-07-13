from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

from intake_normalizer.data import load_requests
from intake_normalizer.models import ProcessingResult, ProgressEvent
from intake_normalizer.pipeline import process_batch, process_request
from intake_normalizer.provider import FixtureGateway, OpenAIResponsesGateway


def _write_jsonl(values: list[ProcessingResult], output: str | Path) -> None:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(value.model_dump(mode="json"), sort_keys=True) for value in values
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intake-normalizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    offline = subparsers.add_parser("offline")
    offline.add_argument("--data", default="data/requests.jsonl")
    offline.add_argument("--fixtures", default="fixtures/provider_sequences.json")
    offline.add_argument("--output", default="reports/offline-results.jsonl")

    live = subparsers.add_parser("live")
    live.add_argument("request_id")
    live.add_argument("--data", default="data/requests.jsonl")
    live.add_argument("--output", default="reports/live-result.json")
    live.add_argument("--timeout", type=float, default=60.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    requests = load_requests(args.data)
    events: list[ProgressEvent] = []

    if args.command == "offline":
        gateway = FixtureGateway(args.fixtures)
        results = process_batch(
            requests,
            gateway,
            emit=events.append,
            sleeper=lambda _: None,
        )
        _write_jsonl(results, args.output)
        print(json.dumps(Counter(result.outcome.value for result in results), indent=2))
        return 0

    request = next(item for item in requests if item.id == args.request_id)
    gateway = OpenAIResponsesGateway(
        os.environ["OPENAI_MODEL"], timeout_seconds=args.timeout
    )
    result = process_request(request, gateway, emit=events.append)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(result.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    print(target)
    return 0
