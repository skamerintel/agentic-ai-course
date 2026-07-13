# Official Reference Catalog

Checked on: **2026-07-12**

OpenAI Responses, structured-output, and evaluation references used by the
capstone slice were rechecked on **2026-07-13**.

This catalog contains the primary references used by the curriculum roadmap.
Modules cite reference IDs from this page. Before writing or teaching a module,
verify its references again and record the new check date in the completed
module.

Avoid pinning lessons to a model name unless the lesson is explicitly about
model selection. Prefer capability checks and documented API behavior.

## Coding-agent workflow and source control

### REF-AGENT-CODEX

- [Codex best practices](https://developers.openai.com/codex/learn/best-practices)
- [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)

### REF-AGENT-CLAUDE-CODE

- [Claude Code overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code memory and project instructions](https://docs.anthropic.com/en/docs/claude-code/memory)

### REF-AGENT-VSCODE

- [Use chat in VS Code](https://code.visualstudio.com/docs/copilot/copilot-chat)

### REF-VSCODE-GIT

- [Source control in VS Code](https://code.visualstudio.com/docs/sourcecontrol/overview)
- [Staging and committing changes](https://code.visualstudio.com/docs/sourcecontrol/staging-commits)
- [Working with GitHub in VS Code](https://code.visualstudio.com/docs/sourcecontrol/github)
- [Resolve merge conflicts in VS Code](https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts)

## Python project engineering

### REF-UV-PROJECTS

- [Working on projects with uv](https://docs.astral.sh/uv/guides/projects/)
- [uv project concepts](https://docs.astral.sh/uv/concepts/projects/)

### REF-UV-BUILD

- [Building and publishing a package with uv](https://docs.astral.sh/uv/guides/package/)
- [Building distributions with uv](https://docs.astral.sh/uv/concepts/projects/build/)

### REF-HATCHLING

- [Hatch build configuration](https://hatch.pypa.io/latest/config/build/)

### REF-PYTHON-PACKAGING

- [Packaging Python projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [The packaging flow](https://packaging.python.org/en/latest/flow/)

### REF-RUFF

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Ruff tutorial](https://docs.astral.sh/ruff/tutorial/)
- [Configuring Ruff](https://docs.astral.sh/ruff/configuration/)

### REF-PYTEST

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)

### REF-PYRIGHT

- [Pyright documentation](https://github.com/microsoft/pyright/blob/main/docs/README.md)
- [Pyright getting started](https://github.com/microsoft/pyright/blob/main/docs/getting-started.md)

### REF-PYTHON-ASYNC

- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html)

### REF-PYTHON-LOGGING

- [Python logging](https://docs.python.org/3/library/logging.html)
- [Logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)

## Model APIs and application behavior

### REF-OPENAI-RESPONSES

- [Migrate to the Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Responses API reference overview](https://developers.openai.com/api/reference/responses/overview)

### REF-OPENAI-CHAT

- [Chat Completions API reference overview](https://developers.openai.com/api/reference/chat-completions/overview)

### REF-OPENAI-STRUCTURED

- [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Function calling](https://developers.openai.com/api/docs/guides/function-calling)

### REF-OPENAI-AGENTS

- [Agents guide](https://developers.openai.com/api/docs/guides/agents)
- [Tools guide](https://developers.openai.com/api/docs/guides/tools)

### REF-OPENAI-STREAMING

- [Streaming API responses](https://developers.openai.com/api/docs/guides/streaming-responses)

### REF-OPENAI-ERRORS

- [OpenAI API error codes](https://developers.openai.com/api/docs/guides/error-codes)

### REF-OPENAI-EVALS

- [Working with evals](https://developers.openai.com/api/docs/guides/evals)

### REF-OPENAI-RETRIEVAL

- [Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- [File search](https://developers.openai.com/api/docs/guides/tools-file-search)

### REF-ANTHROPIC-MESSAGES

- [Messages API reference](https://platform.claude.com/docs/en/api/messages)
- [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)

### REF-ANTHROPIC-TOOLS

- [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)

### REF-ANTHROPIC-STRUCTURED

- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

### REF-ANTHROPIC-STREAMING

- [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)

### REF-CONTEXT-ENGINEERING

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Contextual retrieval](https://www.anthropic.com/engineering/contextual-retrieval)

## Backend and persistence

### REF-PYDANTIC

- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/)

### REF-FASTAPI

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Lifespan events](https://fastapi.tiangolo.com/advanced/events/)

### REF-FASTAPI-ASYNC

- [Concurrency and async/await](https://fastapi.tiangolo.com/async/)
- [Async tests](https://fastapi.tiangolo.com/advanced/async-tests/)
- [Background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Custom and streaming responses](https://fastapi.tiangolo.com/advanced/custom-response/)

### REF-FASTAPI-TESTING

- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Async tests](https://fastapi.tiangolo.com/advanced/async-tests/)

### REF-SQLALCHEMY

- [SQLAlchemy unified tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [SQLAlchemy ORM quick start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [SQLAlchemy session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Transactions and connection management](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### REF-REDIS

- [redis-py guide](https://redis.io/docs/latest/develop/clients/redis-py/)
- [Redis Pub/Sub](https://redis.io/docs/latest/develop/pubsub/)

## Agent orchestration and MCP

### REF-LANGGRAPH-OVERVIEW

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

### REF-LANGGRAPH-STATE

- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)

### REF-FASTMCP

- [FastMCP welcome](https://gofastmcp.com/getting-started/welcome)
- [FastMCP quickstart](https://gofastmcp.com/getting-started/quickstart)
- [FastMCP server](https://gofastmcp.com/servers/server)
- [FastMCP client](https://gofastmcp.com/clients/client)
- [FastMCP resources](https://gofastmcp.com/servers/resources)
- [FastMCP client transports](https://gofastmcp.com/clients/transports)

### REF-FASTMCP-OPERATIONS

- [FastMCP testing](https://gofastmcp.com/development/tests)
- [FastMCP authentication](https://gofastmcp.com/servers/auth/authentication)
- [Run a FastMCP server](https://gofastmcp.com/deployment/running-server)
- [FastMCP HTTP deployment](https://gofastmcp.com/deployment/http)
- [Testing FastMCP servers](https://gofastmcp.com/servers/testing)

## GitHub integration

### REF-GITHUB-REST

- [Getting started with the GitHub REST API](https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api)
- [Authenticating to the REST API](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api)
- [REST API best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
- [REST API pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
- [REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)

### REF-GITHUB-PRS

- [Pull-request REST endpoints](https://docs.github.com/en/rest/pulls)

### REF-GITHUB-WEBHOOKS

- [About webhooks](https://docs.github.com/en/webhooks/about-webhooks)
- [Using webhooks](https://docs.github.com/en/webhooks/using-webhooks)
- [Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
- [Webhook best practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)

## Packaging and containers

### REF-DOCKER

- [Docker get started](https://docs.docker.com/get-started/)
- [Writing a Dockerfile](https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/)
- [Docker Compose](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-docker-compose/)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)

## Security concepts

### REF-OWASP-LLM

- [OWASP Top 10 for LLM and generative AI applications](https://genai.owasp.org/llm-top-10/)
- [Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [Excessive agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
