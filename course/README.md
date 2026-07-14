# Course Materials

The implemented course is organized into modules and cumulative projects.

## Implemented vertical slice

- [M00: Course operating model and baseline](modules/m00/README.md)
- [M01: Git, GitHub, VS Code, and coding-agent discipline](modules/m01/README.md)
- [M02: Modern Python project quality with uv](modules/m02/README.md)
- [M03: HTTP, asynchronous Python, and useful logging](modules/m03/README.md)
- [M04: Operational mental model for LLM applications](modules/m04/README.md)
- [M05: OpenAI Responses API and Chat Completions](modules/m05/README.md)
- [M06: Anthropic Messages API comparison](modules/m06/README.md)
- [M07: Structured outputs and Pydantic validation](modules/m07/README.md)
- [M08: Streaming, resilience, and model-call boundaries](modules/m08/README.md)
- [M09: Tool design and function calling](modules/m09/README.md)
- [M10: Build an agent loop without a framework](modules/m10/README.md)
- [M11: Ground truth and evaluation design](modules/m11/README.md)
- [M12: Failure-driven agent improvement](modules/m12/README.md)
- [M13: Context engineering and retrieval](modules/m13/README.md)
- [M14: FastAPI service architecture](modules/m14/README.md)
- [M15: PostgreSQL and SQLAlchemy state](modules/m15/README.md)
- [M16: Redis, asynchronous jobs, and progress](modules/m16/README.md)
- [M17: Integration testing and operational diagnosis](modules/m17/README.md)
- [M18: LangGraph state and explicit workflows](modules/m18/README.md)
- [M19: Persistence, interrupts, recovery, and approval](modules/m19/README.md)
- [M20: MCP concepts and FastMCP implementation](modules/m20/README.md)
- [M21: GitHub REST APIs, webhooks, and safe actions](modules/m21/README.md)
- [M22: Customer-facing packages with uv and Hatchling](modules/m22/README.md)
- [M23: Docker and local multi-service delivery](modules/m23/README.md)
- [M24: Prototype-to-production review](modules/m24/README.md)
- [M25: Capstone discovery and architecture](modules/m25/README.md)
- [M26: Capstone implementation and evaluation](modules/m26/README.md)
- [M27: Portfolio, résumé, and interview defense](modules/m27/README.md)
- [Project 1: Model API Behavior Lab](projects/p01-model-api-behavior-lab/README.md)
- [Project 2: Typed Intake Normalizer](projects/p02-typed-intake-normalizer/README.md)
- [Project 3: Operations Tool Agent](projects/p03-operations-tool-agent/README.md)
- [Project 4: Eval-Driven Issue Triage](projects/p04-eval-driven-issue-triage/README.md)
- [Project 5: Asynchronous Agent Job Service](projects/p05-asynchronous-agent-job-service/README.md)
- [Project 6: Durable Release Readiness Workflow](projects/p06-durable-release-readiness-workflow/README.md)
- [Project 7: GitHub Workflow MCP Service](projects/p07-github-workflow-mcp-service/README.md)
- [Project 8: Capstone Studio](projects/p08-capstone-studio/README.md)

Start at M00 and do not advance past a comprehension gate until its required
artifacts have been reviewed.

When starting a project, read the generated `START_HERE.md` before changing
code. It identifies the intended initial test failures, setup failures that are
not part of the exercise, the first required task, and the important workspace
files.

Reference-solution access is controlled by the root `course.toml` file and the
`coursectl.py` helper documented in the repository README.

Mentors should use the [instructor materials](instructor/README.md) for gate
operation, private holdouts, reference access, technical defenses, and release
checks.
