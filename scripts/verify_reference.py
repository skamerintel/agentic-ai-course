from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import coursectl  # noqa: E402

PRIVATE_HOLDOUTS = {
    project: ROOT / f"course/instructor/evaluation/{project}/test_holdout.py"
    for project in ("p05", "p06", "p07", "p08")
}
SENSITIVE_ENVIRONMENT_KEYS = {
    "ANTHROPIC_API_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_PROFILE",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_WEB_IDENTITY_TOKEN_FILE",
    "GITHUB_TOKEN",
    "OPENAI_API_KEY",
}


def offline_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("VIRTUAL_ENV", None)
    for key in SENSITIVE_ENVIRONMENT_KEYS:
        environment.pop(key, None)
    environment.update(
        {
            "CI": "true",
            "NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "UV_NO_PROGRESS": "1",
        }
    )
    return environment


@contextmanager
def command_group(label: str):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::group::{label}", flush=True)
    else:
        print(f"\n==> {label}", flush=True)
    try:
        yield
    finally:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print("::endgroup::", flush=True)


def run(command: Sequence[str], workspace: Path) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(
        command,
        cwd=workspace,
        env=offline_environment(),
        check=True,
    )


def verify_reference(project: str, workspace: Path) -> None:
    coursectl.materialize_solution(project, workspace)
    commands = [
        ("dependency sync", ["uv", "sync"]),
        ("Ruff lint", ["uv", "run", "ruff", "check", "."]),
        ("Ruff format", ["uv", "run", "ruff", "format", "--check", "."]),
        ("project tests", ["uv", "run", "pytest"]),
        ("Pyright", ["uv", "run", "pyright", "src"]),
    ]
    for label, command in commands:
        with command_group(label):
            run(command, workspace)

    holdout = PRIVATE_HOLDOUTS.get(project)
    if holdout is not None:
        with command_group("private holdout lint"):
            run(
                [
                    "uv",
                    "run",
                    "ruff",
                    "check",
                    "--config",
                    str(workspace / "pyproject.toml"),
                    str(holdout),
                ],
                workspace,
            )
            run(
                [
                    "uv",
                    "run",
                    "ruff",
                    "format",
                    "--check",
                    "--config",
                    str(workspace / "pyproject.toml"),
                    str(holdout),
                ],
                workspace,
            )
        with command_group("private mentor holdout"):
            run(["uv", "run", "pytest", str(holdout)], workspace)

    with command_group("package build"):
        run(["uv", "build"], workspace)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize and verify one offline reference implementation."
    )
    parser.add_argument("project", choices=sorted(coursectl.PROJECTS))
    parser.add_argument(
        "--workspace",
        type=Path,
        help="keep verification files at this path instead of a temporary directory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.workspace is not None:
        workspace = args.workspace.resolve()
        if workspace.exists() and any(workspace.iterdir()):
            raise SystemExit(f"workspace is not empty: {workspace}")
        verify_reference(args.project, workspace)
    else:
        with tempfile.TemporaryDirectory(prefix=f"agent-course-{args.project}-") as tmp:
            verify_reference(args.project, Path(tmp))
    print(f"{args.project} reference verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
