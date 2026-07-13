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
    "p02": ROOT / "course/projects/p02-typed-intake-normalizer",
    "p03": ROOT / "course/projects/p03-operations-tool-agent",
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


def materialize_solution(project: str, destination: Path) -> None:
    start_project(project, destination)
    reference = ROOT / "course/instructor/reference" / PROJECTS[project].name
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
