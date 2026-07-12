# LLM Application and Agent Engineering Course Specification

## 1. Document purpose

This document defines the intended audience, outcomes, boundaries, teaching
method, technical stack, assessment model, and portfolio expectations for the
course. It is the source of truth for later curriculum and project design.

The course is self-paced and mentor-supported. It is not constrained to a fixed
number of weeks. Progress is controlled by demonstrated comprehension rather
than elapsed time or completion of reading alone.

## 2. Course mission

Prepare an experienced traditional Python developer to compete for entry-level
LLM application and agent engineering roles while demonstrating the practical
judgment, reliability practices, and communication expected of a mid-level
engineer.

The graduate should be able to turn an ambiguous business problem into a
working, evaluated, backend-focused LLM application or agent; use coding agents
productively; identify and correct weak AI-generated code; and explain the
result to technical reviewers.

## 3. Target learner

The learner:

- Is comfortable developing conventional applications in Python.
- Has used a coding agent for personal or “vibe-coded” projects.
- Has little or no background in machine learning, statistics, linear algebra,
  neural networks, or PyTorch.
- Needs foundational professional skills rather than model-training expertise.
- Will continue through the curriculum while conducting a job search.
- Has access to Claude and GPT models without a restrictive learning budget.
- Has a human mentor and will also use an AI reviewer.

The course includes concise refreshers for professional Python and software
engineering topics instead of assuming uniform mastery.

## 4. Target roles

### In scope

- LLM application engineer building software that uses hosted model APIs.
- Agent engineer building tool-using, stateful, evaluated agent workflows.
- Backend engineer working on LLM-powered services and integrations.
- AI-assisted software engineer who uses coding agents responsibly and can
  review, test, and defend their output.

### Out of scope

- Machine learning engineer.
- Model-training or fine-tuning specialist.
- AI researcher or model architect.
- Deep mathematical treatment of transformers or neural networks.
- Frontend specialization.
- A portfolio composed primarily of chatbots.

## 5. Graduate capabilities

By completion, the learner should be able to:

1. Explain the operational behavior and important differences of the model APIs
   used in the course without relying on low-level model architecture.
2. Use the OpenAI Responses API, understand the Chat Completions API, and
   understand the Anthropic Messages API.
3. Work with tokens, context limits, nondeterminism, structured output, tool
   calls, streaming, embeddings, retrieval, and hallucination as engineering
   concerns rather than ML theory.
4. Build a tool-using agent loop without an agent framework before using a
   framework.
5. Define success criteria and ground-truth examples before optimizing an agent.
6. Create validation and evaluation loops, inspect failures, classify failure
   modes, and make evidence-based improvements.
7. Build backend services using FastAPI, Pydantic, PostgreSQL, Redis, and
   asynchronous Python where appropriate.
8. Build stateful agent workflows with the selected orchestration framework.
9. Consume MCP servers and build, test, and run MCP servers with FastMCP.
10. Integrate with GitHub and other external HTTP APIs.
11. Use Docker to package and run course services consistently.
12. Package customer-facing Python code from a development repository using
    `uv` and Hatchling.
13. Use appropriate application logging to investigate agent behavior and
    failures.
14. Use a coding agent to plan, implement, test, review, and debug software
    without surrendering technical ownership.
15. Review AI-generated code, identify defects and weak assumptions, direct the
    AI to correct them, and explain the final implementation.
16. Produce credible GitHub artifacts, architecture explanations, demos, and
    interview-ready technical narratives.

## 6. Teaching philosophy

### 6.1 AI may write the code; the learner owns the result

The course does not optimize for manually typing large volumes of code. Modern
coding agents may generate substantial portions of an implementation. The
learner remains responsible for:

- Clarifying requirements and constraints.
- Evaluating the proposed design.
- Reading and explaining generated code.
- Detecting incorrect assumptions and unnecessary complexity.
- Asking the coding agent for targeted corrections.
- Testing behavior rather than trusting plausible output.
- Understanding failures and tradeoffs.
- Defending the final result during a comprehension gate.

Generated code that the learner cannot explain is not considered completed
work.

### 6.2 Concept, guided practice, then independent judgment

Each major topic progresses through:

1. A practical conceptual model.
2. A small guided implementation or investigation.
3. An independent challenge with realistic requirements.
4. Failure analysis and revision.
5. A comprehension gate.

### 6.3 Production thinking begins before production complexity

Early projects focus on a small number of reliability concerns at a time. Later
projects combine them. Not every project must implement every production
feature, but the learner must understand the difference between a prototype and
a production-ready system.

The repeated engineering loop is:

> Define success -> establish ground truth -> build a baseline -> observe and
> trace behavior -> classify failures -> improve -> re-evaluate -> package and
> deliver.

### 6.4 Critical thinking is explicitly assessed

Exercises should contain ambiguity, imperfect generated code, misleading model
output, incomplete requirements, or competing implementation choices. The
learner must make and justify decisions rather than merely follow a tutorial.

## 7. Curriculum boundaries

### Required depth

- Practical model and API behavior.
- Prompt and context engineering.
- Structured outputs and Pydantic validation.
- Tool design and tool-calling loops.
- Agent state, termination, retries, and error handling.
- Evaluation datasets, ground truth, validation loops, and failure analysis.
- Backend API design and asynchronous execution.
- PostgreSQL application state and Redis caching/coordination concepts.
- Agent orchestration.
- MCP clients and servers.
- Logging and operational diagnosis.
- Docker and Python package builds.
- GitHub and third-party API integrations.
- AI-assisted development and review workflows.

### Conceptual coverage without deep implementation

- Prompt injection and indirect prompt injection.
- Tool authorization and least privilege.
- Human approval for consequential actions.
- Tenant isolation, secrets, PII, and data boundaries.
- Cost and latency tradeoffs.
- Deployment architecture and scaling concerns.

Projects must still avoid obviously unsafe tool execution and should use human
approval where an action is consequential. Full authentication, authorization,
multi-tenancy, and security hardening are not primary implementation goals.

### Optional or advanced coverage

- GitHub Actions for tests, linting, type checking, and container builds.
- A dedicated retrieval framework such as LlamaIndex.
- Deeper cloud infrastructure.
- Advanced Git operations.
- Full production observability platforms.
- Complex distributed task processing.

## 8. Standard technical stack

### 8.1 Engineering refreshers

The curriculum must provide targeted refreshers and diagnostic exercises for:

- Python project structure, imports, exceptions, context managers, and type
  annotations.
- `uv` environments, dependency management, lockfiles, and reproducible setup.
- pytest test organization, fixtures, parametrization, mocking, and the
  distinction between unit and integration tests.
- Git status, diffs, commits, branches, pull requests, merges, and basic conflict
  resolution.
- HTTP methods, headers, status codes, JSON payloads, timeouts, retries, and API
  authentication concepts.
- Relational data modeling, basic SQL, transactions, and SQLAlchemy usage.
- Docker images, containers, ports, volumes, environment variables, and build
  context.
- Python package boundaries, build metadata, wheels, source distributions, and
  clean-environment installation.

Refreshers should be concise and challenge-based. A learner who demonstrates
mastery may pass the corresponding diagnostic quickly; a learner with a gap must
complete the associated practice before proceeding.

### 8.2 Python engineering

- Python
- `uv` for environment, dependency, workspace, and build workflows
- Ruff for linting and formatting
- pytest for automated testing
- Pydantic for runtime data validation, schemas, and structured boundaries
- Pyright used lightly as a static analysis and AI-code-review aid
- SQLAlchemy for database access
- PostgreSQL for durable application data
- Redis for caching and lightweight coordination where justified

Pydantic is taught deeply because LLM output, API payloads, and tool arguments
are untrusted runtime data. Static type checking is complementary rather than a
replacement or competing focus. Learners should be able to interpret basic
Pyright findings and use them to review generated code, but Pyright is not a
major standalone course topic.

### 8.3 Backend services

- FastAPI
- HTTP and REST fundamentals
- Asynchronous Python
- Streaming responses
- Webhooks
- Background-work concepts
- API error handling and status semantics

Frontend work is deliberately minimized. When a project needs a user interface,
the learner may use a coding agent to create a small custom HTML/CSS/JavaScript
interface. The frontend is supporting material and is not a primary assessment
target.

### 8.4 Model APIs

API literacy includes:

- OpenAI Responses API as the primary OpenAI API.
- OpenAI Chat Completions API for comparison, compatibility, and existing
  systems.
- Anthropic Messages API for cross-provider literacy and capability comparison.

Course applications standardize on OpenAI models and an OpenAI-compatible model
endpoint where the selected framework supports that abstraction. The curriculum
should isolate provider-specific code behind a small boundary rather than
duplicate every project across providers.

One early comparison exercise should expose the learner to the different request
and response shapes and practical capabilities of OpenAI and Anthropic APIs.
Capability comparisons should be based on repeatable tasks and current
documentation, not on brand assumptions or low-level architecture.
Subsequent projects should not require parallel implementations.

### 8.5 Agent implementation

The learner first implements a minimal agent loop directly, including:

- Message and state management.
- Tool schema definition.
- Tool selection and dispatch.
- Argument validation.
- Tool-result handling.
- Retry and error paths.
- Termination and loop limits.
- Logging and inspection.

LangGraph is the primary orchestration framework because the course needs
explicit state, controllable workflows, persistence, and human-interrupt
patterns. It should be used consistently rather than teaching several competing
frameworks.

### 8.6 MCP

FastMCP is the standard Python implementation for MCP coursework. The learner
must:

- Understand MCP's purpose and boundaries.
- Configure and consume an existing MCP server.
- Build tools, resources, or prompts where appropriate.
- Build a FastMCP server with typed, validated interfaces.
- Test server behavior and error cases.
- Connect the server to a compatible client.
- Understand transports, authentication, and deployment conceptually.

### 8.7 Logging

Use Python's standard `logging` facilities. Coursework should teach:

- Useful event selection rather than excessive logging.
- Structured fields.
- Request, run, and correlation identifiers.
- Tool-call and model-call boundaries.
- Latency, token, retry, and error information where available.
- Redaction and avoidance of secrets or sensitive content.
- Logs as evidence during failure analysis.

A third-party convenience layer such as Loguru is not required.

### 8.8 Packaging and builds

The learner must understand the difference between a development repository and
a customer-facing distributable artifact.

Using `uv` and Hatchling, the learner should be able to:

- Configure `pyproject.toml` project and build-system metadata.
- Organize distributable code with a clear package boundary, preferably using a
  `src` layout when appropriate.
- Build source distributions and wheels with `uv build`.
- Exclude tests, course notes, local configuration, generated artifacts, and
  secrets from the customer-facing package.
- Inspect the contents and metadata of a built artifact.
- Install the artifact into a clean environment.
- Run tests or a smoke check against the installed artifact rather than only the
  development checkout.
- Use the built package inside a Docker image or downstream example service.
- Explain basic versioning and release metadata.

At least one smaller project and the capstone must produce a verifiable packaged
artifact.

### 8.9 Containers and delivery

Docker is required at a foundational level:

- Write and explain a Dockerfile.
- Build and run a service image.
- Configure environment variables and secrets safely at runtime.
- Connect application, PostgreSQL, and Redis services for local development.
- Understand image layers, build context, and `.dockerignore` at a practical
  level.
- Perform a health or smoke check against the containerized service.

Cloud-specific infrastructure is not currently required.

## 9. Coding-agent workflow

The learner may choose Claude Code, a VS Code coding agent, or Codex to produce
software. Course principles should be tool-neutral, although examples may use
Claude Code where a concrete interface is necessary.

Required coding-agent practices include:

- Writing clear task briefs and acceptance criteria.
- Asking the agent to inspect before changing code.
- Requesting a plan for non-trivial work.
- Managing repository instructions and context.
- Dividing work into reviewable increments.
- Reviewing diffs rather than accepting outcomes blindly.
- Running and interpreting tests, linting, and static checks.
- Asking for root-cause analysis rather than repeated speculative edits.
- Using the agent to challenge a design or identify missing cases.
- Keeping commits focused and understandable.
- Recording important rejected approaches and corrections.

Early exercises may restrict coding-agent use until the learner demonstrates the
relevant concept. Later exercises should increasingly resemble professional
agent-assisted development.

## 10. Git, GitHub, and VS Code scope

The learner should be able to perform and explain these operations from the
command line and recognize their VS Code equivalents:

- Inspect repository status and changes.
- Stage and commit changes.
- Create and switch branches.
- Push branches and open pull requests.
- Review a pull-request diff.
- Merge approved work.
- Resolve a basic merge conflict.

Rebasing, bisecting, advanced history repair, and worktrees are outside the
required scope.

## 11. Module structure

Every module should contain:

1. Learning objectives.
2. Prerequisite check or refresher.
3. Required external reading with citations.
4. A concise concept lesson.
5. A guided lab.
6. An independent challenge.
7. A failure-analysis or code-review exercise.
8. A comprehension gate.
9. Interview questions.
10. Required GitHub and portfolio evidence.

External material should favor official documentation and primary sources. Each
module should record the relevant product or library version and the date its
references were checked so that changing APIs can be audited later.

## 12. Assessment and comprehension gates

A module is not passed by reading it or producing code alone. Gates use a
combination of:

- Automated tests.
- Ruff and selected Pyright checks.
- An AI review rubric.
- A human mentor review rubric.
- A written architecture or decision explanation.
- A learner-led walkthrough or defense.
- Failure diagnosis and correction of intentionally flawed AI-generated code.
- Inspection of the learner's Git history and deliverables.

The learner must be able to answer:

- What problem does this code solve?
- Why was this design chosen?
- Where are its trust boundaries?
- What can fail, and how is failure detected?
- What evidence shows that the agent performs adequately?
- What did the coding agent get wrong or overcomplicate?
- What would need to change for a production deployment?

### Reviewer roles

- **Learner:** produces code, evidence, explanations, and the AI work log.
- **AI reviewer:** applies the documented rubric, identifies concerns, asks
  questions, and does not grant final approval by itself.
- **Human mentor:** reviews judgment and explanations and makes the final gate
  decision.

Each project repository should include both AI-review and mentor-review rubrics.

### AI work log

Projects should initially require a concise AI work log containing:

- Important prompts or task briefs.
- Significant generated proposals that were rejected.
- Corrections the learner requested and why.
- Failures encountered and their causes.
- Lessons that should influence future work.

The requirement may be streamlined or removed if it creates more administrative
work than learning value.

### Configurable solution access

Course tooling should support at least two solution modes through a repository
configuration file:

```toml
[course]
solution_access = "gated" # or "reference"
```

- `gated`: reference solutions remain unavailable until the relevant gate is
  passed or the mentor explicitly unlocks them.
- `reference`: the learner may inspect a reference implementation after making
  a documented attempt.

Reference implementations are comparison material, not canonical answers. A
different implementation may pass when it satisfies the requirements and is
well defended.

## 13. Project progression

The course should contain approximately five to seven smaller projects followed
by one substantial capstone.

Smaller projects collectively cover:

- Direct model API calls and provider comparison.
- Structured extraction or classification with validation.
- A hand-built tool-calling agent loop.
- Ground-truth creation, evaluation, and failure-driven improvement.
- A FastAPI service using PostgreSQL and Redis.
- A GitHub or third-party API integration.
- An MCP client and FastMCP server.
- A stateful orchestrated agent workflow.
- Packaging and container delivery.

Projects should use realistic supplied datasets and simulated business
requirements. They should not all be conversational interfaces.

## 14. Retrieval and context engineering

The course should not present a basic “chat with your documents” application as
a major portfolio achievement. It should teach retrieval as one context
engineering option among several:

- Supplying complete context when it is small and controlled.
- Structured queries against application data.
- Keyword or semantic search.
- Model-managed or agent-managed retrieval.
- Persistent state and memory.
- External tools and APIs.

The learner should understand when retrieval is needed, how to evaluate whether
it found useful evidence, and how irrelevant context can reduce quality. A
dedicated LlamaIndex unit is optional and should be included only when it adds a
capability not already taught through direct APIs and the primary agent
framework.

## 15. Capstone requirements

The exact business domain will be selected later. The capstone must:

- Solve a workflow problem rather than merely provide a chatbot.
- Use OpenAI models through a defined provider boundary.
- Use one or more meaningful external APIs.
- Include a GitHub integration or operate on a realistic GitHub-centered
  workflow.
- Use validated structured data and typed tool interfaces.
- Include stateful or multi-step agent behavior.
- Include realistic ground truth and a repeatable evaluation process.
- Include failure classification and documented improvement iterations.
- Use FastAPI for the backend.
- Persist appropriate data in PostgreSQL and use Redis where justified.
- Include useful application logging and correlation identifiers.
- Include tests at unit and integration boundaries.
- Produce a package built with `uv` and Hatchling.
- Run in Docker with documented setup and a smoke test.
- Include safeguards or approval points for consequential external actions.
- Include architecture, tradeoff, limitations, and production-readiness
  documentation.
- Be reviewable through a GitHub pull-request workflow.

The capstone may include a small custom web interface generated with coding-agent
assistance, but frontend sophistication is not part of the core evaluation.

## 16. Portfolio and job-search artifacts

The learner should finish with:

- Clean public or reviewable GitHub repositories.
- Strong project READMEs with setup, architecture, and evaluation instructions.
- Architecture and data-flow diagrams.
- Short demonstration scripts or recordings.
- Evaluation datasets and summarized results.
- Failure-analysis reports.
- AI work logs demonstrating responsible coding-agent use.
- Pull requests showing review and iteration.
- Resume-ready project bullets.
- Interview stories covering design decisions, failures, tradeoffs, and lessons.

## 17. Completion standard

The learner completes the course when they have:

- Passed all required comprehension gates.
- Completed the required smaller projects.
- Delivered and defended the capstone.
- Demonstrated that they can evaluate and correct AI-generated software.
- Demonstrated practical reliability and evaluation habits.
- Produced the required GitHub and job-search artifacts.
- Explained what remains between each project and a real production deployment.

## 18. Decisions deferred to detailed curriculum design

- Capstone business domain and external APIs beyond GitHub.
- The detailed AI-reviewer prompt and scoring rubric.
- The mechanism used to enforce configurable solution access.
- Whether and where GitHub Actions becomes required rather than advanced.
- Whether database migrations require a dedicated tool such as Alembic.
- Whether the AI work log remains required after early learner feedback.
