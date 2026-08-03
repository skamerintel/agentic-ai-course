# Broken Agent Loop Review

The proposed pseudocode:

```python
while True:
    response = model.ask(history, tools=all_internal_functions)
    if response.tool_name:
        arguments = json.loads(response.arguments)
        result = globals()[response.tool_name](**arguments)
        history.append(str(result))
    else:
        return {"success": True, "answer": response.text}
```

## 1. Execution and authorization risks

`tools=all_internal_functions` and `globals()[response.tool_name](**arguments)`
expose every function defined in the process's global namespace to
model-directed invocation — not a curated, read-only catalog. Anything
importable or defined at module scope (including functions never intended
as tools: file I/O helpers, database writes, subprocess wrappers) becomes
callable by name. There is no allowlist, no read/write distinction, and no
separation between "the model may request this" and "the application will
execute this." The model effectively gets arbitrary code execution scoped
to whatever the host process has loaded. This is the same class of problem
`get_service_status`/`search_incidents`/`get_asset` were built to avoid: our
implementation defines a fixed, hand-registered `ToolRegistry` in
`tools.py`, and `execute()` only ever dispatches to a `ToolDefinition` that
was explicitly registered by `build_registry` — an unknown name never
reaches `globals()` lookup, it returns `UNKNOWN_TOOL`.

## 2. Argument and unknown-tool failures

`json.loads(response.arguments)` and `globals()[response.tool_name]` both
raise uncaught exceptions on bad input — malformed JSON raises
`JSONDecodeError`, and an unknown tool name raises `KeyError` — either of
which crashes the whole loop with no recovery and no signal back to the
model. There is also no argument-shape validation at all: `**arguments`
passes whatever keys were parsed directly into the function call, so wrong
types, missing required fields, or extra fields surface as raw Python
`TypeError`s instead of a structured, model-legible error. Our `execute()`
instead treats both failure modes as expected, first-class outcomes:
unknown tool name → `ToolResult(status=UNKNOWN_TOOL)`; JSON parse failure or
Pydantic `ValidationError` against the tool's strict `arguments_model` →
`ToolResult(status=INVALID_ARGUMENTS)`. Neither case ever raises past the
registry — validation failure is data, not a crash.

## 3. Call/result correlation

`response.tool_name` and `response.arguments` are used, but there is no
`call_id` anywhere in the loop, and `history.append(str(result))` stringifies
the result with no reference back to which request produced it. This makes
multiple tool calls per turn (parallel calls) uncorrelatable — if the model
requests two calls, there is no way to know which result answers which
request once both are stringified into a flat history list, and the model
receiving that history back has no way to match evidence to its own
requests either. Every `ToolCall` and `ToolResult` in our implementation
carries the same `call_id` from request through to the trace and back to
the model (`ToolResult.call_id` is always copied from `ToolCall.call_id`
in `execute()`); the live `ClaudeSession` uses this to key `tool_use_id` on
the `tool_result` content block it sends back, and `ScriptedModelSession`
actively raises `ModelGatewayError` if the returned call IDs don't match
what it expects, making mis-correlation loud rather than silent.

## 4. Required state and trace data

The only state carried between iterations is `history`, a flat list of
stringified results with no iteration counter, no call counter, no
per-signature counts, and no structured record of what happened at each
step (which tool, with what arguments, what status, in what order). There
is nothing to inspect after the fact beyond a best-effort natural-language
reconstruction from `str(result)` — no way to answer "why did this stop,"
"was this a retry," or "did this call actually execute" without re-running
the model. Our `run_agent` maintains explicit typed state — `iteration`,
`tool_call_count`, `signature_counts`, and an append-only `trace:
list[TraceEvent]` with a monotonic `sequence`, each event tagged with its
`kind` (`MODEL_TURN`/`TOOL_CALL`/`TOOL_RESULT`/`FINAL_ANSWER`/`STOP`),
`iteration`, `call_id`, `tool_name`, and `status` — sufficient to answer all
of those questions purely by reading the returned `AgentResult`, without
re-invoking the model.

## 5. Stop and repetition limits

`while True` has no iteration cap, no total-call cap, and no
repeated-call cap — the only exit is the model eventually returning a
falsy `tool_name`, which is entirely at the model's discretion. A model
that keeps requesting tool calls (intentionally, by looping behavior, or by
API malfunction) runs this loop forever, burning cost and wall-clock with no
application-side backstop. Our `run_agent` checks `iteration >
config.max_iterations` before every model call (`ITERATION_LIMIT`), checks
`tool_call_count >= config.max_total_tool_calls` before every dispatch
(`TOTAL_CALL_LIMIT`), and checks `signature_counts[call.signature()] >=
config.max_repeated_calls_per_signature` before every dispatch
(`REPEATED_CALL_LIMIT`) — all three are enforced by code in the loop itself,
not by prompting the model to behave, and each produces an explicit
`StopReason` rather than the loop simply continuing.

## 6. Error categories and retry ownership

`result = globals()[response.tool_name](**arguments)` has no
`try`/`except` around the call at all in the pseudocode as literally
written — but the accompanying description states the intended (and
worse) behavior is to "catch all tool exceptions and retry forever," which
collapses every distinct failure mode (not found, a transient/retryable
condition, a permanent/terminal condition) into one undifferentiated
"try again" path with no bound. This means a terminal error — one that
will never succeed on retry — gets retried exactly as aggressively as a
transient one, and the model never even learns a failure occurred, since
retries are invisible to it. Our implementation categorizes every store
exception explicitly (`ToolNotFoundError`→`NOT_FOUND`,
`RetryableToolError`→`RETRYABLE_ERROR`, `TerminalToolError`→
`TERMINAL_ERROR`) and never auto-retries: the app reports the status once
and hands it back to the model as a normal tool result; the *model* decides
whether to issue a new call (itself still bounded by the repeated-call and
total-call limits above), and a terminal error is never retried by either
side.

## 7. Evidence requirements for a successful final answer

`return {"success": True, "answer": response.text}` marks *any* text
response as `success: True` unconditionally — including one produced
immediately after a tool call that raised, returned not-found, or failed
terminally, since (per the description) all such failures are silently
swallowed by the blanket retry-forever `except`. There is no way, from the
returned value, to tell a well-evidenced answer from one fabricated after
every tool failed. Our loop is more honest but not fully solved: reaching
`StopReason.COMPLETED` still only means "the model chose to stop with
text," not "the text is supported by successful tool evidence" — this is a
deliberate, documented limitation (see `reports/state-diagram.md`'s
Final-answer transition and `reports/final-report.md`'s
Unsupported-answer analysis), not a claim of correctness. What we do
provide, that the broken loop does not, is the ability to check that claim
after the fact: every tool result's `status` is in the trace, correlated by
`call_id`, so a human or a downstream LLM-judge pass can verify whether a
`COMPLETED` answer's claims line up with the `SUCCESS` results that
preceded it — the broken loop discards this evidence entirely by
stringifying results into an unstructured history and reporting blanket
`success: True`.

## 8. Corrected transition diagram

```
                         ┌───────────────┐
                         │     START      │
                         └───────┬────────┘
                                 │
                                 ▼
        ┌───────────────────────────────────────────┐
  ┌────▶│ iteration += 1 > max_iterations? ──yes────┼──▶ STOP(ITERATION_LIMIT)
  │     └───────────────────┬─────────────────────┘
  │                         │ no
  │                         ▼
  │     ┌───────────────────────────────────────────┐
  │     │  MODEL TURN: model.respond(history) ───────┼─raises─▶ STOP(MODEL_ERROR)
  │     └───────────────────┬─────────────────────┘
  │                         │
  │            ┌────────────┼─────────────┐
  │            ▼            ▼             ▼
  │      final_text    tool_calls    neither
  │            │            │             │
  │            ▼            │             ▼
  │   STOP(COMPLETED,       │      STOP(EMPTY_TURN)
  │   answer recorded       │
  │   with trace of         ▼
  │   supporting evidence)  ┌─────────────────────────────────┐
  │                         │ for each call (registry-known    │
  │                         │ tools ONLY, never globals()):    │
  │                         │  1. unknown name → UNKNOWN_TOOL,  │
  │                         │     no dispatch                  │
  │                         │  2. JSON parse / schema           │
  │                         │     validation fails →            │
  │                         │     INVALID_ARGUMENTS, no dispatch│
  │                         │  3. total_call_count limit         │
  │                         │     reached? ──yes─▶ STOP(TOTAL_CALL_LIMIT)
  │                         │  4. repeated signature limit        │
  │                         │     reached? ──yes─▶ STOP(REPEATED_CALL_LIMIT)
  │                         │  5. EXECUTE, map exception to        │
  │                         │     status (no auto-retry):          │
  │                         │     SUCCESS / NOT_FOUND /             │
  │                         │     RETRYABLE_ERROR / TERMINAL_ERROR  │
  │                         │  6. record ToolResult with matching   │
  │                         │     call_id in trace                  │
  │                         └───────────────────┬───────────────────┘
  │                                             │ all calls in turn resolved
  │                                             ▼
  │                          collect ToolResults (call_id-correlated)
  └─────────────────────────────────┘ (loop back to MODEL TURN)
```

Differences from the broken pseudocode: a fixed, read-only tool registry
instead of `globals()` dispatch; strict schema validation before any
execution; every call and result carries and preserves a `call_id`; three
explicit, code-enforced stop limits instead of an unbounded `while True`;
distinct error categories with no automatic retrying; and a "completed"
outcome that at minimum preserves the trace needed to check evidence,
rather than a blanket `success: True`.
