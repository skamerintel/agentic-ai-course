# Operations Tool Agent Report

## Business outcome

An operations analyst can now ask natural-language questions about service
health, managed assets, and incident history and receive answers backed by
deterministic tool evidence rather than model recall. The application — not
the model — owns tool execution, validation, correlation, limits, and
stopping, so every answer can be traced back to a specific tool call, and
every failure mode (unknown tool, bad arguments, missing record, transient
or permanent tool failure) surfaces as an explicit, typed result instead of
a crash or a silently wrong answer.

## Tool design

Three read-only tools, detailed in `reports/tool-catalog.md`:
`get_service_status` (point-in-time snapshot, one service), `search_incidents`
(bounded historical list, up to 5 incidents, most recent first), and
`get_asset` (single-record inventory lookup by ID). They are kept separate
because they answer different questions at different time horizons and carry
different result shapes and error surfaces — see the catalog for the full
rationale. No write tools exist; every real state-changing action here has
an existing human-owned approval process this project does not model.

## Agent state machine

Documented in `reports/state-diagram.md`. The loop
(`run_agent` in `src/operations_agent/agent.py`) owns iteration count, total
tool-call count, per-signature repeat counts, and the full trace. Each model
turn is inspected for `tool_calls` vs. `final_text` vs. neither; each tool
call is validated (unknown tool / malformed or invalid JSON → typed result,
no dispatch), limit-checked, then dispatched, with exceptions from the store
(`ToolNotFoundError`, `RetryableToolError`, `TerminalToolError`) mapped to
`ToolStatus` values. Limits are checked per individual call within a turn,
not per turn, so a multi-call turn can partially execute before a limit
stops it.

## Scenario results

`uv run operations-agent offline --output reports/offline-results.jsonl`
against all nine scenarios in `fixtures/scenarios.json`:

| Scenario | Stop reason | Iterations | Tool calls | Notes |
|---|---|---|---|---|
| S01 | completed | 3 | 2 | sequential status + incidents |
| S02 | completed | 2 | 1 | single asset lookup |
| S03 | completed | 2 | 1 | not-found service, reported as such |
| S04 | completed | 3 | 2 | retryable error, then model-directed retry succeeds |
| S05 | completed | 2 | 1 | terminal error, reported as unverifiable |
| S06 | completed | 3 | 2 | invalid arguments, then corrected |
| S07 | repeated_call_limit | 3 | 2 | 3rd identical call stopped before execution |
| S08 | iteration_limit | 3 | 3 | stopped mid-investigation, no final answer |
| S09 | completed | 2 | 2 | two parallel calls in one turn |

Aggregate: 7 completed, 1 repeated-call-limit stop, 1 iteration-limit stop —
matching the CLI's summary counter output exactly. All nine required paths
from `PROJECT.md` (sequential, parallel, invalid-args-then-correction,
retryable-then-retry, terminal error, not found, repeated-call limit,
iteration limit) are covered by name.

## Error and limit behavior

- **Unknown tool / invalid arguments**: caught during validation, returned
  as `ToolResult(status=UNKNOWN_TOOL|INVALID_ARGUMENTS, ...)` with the
  original `call_id` preserved; never raised past the loop
  (`tools.py::ToolRegistry.execute`).
- **Not found / retryable / terminal**: mapped from store exceptions
  (`ToolNotFoundError`, `RetryableToolError`, `TerminalToolError`) to the
  matching `ToolStatus`. The app does not auto-retry a retryable error — it
  reports the status and lets the model decide to retry on its next turn
  (demonstrated by S04). A terminal error is never retried by either side
  (S05).
- **Iteration limit**: checked before each model call; exceeding
  `max_iterations` stops with no further model call and `final_answer=None`
  (S08).
- **Total-call limit**: checked before each individual tool dispatch within
  a turn; not exercised by the default scenario set, but now covered by
  `tests/test_agent.py::test_total_call_limit_stops_before_exceeding_the_cap`
  (three distinct-signature calls, `max_total_tool_calls=2`, stop confirmed
  at `tool_call_count == 2` with no third `TOOL_RESULT` recorded).
- **Repeated-call limit**: checked per `call.signature()` (tool name +
  canonicalized JSON arguments) before dispatch; the 3rd identical
  `get_service_status("checkout")` call is never executed — `tool_call_count`
  stops at 2 (S07).
- **Empty turn / model error**: both are explicit stop reasons
  (`EMPTY_TURN`, `MODEL_ERROR`); neither loops indefinitely waiting for the
  model or retries a failed provider call on its own. Also not exercised by
  the default scenario set, but now covered directly:
  `test_empty_turn_stops_when_model_returns_neither_calls_nor_text` and
  `test_model_error_stops_explicitly_instead_of_crashing` in
  `tests/test_agent.py`, using fake `ModelSession` implementations
  (`SequenceModelSession`, `RaisingModelSession`) rather than scenario
  fixtures, since neither path fits the scripted-turn shape.

## Trace examples

**S07 (repeated-call limit)** — trace excerpt showing the stop happening at
the `TOOL_CALL` event for the third `s07-3` call, with no corresponding
`TOOL_RESULT`:

```json
{"sequence": 7, "kind": "model_turn", "iteration": 3, "response_id": "S07-turn-3"},
{"sequence": 8, "kind": "tool_call", "iteration": 3, "call_id": "s07-3", "tool_name": "get_service_status"},
{"sequence": 9, "kind": "stop", "iteration": 3, "status": "repeated_call_limit"}
```
`tool_call_count` ends at 2, `final_answer` is `null` — the third call's
intent is visible in the trace, but it was never dispatched.

**S08 (iteration limit)** — three full model-turn/tool-call/tool-result
cycles execute successfully, then the loop stops before requesting a fourth
model turn:

```json
{"sequence": 10, "kind": "stop", "iteration": 3, "status": "iteration_limit"}
```
`iterations` is 3, matching `config.max_iterations` for this scenario;
`tool_call_count` is 3 and `final_answer` is `null` — the model never got a
chance to synthesize an answer.

**S09 (parallel calls)** — one model turn produces two `ToolCall`s
(`s09-status`, `s09-incidents`); both are validated, dispatched, and
returned before the next model turn is requested, and both `call_id`s
reappear unchanged on their `tool_result` events. The second model turn then
returns `final_text` directly with no further tool calls.

## Live Claude demonstration

Per the learner's explicit direction (this project's `PROJECT.md` names an
OpenAI Responses integration; see the deviation note below), the live
session (`ClaudeSession` in `src/operations_agent/model.py`) uses Claude via
AWS Bedrock (`AnthropicBedrock`) instead of OpenAI's Responses API. It
converts `ToolRegistry.schemas()` to Claude's `{name, description,
input_schema}` tool shape, maintains a running message list in place of
`previous_response_id` (Claude has no continuation-token concept), and maps
`tool_use` blocks to `ToolCall`s and `ToolResult`s to `tool_result` content
blocks keyed by `call_id`.

Three live runs against the learner's real Bedrock credentials
(`uv run operations-agent live "..."`) were sanitized and reviewed:

1. `"Is checkout healthy? Include recent incidents."` → two sequential tool
   calls (`get_service_status`, `search_incidents`), both `toolu_bdrk_*`
   call IDs correctly correlated, completed with an evidenced answer citing
   both incidents by ID.
2. `"Who owns asset LAP-500?"` → terminal error on `get_asset`, and the
   model reported it could not verify the answer rather than fabricating an
   owner — no `INSUFFICIENT EVIDENCE`-style hallucination.
3. `"Where is scanner SCN-B14?"` → single successful `get_asset` call,
   answer included the maintenance-required status as a caveat rather than
   omitting it.

## Unsupported-answer analysis

The loop itself does not verify that a `final_text` is evidence-backed —
reaching `StopReason.COMPLETED` means the model chose to stop, not that the
answer is necessarily well-supported (documented as a deliberate design
choice in `reports/state-diagram.md`). Reviewing the nine scripted scenarios
and the three live runs against this gap:

- S03 (not found) and S05 (terminal error): both final answers explicitly
  state the tool could not confirm the requested information, rather than
  guessing. This is correct scripted-model behavior and matched by the live
  terminal-error run above — but it is a property of the *scenario/model
  design*, not something the loop enforces. A model that ignored a
  `NOT_FOUND` or `TERMINAL_ERROR` result and answered confidently anyway
  would still receive `stop_reason=COMPLETED` from this implementation.
- S07 and S08 correctly never reach `COMPLETED` — `final_answer` is `None`
  for both, so there is no unsupported-answer risk in the limit-stop paths
  by construction (there is no text to be unsupported).
- Risk: any future model integration that produces confident text after a
  `NOT_FOUND`/`RETRYABLE_ERROR`/`TERMINAL_ERROR` tool result would be
  reported as `COMPLETED` with no code-level signal that the answer lacks
  support. Detecting this requires a human or LLM-judge review of the trace
  (matching the tool result statuses against the final answer's claims), not
  an automatic guarantee from `run_agent`.
- This exact adversarial case (confident `final_text` immediately after a
  `TERMINAL_ERROR`, on `get_asset("LAP-500")`) is now exercised directly by
  `tests/test_agent.py::test_completed_after_terminal_error_is_detectable_from_the_trace`.
  It confirms two things, not one: (1) `run_agent` still returns
  `StopReason.COMPLETED` and a non-`None` `final_answer` — the loop does
  *not* refuse or flag it, matching the risk above — and (2) the trace
  nonetheless makes the mismatch checkable, by walking the events preceding
  `FINAL_ANSWER` and confirming no `SUCCESS` tool result exists among them.
  That second assertion is the proof-of-detectability that was previously
  only a static claim in this section.

## Prototype-to-production gaps

- No automatic detection of unsupported final answers (see above) — a
  trace-review or LLM-judge step would need to be added before this could
  run unattended in production.
- The live session is only exercised by manual smoke tests, not by the
  automated test suite (by design, per `PROJECT.md`) — a regression in
  `ClaudeSession` would not be caught by CI.
- `OperationsStore` loads all fixture data into memory from flat JSON files;
  a real deployment would back these tools with live service-health,
  incident-management, and asset-inventory systems, each with its own
  latency, pagination, and authentication concerns not modeled here.
- No persistence of `AgentResult`/trace beyond the offline JSONL dump and ad
  hoc CLI output — a production system would need durable trace storage for
  audit and incident review.
- The provider swap from OpenAI to Claude/Bedrock is a deviation from
  `PROJECT.md`'s literal instructions ("Implement the live OpenAI session,"
  `OPENAI_API_KEY`/`OPENAI_MODEL`, Responses function calls,
  `previous_response_id`). The architecture supports either provider
  identically through the `ModelSession` protocol, but this should be
  surfaced explicitly to the mentor, since the written spec still names
  OpenAI/Responses-specific mechanics this implementation does not use.

## AI-generated proposals accepted and rejected

Full detail in `reports/ai-work-log.md` (5 entries). Summary:

- **Accepted**: the full tool catalog (Entry 1), the state diagram including
  its per-call (not per-turn) limit-check placement (Entry 2), the tools
  implementation (Entry 3), the scripted loop implementation including the
  `pyright` cast fixes for handler lambdas (Entry 4), and the Claude/Bedrock
  live session including the `AnthropicBedrock` public-import fix (Entry 5).
- **Rejected**: none outright — but two design decisions were explicitly
  flagged for the learner's judgment rather than treated as settled: (1)
  whether the loop's deliberate non-verification of final-answer evidence
  is the right call given the comprehension gate's concern about unsupported
  answers (Entry 2), and (2) the provider substitution itself, which was
  raised as a direct question to the learner rather than assumed (Entry 5,
  answered via `AskUserQuestion`: swap to Claude, don't track the spec's
  exact OpenAI wording).
- **Also completed**: `reports/broken-loop-review.md`, required by
  `broken-agent-loop-review.md`'s learner task (analysis of the flawed
  pseudocode loop) — covers execution/authorization risk, argument and
  unknown-tool failures, call/result correlation, required trace state,
  stop/repetition limits, error-category and retry ownership, and
  evidence requirements for a successful final answer, with a corrected
  transition diagram (Entry 7 in `reports/ai-work-log.md`).
