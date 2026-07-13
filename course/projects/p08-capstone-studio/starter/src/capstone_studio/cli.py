from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import ValidationError

from capstone_studio.data import load_model, load_model_list
from capstone_studio.models import ArtifactManifest, CapstoneProposal, RequiredArtifact
from capstone_studio.validator import validate_artifact_manifest, validate_proposal


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capstone-studio")
    subparsers = parser.add_subparsers(dest="command", required=True)

    proposal = subparsers.add_parser("validate-proposal")
    proposal.add_argument("proposal", type=Path)
    proposal.add_argument("--json", action="store_true")

    artifacts = subparsers.add_parser("validate-artifacts")
    artifacts.add_argument("manifest", type=Path)
    artifacts.add_argument("requirements", type=Path)
    artifacts.add_argument("--json", action="store_true")
    return parser


def _print_report(report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return
    print(f"{report.subject}: {'PASS' if report.passed else 'BLOCKED'}")
    for finding in report.findings:
        print(f"- [{finding.severity}] {finding.code}: {finding.message}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-proposal":
            report = validate_proposal(load_model(args.proposal, CapstoneProposal))
        else:
            manifest = load_model(args.manifest, ArtifactManifest)
            requirements = load_model_list(args.requirements, RequiredArtifact)
            report = validate_artifact_manifest(manifest, requirements)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"invalid input: {exc}")
        return 2
    _print_report(report, args.json)
    return 0 if report.passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
