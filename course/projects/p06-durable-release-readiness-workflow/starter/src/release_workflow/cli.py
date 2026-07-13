from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from release_workflow.data import (
    load_manifests,
    load_notes_reviews,
    load_policy,
    load_snapshots,
)
from release_workflow.reviewer import FixtureNotesReviewer, OpenAINotesReviewer
from release_workflow.sink import SqliteDecisionSink
from release_workflow.workflow import (
    WorkflowDependencies,
    approval_command,
    build_workflow,
    graph_config,
    initial_state,
)


def _dependencies(args: argparse.Namespace) -> WorkflowDependencies:
    manifests = load_manifests(args.manifests)
    snapshots = load_snapshots(args.snapshots)
    policy = load_policy(args.policy)
    reviews = load_notes_reviews(args.reviews)
    if os.getenv("RELEASE_WORKFLOW_REVIEWER", "fixture") == "openai":
        reviewer = OpenAINotesReviewer(
            os.environ["OPENAI_MODEL"],
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    else:
        reviewer = FixtureNotesReviewer(reviews)
    return WorkflowDependencies(
        manifests=manifests,
        snapshots=snapshots,
        policy=policy,
        reviewer=reviewer,
        sink=SqliteDecisionSink(args.decisions),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="release-workflow")
    parser.add_argument("--manifests", default="data/release-manifests.jsonl")
    parser.add_argument("--snapshots", default="data/repository-snapshots.json")
    parser.add_argument("--policy", default="data/policy-rules.json")
    parser.add_argument("--reviews", default="fixtures/notes-reviews.json")
    parser.add_argument("--checkpoints", default="checkpoints.sqlite")
    parser.add_argument("--decisions", default="decisions.sqlite")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("release_id")
    start.add_argument("--thread-id", required=True)

    resume = subparsers.add_parser("resume")
    resume.add_argument("--thread-id", required=True)
    resume.add_argument(
        "--action", choices=("approve", "edit", "reject"), required=True
    )
    resume.add_argument("--rationale", default="Mentor-approved fixture run")
    resume.add_argument(
        "--edited-decision",
        choices=("ready", "hold", "ready_with_conditions", "rejected"),
    )
    resume.add_argument("--condition", action="append", default=[])
    return parser


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    dependencies = _dependencies(args)
    Path(args.checkpoints).parent.mkdir(parents=True, exist_ok=True)
    with SqliteSaver.from_conn_string(args.checkpoints) as checkpointer:
        checkpointer.setup()
        graph = build_workflow(dependencies, checkpointer=checkpointer)
        config = graph_config(args.thread_id)
        if args.command == "start":
            result = graph.invoke(
                initial_state(args.thread_id, args.release_id), config
            )
        else:
            approval = approval_command(
                args.action,
                args.rationale,
                edited_decision=args.edited_decision,
                conditions=args.condition,
            )
            result = graph.invoke(
                Command(resume=approval.model_dump(mode="json")), config
            )
    _print(result)
    return 0
