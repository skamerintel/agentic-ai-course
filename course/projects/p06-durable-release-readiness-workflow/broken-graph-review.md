# Review Exercise: AI-Generated Release Graph

An AI assistant proposed this workflow:

```text
START
  -> model_parse_manifest
  -> model_count_checks
  -> model_decide_if_checks_passed
  -> model_find_open_issues
  -> model_choose_ready_or_hold
  -> publish_release_decision
  -> ask_human_if_publish_was_ok
  -> END
```

It stores SDK clients, full prompts, every raw response, credentials, and a
randomly generated publication key in graph state. The publish node sends a
notification before any human interrupt. On retry it generates a new key. The
graph has no checkpointer because the developer assumes publication is fast.

## Required review

Identify at least twelve problems. Include:

- Unnecessary model use.
- Hidden deterministic policy.
- State serialization and data minimization.
- Approval placement.
- Thread identity and checkpoints.
- Interrupt resume behavior.
- Side-effect replay and idempotency.
- Streaming and audit evidence.
- Testability.
- Termination and error behavior.

Then submit a simpler state schema and graph diagram.
