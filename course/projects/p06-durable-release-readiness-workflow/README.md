# Project 6: Durable Release Readiness Workflow

## Business brief

A release manager needs a repeatable workflow that gathers release metadata,
checks repository status, reviews release notes, identifies blockers, proposes a
readiness decision, pauses for human approval, and publishes one final decision.

The workflow must survive process restarts and must not duplicate publication
when a crash occurs after the external write but before graph checkpointing.

## Required architecture

- LangGraph `StateGraph` with typed serializable state.
- Explicit deterministic and model-assisted nodes.
- Conditional routing for ready versus hold proposals.
- A checkpointer selected by configuration.
- Typed approve, edit, and reject resume commands.
- An idempotent durable publication boundary.
- Deterministic fixtures for all default tests.

## Repository assets

- `data/release-manifests.jsonl`: visible candidate releases.
- `data/repository-snapshots.json`: issue, pull-request, and check state.
- `data/policy-rules.json`: deterministic blocker rules.
- `fixtures/notes-reviews.json`: scripted model-review results.
- `fixtures/approval-scenarios.jsonl`: approve, edit, and reject cases.
- `fixtures/crash-replay.json`: restart and replay scenarios.
- `broken-graph-review.md`: AI-generated overcomplicated graph exercise.
- `rubrics/`: AI and mentor review criteria.
- `templates/`: state, graph, approval, recovery, replay, and portfolio artifacts.

Private mentor holdout scenarios are not copied by `coursectl start`.

## Setup

```bash
python coursectl.py start p06 work/p06
cd work/p06
uv sync
uv run pytest
```

## Required workflow

### 1. Approve state and graph design

Complete `reports/state-and-graph-design.md`. Every field, reducer, node, edge,
and model call must have a reason before implementation begins.

### 2. Review the broken graph

Identify unnecessary model nodes, hidden routing policy, unbounded state,
side effects before approval, and replay-unsafe publication. Produce a simpler
responsibility map.

### 3. Implement and stream the graph

Build deterministic repository checks and blocker policy. Use the supplied
notes-review fixture behind a reviewer interface. Stream safe node updates and
compare the graph with Project 3's hand-built loop.

### 4. Add persistence and human approval

Compile with a checkpointer and stable `thread_id`. Pause with an interrupt
before publication. Validate approve, edit, and reject payloads.

### 5. Demonstrate restart recovery

Pause a workflow using a SQLite checkpoint database. Close the process-scoped
objects, reconstruct the graph, and resume the same thread.

### 6. Demonstrate replay-safe publication

Use the crash-after-write fixture. The first publish commits to the durable sink
and raises. Resume from the prior checkpoint. The node may execute again, but
the sink must contain one record and return the existing receipt.

### 7. Optional live model review

Replace the scripted notes reviewer with an OpenAI-compatible structured-output
adapter. Graph policy, approval, persistence, and default tests remain offline.

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
uv build
```

## Definition of done

- State is typed, serializable, and no larger than required.
- Deterministic policy does not depend on a model.
- Ready and hold paths have transition tests.
- Streamed updates are meaningful and do not reveal private reasoning.
- Checkpoints use a stable workflow identity.
- Approval pauses before publication.
- Approve, edit, and reject are validated and auditable.
- Restart recovery works with a recreated graph process.
- Crash replay produces one durable publication.
- Default tests require no network or live model.
- The graph is compared critically with the hand-built loop.

## Comprehension gate

The learner demonstrates a ready release, blocked release, edited approval,
rejection, restart resume, and crash replay. The mentor selects one checkpoint
and asks the learner to reconstruct what ran, what may rerun, and which boundary
prevents duplicate effects.
