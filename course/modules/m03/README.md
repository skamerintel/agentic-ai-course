# M03: HTTP, Asynchronous Python, and Useful Logging

## Learning objectives

By the end of this module, you can:

- Explain HTTP methods, status codes, headers, timeouts, and idempotency.
- Decide when asynchronous I/O helps a backend workflow.
- Prevent lost task exceptions and uncontrolled retries.
- Use correlation identifiers to reconstruct one request across components.
- Redact secrets and sensitive payloads from logs.

## Prerequisite diagnostic

For each situation, decide whether retrying is normally safe without an
idempotency mechanism:

- A timed-out `GET` request.
- A timed-out request that creates a billing charge.
- A model request that may have completed after the client disconnected.
- A database read that returned a transient connection error.

State your assumptions. “Retry all exceptions” is not an acceptable policy.

## Required reading

- [Python asyncio references](../../../docs/reference-catalog.md#ref-python-async)
- [Python logging references](../../../docs/reference-catalog.md#ref-python-logging)

## Concept lesson

### A timeout is part of correctness

Without a timeout, a request may wait indefinitely and consume capacity. Choose
timeouts based on expected behavior and the caller's deadline. Report which
operation timed out and whether the outcome is known.

### Retry the condition, not the inconvenience

Classify failures before retrying:

- Transient transport or service failure may be retryable.
- Authentication and validation errors are usually terminal until input or
  configuration changes.
- A write with an unknown outcome is unsafe to repeat without idempotency.
- Backoff must be bounded by the caller's deadline.

### Async is about waiting

Asynchronous Python helps when one process spends substantial time waiting on
independent I/O. It does not make CPU-heavy work faster. Every created task must
have an owner that awaits it, observes failure, or deliberately supervises it.

### Logs are an operational narrative

Useful events identify:

- What operation began or ended.
- Which request or run it belongs to.
- Duration and outcome.
- Retry attempt and reason.
- Stable identifiers, not secret values.

Do not log API keys, authorization headers, entire private prompts, or raw
customer records by default.

## Guided lab

Use the supplied [async client lab](lab/README.md). Run the local HTTP server and
client, then add:

- A request timeout.
- A correlation identifier header.
- Structured log fields.
- A bounded retry for the explicitly transient endpoint.

## Independent challenge

Repair a client with these defects:

- No timeout.
- Blanket retry of all failures.
- Authorization token written to logs.
- Detached task whose exception is never observed.
- New correlation identifier generated for every retry.

Write tests using the local server or a controlled fake. Do not require a public
network.

## Failure-analysis exercise

Given interleaved log lines from three requests, reconstruct the timeline for
one correlation identifier. Identify where latency occurred and whether a retry
was safe.

## Comprehension gate

Explain and demonstrate:

- Timeout selection.
- Retry classification.
- Correlation-ID lifecycle.
- Task ownership and cancellation.
- Redaction policy.

The mentor will introduce a failure and ask you to diagnose it from logs.

## Interview questions

1. When is an HTTP retry unsafe?
2. What problem does an idempotency key solve?
3. When should FastAPI code use `async def`?
4. What information belongs in an LLM application log?

## Required GitHub evidence

- Corrected client and tests.
- Retry decision table.
- Redacted correlated logs.
- Failure timeline.
