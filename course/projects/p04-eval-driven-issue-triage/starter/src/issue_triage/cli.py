from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from issue_triage.context import build_context
from issue_triage.data import (
    fingerprint_files,
    load_issues,
    load_known_issues,
    load_predictions,
    load_retrieval_queries,
    load_truth,
)
from issue_triage.evaluate import compare_reports, evaluate_predictions
from issue_triage.retrieval import evaluate_retrieval, retrieve_candidates
from issue_triage.triage import predict_openai


def _write_json(value: object, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _evaluate(predictions_path: str, truth_path: str) -> dict:
    return evaluate_predictions(
        load_truth(truth_path),
        load_predictions(predictions_path),
        dataset_fingerprint=fingerprint_files(truth_path),
        prediction_fingerprint=fingerprint_files(predictions_path),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="issue-triage")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--predictions", required=True)
    evaluate.add_argument("--truth", default="data/ground-truth-dev.jsonl")
    evaluate.add_argument("--output", required=True)

    compare = subparsers.add_parser("compare")
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--truth", default="data/ground-truth-dev.jsonl")
    compare.add_argument("--output", required=True)

    retrieval = subparsers.add_parser("retrieval")
    retrieval.add_argument("--issues", default="data/issues-dev.jsonl")
    retrieval.add_argument("--corpus", default="data/known-issues.jsonl")
    retrieval.add_argument("--queries", default="data/retrieval-queries.jsonl")
    retrieval.add_argument("--output", required=True)

    live = subparsers.add_parser("live")
    live.add_argument("issue_id")
    live.add_argument("--issues", default="data/issues-dev.jsonl")
    live.add_argument("--corpus", default="data/known-issues.jsonl")
    live.add_argument("--rules", default="data/ownership-rules.json")
    live.add_argument(
        "--mode",
        choices=("none", "structured", "full", "retrieval"),
        default="retrieval",
    )
    live.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "evaluate":
        report = _evaluate(args.predictions, args.truth)
    elif args.command == "compare":
        report = compare_reports(
            _evaluate(args.baseline, args.truth),
            _evaluate(args.candidate, args.truth),
        )
    elif args.command == "retrieval":
        report = evaluate_retrieval(
            load_issues(args.issues),
            load_known_issues(args.corpus),
            load_retrieval_queries(args.queries),
        )
    else:
        issues = {item.issue_id: item for item in load_issues(args.issues)}
        issue = issues[args.issue_id]
        corpus = load_known_issues(args.corpus)
        candidates = retrieve_candidates(issue, corpus)
        context = build_context(issue, corpus, candidates, args.rules, args.mode)
        prediction = predict_openai(issue, context, os.environ["OPENAI_MODEL"])
        report = prediction.model_dump(mode="json")
    _write_json(report, args.output)
    print(args.output)
    return 0
