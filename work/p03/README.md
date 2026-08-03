# Operations Tool Agent Workspace

Read `PROJECT.md`, approve the tool catalog and state diagram, then complete the
TODOs in `tools.py`, `agent.py`, and the live session in `model.py`.

```bash
uv sync
uv run pytest
uv run operations-agent offline --output reports/offline-results.jsonl
```

Do not add LangGraph or another agent framework.
