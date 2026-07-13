# Durable Release Readiness Workflow

This is the learner workspace for Project 6. Complete the state and graph design
in `reports/` before asking a coding agent to implement the TODOs.

```bash
uv sync
uv run pytest
```

Start and pause a fixture-backed workflow:

```bash
uv run release-workflow start REL-100 --thread-id demo-100
```

Resume it:

```bash
uv run release-workflow resume --thread-id demo-100 --action approve
```
