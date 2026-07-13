from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECTS = {
    "p01": ROOT / "course/projects/p01-model-api-behavior-lab",
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


def start_project(project: str, destination: Path) -> None:
    source = PROJECTS[project]
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    _copy_tree(source / "starter", destination)
    _copy_tree(source / "data", destination / "data")
    _copy_tree(source / "fixtures", destination / "fixtures")
    _copy_tree(source / "rubrics", destination / "rubrics")
    _copy_tree(source / "templates", destination / "templates")
    shutil.copy2(source / "README.md", destination / "PROJECT.md")
    shutil.copy2(
        source / "flawed-comparison-report.md",
        destination / "flawed-comparison-report.md",
    )

    reports = destination / "reports"
    reports.mkdir(exist_ok=True)
    shutil.copy2(
        source / "templates/experiment-contract.md",
        reports / "experiment-contract.md",
    )
    shutil.copy2(source / "templates/ai-work-log.md", reports / "ai-work-log.md")


def materialize_solution(project: str, destination: Path) -> None:
    start_project(project, destination)
    reference = ROOT / "course/instructor/reference/p01-model-api-behavior-lab"
    _copy_tree(reference, destination)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="coursectl")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="show course configuration and unlocks")

    start = subparsers.add_parser("start", help="create a learner workspace")
    start.add_argument("project", choices=sorted(PROJECTS))
    start.add_argument("destination", type=Path)

    solution = subparsers.add_parser("solution", help="materialize a reference")
    solution.add_argument("project", choices=sorted(PROJECTS))
    solution.add_argument("destination", type=Path)
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

    try:
        if args.command == "start":
            start_project(args.project, args.destination.resolve())
        else:
            if not solution_allowed(args.project, config, progress):
                print(
                    "reference is gated; the mentor must unlock it in "
                    ".course-progress.toml",
                    file=sys.stderr,
                )
                return 3
            materialize_solution(args.project, args.destination.resolve())
    except (FileExistsError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(args.destination.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
