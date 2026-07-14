# Implementation Status

Updated: **2026-07-14**

## Complete

- Formal course specification.
- Curriculum roadmap and seven-project sequence.
- Official reference catalog.
- M00-M24 lesson materials.
- M25 capstone discovery, workflow scoping, architecture, evaluation planning,
  and proposal defense.
- M26 risk-driven vertical delivery, failure review, measured iterations,
  packaging, containerization, and implementation defense.
- M27 portfolio, résumé, demonstration, interview, and changed-constraint
  defense.
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
- Project 7 capability and permission policies, GitHub API and webhook fixtures,
  approval scenarios, broad-tool and delivery review exercises, starter
  workspace, rubrics, and integration, package, container, readiness, and
  portfolio templates.
- Project 7 reference bounded FastMCP tools and resource, fixture and HTTP GitHub
  gateways, pagination and failure classification, durable proposal/approval,
  marker-reconciled comment execution, signed webhook ingestion, and delivery
  deduplication.
- Project 7 multi-stage installed-wheel Dockerfile, Compose fixture evaluation,
  administrative approval CLI, and private trust-boundary holdout.
- `coursectl.py` project materialization and configurable honor-system solution
  access for Projects 1 through 8.
- Project 8 Capstone Studio with four candidate domains, a recommended support
  escalation default, nine synthetic scenario seeds, five milestone gates,
  sixteen required portfolio artifacts, and proposal/portfolio validators.
- Project 8 strict Pydantic proposal contract, weak proposal exercise, thirteen
  artifact templates, AI/mentor/technical-defense rubrics, gated exemplar, and
  private changed-constraint and portfolio-defense challenge sets.
- Project 8 reference cross-field validator and support-escalation exemplar that
  preserve independent capstone implementation rather than supplying a solved
  product.
- Project-specific startup helpers that generate `START_HERE.md`, print setup
  commands, distinguish intentional TODO failures from environment failures,
  identify the first learning task, and retain path-only output through
  `--quiet`.
- Read-only GitHub Actions CI with frozen root tools, asset and link validation,
  M02/M03 reference checks, and a bounded P01-P08 offline reference matrix.
- Local CI-equivalent helpers for repository validation and isolated reference
  materialization, plus weekly Dependabot updates for SHA-pinned workflow
  actions.
- The live Bedrock prompt-cache experiment is isolated under `scratch/` behind
  a `__main__` guard so test discovery cannot execute a paid request.

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
- Project 7 reference passes Ruff, format checking, Pyright, and 20 pytest tests
  covering MCP capabilities, GitHub HTTP behavior, approval, and webhooks.
- Project 7 private holdout passes all five trust-boundary and replay scenarios.
- Project 7 builds a clean wheel and source distribution; the wheel contains
  only runtime package files and installs successfully in a clean environment.
- The clean-installed Project 7 package constructs a FastMCP server and executes
  a deterministic client tool outside the repository checkout.
- Project 7 Compose configuration and Docker BuildKit static checks validate
  successfully.
- Project 7 learner starter passes seven model, fixture, and architecture tests
  and fails only at 13 intended HTTP gateway, state, MCP, and webhook TODO gates.
- Project 8 reference passes Ruff, formatting, Pyright, 10 project tests, and all
  six private holdout checks covering authority, state, API depth, optional MCP,
  and final evidence completeness.
- Project 8 builds a clean wheel and source distribution with uv and Hatchling;
  the CLI accepts the exemplar and reports all blocking findings for the weak
  proposal in one run.
- The Project 8 wheel installs into a clean environment outside the source
  checkout, and its console entry point validates the exemplar successfully.
- Project 8 learner starter passes three strict model/fixture tests and fails
  only at seven intended proposal and artifact validator TODO gates.
- The frozen repository-quality path passes 23 repository tests, Ruff,
  formatting, 56 JSON/JSONL assets, 13 TOML files, four YAML files, 146 Markdown
  files, and all required module/project paths.
- CI-equivalent M02 and M03 reference checks pass 16 package/acceptance tests and
  three asynchronous-client tests, plus their lint and type checks.
- The P01-P08 reference matrix passes every project test, Pyright check, package
  build, and the 20 combined executable private holdout tests for P05-P08.

## Deliberately not verified

- Live OpenAI and Anthropic requests require learner credentials and selected
  current model identifiers. They are a required learner gate, not part of the
  repository's default automated verification.
- GitHub pull-request and mentor-review workflows require the learner's remote
  repository and cannot be completed by repository tests.
- Project 5's real PostgreSQL and Redis smoke test requires the learner or
  mentor to start the supplied Docker Compose services explicitly.
- Project 7's Docker image build and external container smoke test require an
  explicit learner or mentor Docker run; repository verification validates its
  Compose configuration and clean installed-wheel runtime separately.
- The learner-selected capstone product, live APIs, PostgreSQL/Redis stack,
  Docker smoke test, evaluation iterations, portfolio, and human defense cannot
  be completed by the course-authoring repository.
- The hosted GitHub Actions run cannot be observed until this branch is pushed;
  the same workflow commands have been completed locally.

## Course-authoring status

- All planned course modules and project scaffolds are implemented.
- The next work is learner execution of Project 8, mentor gate reviews, and
  maintenance as upstream APIs and frameworks evolve.
