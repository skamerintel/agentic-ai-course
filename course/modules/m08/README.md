# M08: Streaming, Resilience, and Model-Call Boundaries

## Learning objectives

By the end of this module, you can:

- Distinguish token streaming, typed provider events, and application progress.
- Classify retryable, terminal, validation, policy, and refusal outcomes.
- Design bounded retries with stable correlation and idempotency identifiers.
- Handle cancellation, partial output, timeout, and unknown outcomes explicitly.
- Build a provider boundary that is testable without live model calls.

## Prerequisite diagnostic

For each event, decide whether a retry can help:

- Network connection failed before a request was sent.
- The provider returned a rate-limit response.
- The model returned an urgency value outside the schema.
- The model refused the request.
- Business policy rejected invented evidence.
- The client timed out after the provider may have completed the request.

State what additional information you need. Retry decisions are contextual, not
exception-name memorization.

## Required reading

- [OpenAI streaming reference](../../../docs/reference-catalog.md#ref-openai-streaming)
- [OpenAI error guidance](../../../docs/reference-catalog.md#ref-openai-errors)
- [Python asyncio references](../../../docs/reference-catalog.md#ref-python-async)
- [Python logging references](../../../docs/reference-catalog.md#ref-python-logging)

## Concept lesson

### Three meanings of streaming

1. **Token or text streaming:** display output as the model generates it.
2. **Provider event streaming:** observe typed lifecycle, content, tool, and
   completion events.
3. **Application progress:** report stages such as queued, calling provider,
   validating, retrying, and completed.

Do not stream tokens merely because the API supports it. Project 2 produces a
small typed record, so application progress is more useful than exposing partial
JSON to downstream consumers.

### Model calls need an explicit boundary

Business code should not import SDK response types everywhere. The provider
boundary should return a small set of explicit outcomes:

- Structured success.
- Refusal.
- Retryable provider failure.
- Terminal provider failure.

Schema and business-policy validation occur after structured success and remain
separate outcomes.

### Retry only operations with a useful chance of success

Retry policy should define:

- Eligible failure categories.
- Maximum attempts.
- Backoff and jitter strategy.
- Overall deadline.
- Stable request and correlation identifiers.
- Idempotency requirements.
- What evidence is logged.

Validation and policy failures need changed data, schema, prompt, or policy—not
an identical retry.

### Partial output is not a completed contract

Streaming text or events may stop before completion. Do not publish a partially
generated typed record as final. Buffer, validate, and atomically promote a
completed record, or design a separate incremental contract.

### Test failures without paying providers

Inject a provider callable or gateway. Deterministic fakes should produce:

- Success.
- Refusal.
- Transient failures followed by success.
- Exhausted transient failures.
- Terminal failure.
- Schema-invalid output.
- Policy-invalid output.

The live SDK adapter is then a thin integration boundary.

## Guided lab

Use Project 2's fixture gateway. For one request, replay:

1. Rate limit.
2. Temporary server failure.
3. Structured success.

Emit application progress events for each attempt. Confirm that the correlation
identifier is stable and that only retryable failures consume another attempt.

## Independent challenge

Complete Project 2's retry and outcome pipeline. Requirements:

- Bounded attempts.
- Injectable sleep function for fast tests.
- No retry for refusal, schema error, or policy error.
- Stable source and correlation identifiers.
- Explicit final outcome with attempt count.
- Sanitized logging.
- Batch progress events.

Then implement the live OpenAI `responses.parse` adapter with Pydantic output.
Provider imports and credentials must not be required for offline tests.

## Failure-analysis exercise

Repair a generated loop that retries every exception forever, generates a new
request identifier each time, logs the full customer request, and returns the
last partial object after timeout.

## Comprehension gate

Demonstrate and explain:

- Retryable failure followed by success.
- Exhausted retryable failure.
- Terminal provider failure.
- Refusal.
- Schema failure.
- Policy failure.
- Application progress event sequence.

The mentor changes one failure category and asks whether retry behavior should
change.

## Interview questions

1. Why should schema validation failures not be retried unchanged?
2. How do provider streaming events differ from application progress?
3. What makes a model call safe to retry?
4. How do you test a model boundary without live API calls?

## Required GitHub evidence

- Failure taxonomy.
- Retry decision table.
- Deterministic provider-failure tests.
- Progress-event transcript.
- Sanitized live structured-output example.
- Final Project 2 pull request and reviews.
