# M15: PostgreSQL and SQLAlchemy State

## Learning objectives

By the end of this module, you can:

- Model durable jobs, attempts, outcomes, and audit events relationally.
- Define keys, constraints, and state-transition invariants.
- Use SQLAlchemy 2-style sessions and explicit transaction scopes.
- Explain sync versus async database access.
- Test repositories with isolated databases.
- Identify data that should not be retained.

## Prerequisite diagnostic

Design tables for a job that may have multiple provider attempts and many state
events. Answer these questions before writing code:

- Which value enforces idempotent submission?
- Can an attempt exist without a job?
- Which fields must be queryable without decoding JSON?
- Which writes must commit atomically?
- What must survive a process restart?

## Required reading

- [SQLAlchemy references](../../../docs/reference-catalog.md#ref-sqlalchemy)
- [PostgreSQL and SQL refresher](../m02/README.md)
- [Pydantic references](../../../docs/reference-catalog.md#ref-pydantic)

## Concept lesson

### Model the questions the system must answer

Project 5 must answer: current job status, submission identity, cancellation
state, attempt count, final result, failure category, and transition history.
Store operationally important fields in typed columns. JSON is appropriate for
bounded payloads or provider metadata, not as a substitute for a data model.

### Constraints protect invariants under concurrency

Application checks alone cannot prevent two processes from inserting the same
idempotency key. Use a unique database constraint and handle the race. Use
foreign keys for attempts and audit events. Treat state transitions as
conditional writes, not unconditional object mutation.

### A session is a transaction boundary, not a global cache

Create one session per application operation. Commit a logically complete state
change and its audit event together. Roll back the whole operation when an
invariant fails. Do not share one `AsyncSession` across concurrent tasks.

### Cancellation and completion race

If cancellation commits before completion, the final result must not overwrite
it. If completion commits first, a later cancellation should report the
terminal state rather than rewrite history. Encode and test the selected policy.

### Retention is part of the schema decision

Issue bodies and model outputs may contain sensitive data. Document what is
stored, why it is needed, and when it should be deleted. Avoid logging entire
payloads merely because they are convenient during development.

## Guided lab

Draw the Project 5 entity relationship diagram. Implement repository operations
for create, claim, complete, fail, cancel, and fetch. Each transition must append
a durable audit event in the same transaction.

## Independent challenge

Repair a supplied schema that stores the complete job, attempts, and status in
one JSON column. Demonstrate two operational queries that the repaired schema
can answer directly.

## Failure-analysis exercise

Reproduce a partial write where the job becomes `succeeded` but no result or
audit event is stored. Identify the missing transaction boundary and add a test
that proves atomic rollback.

## Comprehension gate

Explain the entity model, unique and foreign-key constraints, transaction scope,
and cancellation race. The mentor changes one persistence requirement and asks
which schema, repository, and test changes follow.

## Interview questions

1. Why is check-then-insert insufficient for idempotency?
2. What should define a SQLAlchemy session boundary?
3. How do you test a transaction rollback?
4. When is a JSON column appropriate?

## Required GitHub evidence

- Entity relationship diagram.
- State-transition table.
- Repository and concurrency tests.
- Data-retention note.
