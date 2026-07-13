# Project 6 Reference Notes

The reference workflow intentionally keeps most decisions deterministic:

- Repository facts and policy produce blockers in normal Python.
- Only release-note completeness sits behind a replaceable reviewer interface.
- State contains serializable business evidence, not SDK clients or secrets.
- Progress uses an append reducer; current proposal, approval, and final decision
  replace prior values.
- Conditional routing chooses ready or hold before the approval interrupt.
- The interrupt occurs before publication and validates the resume payload.
- SQLite checkpoints preserve thread state across graph reconstruction.
- The SQLite decision sink owns the workflow idempotency key.

The crash fixture commits publication and then raises before LangGraph can
checkpoint the publish node. Resume re-executes the node, and the sink returns
the existing receipt. This demonstrates durable replay with an
application-owned idempotency guarantee, not exactly-once node execution.
