from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATTERNS = ("__pycache__", ".pytest_cache", ".ruff_cache", "*.pyc")


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*CACHE_PATTERNS),
    )


def run(command: list[str], workspace: Path) -> None:
    print("$ " + " ".join(command), flush=True)
    environment = os.environ.copy()
    environment.pop("VIRTUAL_ENV", None)
    environment.update(
        {
            "CI": "true",
            "NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "UV_NO_PROGRESS": "1",
        }
    )
    subprocess.run(command, cwd=workspace, env=environment, check=True)


def verify_m02(root: Path) -> None:
    workspace = root / "m02"
    copy_tree(ROOT / "course/modules/m02/lab", workspace)
    reference = ROOT / "course/instructor/reference/m02-ticket-rules"
    copy_tree(reference / "src", workspace / "src")
    copy_tree(reference / "tests", workspace / "tests")

    run(["uv", "sync"], workspace)
    run(["uv", "run", "ruff", "check", "."], workspace)
    run(["uv", "run", "ruff", "format", "--check", "."], workspace)
    run(["uv", "run", "pytest", "tests", "acceptance_tests"], workspace)
    run(["uv", "run", "pyright", "src"], workspace)


def verify_m03(root: Path) -> None:
    workspace = root / "m03"
    copy_tree(ROOT / "course/modules/m03/lab", workspace)
    reference = ROOT / "course/instructor/reference/m03-async-client"
    shutil.copy2(reference / "client.py", workspace / "client.py")
    shutil.copy2(reference / "test_client.py", workspace / "test_client.py")

    run(["ruff", "check", "."], workspace)
    run(["ruff", "format", "--check", "."], workspace)
    run(["python", "-m", "unittest", "test_client.py"], workspace)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="agent-course-modules-") as tmp:
        root = Path(tmp)
        verify_m02(root)
        verify_m03(root)
    print("M02 and M03 reference verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
