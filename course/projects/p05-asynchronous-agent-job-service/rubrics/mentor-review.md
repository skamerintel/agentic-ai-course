# Project 5 Mentor Review Rubric

## Blocking conditions

- Routes call the provider or SQLAlchemy directly.
- Redis is the only source of job truth.
- Idempotency depends only on process memory or an expiring key.
- Default tests require live model calls.
- Cancellation can silently overwrite a committed terminal result.
- Raw provider exceptions are returned to clients.
- The learner cannot trace state across layers.

## Review sequence

1. Inspect architecture and state decisions before code.
2. Run the quality suite and offline integration test.
3. Submit the same idempotency key concurrently.
4. Exercise queued and running cancellation.
5. Delete Redis progress and verify durable records.
6. Run one private holdout scenario.
7. Ask the learner to diagnose one correlated trace.

## Passing evidence

The learner explains the implementation without relying on AI summaries,
defends all durable and transient choices, identifies the in-process runner's
limitations, and proposes a credible durable-worker migration.
