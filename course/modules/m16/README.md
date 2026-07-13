# M16: Redis, Asynchronous Jobs, and Progress

## Learning objectives

By the end of this module, you can:

- Distinguish durable records from transient coordination data.
- Defend every Redis key, value, and expiration time.
- Design idempotent submission and cancellation behavior.
- Expose meaningful job progress through polling or streaming.
- Explain the limits of in-process background tasks.
- Plan migration to a durable worker architecture.

## Prerequisite diagnostic

Classify each item as PostgreSQL, Redis, process memory, or recomputable data:

1. Final job result.
2. Current job status.
3. Last ten progress messages for a live browser.
4. Idempotency key.
5. Active in-process task object.
6. Durable attempt history.

For every Redis choice, explain what happens after expiration or restart.

## Required reading

- [Redis references](../../../docs/reference-catalog.md#ref-redis)
- [FastAPI asynchronous references](../../../docs/reference-catalog.md#ref-fastapi-async)
- [Python async references](../../../docs/reference-catalog.md#ref-python-async)

## Concept lesson

### Redis is not automatically the job database

Project 5 keeps job truth in PostgreSQL. Redis stores short-lived progress
events because losing those events should not lose the job, result, or audit
history. Every key has a documented TTL and fallback behavior.

### Delivery semantics matter

Pub/Sub is useful for live broadcast but does not replay messages for a client
that disconnected. Expiring lists or streams can support bounded replay, but
they still require trimming, retention, and consumer-failure decisions. Do not
promise durable delivery from a transient mechanism.

### Submission idempotency must survive a process restart

Clients retry after timeouts. A durable unique idempotency key prevents duplicate
jobs even if process memory and Redis are empty. The same key with a materially
different request should be rejected or explicitly versioned.

### In-process background work has a small reliability envelope

An in-process task is useful for learning and small single-process deployments,
but it can be lost during restart and is not coordinated across replicas. A
production path normally adds a durable queue and separate worker while keeping
the service and repository contracts stable.

### Progress is a product contract

Emit bounded events such as `queued`, `running`, `provider_started`, and a final
state. Do not stream private chain-of-thought, raw credentials, or unbounded
provider payloads. Correlate events with the durable job identifier.

## Guided lab

Implement an expiring Redis progress adapter and an in-memory test adapter.
Delete the Redis key mid-run and demonstrate that the job and audit history are
still available from PostgreSQL.

## Independent challenge

Compare polling, server-sent events, Redis Pub/Sub, and a bounded Redis list for
the supplied client requirements. Implement one and document why the others
were not selected.

## Failure-analysis exercise

Diagnose a service that stores the only copy of job status and results in Redis.
After TTL expiry, explain which user promises are broken and migrate durable
state to PostgreSQL.

## Comprehension gate

Defend every Redis key and TTL, trace duplicate submission and cancellation,
and explain exactly what is lost during a process restart. Present the minimal
changes required to introduce a durable worker.

## Interview questions

1. When should Redis not be used?
2. How does Pub/Sub differ from replayable progress storage?
3. How do idempotency keys prevent duplicate work?
4. Why can FastAPI background tasks be insufficient?

## Required GitHub evidence

- State-lifecycle table.
- Redis key and TTL inventory.
- Duplicate and cancellation tests.
- Durable-worker migration note.
