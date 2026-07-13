# Implementation Status

Updated: **2026-07-12**

## Complete

- Formal course specification.
- Curriculum roadmap and seven-project sequence.
- Official reference catalog.
- M00-M19 lesson materials.
- M01 generated Git conflict lab.
- M02 flawed-test exercise, mentor acceptance tests, and reference repair.
- M03 local HTTP failure simulator and tested reference async client.
- Project 1 business brief, eight-record incident dataset, offline provider
  fixtures, starter workspace, tests, rubrics, templates, and flawed report.
- Project 1 reference normalization, scoring, aggregation, and live provider
  adapters.
- Project 2 business dataset, mentor ground truth, deterministic provider
  sequences, starter workspace, tests, rubrics, and review templates.
- Project 2 reference strict Pydantic schema, source-aware policy validation,
  classified retry pipeline, progress events, and live OpenAI structured-output
  adapter.
- Project 3 deterministic operations datasets, scripted model scenarios, starter
  workspace, tests, rubrics, and review templates.
- Project 3 reference strict tool registry, classified tool results, explicit
  hand-built agent loop, trace and limit controls, and live OpenAI Responses
  function-calling session.
- Project 4 development corpus, mentor ground truth, annotator labels,
  ownership rules, known-issue corpus, retrieval queries, baseline and candidate
  predictions, starter workspace, tests, rubrics, and review templates.
- Project 4 reference multi-metric and slice evaluator, dataset fingerprints,
  regression comparison, deterministic ownership, inspectable lexical
  retrieval, context-size reporting, and live OpenAI structured-output triage.
- Project 4 private four-record mentor holdout with reference predictions.
- Project 5 API requirements, job and load scenarios, monolith review exercise,
  Docker Compose development services, starter workspace, tests, rubrics, and
  architecture, state, data, testing, incident, and portfolio templates.
- Project 5 reference FastAPI application factory, typed HTTP contracts,
  SQLAlchemy job/attempt/audit repository, transaction-safe state transitions,
  durable idempotency, Redis progress adapter, in-process runner, deterministic
  provider, and optional OpenAI Responses provider.
- Project 5 private mentor holdout covering conflicting retries, cancellation
  races, transient-progress loss, and secret-bearing provider exceptions.
- Project 6 release manifests, repository snapshots, deterministic policy,
  scripted notes reviews, approval and crash fixtures, starter workspace,
  rubrics, and state, approval, recovery, replay, and portfolio templates.
- Project 6 reference typed LangGraph state, deterministic blocker routing,
  streamed updates, human approval interrupt, SQLite checkpoint reconstruction,
  approve/edit/reject paths, and idempotent SQLite publication sink.
- Project 6 private mentor holdout covering invalid resume data, checkpointed
  evidence versus changed source data, crash replay, and thread isolation.
- `coursectl.py` project materialization and configurable honor-system solution
  access for Projects 1 through 6.

## Verification completed

- `coursectl` `unittest` suite passes.
- Repository Python files pass Ruff lint and format checks.
- JSON, JSONL, and TOML assets parse successfully.
- Markdown local links resolve.
- M02 reference passes its learner and mentor acceptance tests plus Pyright.
- M03 reference passes success, transient-retry, invalid-request, and timeout
  tests against a local HTTP server.
- Project 1 reference passes Ruff, format checking, 10 pytest tests, Pyright, and
  the offline experiment command.
- Project 1 learner starter fails only at the intended normalization and scoring
  TODOs.
- Project 2 reference passes Ruff, format checking, 12 pytest tests, Pyright,
  strict OpenAI JSON Schema conversion, and the offline batch command.
- Project 2 learner starter fails only at the intended weak-schema checks and
  policy/pipeline TODOs.
- Project 3 reference passes Ruff, format checking, nine pytest tests, Pyright,
  strict function-schema inspection, and the offline scenario command.
- Project 3 learner starter fails only at the intended tool-registry and
  agent-loop TODOs.
- Project 4 reference passes Ruff, format checking, nine pytest tests, Pyright,
  baseline/candidate comparison, and retrieval evaluation commands.
- Project 4 baseline and candidate fixtures expose dimension-specific gains and
  an intentional feature-slice regression; retrieval reaches 1.0 hit@3 and MRR
  while reporting context size.
- Project 4 reference predictions score 1.0 on every overall metric across the
  private four-record mentor holdout.
- Project 4 learner starter passes its two data-contract tests and fails only at
  the intended evaluator, ownership, and retrieval TODOs.
- Project 5 reference passes Ruff, format checking, Pyright, 18 offline pytest
  tests, and one opt-in Docker smoke test is skipped by default.
- Project 5 private holdout passes all four operational scenarios.
- Project 5 builds both a wheel and source distribution with uv and Hatchling.
- Project 5 learner starter passes six foundational tests and fails only at 12
  intended repository, Redis-progress, and application-service TODO gates.
- Project 6 reference passes Ruff, format checking, Pyright, and 15 pytest
  tests covering graph transitions, interrupts, SQLite restart, and replay.
- Project 6 private holdout passes all five mentor checks.
- Project 6 start and resume CLI paths work against persisted SQLite checkpoints
  and decisions.
- Project 6 builds both a wheel and source distribution with uv and Hatchling.
- Project 6 learner starter passes three schema and architecture tests and fails
  only at 12 intended policy, graph, and durable-sink TODO gates.

## Deliberately not verified

- Live OpenAI and Anthropic requests require learner credentials and selected
  current model identifiers. They are a required learner gate, not part of the
  repository's default automated verification.
- GitHub pull-request and mentor-review workflows require the learner's remote
  repository and cannot be completed by repository tests.
- Project 5's real PostgreSQL and Redis smoke test requires the learner or
  mentor to start the supplied Docker Compose services explicitly.

## Next vertical slice

- M20: MCP concepts and FastMCP implementation.
- M21: GitHub REST APIs, webhooks, and safe actions.
- M22: Customer-facing packages with uv and Hatchling.
- M23: Docker and local multi-service delivery.
- M24: Prototype-to-production review.
- Project 7: GitHub Workflow MCP Service.
