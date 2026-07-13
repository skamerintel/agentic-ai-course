# Project 5 Reference Notes

The reference implementation makes PostgreSQL the durable source of truth:

- A unique idempotency key and request fingerprint prevent duplicate or
  conflicting submissions.
- Jobs, provider attempts, results, and audit events are relational records.
- State changes and audit events share one transaction.
- Cancellation committed before completion discards the provider result.
- Redis stores only bounded progress events and a short-lived sequence counter.
- Losing Redis does not lose job state, attempt history, result, or audit data.
- Provider exceptions are classified at the provider or service boundary.
- The in-process runner is intentionally not restart-safe.

`create_all` is used to keep the exercise focused. A production service should
introduce versioned migrations, a durable queue, worker leases or heartbeats,
reconciliation for abandoned running jobs, authentication, and stronger
operational monitoring.
