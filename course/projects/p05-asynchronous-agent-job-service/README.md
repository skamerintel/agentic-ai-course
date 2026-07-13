# Project 5: Asynchronous Agent Job Service

## Business brief

The issue-triage engine must become a backend service. Clients submit work,
receive a job identifier, inspect progress, cancel work, and retrieve a final
result. The service must preserve enough state to explain what happened after a
process restart or provider failure.

This project is about the engineering around model calls. A deterministic fake
provider is the default. A live OpenAI adapter is an optional demonstration.

## Required architecture

- FastAPI routes with typed request, response, and error models.
- Application service containing job policy and transitions.
- SQLAlchemy repository with PostgreSQL as the production database.
- Redis adapter used only for expiring progress events.
- Provider interface with deterministic fake and optional OpenAI adapters.
- In-process task runner with an explicit durable-worker migration plan.

## Repository assets

- `api-requirements.md`: simulated client and business requirements.
- `data/job-scenarios.jsonl`: visible acceptance and failure scenarios.
- `fixtures/client-interactions.json`: example HTTP exchanges.
- `fixtures/load-scenarios.json`: duplicates, restarts, expiry, and races.
- `broken-monolith-review.md`: AI-generated architecture failure exercise.
- `rubrics/`: AI and mentor review criteria.
- `templates/`: architecture, data, state, testing, incident, and portfolio
  artifacts.
- `docker-compose.yml`: PostgreSQL and Redis development services.

The mentor holdout scenarios are outside the learner workspace and are not
copied by `coursectl start`.

## Setup

```bash
python coursectl.py start p05 work/p05
cd work/p05
uv sync
uv run pytest
```

Start real development services when working on Docker-backed checks:

```bash
docker compose up -d postgres redis
```

## Required workflow

### 1. Approve the architecture before implementation

Complete `reports/architecture-decision.md`. Compare at least two designs for
durable jobs and transient progress. Identify failure behavior during process,
PostgreSQL, Redis, and provider outages.

### 2. Refactor the monolith

Review `broken-monolith-review.md`. Map each concern to HTTP, application,
persistence, progress, provider, or process-lifecycle ownership. Do not copy its
implementation.

### 3. Implement durable state

Persist jobs, attempts, results, cancellation state, idempotency keys, and audit
events. Each state transition and corresponding event must commit atomically.

### 4. Implement transient progress

Use Redis for expiring progress only. Demonstrate that Redis loss or expiry does
not lose the durable job status, attempt history, or result.

### 5. Implement and test the API

Required endpoints:

- `POST /v1/jobs`
- `GET /v1/jobs/{job_id}`
- `DELETE /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/result`
- `GET /v1/jobs/{job_id}/progress`
- `GET /health/live`
- `GET /health/ready`

### 6. Diagnose operational scenarios

Run the supplied duplicate, cancellation, failure, progress-expiry, and restart
scenarios. Submit one incident-style diagnosis with correlated evidence.

### 7. Demonstrate optional live model use

The live provider may call an OpenAI-compatible endpoint, selected by
configuration. The default test suite must remain offline and deterministic.

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
```

Optional Docker-backed checks:

```bash
JOB_SERVICE_RUN_DOCKER_TESTS=1 uv run pytest -m docker
```

## Definition of done

- Routes contain no provider or SQLAlchemy implementation logic.
- Duplicate submissions return one durable job.
- Cancellation and completion races follow the documented policy.
- Attempts and state events remain queryable after restart.
- Redis keys and TTLs have documented fallback behavior.
- Provider failures are classified without leaking private exception text.
- Unit, repository, API integration, and smoke-test responsibilities are clear.
- No default test requires a live model or network access.
- A durable-worker migration path is documented.
- AI and mentor reviews are complete.

## Comprehension gate

The mentor selects duplicate, cancelled, failed, and completed jobs. The learner
must trace each through HTTP responses, PostgreSQL rows, Redis progress, logs,
and provider attempts, then explain what survives every relevant failure.
