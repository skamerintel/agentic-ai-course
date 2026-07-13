# Eval-Driven Issue Triage Workspace

Read `PROJECT.md`, approve the labeling policy, and run the baseline before
changing retrieval, prompts, or code.

```bash
uv sync
uv run pytest
uv run issue-triage evaluate \
  --predictions fixtures/baseline-predictions.jsonl \
  --output reports/baseline.json
```

Do not copy mentor holdout files into this workspace.
