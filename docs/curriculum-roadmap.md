# Curriculum Roadmap

Status: **Design baseline**  
Primary specification: [Course specification](course-specification.md)  
Project details: [Project sequence](project-sequence.md)  
Official sources: [Reference catalog](reference-catalog.md)

## 1. How to use this roadmap

The course is mastery-based rather than time-based. Modules establish concepts
and focused skills; projects combine them under realistic business constraints.
A learner may move quickly through a refresher only after passing its diagnostic
and comprehension gate.

Every module must eventually be implemented with the standard structure defined
in the course specification:

1. Learning objectives.
2. Prerequisite check or refresher.
3. Required external reading.
4. Concept lesson.
5. Guided lab.
6. Independent challenge.
7. Failure-analysis or code-review exercise.
8. Comprehension gate.
9. Interview questions.
10. GitHub or portfolio evidence.

This roadmap defines those elements at curriculum-design depth. It does not yet
contain complete lesson prose, datasets, starter repositories, or solutions.

## 2. Coding-agent progression

The learner may use Claude Code, a VS Code coding agent, or Codex. The permitted
level of assistance expands as the learner demonstrates ownership.

### Stage A: inspect and explain

During diagnostics and early refreshers, the coding agent may explain code,
propose tests, and identify defects. The learner must make or dictate small
changes and explain every changed line.

### Stage B: generate under a contract

During model API and structured-output work, the learner writes requirements,
schemas, acceptance criteria, and tests before asking the coding agent to
implement meaningful sections.

### Stage C: collaborate and review

During agent, backend, LangGraph, and MCP work, the coding agent may implement
larger increments. The learner reviews plans and diffs, runs checks, rejects weak
approaches, and records important corrections.

### Stage D: professional delegation

During the capstone, the learner may delegate broadly while retaining ownership
of architecture, risk, evaluation, integration boundaries, and final approval.

At every stage, generated code that the learner cannot explain fails the gate.

## 3. Phase and project map

| Phase | Modules | Major deliverable |
| --- | --- | --- |
| 0. Engineering baseline | M00-M03 | Baseline gate and repaired sample service |
| 1. Model APIs and contracts | M04-M08 | Projects 1 and 2 |
| 2. Agents and evaluation | M09-M13 | Projects 3 and 4 |
| 3. Backend agent services | M14-M17 | Project 5 |
| 4. LangGraph, MCP, and GitHub | M18-M21 | Projects 6 and 7 foundation |
| 5. Packaging and delivery | M22-M24 | Completed Project 7 distribution |
| 6. Capstone and job evidence | M25-M27 | Capstone and portfolio defense |

## 4. Phase 0: Engineering baseline

### M00. Course operating model and baseline diagnostic

**Outcome:** Establish the learner's starting point and the evidence required to
claim mastery.

**Core lesson:** Course workflow, solution modes, AI work logs, review rubrics,
academic honesty in an AI-assisted course, and the distinction between generated
output and owned engineering work.

**Guided lab:** Clone a deliberately small repository, run its checks, inspect
its history, and use the configured coding agent to explain the architecture
without modifying it.

**Independent challenge:** Produce a short technical inventory identifying
entry points, dependencies, data boundaries, likely failures, and unanswered
questions.

**Failure exercise:** Review a confident but inaccurate AI-generated repository
summary and correct it using code evidence.

**Gate:** The learner explains the repository without relying on the agent's
summary and submits a compliant AI work log.

**Evidence:** Baseline report, first pull request, and mentor diagnostic rubric.

**References:** REF-AGENT-CODEX, REF-AGENT-CLAUDE-CODE, REF-AGENT-VSCODE.

### M01. Git, GitHub, VS Code, and coding-agent discipline

**Outcome:** Use a reviewable branch and pull-request workflow from either the
terminal or VS Code.

**Core lesson:** Status, diffs, staging, commits, branches, remotes, pull
requests, merges, basic conflict resolution, repository instructions, agent
planning, and diff review.

**Guided lab:** Make a small change on a branch, inspect the diff in VS Code,
commit it, open a pull request, and merge after review.

**Independent challenge:** Resolve a supplied merge conflict and explain which
intent from each branch was preserved.

**Failure exercise:** Repair a branch containing mixed concerns, an accidental
secret, and a misleading commit message.

**Gate:** Complete a clean pull-request cycle and explain the difference between
working tree, index, commit, branch, and remote.

**Evidence:** Pull request, conflict-resolution note, and reviewed diff.

**References:** REF-VSCODE-GIT and the learner's selected coding-agent reference.

### M02. Modern Python project quality with uv

**Outcome:** Create and evaluate a reproducible Python project with automated
quality checks.

**Core lesson:** `pyproject.toml`, `uv` environments and lockfiles, project
layout, imports, exceptions, type annotations, Ruff, pytest fixtures and
parametrization, mocking boundaries, and basic Pyright interpretation.

**Guided lab:** Convert a loose script into a `uv` project with linting,
formatting, tests, and a typed public interface.

**Independent challenge:** Ask a coding agent to repair a flawed package, then
review and revise its work until tests, Ruff, and selected type checks pass.

**Failure exercise:** Diagnose tests that pass for the wrong reason because they
mock the unit under test.

**Gate:** Explain each quality tool's distinct role and defend the final test
boundaries.

**Evidence:** Project configuration, test report, static-check report, and AI
correction log.

**References:** REF-UV-PROJECTS, REF-RUFF, REF-PYTEST, REF-PYRIGHT.

### M03. HTTP, asynchronous Python, and useful logging

**Outcome:** Reason about networked backend behavior and diagnose failures from
logs.

**Core lesson:** HTTP requests and responses, JSON, authentication headers,
timeouts, retries, idempotency, synchronous versus asynchronous I/O, tasks and
cancellation, log levels, structured fields, and correlation identifiers.

**Guided lab:** Build an async client for a supplied local API and add
correlated request logging.

**Independent challenge:** Correct an AI-generated client that has no timeout,
retries unsafe operations, leaks a token into logs, and loses exceptions from
background tasks.

**Failure exercise:** Reconstruct a failed request from interleaved logs.

**Gate:** Explain when `async` helps, when it does not, and how the logs connect
one user request to downstream work.

**Evidence:** Corrected client, failure timeline, and logging policy.

**References:** REF-PYTHON-ASYNC, REF-PYTHON-LOGGING.

## 5. Phase 1: Model APIs and reliable data contracts

### M04. Operational mental model for LLM applications

**Outcome:** Predict common model behavior without studying model architecture.

**Core lesson:** Tokens, context windows, instructions versus data,
nondeterminism, hallucination, context pollution, model capability differences,
latency, cost, and why fluent output is not evidence of correctness.

**Guided lab:** Run controlled prompt variations and record output stability,
format adherence, latency, and failure cases.

**Independent challenge:** Design a small experiment comparing two model
configurations against a supplied task and rubric.

**Failure exercise:** Identify unsupported conclusions in an AI-generated model
comparison.

**Gate:** Explain observed differences using evidence rather than model-brand
assumptions.

**Evidence:** Experiment notebook and capability decision record.

**References:** REF-OPENAI-RESPONSES, REF-ANTHROPIC-MESSAGES,
REF-CONTEXT-ENGINEERING.

### M05. OpenAI Responses API and Chat Completions literacy

**Outcome:** Use the Responses API directly and recognize Chat Completions code
in an existing system.

**Core lesson:** Request and response objects, instructions and messages,
conversation state, response item types, usage metadata, error handling, and the
important interface differences between Responses and Chat Completions.

**Guided lab:** Implement the same bounded text task with both API surfaces and
normalize the result behind a small application interface.

**Independent challenge:** Migrate a supplied Chat Completions function to
Responses while preserving tests and behavior.

**Failure exercise:** Correct code that assumes every Responses output item is a
text message.

**Gate:** Trace a complete request, identify provider-specific code, and defend
the normalization boundary.

**Evidence:** Migration pull request and API comparison table.

**References:** REF-OPENAI-RESPONSES, REF-OPENAI-CHAT.

### M06. Anthropic Messages API comparison

**Outcome:** Understand a second major API shape without duplicating the course
across providers.

**Core lesson:** Messages request and response structure, system instructions,
content blocks, usage, tool-use shape, streaming shape, and practical capability
comparison with OpenAI.

**Guided lab:** Implement one task with the Messages API and capture a normalized
result using the interface from M05.

**Independent challenge:** Run the Phase 1 benchmark against OpenAI and
Anthropic, then recommend a provider for that narrow task using measured
evidence.

**Failure exercise:** Review an abstraction that erases important provider
semantics and redesign the boundary.

**Gate:** Explain what should and should not be normalized across providers.

**Evidence:** Provider comparison report and adapter review.

**References:** REF-ANTHROPIC-MESSAGES, REF-ANTHROPIC-TOOLS,
REF-ANTHROPIC-STREAMING.

**Major deliverable:** Project 1, Model API Behavior Lab.

### M07. Structured outputs and Pydantic validation

**Outcome:** Treat model output as untrusted data and turn it into a validated
application contract.

**Core lesson:** JSON Schema, Pydantic models, strict versus coercive behavior,
field and model validators, optional and discriminated data, structured output,
refusal and validation failure paths, and schema evolution.

**Guided lab:** Extract a typed incident record from messy text and report all
validation failures explicitly.

**Independent challenge:** Design a schema for ambiguous supplied business
requirements, generate adversarial examples, and revise the schema after review.

**Failure exercise:** Correct AI-generated Pydantic models that overuse optional
fields and silently coerce dangerous values.

**Gate:** Defend every required field, constraint, and validation rule using a
business requirement.

**Evidence:** Schema decision record, validation matrix, and tests.

**References:** REF-PYDANTIC, REF-OPENAI-STRUCTURED,
REF-ANTHROPIC-STRUCTURED.

### M08. Streaming, resilience, and model-call boundaries

**Outcome:** Build a model client that behaves predictably under partial output
and transient failure.

**Core lesson:** Streaming events, timeouts, retryable versus terminal errors,
backoff, idempotency, cancellation, rate-limit awareness, usage accounting,
provider adapters, and test doubles.

**Guided lab:** Stream a response to a terminal or minimal HTML page while
recording timing and usage information.

**Independent challenge:** Repair a batch processor that duplicates work,
retries validation errors, and corrupts partial streamed state.

**Failure exercise:** Use logs and fixtures to distinguish provider failure,
transport failure, invalid output, and application failure.

**Gate:** Present the model-call boundary and explain its retry and cancellation
policy.

**Evidence:** Resilient client library, failure taxonomy, and tests.

**References:** REF-OPENAI-STREAMING, REF-ANTHROPIC-STREAMING,
REF-PYTHON-ASYNC.

**Major deliverable:** Project 2, Typed Intake Normalizer.

## 6. Phase 2: Tool-using agents and evaluation

### M09. Tool design and function calling

**Outcome:** Design tools that models can select and applications can execute
safely.

**Core lesson:** When to use a tool, narrow tool responsibilities, names and
descriptions, typed arguments, read versus write tools, deterministic execution,
errors as data, tool-result size, and approval boundaries.

**Guided lab:** Expose three read-only business tools and inspect tool-selection
behavior across realistic requests.

**Independent challenge:** Redesign a supplied set of overlapping, vague tools
and measure whether selection improves.

**Failure exercise:** Identify excessive agency, hidden side effects, and schema
ambiguity in AI-generated tool definitions.

**Gate:** Defend each tool boundary and identify which operations require human
approval.

**Evidence:** Tool catalog, selection test matrix, and design review.

**References:** REF-OPENAI-STRUCTURED, REF-ANTHROPIC-TOOLS, REF-OWASP-LLM.

### M10. Build an agent loop without a framework

**Outcome:** Understand the machinery hidden by agent frameworks.

**Core lesson:** State, message history, tool dispatch, validated arguments,
tool-result correlation, loop limits, termination, retries, repeated actions,
error propagation, and run logging.

**Guided lab:** Implement a minimal OpenAI tool loop over deterministic local
tools.

**Independent challenge:** Add one recoverable tool failure, one terminal
failure, and explicit loop-stop conditions without introducing LangGraph.

**Failure exercise:** Debug an agent that calls the same tool indefinitely and
another that reports success after a failed side effect.

**Gate:** Draw and narrate every possible transition through the loop.

**Evidence:** Agent trace, state diagram, and failure tests.

**References:** REF-OPENAI-STRUCTURED, REF-OPENAI-RESPONSES,
REF-PYTHON-LOGGING.

**Major deliverable:** Project 3, Operations Tool Agent.

### M11. Ground truth and evaluation design

**Outcome:** Define evidence of agent quality before attempting optimization.

**Core lesson:** Task definition, representative datasets, expected outputs,
deterministic checks, rubric-based grading, human labels, false positives and
negatives, baseline measurements, slices, regression sets, and evaluation
leakage.

**Guided lab:** Create and run an evaluation set for a supplied issue-triage
task.

**Independent challenge:** Add difficult and adversarial cases, explain the
labeling policy, and quantify uncertainty or disagreement.

**Failure exercise:** Critique an evaluation that uses only happy paths and a
single aggregate score.

**Gate:** Defend dataset coverage and explain what the metrics cannot prove.

**Evidence:** Versioned dataset, labeling guide, baseline report, and evaluator
tests.

**References:** REF-OPENAI-EVALS, REF-PYTEST.

### M12. Failure-driven agent improvement

**Outcome:** Improve a system by studying failures instead of repeatedly editing
prompts by intuition.

**Core lesson:** Trace inspection, failure taxonomies, prompt versus schema
versus tool versus data failures, controlled experiments, regression testing,
and avoiding overfitting to the evaluation set.

**Guided lab:** Classify baseline failures and implement one isolated change at
a time.

**Independent challenge:** Produce two measurable improvement iterations and
one rejected experiment.

**Failure exercise:** Detect a reported improvement caused by changed labels or
removed hard examples.

**Gate:** Show the before/after evidence and explain why the change should
generalize.

**Evidence:** Failure ledger, experiment records, and evaluation report.

**References:** REF-OPENAI-EVALS, REF-PYTHON-LOGGING.

### M13. Context engineering, retrieval, and memory choices

**Outcome:** Select the smallest context mechanism that satisfies the task.

**Core lesson:** Full-context input, structured database queries, keyword and
semantic retrieval, metadata filters, retrieval quality, citations, short-term
state, long-term memory, context compression, and irrelevant-context damage.

**Guided lab:** Compare full-context, structured lookup, and retrieval on a
small supplied knowledge task.

**Independent challenge:** Design a context plan for a larger business scenario
and justify which information is loaded, searched, summarized, or excluded.

**Failure exercise:** Diagnose a “RAG” system whose generation appears fluent
while retrieval returns irrelevant evidence.

**Gate:** Separate retrieval quality from answer quality and defend the selected
context strategy.

**Evidence:** Retrieval test set, context decision record, and failure analysis.

**References:** REF-CONTEXT-ENGINEERING, REF-OPENAI-RETRIEVAL.

**Major deliverable:** Project 4, Eval-Driven Issue Triage Engine.

## 7. Phase 3: Backend agent services

### M14. FastAPI service architecture

**Outcome:** Expose LLM functionality through a testable backend rather than a
monolithic script.

**Core lesson:** Route and application layers, dependency injection, request and
response models, error mapping, lifecycle, configuration, health endpoints,
OpenAPI, and separation of model-provider code from business logic.

**Guided lab:** Wrap a prior project in a FastAPI service with no model logic in
route handlers.

**Independent challenge:** Review and refactor an AI-generated “god endpoint.”

**Failure exercise:** Diagnose leaked provider exceptions, unvalidated response
data, and incorrect HTTP status semantics.

**Gate:** Trace a request across all layers and explain each dependency boundary.

**Evidence:** Architecture diagram, API contract, and route/service tests.

**References:** REF-FASTAPI, REF-PYDANTIC, REF-FASTAPI-TESTING.

### M15. PostgreSQL and SQLAlchemy state

**Outcome:** Persist business and agent-run state with explicit transactional
boundaries.

**Core lesson:** Relational modeling, keys and constraints, transactions,
sessions, repositories, SQLAlchemy 2-style queries, sync versus async database
access, and test isolation.

**Guided lab:** Persist jobs, model attempts, validation outcomes, and final
results.

**Independent challenge:** Repair an AI-generated schema that stores opaque JSON
for everything and cannot answer required operational questions.

**Failure exercise:** Investigate a partial write caused by a missing transaction
boundary.

**Gate:** Explain the data model, transaction scope, and which data should not be
stored.

**Evidence:** Entity diagram, repository tests, and data-retention note.

**References:** REF-SQLALCHEMY.

### M16. Redis, asynchronous jobs, and streamed progress

**Outcome:** Use Redis only where transient coordination or caching has a clear
benefit.

**Core lesson:** Durable versus ephemeral state, cache keys and expiration,
idempotency keys, lightweight job coordination, status polling, streamed
progress, cancellation, and the limits of in-process background tasks.

**Guided lab:** Add job status and short-lived progress events to the backend
service.

**Independent challenge:** Decide whether supplied requirements need Redis,
PostgreSQL, in-memory state, or a combination, then implement the decision.

**Failure exercise:** Correct a design that treats Redis as the only durable
record and loses completed work after eviction.

**Gate:** Defend every Redis key, lifetime, and failure fallback.

**Evidence:** State-lifecycle table, concurrency tests, and operational notes.

**References:** REF-REDIS, REF-FASTAPI-ASYNC, REF-PYTHON-ASYNC.

### M17. Integration testing and operational diagnosis

**Outcome:** Test the boundaries that most often fail in an LLM backend.

**Core lesson:** Unit versus integration versus contract tests, model fixtures,
recorded provider responses, database isolation, dependency overrides, log
capture, deterministic tests, and smoke checks.

**Guided lab:** Build an integration test that exercises API, service, database,
and a fake model boundary.

**Independent challenge:** Diagnose a supplied intermittent failure using tests
and correlated logs.

**Failure exercise:** Identify brittle tests that assert provider wording or
depend on live network calls.

**Gate:** Present a test strategy showing which risks are covered at each layer.

**Evidence:** Test matrix, integration suite, and incident-style diagnosis.

**References:** REF-PYTEST, REF-FASTAPI-TESTING, REF-PYTHON-LOGGING.

**Major deliverable:** Project 5, Asynchronous Agent Job Service.

## 8. Phase 4: LangGraph, MCP, and GitHub integration

### M18. LangGraph state and explicit workflows

**Outcome:** Translate an understood agent loop into a graph with inspectable
state and transitions.

**Core lesson:** State schemas, nodes, edges, conditional routing, reducers,
model and tool nodes, recursion limits, graph invocation, and streaming graph
events.

**Guided lab:** Rebuild the hand-written loop from M10 in LangGraph and compare
the two implementations.

**Independent challenge:** Model a non-conversational business workflow with at
least one deterministic branch and one model-assisted decision.

**Failure exercise:** Simplify an AI-generated graph that uses a node and model
call for every trivial operation.

**Gate:** Explain why each piece of state and every edge exists.

**Evidence:** Graph diagram, implementation comparison, and transition tests.

**References:** REF-LANGGRAPH-OVERVIEW, REF-LANGGRAPH-STATE.

### M19. Persistence, interrupts, recovery, and human approval

**Outcome:** Build workflows that can pause, resume, and recover without
repeating unsafe work.

**Core lesson:** Checkpoints, thread identity, durable state, interrupts, resume
commands, human approval, idempotent tools, retry placement, and replay risks.

**Guided lab:** Pause a workflow before a write action, inspect and edit the
proposed action, then resume it.

**Independent challenge:** Recover a workflow after a simulated process crash
without duplicating a completed side effect.

**Failure exercise:** Diagnose a resumed workflow that sends the same external
request twice.

**Gate:** Demonstrate pause, edit, reject, resume, and crash recovery paths.

**Evidence:** Recovery runbook, state snapshots, and side-effect tests.

**References:** REF-LANGGRAPH-STATE, REF-OWASP-LLM.

**Major deliverable:** Project 6, Durable Release Readiness Workflow.

### M20. MCP concepts and FastMCP implementation

**Outcome:** Consume an MCP server and build a typed, testable FastMCP server.

**Core lesson:** MCP clients and servers, tools, resources, prompts, transport
choices, capability discovery, typed inputs, result design, client testing,
authentication concepts, and deployment boundaries.

**Guided lab:** Connect a FastMCP client to a supplied server, then add one
read-only tool to a new server.

**Independent challenge:** Design and build a server around a supplied business
API with narrow, validated operations.

**Failure exercise:** Review an MCP server exposing dozens of vague tools,
unbounded results, and hidden side effects.

**Gate:** Explain the MCP lifecycle, test tools without a model, and justify the
server's capability surface.

**Evidence:** Server and client tests, tool catalog, and transport decision.

**References:** REF-FASTMCP, REF-FASTMCP-OPERATIONS.

### M21. GitHub REST APIs, webhooks, and safe actions

**Outcome:** Build a realistic GitHub integration that reacts to events and
separates recommendations from writes.

**Core lesson:** Authentication options, permissions, pagination, rate limits,
pull-request and issue APIs, webhook events, signature validation, delivery
idempotency, retries, and approval before consequential writes.

**Guided lab:** Read repository and pull-request data and handle a signed webhook
fixture.

**Independent challenge:** Add a proposed write operation that requires explicit
approval before execution.

**Failure exercise:** Correct an integration that trusts webhook JSON without
signature validation and comments repeatedly after redelivery.

**Gate:** Trace one webhook from receipt through validation, deduplication,
agent decision, approval, and GitHub action.

**Evidence:** Integration sequence diagram, permission inventory, and webhook
tests.

**References:** REF-GITHUB-REST, REF-GITHUB-PRS, REF-GITHUB-WEBHOOKS,
REF-OWASP-LLM.

## 9. Phase 5: Packaging and delivery

### M22. Customer-facing packages with uv and Hatchling

**Outcome:** Build a clean wheel and source distribution from a development
repository and prove that the installed artifact works.

**Core lesson:** Distribution versus import package, `src` layout, project and
build metadata, Hatchling configuration, included and excluded files, versioning,
build artifacts, clean-environment installs, and smoke tests.

**Guided lab:** Package a prior project's reusable client or domain library and
inspect the wheel contents.

**Independent challenge:** Remove tests, notes, local data, and secrets from an
over-inclusive AI-generated build configuration without excluding required
runtime assets.

**Failure exercise:** Diagnose a package that works from the checkout but fails
after installation because imports accidentally depend on repository layout.

**Gate:** Build with `uv build`, install into a clean environment, and run the
public API smoke test.

**Evidence:** `pyproject.toml`, artifact inventory, install transcript, and
packaging decision record.

**References:** REF-UV-BUILD, REF-HATCHLING, REF-PYTHON-PACKAGING.

### M23. Docker and local multi-service delivery

**Outcome:** Deliver a reproducible service image connected to PostgreSQL and
Redis for local evaluation.

**Core lesson:** Images and containers, Dockerfile instructions, build context,
`.dockerignore`, layer caching, runtime configuration, health checks, non-root
execution concepts, and Docker Compose service networking.

**Guided lab:** Containerize the FastAPI service and run it with database and
Redis services.

**Independent challenge:** Repair a large, secret-leaking, development-only
Dockerfile generated by a coding agent.

**Failure exercise:** Diagnose a container that imports local source instead of
the wheel produced in M22.

**Gate:** Start the stack from documented commands and pass an external smoke
test against a clean build.

**Evidence:** Dockerfile, Compose configuration, image notes, and smoke-test
output.

**References:** REF-DOCKER, REF-UV-BUILD.

**Major deliverable:** Project 7, GitHub Workflow MCP Service.

### M24. Prototype-to-production review

**Outcome:** Identify what remains before a prototype can be responsibly
operated without requiring full production implementation.

**Core lesson:** Trust boundaries, prompt injection, excessive agency, output
validation, secrets, data retention, tenant isolation, approval gates, cost and
latency budgets, scaling, dependency risk, deployment architecture, incident
response, and CI concepts.

**Guided lab:** Apply a production-readiness checklist to Project 7.

**Independent challenge:** Produce a prioritized hardening roadmap constrained
by a fictional engineering budget.

**Failure exercise:** Challenge an AI review that labels a system “production
ready” because it has tests and Docker.

**Gate:** Separate release blockers, near-term hardening, and future scaling
concerns with clear reasoning.

**Evidence:** Threat sketch, readiness scorecard, and hardening roadmap.

**Advanced extension:** Add GitHub Actions for Ruff, tests, selected type checks,
package builds, and container builds.

**References:** REF-OWASP-LLM, REF-GITHUB-REST, REF-DOCKER.

## 10. Phase 6: Capstone and job evidence

### M25. Capstone discovery and architecture

**Outcome:** Turn a realistic but ambiguous business problem into an evaluable
agent system proposal.

**Core lesson:** Stakeholder questions, scope boundaries, user and system goals,
non-goals, workflow mapping, ground truth, tool inventory, data contracts,
external API constraints, approval points, architecture decisions, and delivery
increments.

**Guided lab:** Critique two contrasting capstone proposals using the course
rubrics.

**Independent challenge:** Produce and defend the learner's proposal before
implementation begins.

**Failure exercise:** Remove features that are impressive but do not improve the
business outcome or evaluation evidence.

**Gate:** Mentor approval of requirements, architecture, evaluation plan, and
milestone plan.

**Evidence:** Project brief, architecture diagram, risk register, evaluation
plan, and initial issue backlog.

**References:** Relevant references from all prior phases.

### M26. Capstone implementation and evaluation

**Outcome:** Deliver the approved system through reviewable increments and prove
its behavior.

**Core lesson:** Applied integration of OpenAI, Pydantic, FastAPI, PostgreSQL,
Redis where justified, LangGraph, GitHub and another API, logging, evaluation,
FastMCP where appropriate, packaging, and Docker.

**Guided lab:** Mentor milestone reviews replace a conventional guided lab.

**Independent challenge:** Implement, evaluate, package, containerize, and
document the complete system.

**Failure exercise:** At least one milestone is a formal red-team and failure
review rather than feature development.

**Gate:** Automated checks, AI review, mentor review, live demonstration,
failure recovery demonstration, and technical defense.

**Evidence:** Complete capstone repository and all artifacts required by the
course specification.

### M27. Portfolio, résumé, and interview defense

**Outcome:** Convert course work into credible hiring evidence without
overstating production experience.

**Core lesson:** Project narrative, concise architecture communication, metrics
with caveats, meaningful résumé bullets, repository presentation, demonstration
scripts, system-design discussion, debugging stories, and honest limitations.

**Guided lab:** Rewrite weak project bullets and rehearse a five-minute technical
walkthrough.

**Independent challenge:** Produce a portfolio packet and answer adversarial
interview questions about design, failures, AI-generated code, security, and
production gaps.

**Failure exercise:** Remove vague claims such as “production ready” or
“improved accuracy” when evidence is absent.

**Gate:** Human mentor conducts a mock portfolio and technical interview.

**Evidence:** Final READMEs, résumé bullets, demo scripts, architecture deck,
and interview story bank.

## 11. Major comprehension gates

| Gate | Required proof |
| --- | --- |
| G0 Engineering baseline | Clean PR workflow, repaired code, tests, and oral explanation |
| G1 Model API literacy | Direct Responses implementation and evidence-based provider comparison |
| G2 Reliable model boundary | Typed structured output, resilient client, and failure taxonomy |
| G3 Agent mechanics | Hand-built loop, transition diagram, termination and error tests |
| G4 Evaluation practice | Versioned ground truth, baseline, failure ledger, measured iteration |
| G5 Backend service | API, PostgreSQL, justified Redis use, integration tests, correlated logs |
| G6 Durable orchestration | LangGraph persistence, interrupt, approval, and recovery demonstration |
| G7 MCP and integration | Tested FastMCP server, GitHub event flow, guarded writes |
| G8 Delivery | Clean wheel/sdist, clean install, Docker stack, smoke test, readiness review |
| G9 Capstone | Full technical defense and portfolio-quality delivery |

## 12. Implementation order for course authors

Build course content in vertical slices rather than writing every lecture first:

1. Implement M00-M06 and Project 1, including its dataset and gate.
2. Implement M07-M08 and Project 2.
3. Implement M09-M10 and Project 3.
4. Implement M11-M13 and Project 4.
5. Implement M14-M17 and Project 5.
6. Implement M18-M19 and Project 6.
7. Implement M20-M24 and Project 7.
8. Implement the learner-selected Project 8 Capstone Studio and M25-M27.

Each slice must include readings, lesson material, starter assets, tests, review
rubrics, a reference implementation, and both configured solution-access paths
before the next slice is considered complete.
