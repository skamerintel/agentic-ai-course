# M17: Integration Testing and Operational Diagnosis

## Learning objectives

By the end of this module, you can:

- Assign risks to unit, repository, integration, contract, and smoke tests.
- Replace live providers with deterministic boundary fakes.
- Isolate database state and application dependencies in tests.
- Test races, retries, expiration, and restart behavior.
- Use correlation identifiers and logs to diagnose cross-layer failures.
- Avoid brittle assertions on model wording.

## Prerequisite diagnostic

For each risk, choose the cheapest test that can catch it reliably:

- Wrong HTTP status code.
- Invalid database constraint.
- Provider SDK response-shape change.
- Duplicate submission under concurrency.
- Exact model wording differs.
- PostgreSQL unavailable at startup.

Explain which tests require real PostgreSQL or Redis and which should run with
local fakes.

## Required reading

- [pytest references](../../../docs/reference-catalog.md#ref-pytest)
- [FastAPI testing references](../../../docs/reference-catalog.md#ref-fastapi-testing)
- [Python logging references](../../../docs/reference-catalog.md#ref-python-logging)

## Concept lesson

### Test risks, not framework trivia

Unit tests cover state-transition policy and error mapping. Repository tests
cover constraints and transactions. API integration tests cover validation,
dependencies, persistence, and response contracts. A small Docker-backed suite
checks behavior that SQLite or an in-memory Redis fake cannot prove.

### Provider boundaries should be deterministic by default

Tests must not require a live model call. Use a scripted provider that can
succeed, delay, or fail predictably while preserving the same interface as the
live adapter. Add a separately invoked live smoke test only when credentials and
cost are intentionally accepted.

### Assert structured behavior

Assert status, persisted fields, failure categories, evidence identifiers, and
state transitions. Do not assert an entire natural-language answer unless exact
wording is itself the contract.

### Correlation identifiers connect the evidence

Use one identifier across the HTTP request, job record, provider attempt,
progress event, and log entry. Logs should reveal transitions and classified
failures without copying sensitive request bodies.

### Intermittent failures need timelines

When cancellation races completion, collect ordered database events, progress
events, and logs. Compare what each layer observed. A plausible final status is
not enough if the transition history violates policy.

## Guided lab

Build an integration test that submits a job through HTTP, runs a scripted
provider, persists an attempt and result, and retrieves the final response. No
route or service is called directly.

## Independent challenge

Reproduce and diagnose one supplied intermittent scenario: duplicate submit,
cancellation race, provider failure, progress expiry, or simulated restart.
Write an incident-style report with evidence and a regression test.

## Failure-analysis exercise

Review tests that call a live model, sleep for arbitrary durations, share one
database, assert exact prose, and pass only when executed in file order. Replace
each brittle assumption with a controlled boundary or observable condition.

## Comprehension gate

Present a test matrix mapping each important failure to a test level. Then use
correlated logs and persisted events to diagnose an unseen failing scenario.

## Interview questions

1. What distinguishes a unit test from an integration test in a FastAPI app?
2. How do you test nondeterministic model integrations reliably?
3. Which behavior must be tested against real PostgreSQL or Redis?
4. How do correlation identifiers help incident diagnosis?

## Required GitHub evidence

- Test-strategy matrix.
- Offline integration suite.
- Optional Docker-backed smoke suite.
- Incident-style diagnosis and regression test.
