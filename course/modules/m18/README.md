# M18: LangGraph State and Explicit Workflows

## Learning objectives

By the end of this module, you can:

- Translate a known workflow into typed state, nodes, and edges.
- Separate deterministic policy from model-assisted judgment.
- Choose state fields and reducers intentionally.
- Use conditional routing without hiding business rules in prompts.
- Stream meaningful graph updates.
- Compare a graph implementation with a hand-built agent loop.

## Prerequisite diagnostic

Return to the loop from M10 and identify:

- Persistent state.
- One-step local variables.
- Model decisions.
- Deterministic decisions.
- Termination conditions.
- Events worth exposing to a caller.

If every step becomes a model node, explain which behavior becomes harder to
test and defend.

## Required reading

- [LangGraph overview and Graph API](../../../docs/reference-catalog.md#ref-langgraph-overview)
- [LangGraph state references](../../../docs/reference-catalog.md#ref-langgraph-state)
- [M10 hand-built agent loop](../m10/README.md)

## Concept lesson

### A graph makes transitions inspectable

LangGraph does not remove the need to understand an agent loop. It gives the
engineer named state, nodes, edges, checkpoints, interrupts, and event streams.
A useful graph exposes business transitions that reviewers can reason about.

Project 6 uses a non-conversational release workflow:

1. Load release inputs.
2. Check repository facts.
3. Review release notes.
4. Derive blockers.
5. Route to a ready or hold proposal.
6. Pause for human approval.
7. Finalize and publish once.

### State is a contract

Store information required by later nodes, recovery, review, or external
observation. Avoid storing clients, database connections, or convenient local
variables. State should be serializable and understandable at a checkpoint.

Define whether each field is replaced or reduced. A list reducer is appropriate
for append-only progress events; replacement is usually safer for one current
proposal or approval. An accidental reducer can retain stale or duplicate data.

### Nodes should have one observable responsibility

A node reads state and returns a partial state update. Keep deterministic rules
in normal Python. Put model use behind a narrow reviewer interface. Do not add a
model call merely because a framework makes doing so easy.

### Conditional edges express routing policy

Project 6 routes from blocker derivation to either a ready proposal or hold
proposal. The routing function should be deterministic, named, and tested. A
prompt should not secretly choose a branch that policy can decide exactly.

### Streaming is an operational interface

Stream node updates or custom progress that a caller can interpret. Do not
expose private reasoning or serialize the entire state after every trivial step.
Events should identify the workflow, stage, and safe summary.

### Graphs do not justify unnecessary complexity

Compare the graph to M10's direct loop. A graph earns its complexity when the
workflow needs inspectable branches, persistence, interrupts, streaming, or
recovery. A short deterministic function may remain the better design.

## Guided lab

Diagram Project 3's hand-built loop and a LangGraph translation. Identify which
state and transitions remain the same. Implement a small graph with one
deterministic branch and stream its node updates.

## Independent challenge

Design Project 6 before generating code. Submit:

- Typed state schema.
- Node responsibility table.
- Edge and routing diagram.
- Reducer rationale.
- List of steps that must not call a model.

Then compare the implemented graph against that approved design.

## Failure-analysis exercise

Simplify an AI-generated graph containing separate model calls to parse a
boolean, count blockers, choose a known policy branch, format a fixed status,
and decide whether to stop. Replace unnecessary nodes and calls with direct
code, then explain what became easier to test.

## Comprehension gate

The learner traces a ready and blocked release through every state update and
edge, explains every reducer, and compares termination with M10's explicit
loop. The mentor names one state field and asks what fails if it is removed.

## Interview questions

1. When does a graph improve an agent architecture?
2. What belongs in graph state?
3. How do reducers affect correctness?
4. When should routing be deterministic rather than model-assisted?

## Required GitHub evidence

- State schema and graph diagram.
- Node and edge responsibility table.
- Transition and streaming tests.
- Comparison with the hand-built loop.
