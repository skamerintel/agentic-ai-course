# Continuous Integration

The course CI validates repository quality and every offline reference
implementation without credentials or live services.

Primary references: [GitHub Actions](reference-catalog.md#ref-github-actions)
and [uv in GitHub Actions](reference-catalog.md#ref-uv-github-actions).

## Pull-request checks

The `Course CI` workflow runs on pushes, pull requests, and manual dispatches.
It uses read-only repository permissions and cancels superseded runs on the same
branch.

### Repository quality

- Install the frozen root development environment with uv.
- Run Ruff lint and formatting checks across tracked course Python.
- Run standard-library repository unit tests.
- Parse JSON, JSONL, TOML, `uv.lock`, and YAML assets.
- Resolve local Markdown links outside fenced and inline code.
- Verify M00-M27, P01-P08, and required course-control files exist.
- Exercise the M02 package-repair and M03 asynchronous-client references.

### Reference matrix

For each project P01-P08, CI creates a temporary workspace, overlays the gated
reference, and runs:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
uv build
```

Projects 5-8 also run their private executable mentor holdouts. Matrix jobs run
at most four projects concurrently.

## Deliberate exclusions

CI removes OpenAI, Anthropic, GitHub, and AWS credentials from reference-test
processes. It does not run:

- paid or credentialed model requests;
- live GitHub or other business APIs;
- Docker-backed PostgreSQL or Redis integration tests;
- external container smoke tests;
- remote pull-request or human mentor gates.

Those remain explicit learner or mentor demonstrations. Default CI must remain
deterministic and safe for pull requests from forks.

## Run locally

Install the validation tools:

```bash
uv sync --only-group dev --frozen
```

Run the repository-quality job:

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync python -m unittest discover -s tests -p "test_*.py"
uv run --no-sync python scripts/validate_course.py
uv run --no-sync python scripts/verify_module_references.py
```

Verify one reference implementation:

```bash
uv run --no-project --python 3.13 python scripts/verify_reference.py p08
```

Use `--workspace /tmp/p08-reference-check` to preserve a failed verification
workspace for diagnosis. Never point it at a non-empty directory.

## Dependency maintenance

Workflow actions are pinned to immutable commit SHAs. Dependabot checks them
weekly. The action comments record the corresponding release tags. The uv
version is pinned in the workflow and should be updated deliberately with a
successful full reference matrix.

Before assigning a new revision to a learner, complete the
[course release checklist](release-checklist.md); CI does not perform human gate,
clean-clone usability, or pilot-learner decisions.
