# M19: Persistence, Interrupts, Recovery, and Human Approval

## Learning objectives

By the end of this module, you can:

- Persist and resume graph execution by stable thread identity.
- Place interrupts before consequential actions.
- Implement approve, edit, and reject resume paths.
- Explain replay behavior and checkpoint boundaries.
- Make side effects idempotent when nodes may execute again.
- Recover after a simulated crash without duplicating a write.

## Prerequisite diagnostic

A node sends a release decision and then the process crashes before its next
checkpoint. On restart, the graph executes that node again. Answer:

- Which state was durable?
- Why can the node repeat?
- Where should the idempotency key live?
- What evidence distinguishes replay from a new request?
- Which operations are safe to repeat?

## Required reading

- [LangGraph persistence, interrupts, streaming, and durable execution](../../../docs/reference-catalog.md#ref-langgraph-state)
- [OWASP LLM application references](../../../docs/reference-catalog.md#ref-owasp-llm)

## Concept lesson

### Thread identity selects durable workflow history

A checkpointer stores state snapshots associated with a thread identifier. A
new process can compile the same graph with the same checkpoint store and resume
that thread. Treat thread IDs as durable application identifiers, not random
values regenerated on every request.

### Interrupt before the consequential action

An interrupt pauses execution and exposes a serializable approval payload.
Resume with an approve, edit, or reject command. Code before an interrupt may
run again when the node resumes, so do not perform side effects before calling
the interrupt.

### Human edits are new trusted input

Validate resume payloads with a typed schema. An edit can change the final
decision or conditions, but it should not silently rewrite source evidence.
Record the original proposal, human response, and final decision separately.

### Checkpoints do not make side effects exactly once

Durable execution replays from a checkpoint. If an external write succeeds and
the node crashes before completion is checkpointed, that write may be attempted
again. Use a durable idempotency key at the side-effect boundary and return the
existing receipt when the same payload is replayed.

### Put retries around the smallest safe operation

Retry a transient read or model call only when it is safe and classified. Do not
retry an entire workflow blindly. A write with uncertain outcome must be
reconciled by idempotency key or external lookup before repeating.

### Recovery requires a runbook

For each node, document whether it is deterministic, replay-safe, externally
idempotent, or requires reconciliation. Inspect checkpoint state and durable
side-effect receipts before resuming an interrupted or failed workflow.

## Guided lab

Pause Project 6 at the approval node. Inspect the checkpoint and interrupt
payload. Resume through approve, edit, and reject. Restart with the same SQLite
checkpoint database and prove the workflow remains resumable.

## Independent challenge

Use a publisher that commits a decision and then raises a simulated crash.
Resume the workflow. Prove that the publish node runs again but the durable sink
contains one decision and returns one receipt.

## Failure-analysis exercise

Diagnose a workflow that sends two notifications after recovery. The developer
assumed checkpointing implied exactly-once execution and generated a new
idempotency key inside the publish node. Correct the key ownership and add a
replay regression test.

## Comprehension gate

Demonstrate pause, approve, edit, reject, process restart, and crash replay. For
each path, identify the checkpoint, resume command, durable state, and side
effect evidence. Explain what the framework guarantees and what the application
must guarantee.

## Interview questions

1. How does thread identity relate to checkpoints?
2. Why must side effects after a checkpoint still be idempotent?
3. What code may repeat around an interrupt?
4. How do you recover an external write with an uncertain outcome?

## Required GitHub evidence

- Recovery and replay runbook.
- Checkpoint and interrupt snapshots.
- Approve, edit, and reject tests.
- Crash-after-write idempotency test.
