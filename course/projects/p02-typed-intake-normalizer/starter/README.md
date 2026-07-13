# Typed Intake Normalizer Workspace

Read `PROJECT.md`, complete the schema decision record, and write invalid
examples before asking a coding agent to implement the TODOs.

```bash
uv sync
uv run pytest
uv run intake-normalizer offline --output reports/offline-results.jsonl
```

Default tests and offline runs never require API credentials.
