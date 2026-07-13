# M10: Build an Agent Loop Without a Framework

## Learning objectives

By the end of this module, you can:

- Draw and implement the states in a model-tool execution loop.
- Correlate every tool result with its model-issued call identifier.
- Preserve a complete trace of model turns, tool calls, results, and stops.
- Enforce iteration, total-call, and repeated-call limits.
- Distinguish model, tool, validation, and loop-control failures.
- Explain what an orchestration framework will later provide.

## Prerequisite diagnostic

Draw the transitions for this sequence:

```text
user request -> model tool call -> invalid arguments -> model corrected call
-> retryable tool error -> model repeats call -> success -> final answer
```

Mark which component owns every transition. If the model is shown directly
executing a tool, revise the diagram.

## Required reading

- [OpenAI function-calling references](../../../docs/reference-catalog.md#ref-openai-structured)
- [OpenAI Responses references](../../../docs/reference-catalog.md#ref-openai-responses)
- [OpenAI agent references](../../../docs/reference-catalog.md#ref-openai-agents)
- [Python logging references](../../../docs/reference-catalog.md#ref-python-logging)

## Concept lesson

### The minimal loop

1. Send the user request and available tool definitions to the model.
2. Inspect typed output items.
3. If the model returns tool calls, validate and execute them.
4. Return each result with the matching call identifier.
5. Ask the model to continue.
6. Stop on a final answer or an application limit.

The application, not the model, controls execution and stopping.

### State must be explicit

Project 3 records:

- User request.
- Iteration number.
- Model response identifier.
- Tool calls and raw argument text.
- Validated tool results.
- Repeated-call signatures.
- Total call count.
- Stop reason.
- Final answer when available.

Provider-side conversation state may use a response identifier, but the
application trace still needs enough information to understand what happened.

### Call identifiers are not optional bookkeeping

When a model issues multiple tool calls, results must be returned with the
correct `call_id`. A result associated with the wrong call can corrupt the next
model decision even when the tool data itself is correct.

### The model chooses; the application limits

Essential limits include:

- Maximum model iterations.
- Maximum total tool calls.
- Maximum repeats of the same tool and canonical arguments.
- Maximum tool result size.
- Known tool names only.
- Validated arguments only.

Limits are safety and reliability controls, not prompt suggestions.

### Do not hide errors behind “the agent failed”

Classify:

- Model-provider failure.
- Invalid model tool arguments.
- Unknown tool.
- Tool not found.
- Retryable tool failure.
- Terminal tool failure.
- Repeated-call limit.
- Total-call limit.
- Iteration limit.
- Empty model turn.

The trace should make the stopping condition obvious.

### Tool retries can be model-directed

Project 3 returns retryable tool errors to the model. The model may repeat the
call, choose another tool, or answer with uncertainty. The loop allows a small
number of repeats but does not automatically repeat every failed tool call.

### Final answers need evidence discipline

When tools cannot support an answer, the model should say that evidence is
insufficient. A fluent guess after `not_found` or `terminal_error` is a failed
agent outcome even if the loop technically completed.

## Guided lab

Use the scripted model session for a three-turn scenario:

1. `get_service_status`.
2. `search_incidents`.
3. Final answer.

Trace each state transition and verify call/result correlation. Then replay an
invalid-argument scenario and a retryable-tool scenario.

## Independent challenge

Complete Project 3's loop with:

- Typed model turns and tool calls.
- Pydantic argument validation.
- Deterministic dispatch.
- Full trace events.
- Iteration, total-call, and repeated-signature limits.
- Explicit stop reasons.
- Scripted offline model sessions.
- A thin live OpenAI Responses session.

Do not introduce LangGraph, LangChain agents, or another orchestration framework.

## Failure-analysis exercise

Repair the supplied broken loop. It executes unvalidated JSON, discards call
identifiers, retries tools forever, reports success after terminal failure, and
stores only the final answer.

## Comprehension gate

Demonstrate:

- Normal multi-tool completion.
- Invalid arguments followed by correction.
- Retryable tool failure followed by recovery.
- Terminal tool failure and an insufficient-evidence answer.
- Unknown or missing data.
- Repeated-call stop.
- Iteration-limit stop.

The mentor selects one trace and asks the learner to narrate every transition
without executing the code.

## Interview questions

1. What are the states in a tool-using agent loop?
2. Why must tool results preserve call identifiers?
3. How do repeated-call and iteration limits differ?
4. What should an agent do when its tools cannot support an answer?

## Required GitHub evidence

- State and transition diagram.
- Complete scenario traces.
- Limit and failure tests.
- Broken-loop review.
- Sanitized live tool-call transcript.
- Final Project 3 pull request and reviews.
