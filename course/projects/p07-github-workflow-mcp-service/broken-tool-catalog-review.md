# Review Exercise: Over-Broad MCP Tool Catalog

An AI assistant proposes these tools:

- `github_request(method, url, headers, body)`
- `run_git_command(command)`
- `approve_and_execute(action)`
- `read_any_file(path)`
- `manage_webhook(payload)`
- `admin_repository(settings)`

It gives every tool the same GitHub token and describes all repository text as
trusted context.

## Required review

Identify capability, authorization, validation, prompt-injection, result-size,
audit, testing, and deployment problems. Replace the catalog with the minimum
Project 7 tools and resources. Explicitly identify administrative actions that
must remain outside MCP.
