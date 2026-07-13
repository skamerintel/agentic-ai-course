# M21: GitHub REST APIs, Webhooks, and Safe Actions

## Learning objectives

By the end of this module, you can:

- Use bounded GitHub REST reads with authentication, timeouts, and pagination.
- Interpret rate-limit, permission, not-found, and transient failures.
- Validate webhook signatures before parsing trusted event data.
- Deduplicate webhook deliveries durably.
- Treat issue and pull-request text as untrusted data.
- Guard writes with explicit human approval and idempotency.

## Prerequisite diagnostic

Trace a pull-request webhook through signature validation, delivery
deduplication, policy evaluation, approval, and a comment write. Identify the
GitHub permission required by every step and what happens during redelivery.

## Required reading

- [GitHub REST references](../../../docs/reference-catalog.md#ref-github-rest)
- [Pull-request references](../../../docs/reference-catalog.md#ref-github-prs)
- [Webhook references](../../../docs/reference-catalog.md#ref-github-webhooks)
- [OWASP LLM application references](../../../docs/reference-catalog.md#ref-owasp-llm)

## Concept lesson

### The adapter owns GitHub protocol details

Keep API version headers, authentication, pagination, timeouts, rate-limit
classification, and response validation behind a gateway. MCP tools should call
business operations, not construct arbitrary REST requests.

### Pagination is part of correctness

A successful first page is not a complete result. Follow supported pagination
links within a documented maximum. Return truncation metadata when the service
intentionally caps results.

### Rate limiting differs from permission failure

Classify a depleted rate limit using status and response headers. Preserve a
safe retry time for callers. A normal permission denial should not enter an
automatic retry loop.

### Verify the raw webhook body first

Compute the HMAC signature over the exact request bytes and compare it using a
constant-time operation. Parse JSON only after signature validation. Require a
delivery identifier and event name.

### Redelivery is normal

Store delivery IDs durably. Replaying the same delivery and payload returns an
idempotent duplicate response. Reusing an ID for different bytes is a conflict,
not a duplicate.

### External text is data, not instructions

Issue bodies, comments, repository files, and webhook fields can contain
instructions aimed at an agent. Preserve source identifiers, limit content, and
keep authorization and tool selection outside that text.

### Approval and execution are separate records

A proposed comment is not a GitHub write. Human approval records actor and
time. Execution uses the proposal ID as a durable idempotency key and stores the
GitHub receipt. Replay returns that receipt without writing again.

## Guided lab

Use fixture-backed GitHub reads, then validate a signed pull-request webhook.
Replay the delivery and prove it is not processed twice.

## Independent challenge

Implement the guarded comment path. Demonstrate execution before approval,
approved execution, execution replay, stale proposal handling, and permission
failure.

## Failure-analysis exercise

Correct an integration that parses webhook JSON before signature validation,
uses an in-memory delivery set, and posts a second comment after redelivery.

## Comprehension gate

Trace one webhook and one approved write across HTTP, durable state, MCP tools,
GitHub permissions, and logs. Explain every retry and non-retry decision.

## Required GitHub evidence

- Integration sequence diagram.
- Permission inventory.
- Pagination and rate-limit tests.
- Signature, deduplication, and guarded-write tests.
