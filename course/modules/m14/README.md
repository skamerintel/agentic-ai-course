# M14: FastAPI Service Architecture

## Learning objectives

By the end of this module, you can:

- Separate HTTP, application, persistence, and model-provider concerns.
- Design typed request, response, and error contracts.
- Use FastAPI dependencies and application lifespan deliberately.
- Map domain failures to appropriate HTTP semantics.
- Explain when asynchronous endpoints help and when they do not.
- Review and refactor an AI-generated monolithic endpoint.

## Prerequisite diagnostic

Sketch the path of a request from `POST /jobs` to a model provider and database.
For every layer, state which details it may know. If your route handler creates
database rows, calls OpenAI, implements retries, and formats errors itself,
explain what becomes difficult to test or change.

## Required reading

- [FastAPI references](../../../docs/reference-catalog.md#ref-fastapi)
- [FastAPI asynchronous references](../../../docs/reference-catalog.md#ref-fastapi-async)
- [FastAPI testing references](../../../docs/reference-catalog.md#ref-fastapi-testing)
- [Pydantic references](../../../docs/reference-catalog.md#ref-pydantic)

## Concept lesson

### Routes translate HTTP; they do not own the use case

A route should validate transport input, obtain dependencies, call an
application service, and translate the outcome into an HTTP response. It should
not know provider SDK response shapes or write several database tables itself.

Use four boundaries:

1. HTTP schemas and routes.
2. Application service and state-transition policy.
3. Repository and transient-progress adapters.
4. Model-provider adapter.

The boundaries are useful only when tests can replace the outer adapters
without rewriting business logic.

### API contracts include failures

Document success and failure responses. Project 5 distinguishes:

- `202 Accepted`: a new job was accepted.
- `200 OK`: an idempotent retry returned the existing job.
- `404 Not Found`: the job identifier is unknown.
- `409 Conflict`: a result was requested before it exists.
- `422 Unprocessable Entity`: the HTTP payload violates the schema.
- `503 Service Unavailable`: readiness dependencies are unavailable.

Provider errors belong in job state and audit data after submission. They should
not leak SDK exception text or become an unrelated HTTP 500 response.

### Dependencies make boundaries replaceable

FastAPI dependencies can supply configuration, services, sessions, and
authorization context. Dependency injection is not permission to create a deep
graph of hidden global state. Prefer a small application factory whose
dependencies can be replaced in tests.

### Lifespan owns process-scoped resources

Create engines, clients, and task runners once during application startup and
close them during shutdown. Do not create a database engine or provider client
for every request.

### Async is about waiting, not speed by declaration

An `async def` route helps only when downstream work yields control while
waiting. Blocking database or network calls inside it still block execution.
CPU-heavy work and durable background execution need different designs.

## Guided lab

Inspect Project 5's supplied monolithic endpoint. Mark each line as transport,
business policy, persistence, provider, or operational concern. Propose module
boundaries and write three tests that become easier after the refactor.

## Independent challenge

Implement the Project 5 application factory and routes. Route handlers may not:

- Import the OpenAI SDK.
- Construct SQL statements.
- Decide state transitions.
- Catch broad `Exception` merely to return HTTP 500.

## Failure-analysis exercise

Diagnose an endpoint that returns `200 OK` before validating the persisted
result, exposes a provider exception to the client, and creates a new database
engine on every request.

## Comprehension gate

Trace one successful submission and one failed job from HTTP payload through
every dependency boundary. Explain why each class or function owns its current
responsibility and what test would fail if the boundary were violated.

## Interview questions

1. How do you keep FastAPI routes thin without creating unnecessary layers?
2. When should an API return `202 Accepted`?
3. What belongs in application lifespan?
4. Why does `async def` not automatically make a service scalable?

## Required GitHub evidence

- API contract and architecture diagram.
- Refactoring notes for the supplied monolith.
- Route and service tests.
- Error-mapping table.
