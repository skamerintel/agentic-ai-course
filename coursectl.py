from __future__ import annotations

import argparse
import shlex
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECTS = {
    "p01": ROOT / "course/projects/p01-model-api-behavior-lab",
    "p02": ROOT / "course/projects/p02-typed-intake-normalizer",
    "p03": ROOT / "course/projects/p03-operations-tool-agent",
    "p04": ROOT / "course/projects/p04-eval-driven-issue-triage",
    "p05": ROOT / "course/projects/p05-asynchronous-agent-job-service",
    "p06": ROOT / "course/projects/p06-durable-release-readiness-workflow",
    "p07": ROOT / "course/projects/p07-github-workflow-mcp-service",
    "p08": ROOT / "course/projects/p08-capstone-studio",
}


@dataclass(frozen=True)
class ProjectGuide:
    title: str
    first_reads: tuple[str, ...]
    learner_test_expectation: str
    first_task: str


PROJECT_GUIDES = {
    "p01": ProjectGuide(
        title="Model API Behavior Lab",
        first_reads=(
            "PROJECT.md",
            "reports/experiment-contract.md",
            "data/incidents.jsonl",
        ),
        learner_test_expectation=(
            "Failures in normalization and scoring are intentional TODO gates."
        ),
        first_task=(
            "Map each failing test to the experiment contract before changing code."
        ),
    ),
    "p02": ProjectGuide(
        title="Typed Intake Normalizer",
        first_reads=(
            "PROJECT.md",
            "weak-schema-review.md",
            "reports/schema-decision.md",
        ),
        learner_test_expectation=(
            "Weak-schema, policy, and pipeline failures are intentional TODO gates."
        ),
        first_task=(
            "Defend the target schema and failure taxonomy before implementing retries."
        ),
    ),
    "p03": ProjectGuide(
        title="Operations Tool Agent",
        first_reads=(
            "PROJECT.md",
            "broken-agent-loop-review.md",
            "reports/tool-catalog.md",
        ),
        learner_test_expectation=(
            "Tool-registry and agent-loop failures are intentional TODO gates."
        ),
        first_task=(
            "Approve bounded tool contracts and loop termination rules before coding."
        ),
    ),
    "p04": ProjectGuide(
        title="Eval-Driven Issue Triage",
        first_reads=(
            "PROJECT.md",
            "reports/labeling-policy.md",
            "reports/experiment-manifest.md",
        ),
        learner_test_expectation=(
            "Two data-contract tests should pass; evaluator, ownership, and retrieval "
            "TODO gates should fail."
        ),
        first_task=(
            "Freeze the labeling policy and baseline contract before improving results."
        ),
    ),
    "p05": ProjectGuide(
        title="Asynchronous Agent Job Service",
        first_reads=(
            "PROJECT.md",
            "api-requirements.md",
            "reports/architecture-decision.md",
        ),
        learner_test_expectation=(
            "Six foundation tests should pass; 12 repository, Redis-progress, and "
            "application-service TODO gates should fail."
        ),
        first_task=(
            "Define job state, transaction, idempotency, and cancellation contracts."
        ),
    ),
    "p06": ProjectGuide(
        title="Durable Release Readiness Workflow",
        first_reads=(
            "PROJECT.md",
            "broken-graph-review.md",
            "reports/state-and-graph-design.md",
        ),
        learner_test_expectation=(
            "Three schema/architecture tests should pass; 12 policy, graph, and "
            "durable-sink TODO gates should fail."
        ),
        first_task=(
            "Design state, transitions, interrupt authority, and replay behavior first."
        ),
    ),
    "p07": ProjectGuide(
        title="GitHub Workflow MCP Service",
        first_reads=(
            "PROJECT.md",
            "broken-tool-catalog-review.md",
            "reports/capability-catalog.md",
        ),
        learner_test_expectation=(
            "Seven model/fixture/architecture tests should pass; 13 HTTP, state, MCP, "
            "and webhook TODO gates should fail."
        ),
        first_task=(
            "Approve the capability and permission surface before implementing tools."
        ),
    ),
    "p08": ProjectGuide(
        title="Capstone Studio",
        first_reads=(
            "PROJECT.md",
            "candidate-briefs.md",
            "reports/project-brief.md",
        ),
        learner_test_expectation=(
            "Three strict model/fixture tests should pass; seven proposal and artifact "
            "validator TODO gates should fail."
        ),
        first_task=(
            "Select and defend a workflow domain, then complete the M25 proposal "
            "artifacts before building product code."
        ),
    ),
}


def read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as source:
        return tomllib.load(source)


def solution_allowed(
    project: str,
    course_config: dict[str, Any],
    progress: dict[str, Any],
) -> bool:
    access = course_config.get("course", {}).get("solution_access", "gated")
    if access == "reference":
        return True
    if access != "gated":
        raise ValueError(f"unsupported solution_access value: {access!r}")
    return bool(progress.get("unlocked", {}).get(project, False))


def _copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)


def render_start_here(project: str, reference: bool = False) -> str:
    guide = PROJECT_GUIDES[project]
    reads = "\n".join(
        f"{index}. `{path}`" for index, path in enumerate(guide.first_reads, start=1)
    )
    if reference:
        expectation = (
            "This workspace includes the reference overlay. Its automated tests should "
            "pass; a failure is not an intentional learner TODO."
        )
        first_task = (
            "Compare the reference only after a documented attempt. Treat it as one "
            "defensible implementation, not the canonical answer."
        )
        workspace_kind = "reference workspace"
    else:
        expectation = guide.learner_test_expectation
        first_task = guide.first_task
        workspace_kind = "learner workspace"

    return f"""# Start Here: {project.upper()} — {guide.title}

This is a generated {workspace_kind}. Begin here before delegating changes to a
coding agent.

## First five minutes

Read these files in order:

{reads}

Then establish the local baseline:

```bash
uv sync
uv run pytest
```

## Expected first test run

{expectation}

Dependency-resolution errors, import failures during test collection, missing
commands, or failures outside the documented TODO boundaries are setup problems,
not learning gates. Diagnose those before implementing project behavior.

## First task

{first_task}

## Workspace map

- `PROJECT.md`: business brief, workflow, gates, and definition of done.
- `README.md`: starter-package commands and implementation notes.
- `reports/`: working copies of required learner artifacts.
- `templates/`: clean artifact templates for comparison or reset.
- `data/` and `fixtures/`: versioned development evidence when supplied.
- `rubrics/`: AI and mentor review criteria when supplied.

Do not inspect private mentor holdouts. Reference access is controlled by the
course repository's `course.toml` and `.course-progress.toml` files.
"""


def _write_start_here(project: str, destination: Path, reference: bool) -> None:
    (destination / "START_HERE.md").write_text(
        render_start_here(project, reference=reference),
        encoding="utf-8",
    )


def render_start_summary(
    project: str,
    destination: Path,
    reference: bool = False,
) -> str:
    guide = PROJECT_GUIDES[project]
    kind = "reference" if reference else "learner"
    expectation = (
        "Reference tests should pass." if reference else guide.learner_test_expectation
    )
    return "\n".join(
        (
            f"Created {project} {kind} workspace: {destination}",
            "",
            "Next:",
            f"  cd {shlex.quote(str(destination))}",
            "  uv sync",
            "  uv run pytest",
            "",
            f"Expected first test run: {expectation}",
            f"First task: {guide.first_task if not reference else 'Read START_HERE.md after completing a documented attempt.'}",
            "Read START_HERE.md for the workspace map and gate guidance.",
        )
    )


def start_project(project: str, destination: Path) -> None:
    source = PROJECTS[project]
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    _copy_tree(source / "starter", destination)
    for directory in ("data", "fixtures", "rubrics", "templates"):
        shared = source / directory
        if shared.exists():
            _copy_tree(shared, destination / directory)
    shutil.copy2(source / "README.md", destination / "PROJECT.md")
    for document in source.glob("*.md"):
        if document.name != "README.md":
            shutil.copy2(document, destination / document.name)

    reports = destination / "reports"
    reports.mkdir(exist_ok=True)
    templates = source / "templates"
    if templates.exists():
        for template in templates.glob("*.md"):
            shutil.copy2(template, reports / template.name)
    _write_start_here(project, destination, reference=False)


def materialize_solution(project: str, destination: Path) -> None:
    start_project(project, destination)
    reference = ROOT / "course/instructor/reference" / PROJECTS[project].name
    _copy_tree(reference, destination)
    _write_start_here(project, destination, reference=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="coursectl")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="show course configuration and unlocks")

    start = subparsers.add_parser("start", help="create a learner workspace")
    start.add_argument("project", choices=sorted(PROJECTS))
    start.add_argument("destination", type=Path)
    start.add_argument(
        "--quiet",
        action="store_true",
        help="print only the created workspace path",
    )

    solution = subparsers.add_parser("solution", help="materialize a reference")
    solution.add_argument("project", choices=sorted(PROJECTS))
    solution.add_argument("destination", type=Path)
    solution.add_argument(
        "--quiet",
        action="store_true",
        help="print only the created workspace path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = read_toml(ROOT / "course.toml")
    progress = read_toml(ROOT / ".course-progress.toml")

    if args.command == "status":
        access = config.get("course", {}).get("solution_access", "gated")
        print(f"solution access: {access}")
        for project in PROJECTS:
            allowed = solution_allowed(project, config, progress)
            print(f"{project}: {'reference available' if allowed else 'gated'}")
        return 0

    destination = args.destination.resolve()
    reference = args.command == "solution"
    try:
        if args.command == "start":
            start_project(args.project, destination)
        else:
            if not solution_allowed(args.project, config, progress):
                print(
                    "reference is gated; the mentor must unlock it in "
                    ".course-progress.toml",
                    file=sys.stderr,
                )
                return 3
            materialize_solution(args.project, destination)
    except (FileExistsError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.quiet:
        print(destination)
    else:
        print(render_start_summary(args.project, destination, reference=reference))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
