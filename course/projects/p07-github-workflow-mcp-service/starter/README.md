# GitHub Workflow MCP

This is the learner workspace for Project 7. Complete the capability catalog and
permission inventory before implementing TODOs.

```bash
uv sync
uv run pytest
uv run github-workflow-mcp serve-http
```

Human approval is an administrative command and is intentionally not an MCP
tool:

```bash
uv run github-workflow-mcp approve PROPOSAL_ID --actor mentor@example.com
```
