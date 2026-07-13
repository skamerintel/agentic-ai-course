# Project 6 Mentor Review Rubric

## Blocking conditions

- Deterministic policy is delegated to a model without justification.
- Approval occurs after publication.
- Resume payloads are unvalidated.
- A new thread ID is generated when resuming.
- Publication uses a new idempotency key on replay.
- Crash recovery creates duplicate durable decisions.
- The learner cannot explain which node may rerun.
- Tests require live model access.

## Review sequence

1. Approve the state and graph design.
2. Run transition and streaming tests.
3. Inspect a paused checkpoint and interrupt payload.
4. Exercise approve, edit, and reject.
5. Recreate the graph process and resume from SQLite.
6. Run the crash-after-write scenario.
7. Run one private holdout scenario.

## Passing evidence

The learner can explain every state field and edge, distinguish framework
durability from application idempotency, and trace one workflow across pause,
restart, resume, replay, and publication receipt.
