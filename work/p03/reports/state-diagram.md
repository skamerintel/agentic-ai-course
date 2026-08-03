# Agent State and Transition Design

## State fields

The loop (`run_agent` in `agent.py`) owns all state; nothing lives in the
model or the tool layer:

- `iteration: int` — starts at 0, incremented once per model turn requested.
- `tool_call_count: int` — total tool calls executed (not merely requested)
  across the whole run.
- `call_signature_counts: dict[str, int]` — count per `ToolCall.signature()`
  (`"{name}:{sorted-json-args}"`), used to enforce the repeated-call limit.
- `pending_tool_outputs: list[ToolResult] | None` — results from the previous
  iteration to hand back into `session.respond(tool_outputs=...)` on the next
  call; `None` on the very first call.
- `trace: list[TraceEvent]` — append-only, monotonically increasing
  `sequence`, one entry per `MODEL_TURN`, `TOOL_CALL`, `TOOL_RESULT`,
  `FINAL_ANSWER`, or `STOP` kind.
- `stop_reason: StopReason | None` — set exactly once, when the loop exits.
- `final_answer: str | None` — set only on `StopReason.COMPLETED`; `None` for
  every limit/error stop reason.
- `config: AgentConfig` — `max_iterations`, `max_total_tool_calls`,
  `max_repeated_calls_per_signature`; read-only, supplied by the caller
  (or scenario `config` overrides), never mutated during the run.

## Model-turn transition

On each iteration: increment `iteration`; if `iteration > config.max_iterations`
before calling the model, stop with `ITERATION_LIMIT` instead of making the
call (see Iteration limit). Otherwise call
`session.respond(pending_tool_outputs)`, append a `MODEL_TURN` trace event
with the returned `response_id`, then branch on the returned `ModelTurn`:

- `tool_calls` non-empty → go to **Tool-validation transition** for every
  call in the turn (parallel calls in one turn are all validated/dispatched
  before the next model turn is requested).
- `final_text` set (and `tool_calls` empty — `ModelTurn` forbids both) → go
  to **Final-answer transition**.
- neither set (`response_id` only, no calls, no text) → go to **Provider and
  empty-turn failures**, `EMPTY_TURN`.

## Tool-validation transition

For each `ToolCall` in the turn, before any execution:

1. Look up `call.name` in the `ToolRegistry`. Unknown name → build a
   `ToolResult(status=UNKNOWN_TOOL, call_id=call.call_id, tool_name=call.name)`
   directly, skip dispatch, still counts toward `tool_call_count` and the
   repeated-call signature (an unknown tool repeatedly requested must still
   be limited).
2. Parse `call.arguments` (JSON) against the tool's `arguments_model`.
   Malformed JSON or schema mismatch (extra fields, wrong type, failed
   constraint) → `ToolResult(status=INVALID_ARGUMENTS, ...)`, no dispatch.
   This must never raise past the loop — invalid input is a normal, expected
   `ToolResult`, not an exception.
3. Otherwise the call is well-formed → proceed to limit checks
   (**Total-call limit**, **Repeated-call limit**) before **Tool-execution
   transition**. Limit checks happen per-call, in call order within the
   turn, so a turn with 3 parallel calls can execute call 1, hit the limit,
   and stop before executing calls 2–3.

Every outcome — valid, invalid, unknown — is appended to the trace as a
`TOOL_CALL` event (`status` recorded even before execution for unknown/
invalid cases) immediately when the call is inspected, so the trace shows
call intent regardless of whether execution happens.

## Tool-execution transition

For a validated call that passed limit checks: increment
`tool_call_count` and `call_signature_counts[call.signature()]`, then invoke
the registered handler through the store. Map store-level exceptions to
`ToolStatus`:

- `ToolNotFoundError` → `NOT_FOUND`.
- `RetryableToolError` → `RETRYABLE_ERROR` (the app does not auto-retry; it
  reports the status and lets the *model* decide to retry on its next turn).
- `TerminalToolError` → `TERMINAL_ERROR` (no retry should be attempted by
  either the app or, per instructions, the model).
- Successful return → `SUCCESS`, with the handler's return value as `data`.

Every outcome becomes a `ToolResult` with the original `call_id` preserved
unchanged from the `ToolCall`, and a `TOOL_RESULT` trace event is appended
(`sequence`, `iteration`, `call_id`, `tool_name`, `status`).

## Tool-result transition

All `ToolResult`s produced across every call in the current turn (validated,
invalid, unknown, executed) are collected in call order into
`pending_tool_outputs` and the loop returns to **Model-turn transition** for
the next iteration — unless a limit was hit mid-turn, in which case the loop
stops immediately (see Total-call limit / Repeated-call limit) without
completing the remaining calls in that turn or requesting another model
turn.

## Final-answer transition

Reached only when the model turn has `final_text` set and no `tool_calls`.
Append a `FINAL_ANSWER` trace event, set `final_answer = final_text`, set
`stop_reason = COMPLETED`, append a `STOP` trace event, and return the
`AgentResult`. The loop does not independently verify that the final text is
"supported" by prior tool evidence — that check is a downstream trace-review
step (see `PROJECT.md` step 6), not a loop invariant. Reaching `COMPLETED`
means the model chose to stop, not that the answer was necessarily
well-evidenced.

## Iteration limit

Checked at the top of every **Model-turn transition**, before calling
`session.respond`. If the next iteration would exceed
`config.max_iterations`, the loop stops with `stop_reason = ITERATION_LIMIT`,
`final_answer = None`, and appends a `STOP` trace event — no further model
call is made. This bounds wall-clock/cost even if the model never produces
`final_text` (scenario S08).

## Total-call limit

Checked immediately before executing each individual validated call (not
per-turn). If `tool_call_count` has already reached
`config.max_total_tool_calls`, the loop stops with
`stop_reason = TOTAL_CALL_LIMIT`, `final_answer = None`, without executing
that call or any later call in the same turn, and without requesting another
model turn.

## Repeated-call limit

Checked immediately before executing each individual validated call, using
`call.signature()` (tool name + canonicalized JSON arguments). If executing
this call would make `call_signature_counts[signature]` exceed
`config.max_repeated_calls_per_signature`, the loop stops with
`stop_reason = REPEATED_CALL_LIMIT`, `final_answer = None`, without executing
that call. This is what prevents the model from calling the exact same tool
with the exact same arguments indefinitely (scenario S07: limit of 2 stops
before the 3rd identical `get_service_status("checkout")` call executes,
`tool_call_count` ends at 2).

## Provider and empty-turn failures

- `ModelGatewayError` (or any provider-level exception raised by
  `session.respond`, live or scripted) is caught by the loop, not allowed to
  propagate: append a `STOP` trace event, set
  `stop_reason = MODEL_ERROR`, `final_answer = None`, and return.
- An `EMPTY_TURN` (model returns a turn with neither `tool_calls` nor
  `final_text`) is treated as a distinct, explicit stop —
  `stop_reason = EMPTY_TURN`, `final_answer = None` — rather than looping
  forever waiting for the model to say something.
- Neither failure mode allows the loop to retry indefinitely on its own;
  every provider-side failure resolves to exactly one terminal
  `AgentResult`.

## Diagram

```
                         ┌─────────────────────┐
                         │        START          │
                         └──────────┬─────────────┘
                                    │
                                    ▼
              ┌──────────────────────────────────────┐
      ┌──────▶│  iteration += 1; iteration > max? ────┼───yes──▶ STOP(ITERATION_LIMIT)
      │       └──────────────────┬───────────────────┘
      │                          │ no
      │                          ▼
      │       ┌──────────────────────────────────────┐
      │       │ MODEL TURN: session.respond(outputs)   │──raises──▶ STOP(MODEL_ERROR)
      │       └──────────────────┬───────────────────┘
      │                          │
      │           ┌──────────────┼───────────────┐
      │           ▼              ▼               ▼
      │     final_text set   tool_calls set   neither set
      │           │              │               │
      │           ▼              │               ▼
      │   STOP(COMPLETED,        │        STOP(EMPTY_TURN)
      │    final_answer set)     │
      │                          ▼
      │           ┌───────────────────────────────────┐
      │           │ for each call in turn (in order):   │
      │           │  1. VALIDATE (unknown tool /        │
      │           │     invalid args -> ToolResult,     │
      │           │     no dispatch)                    │
      │           │  2. total_calls limit reached? ─────┼──yes──▶ STOP(TOTAL_CALL_LIMIT)
      │           │  3. repeated signature limit         │
      │           │     reached? ────────────────────────┼──yes──▶ STOP(REPEATED_CALL_LIMIT)
      │           │  4. EXECUTE -> map exception to      │
      │           │     status (SUCCESS/NOT_FOUND/       │
      │           │     RETRYABLE_ERROR/TERMINAL_ERROR)  │
      │           └──────────────────┬───────────────────┘
      │                              │ all calls in turn produced ToolResults
      │                              ▼
      │                collect into pending_tool_outputs
      └───────────────────────────────┘  (loop back to MODEL TURN)
```
