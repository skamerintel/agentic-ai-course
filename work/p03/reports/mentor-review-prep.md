# Mentor Review & Comprehension Gate Prep

Worked answers to `rubrics/mentor-review.md`'s defense prompts, plus a
comprehension-gate rehearsal using model turns that do not appear in
`fixtures/scenarios.json`. This is preparation to narrate the loop cold,
not new scenario fixtures — nothing here changes `src/` or `fixtures/`.

## Defense prompts

### 1. Predict the result of this malformed tool call

Given `{"call_id": "x1", "name": "get_asset", "arguments": "{\"asset\": \"SCN-B14\"}"}`
(wrong key: `asset` instead of `asset_id`):

- `tools.py:57` — `get_asset` is a registered tool name, so this is not
  `UNKNOWN_TOOL`.
- `tools.py:68-69` — the JSON string parses fine, but
  `GetAssetArgs.model_validate({"asset": "SCN-B14"})` fails:
  `extra="forbid"` rejects the unrecognized `asset` key and `asset_id` is
  required and missing.
- Caught at `tools.py:70` (`ValidationError`), returns
  `ToolResult(call_id="x1", tool_name="get_asset", status=INVALID_ARGUMENTS,
  message=str(error))`. The handler and store are never called. `call_id`
  is preserved on the result.

### 2. Explain why these two call signatures are or are not repeats

`ToolCall.signature()` (`models.py:58-64`) is
`f"{name}:{canonicalized_json_args}"`, where the arguments are re-serialized
via `json.dumps(parsed, sort_keys=True, separators=(",", ":"))`.

- `get_service_status({"service_name": "checkout"})` called twice → same
  signature → counted as a repeat by `signature_counts` (`agent.py:123-129`).
- `get_service_status({"service_name": "checkout"})` vs.
  `get_service_status({"service_name": "CHECKOUT"})` → **different**
  signatures, even though `OperationsStore` matches case-insensitively
  (`data.py`). Repeat detection is syntactic on the canonicalized argument
  JSON, not semantic on what the store would actually resolve to. Worth
  naming as a known edge case if asked: a model could evade the
  repeated-call limit by varying case or key order alone — key order
  doesn't work (canonicalized), but case does.

### 3. Trace two parallel calls and their outputs

Using scenario S09 (`fixtures/scenarios.json`, "Compare current checkout
status with its latest incident in one step"):

- One `ModelTurn` returns two `ToolCall`s in the same turn: `s09-status`
  (`get_service_status`) and `s09-incidents` (`search_incidents`).
- `agent.py:109-141` loops over `turn.tool_calls` **sequentially within the
  turn** — not concurrently in execution, but both belong to the same
  iteration and same model turn. For each: a `TOOL_CALL` trace event is
  appended, limit checks run, the call is dispatched, then a `TOOL_RESULT`
  event is appended — each event carries its own `call_id`.
- Both results accumulate in `pending_outputs` and are handed back together
  via `session.respond(pending_outputs)` on the next loop iteration
  (`agent.py:67`).
- `tests/test_agent.py::test_trace_preserves_parallel_call_ids` asserts
  both `s09-status` and `s09-incidents` survive into the `TOOL_RESULT`
  trace events as a set — proving no cross-call mixups.

### 4. Show where a retryable tool error becomes model input

Using scenario S04 ("Is payments healthy right now?"):

- First call `get_service_status("payments")` matches
  `data/failure_plan.json`'s `"get_service_status:payments": ["retryable"]`
  entry; the store raises `RetryableToolError`.
- `tools.py:87-93` catches it and returns
  `ToolResult(status=RETRYABLE_ERROR, ...)` — no exception escapes, no
  auto-retry inside `tools.py`.
- That result is appended to `pending_outputs` (`agent.py:131`), which
  becomes the `tool_outputs` argument to `session.respond(pending_outputs)`
  on the very next loop iteration (`agent.py:67`) — this is the moment a
  retryable error becomes model input.
- The *model* (in S04, the scripted second step) decides to call
  `get_service_status("payments")` again; this second attempt succeeds.
  The app never retries on its own — retry is entirely model-directed, and
  still bounded by the repeated-call limit if it kept failing.

### 5. Explain one stop reason from a JSON trace

Using scenario S07's trace tail ("Keep checking checkout until something
changes", `max_repeated_calls_per_signature: 2`):

- The third `get_service_status("checkout")` call (`s07-3`) produces a
  `TOOL_CALL` trace event but **no matching `TOOL_RESULT`** — the limit
  check at `agent.py:125-126` runs *before* dispatch and returns
  `stop(StopReason.REPEATED_CALL_LIMIT)` immediately.
- The trace's last two events are that dangling `TOOL_CALL` followed by a
  `STOP` event with `status="repeated_call_limit"`.
- `result.tool_call_count == 2` (only the first two calls actually
  executed) and `result.final_answer is None` — confirmed by
  `tests/test_agent.py::test_repeated_call_limit_stops_before_third_execution`.

### 6. Show an AI proposal you rejected

Honest answer: nothing was outright rejected across the 10 work-log entries
(`reports/ai-work-log.md`). Two decisions were explicitly escalated to me
as open questions rather than silently assumed by the AI, which is the
closest equivalent:

- **Entry 2** — whether `run_agent` should verify that a final answer is
  evidence-backed before returning `COMPLETED`. I chose to keep the
  current design (no automatic verification, but a trace that makes the
  mismatch checkable after the fact) rather than add an enforcement step.
- **Entry 5** — whether to keep PROJECT.md's literal OpenAI/Responses API
  spec or swap providers. I chose to swap to Claude via AWS Bedrock and not
  track the spec's exact OpenAI wording — a deliberate, disclosed deviation
  from the written brief, not an AI-generated shortcut I caught and fixed.

If asked directly for a *rejection*, say so plainly rather than inventing
one — the honest answer is "none yet, but here are two decisions I made
deliberately instead of accepting the default."

## Comprehension-gate rehearsal (unseen turns)

The gate: the mentor selects one scenario trace and one **unseen** model
turn; predict validation, execution, next input, and stop behavior. These
three turns are not in `fixtures/scenarios.json` — constructed here purely
for rehearsal.

### Rehearsal A — invalid arguments (out-of-range limit)

```json
{"tool_calls": [{"call_id": "z9", "name": "search_incidents",
  "arguments": "{\"service_name\": \"checkout\", \"limit\": 12}"}]}
```

1. **Validation**: `SearchIncidentsArgs.limit` is `Field(ge=1, le=5)`
   (`models.py:44`); `12` fails the pattern/range constraint →
   `INVALID_ARGUMENTS`.
2. **Execution**: none — validation fails before the handler runs
   (`tools.py:70`).
3. **Next input**: `ToolResult(call_id="z9", status=INVALID_ARGUMENTS,
   message=...)` joins `pending_outputs`, fed into the next
   `session.respond()` call.
4. **Stop behavior**: no stop triggered by this alone — it isn't a repeat,
   doesn't exceed any count. If the model kept resubmitting the same
   invalid call, the *signature* would still differ only if the arguments
   differ; an identical resubmission would eventually trip
   `REPEATED_CALL_LIMIT`.

### Rehearsal B — total-call limit

```json
[
  {"tool_calls": [{"call_id": "c1", "name": "get_service_status", "arguments": "{\"service_name\": \"checkout\"}"}]},
  {"tool_calls": [{"call_id": "c2", "name": "get_service_status", "arguments": "{\"service_name\": \"payments\"}"}]},
  {"tool_calls": [{"call_id": "c3", "name": "get_service_status", "arguments": "{\"service_name\": \"support-queue\"}"}]}
]
```
against `AgentConfig(max_total_tool_calls=2)`.

1. **Validation**: all three calls are individually valid — distinct,
   well-formed `service_name` values.
2. **Execution**: `c1` and `c2` dispatch and execute normally
   (`tool_call_count` goes 0→1→2). Before `c3` dispatches, `agent.py:120-121`
   checks `tool_call_count >= config.max_total_tool_calls` (`2 >= 2`) and
   stops — `c3` gets a `TOOL_CALL` trace event but never executes, exactly
   like the repeated-call case in prompt 5.
3. **Next input**: none — the loop stops, no further `session.respond()`
   call happens.
4. **Stop behavior**: `StopReason.TOTAL_CALL_LIMIT`, `tool_call_count == 2`,
   `final_answer is None`. Demonstrated by
   `tests/test_agent.py::test_total_call_limit_stops_before_exceeding_the_cap`
   — this path had no coverage until the AI review
   (`reports/ai-review.md`) flagged it, so cite that test directly if asked
   to prove it, not just describe it.

### Rehearsal C — unsupported answer after a terminal error

```json
[
  {"tool_calls": [{"call_id": "a1", "name": "get_asset", "arguments": "{\"asset_id\": \"LAP-500\"}"}]},
  {"final_text": "LAP-500 is confirmed assigned to Maya Chen."}
]
```

`LAP-500` is the existing `TERMINAL_ERROR` fixture in
`data/failure_plan.json`.

1. **Validation**: `asset_id` matches `GetAssetArgs`'s pattern — valid.
2. **Execution**: the store raises `TerminalToolError`; `tools.py:94-100`
   maps it to `ToolResult(status=TERMINAL_ERROR)`. No retry attempted by
   the app.
3. **Next input**: that `TERMINAL_ERROR` result is fed back via
   `session.respond(pending_outputs)`; the (hypothetical, adversarial)
   model turn ignores it and returns confident `final_text` anyway.
4. **Stop behavior**: `StopReason.COMPLETED` — **the loop does not refuse
   this.** `run_agent` has no code-level check that `final_text` is
   supported by a preceding `SUCCESS` result; reaching `COMPLETED` only
   means the model chose to stop with text (see
   `reports/final-report.md`'s Unsupported-answer analysis). This is the
   single most important "gotcha" to be ready to state plainly if asked —
   do not claim the loop prevents this.
   - What the loop *does* provide: the trace still lets a reviewer catch
     it. Walking the trace, the only `TOOL_RESULT` before `FINAL_ANSWER`
     has `status == TERMINAL_ERROR`, not `SUCCESS` — so the mismatch is
     visible to anyone (or any LLM-judge pass) that checks trace statuses
     against the final answer's claims. Exercised directly by
     `tests/test_agent.py::test_completed_after_terminal_error_is_detectable_from_the_trace`.

## Where each rubric category is demonstrated

| Rubric category | Primary evidence |
|---|---|
| 1. Tool boundaries and descriptions | `reports/tool-catalog.md` |
| 2. Strict argument validation | `models.py` (`extra="forbid"`, `strict=True` on all three Args models); Rehearsal A |
| 3. Error and result contracts | `tools.py` exception→`ToolStatus` mapping; Defense prompt 1 |
| 4. Agent state and transition design | `reports/state-diagram.md`; `agent.py` |
| 5. Call-ID correlation | Defense prompt 3; `test_trace_preserves_parallel_call_ids` |
| 6. Iteration, total-call, repeated-call controls | S07/S08 scenarios; Rehearsal B; `tests/test_agent.py` |
| 7. Complete and useful traces | `models.py::TraceEvent`; Defense prompt 5 |
| 8. Offline scenario coverage | `fixtures/scenarios.json` S01-S09; `reports/final-report.md` |
| 9. Live function-calling integration | `model.py::ClaudeSession` (Claude/Bedrock, disclosed deviation from OpenAI — `reports/ai-work-log.md` Entry 5) |
| 10. AI-generated code review and oral defense | This document; `reports/ai-work-log.md` (10 entries); `reports/ai-review.md` |

## Known open items to state proactively, not wait to be asked

- The OpenAI→Claude/Bedrock provider swap deviates from PROJECT.md's literal
  spec — disclosed and learner-approved (`ai-work-log.md` Entry 5), not
  hidden.
- `run_agent` does not verify final-answer evidence; `COMPLETED` means "the
  model stopped," not "the answer is supported." Rehearsal C is the
  concrete version of this.
- If both `ANTHROPIC_API_KEY` and AWS Bedrock credentials are set at once,
  `_build_client()` (`model.py`) silently prefers the direct API with no
  warning (`reports/ai-work-log.md` Entry 9's remaining risk).
</content>
