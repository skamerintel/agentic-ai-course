from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "work",
}
LINK_PATTERN = re.compile(
    r"!?\[[^\]\n]*\]\((?P<target><[^>\n]+>|[^)\s\n]+)"
    r"(?:\s+[\"'][^\"']*[\"'])?\)"
)
ACTION_USE_PATTERN = re.compile(
    r"^\s*(?:-\s*)?uses:\s*(?P<action>[^@\s]+)@(?P<reference>[^\s#]+)",
    re.MULTILINE,
)
FULL_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def repository_files(root: Path = ROOT) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
            continue
        if path.is_file():
            yield path


def validate_json_assets(root: Path = ROOT) -> tuple[list[str], int]:
    issues: list[str] = []
    checked = 0
    for path in repository_files(root):
        if path.suffix == ".json":
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                issues.append(f"{path.relative_to(root)}: invalid JSON: {exc}")
        elif path.suffix == ".jsonl":
            checked += 1
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeError) as exc:
                issues.append(f"{path.relative_to(root)}: unreadable JSONL: {exc}")
                continue
            for line_number, line in enumerate(lines, start=1):
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    issues.append(
                        f"{path.relative_to(root)}:{line_number}: invalid JSONL: {exc}"
                    )
    return issues, checked


def validate_toml_assets(root: Path = ROOT) -> tuple[list[str], int]:
    issues: list[str] = []
    paths = [path for path in repository_files(root) if path.suffix == ".toml"]
    lock = root / "uv.lock"
    if lock.is_file() and lock not in paths:
        paths.append(lock)
    for path in paths:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            issues.append(f"{path.relative_to(root)}: invalid TOML: {exc}")
    return issues, len(paths)


def validate_yaml_assets(root: Path = ROOT) -> tuple[list[str], int]:
    issues: list[str] = []
    paths = [
        path for path in repository_files(root) if path.suffix in {".yaml", ".yml"}
    ]
    for path in paths:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            issues.append(f"{path.relative_to(root)}: invalid YAML: {exc}")
    return issues, len(paths)


def validate_workflow_security(root: Path = ROOT) -> tuple[list[str], int]:
    issues: list[str] = []
    workflow_directory = root / ".github/workflows"
    paths = [
        *workflow_directory.glob("*.yaml"),
        *workflow_directory.glob("*.yml"),
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        permissions = parsed.get("permissions") if isinstance(parsed, dict) else None
        if not isinstance(permissions, dict) or permissions.get("contents") != "read":
            issues.append(
                f"{path.relative_to(root)}: top-level contents permission must be read"
            )
        if "pull_request_target:" in content:
            issues.append(
                f"{path.relative_to(root)}: pull_request_target is forbidden "
                "for course CI"
            )
        for match in ACTION_USE_PATTERN.finditer(content):
            action = match.group("action")
            reference = match.group("reference")
            if action.startswith("./"):
                continue
            if FULL_COMMIT_SHA.fullmatch(reference) is None:
                issues.append(
                    f"{path.relative_to(root)}: {action} must use a full commit SHA"
                )
    return issues, len(paths)


def markdown_without_code(value: str) -> str:
    visible: list[str] = []
    fence: str | None = None
    for line in value.splitlines():
        stripped = line.lstrip()
        marker = stripped[:3]
        if fence is None and marker in {"```", "~~~"}:
            fence = marker
            continue
        if fence == marker:
            fence = None
            continue
        if fence is None:
            visible.append(re.sub(r"`[^`\n]*`", "", line))
    return "\n".join(visible)


def _local_target(source: Path, target: str) -> Path | None:
    target = target.removeprefix("<").removesuffix(">")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith(("#", "mailto:")):
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    return (source.parent / path_text).resolve()


def validate_markdown_links(root: Path = ROOT) -> tuple[list[str], int]:
    issues: list[str] = []
    paths = [path for path in repository_files(root) if path.suffix == ".md"]
    for path in paths:
        content = markdown_without_code(path.read_text(encoding="utf-8"))
        for match in LINK_PATTERN.finditer(content):
            raw_target = match.group("target")
            target = _local_target(path, raw_target)
            if target is not None and not target.exists():
                issues.append(
                    f"{path.relative_to(root)}: missing local link target {raw_target}"
                )
    return issues, len(paths)


def validate_required_layout(root: Path = ROOT) -> tuple[list[str], int]:
    required = [
        root / "coursectl.py",
        root / "course.toml",
        root / ".github/workflows/course-ci.yml",
        root / "docs/instructor-handbook.md",
        root / "docs/release-checklist.md",
        root / "course/instructor/README.md",
        *(root / f"course/modules/m{number:02}/README.md" for number in range(28)),
        *(root / f"course/projects/p{number:02}-" for number in range(1, 9)),
    ]
    issues: list[str] = []
    for path in required:
        if path.name.endswith("-"):
            if not any(path.parent.glob(f"{path.name}*")):
                issues.append(
                    f"missing project directory matching {path.relative_to(root)}*"
                )
        elif not path.exists():
            issues.append(f"missing required path {path.relative_to(root)}")
    return issues, len(required)


def run_validations(root: Path = ROOT) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    counts: dict[str, int] = {}
    checks = {
        "JSON/JSONL": validate_json_assets,
        "TOML": validate_toml_assets,
        "YAML": validate_yaml_assets,
        "workflow security": validate_workflow_security,
        "Markdown": validate_markdown_links,
        "required paths": validate_required_layout,
    }
    for label, check in checks.items():
        found, count = check(root)
        issues.extend(found)
        counts[label] = count
    return issues, counts


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate course assets, links, and required repository layout."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    issues, counts = run_validations(root)
    for label, count in counts.items():
        print(f"{label}: checked {count}")
    if issues:
        print("\nValidation failures:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("Course asset validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
