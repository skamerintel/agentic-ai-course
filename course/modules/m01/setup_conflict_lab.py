from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def write_policy(path: Path, body: str) -> None:
    path.write_text(f"# Processing policy\n\n{body}\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python setup_conflict_lab.py DESTINATION")
        return 2

    destination = Path(sys.argv[1]).expanduser().resolve()
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    run("git", "init", "-b", "main", cwd=destination)
    run("git", "config", "user.name", "Course Learner", cwd=destination)
    run("git", "config", "user.email", "learner@example.invalid", cwd=destination)

    policy = destination / "processing-policy.md"
    write_policy(policy, "Every accepted record is processed once.")
    run("git", "add", "processing-policy.md", cwd=destination)
    run("git", "commit", "-m", "Add initial processing policy", cwd=destination)

    run("git", "switch", "-c", "feature/validation-copy", cwd=destination)
    write_policy(
        policy,
        "Invalid records must be rejected and include a human-readable reason.",
    )
    run("git", "add", "processing-policy.md", cwd=destination)
    run("git", "commit", "-m", "Require validation failure reasons", cwd=destination)

    run("git", "switch", "main", cwd=destination)
    write_policy(
        policy,
        "Every processed record must retain its correlation identifier.",
    )
    run("git", "add", "processing-policy.md", cwd=destination)
    run("git", "commit", "-m", "Require correlation identifiers", cwd=destination)

    print(destination)
    print("Next: git merge feature/validation-copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
