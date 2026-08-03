# Project 3 AI Work Log

## Entry 1

- Date and task: 2026-07-27 — draft `reports/tool-catalog.md` (workflow step 1,
  tool catalog approval) for `get_service_status`, `search_incidents`,
  `get_asset`.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: existing Pydantic
  argument models in `src/operations_agent/models.py`
  (`GetServiceStatusArgs`, `SearchIncidentsArgs`, `GetAssetArgs`), the
  `OperationsStore` handler logic and error types in
  `src/operations_agent/data.py`, and the fixture shapes in `data/*.json`
  were read first so the catalog describes what the code already declares
  rather than inventing new argument or result shapes.
- Important proposal or generated change: full draft of
  `reports/tool-catalog.md` — per-tool name, decision supported, model-facing
  description, argument schema, data source, result shape/bound, error
  categories, read/write classification, intentionally excluded fields, and
  hypothetical write-approval requirement; plus prose answers for why
  service-status and incident-search are separate tools and why no write
  tools exist.
- Evidence reviewed: `src/operations_agent/models.py`,
  `src/operations_agent/data.py`, `src/operations_agent/tools.py`,
  `data/services.json`, `data/assets.json`, `data/incidents.json`,
  `data/failure_plan.json`.
- Accepted portions: entire draft accepted as-is by the learner.
- Rejected or corrected portions: none.
- Checks run: none (no code changed; documentation step only).
- Remaining risk or uncertainty: catalog was written against the current
  schemas/handlers, which are themselves still stubs in places (e.g.
  `build_registry` in `tools.py` raises `NotImplementedError`); if argument
  constraints or error categories change during implementation, the catalog
  will need a follow-up pass to stay accurate.

## Entry 2

- Date and task: 2026-07-27 — draft `reports/state-diagram.md` (workflow
  step 2, state machine) covering model-turn, tool-validation,
  tool-execution, tool-result, final-answer transitions and every stop
  limit.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: the `agent.py`
  stub (`AgentConfig`, `run_agent` signature), the `ModelSession` protocol
  and `ScriptedModelSession` in `model.py`, the `StopReason`/`TraceKind`/
  `ToolStatus` enums and `AgentResult`/`TraceEvent` shapes in `models.py`,
  and the expected stop reasons/counts encoded in `tests/test_agent.py`
  and `fixtures/scenarios.json` (S07 repeated-call limit at count 2, S08
  iteration limit at 3, S09 parallel call_id preservation) were read first
  so the diagram matches what the tests already require rather than
  proposing a different design.
- Important proposal or generated change: full draft of
  `reports/state-diagram.md` — state fields owned by the loop, all named
  transitions, iteration/total-call/repeated-call limit semantics (checked
  per-call within a turn, not per-turn), provider/empty-turn failure
  handling, and an ASCII state diagram; explicit note that the loop itself
  does not verify final-answer evidence support (that's a separate
  trace-review step per `PROJECT.md`, not a loop invariant).
- Evidence reviewed: `src/operations_agent/agent.py`,
  `src/operations_agent/model.py`, `src/operations_agent/models.py`,
  `tests/test_agent.py`, `fixtures/scenarios.json`.
- Accepted portions: entire draft accepted as-is by the learner.
- Rejected or corrected portions: none.
- Checks run: none (no code changed; documentation step only).
- Remaining risk or uncertainty: the per-call (vs. per-turn) limit-check
  placement is a design choice inferred from test expectations, not stated
  explicitly in `PROJECT.md`; if the learner's `run_agent` implementation
  takes a different approach, this diagram will need a follow-up revision
  to stay accurate. Also flagged for the learner: whether the loop
  deliberately not verifying final-answer evidence is the right call, given
  the comprehension gate's concern about unsupported final answers being
  accepted as successful evidence.

## Entry 3

- Date and task: 2026-07-27 — implement `src/operations_agent/tools.py`
  (workflow step 3, tools independent of the agent loop): `build_registry`,
  `ToolRegistry.schemas`, and `ToolRegistry.execute`.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: `tests/test_tools.py`
  (three tests: schema shape/strictness, invalid-argument call-id
  preservation, not_found/unknown/retryable/terminal status mapping), the
  `ToolStatus` enum and argument models in `models.py`, and the exception
  types (`ToolNotFoundError`, `RetryableToolError`, `TerminalToolError`) and
  handler methods in `data.py` were read first, plus the approved tool
  catalog from Entry 1, so the implementation matched already-agreed
  schemas/behavior rather than inventing new ones.
- Important proposal or generated change: registered all three tools in
  `build_registry` with catalog-consistent descriptions and store-backed
  handlers; implemented `schemas()` by deriving the OpenAI-style function
  schema directly from each `arguments_model.model_json_schema()` (relies on
  `extra="forbid"` already producing `additionalProperties: false`);
  implemented `execute()` as unknown-tool lookup → JSON parse + Pydantic
  validation (`ValidationError`/`JSONDecodeError` → `INVALID_ARGUMENTS`) →
  handler dispatch with exception-to-status mapping
  (`ToolNotFoundError`→`NOT_FOUND`, `RetryableToolError`→`RETRYABLE_ERROR`,
  `TerminalToolError`→`TERMINAL_ERROR`) → `SUCCESS`, always preserving
  `call_id`.
- Evidence reviewed: `tests/test_tools.py`, `src/operations_agent/models.py`,
  `src/operations_agent/data.py`, `reports/tool-catalog.md`, generated
  `model_json_schema()` output for `GetServiceStatusArgs` (checked via a
  throwaway `uv run python3` snippet) to confirm `additionalProperties` and
  `required` come through as expected before relying on it in `schemas()`.
- Accepted portions: entire implementation accepted; no changes requested
  by the learner.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest tests/test_tools.py` (3 passed), `uv run pytest`
  (full suite — `test_tools.py` all green; remaining 4 failures are in
  `test_agent.py`, all raising `NotImplementedError` from `agent.py`'s
  `run_agent` stub, expected since the loop is step 4, not yet started),
  `uv run ruff check src/operations_agent/tools.py` (all checks passed).
- Remaining risk or uncertainty: `schemas()` assumes every future tool's
  argument model uses `extra="forbid"` so `additionalProperties` stays
  `False` without extra enforcement in `schemas()` itself — if a new tool
  omits that config, the schema test would still catch it, but nothing in
  `tools.py` guards it structurally. `pyright` has not yet been run against
  this file.

## Entry 4

- Date and task: 2026-07-27 — implement the scripted agent loop (workflow
  step 4): `run_agent` in `src/operations_agent/agent.py`, driven against
  every scenario in `fixtures/scenarios.json`.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: the approved
  `reports/state-diagram.md` from Entry 2, `tests/test_agent.py` (stop
  reasons and counts expected per scenario), and `fixtures/scenarios.json`
  (S01–S09 covering sequential/parallel calls, invalid-args correction,
  retryable/terminal errors, not-found, repeated-call limit, iteration
  limit) were read first; the diagram's per-call (not per-turn) limit
  placement was implemented as designed rather than re-derived.
- Important proposal or generated change: implemented `run_agent` in two
  increments — (1) core loop: iteration counter, `session.respond` call
  wrapped for `ModelGatewayError` → `MODEL_ERROR`, trace events for every
  `MODEL_TURN`/`TOOL_CALL`/`TOOL_RESULT`/`FINAL_ANSWER`/`STOP`, final-text
  and empty-turn branches, iteration-limit check before each model call;
  (2) total-call and repeated-call limits checked per-call (via
  `call.signature()`) before dispatch, stopping mid-turn without executing
  the limit-breaching call. Also fixed 4 pre-existing `pyright` errors in
  `tools.py` (Entry 3's handler lambdas lost the specific Pydantic subtype
  through the generic `ToolHandler = Callable[[BaseModel], Any]` alias) by
  adding explicit `cast(...)` at each handler call site.
- Evidence reviewed: `reports/state-diagram.md`, `tests/test_agent.py`,
  `fixtures/scenarios.json`, `src/operations_agent/model.py`,
  `src/operations_agent/models.py`, `src/operations_agent/tools.py`.
- Accepted portions: entire implementation, both increments, accepted as-is
  by the learner.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest tests/test_agent.py` (first increment: 3/4
  passed, repeated-call-limit test failed as expected before increment 2;
  after increment 2, 4/4 passed), `uv run pytest` (full suite, 9/9 passed),
  `uv run ruff check .` and `uv run ruff format --check .` (all files
  clean after manual line-length fixes), `uv run pyright src` (0 errors
  after the `tools.py` cast fixes).
- Remaining risk or uncertainty: `run_agent` only handles `ModelGatewayError`
  as the provider-failure path; the live `OpenAIResponsesSession` (step 5,
  not yet implemented) may raise other exception types on network/timeout
  failure that would currently propagate uncaught rather than mapping to
  `MODEL_ERROR` — worth revisiting once the live session exists. Also, the
  loop stops mid-turn on a limit breach without executing or recording a
  `TOOL_RESULT` for the breaching call itself (only the `TOOL_CALL` trace
  event exists for it) — this matches the state diagram design but should
  be called out explicitly during trace narration.

## Entry 5

- Date and task: 2026-07-27 — implement the live model session (workflow
  step 5), swapped from the scaffolded OpenAI Responses design to Claude via
  AWS Bedrock at the learner's explicit request (asked directly whether
  OpenAI was required; learner chose to swap providers and not track
  PROJECT.md's exact OpenAI wording).
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: the existing
  `ModelSession` protocol and `ModelGatewayError` contract in `model.py`
  (provider-agnostic `respond(tool_outputs) -> ModelTurn`), the
  `ToolRegistry.schemas()` OpenAI-ish output shape in `tools.py` (left
  unchanged), and prior repo history for the Bedrock credential pattern
  (`work/p01` commit c0af245) were reviewed first, though that prior
  approach used `boto3`/`pydantic-ai`'s `BedrockProvider` with an explicit
  `region_name`; this implementation instead confirmed (by reading the
  installed `anthropic` SDK source) that `AnthropicBedrock` natively reads
  `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` from the environment, so no
  `boto3` dependency or explicit region argument was needed.
- Important proposal or generated change: replaced the `OpenAIResponsesSession`
  stub with `ClaudeSession` in `model.py` — converts
  `ToolRegistry.schemas()`'s `{type, name, description, parameters, strict}`
  shape to Claude's `{name, description, input_schema}` via
  `_to_claude_tools`; maintains a running message list in place of
  `previous_response_id` (Claude has no continuation-token concept); maps
  `tool_use` content blocks to `ToolCall`s and `ToolResult`s to `tool_result`
  content blocks keyed by `call_id`; wraps `anthropic.APIError` as
  `ModelGatewayError` so `run_agent`'s existing `MODEL_ERROR` path applies
  unchanged; uses `AnthropicBedrock` (not `Anthropic`) as the client.
  Updated `pyproject.toml` (`openai` → `anthropic`), `.env.example`
  (`OPENAI_API_KEY`/`OPENAI_MODEL` → `ANTHROPIC_API_KEY`/`ANTHROPIC_MODEL`),
  and `cli.py`'s `live` command to build a `ClaudeSession` reading
  `ANTHROPIC_MODEL`. Fixed one `pyright` `reportPrivateImportUsage` error by
  importing `AnthropicBedrock` from its public re-export path
  `anthropic.lib.bedrock` instead of the top-level `anthropic` namespace.
- Evidence reviewed: `model.py`, `tools.py`, `cli.py`, `pyproject.toml`,
  `.env.example`, prior repo commit c0af245, installed `anthropic` SDK
  source for `AnthropicBedrock.__init__` and its `_infer_region` helper.
- Accepted portions: entire implementation accepted; the provider-swap
  decision itself was made by the learner in response to a direct clarifying
  question, not assumed.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest` (9/9 passed, unchanged from before the swap —
  confirms `run_agent`/`tools.py` remained untouched), `uv run ruff check .`
  and `uv run ruff format --check .` (clean), `uv run pyright src` (0 errors
  after the import-path fix), plus three live smoke tests against the
  learner's real Bedrock token via `uv run operations-agent live "..."`:
  a completed/evidenced checkout-health answer with correct `toolu_bdrk_*`
  call-id correlation across two sequential tool calls, a terminal-error
  asset lookup (LAP-500) correctly reported as unverifiable rather than
  fabricated, and a successful single-call asset lookup (SCN-B14).
- Remaining risk or uncertainty: live calls are excluded from the automated
  test suite per PROJECT.md, so this provider is only verified by the manual
  smoke tests above, not by CI-run tests — any future regression in
  `ClaudeSession` would not be caught automatically. The swap away from
  OpenAI is a deviation from PROJECT.md's literal instructions ("Implement
  the live OpenAI session," `OPENAI_API_KEY`/`OPENAI_MODEL`,
  `previous_response_id`); this should be flagged explicitly to the mentor
  during review since the written spec still names OpenAI/Responses
  API-specific mechanics that this implementation does not use.

## Entry 6

- Date and task: 2026-07-27 — draft `reports/final-report.md` (workflow
  step 6, trace analysis) covering business outcome, tool design, state
  machine, scenario results, error/limit behavior, trace examples, the live
  Claude demonstration, unsupported-answer analysis, prototype-to-production
  gaps, and a summary of accepted/rejected AI proposals.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: the offline batch
  output (`uv run operations-agent offline --output
  reports/offline-results.jsonl`, run fresh for this entry: 7 completed, 1
  repeated_call_limit, 1 iteration_limit across the 9 scenarios), individual
  scenario traces pretty-printed from that JSONL (S07, S08, S09 examined in
  detail), the three live Claude/Bedrock smoke-test transcripts from Entry
  5, and all five prior work-log entries were reviewed first so the report
  cites concrete evidence rather than restating the templates.
- Important proposal or generated change: full draft of
  `reports/final-report.md`; notably the "Unsupported-answer analysis"
  section states plainly that `run_agent` does not itself verify a
  `final_text` is evidence-backed — `COMPLETED` only means the model chose
  to stop — and that the scenarios/live runs happen to produce
  well-evidenced answers by design of the scripted model and Claude's own
  behavior, not by loop enforcement; also explicitly flagged that
  `reports/broken-loop-review.md` (required by
  `broken-agent-loop-review.md`) has not been started yet.
- Evidence reviewed: `reports/offline-results.jsonl` (regenerated),
  `fixtures/scenarios.json`, `src/operations_agent/agent.py`,
  `reports/state-diagram.md`, `reports/tool-catalog.md`,
  `reports/ai-work-log.md` Entries 1-5.
- Accepted portions: entire draft accepted by the learner.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest` (9/9 passed), `uv run ruff check .` and
  `uv run ruff format --check .` (clean) — re-run after drafting to confirm
  the report-writing pass didn't touch source and nothing regressed.
- Remaining risk or uncertainty: the report's claim that Claude "correctly"
  avoided fabricating answers after not-found/terminal errors is based on
  three manual smoke-test runs and the scripted scenarios only — it is not
  a guarantee enforced by `run_agent`, and a different live model turn could
  still produce an unsupported `COMPLETED` answer without the loop
  detecting it. `reports/broken-loop-review.md` was written afterward
  (Entry 7) — this entry's "remains outstanding" note was accurate only at
  the time it was drafted.

## Entry 7

- Date and task: 2026-07-27 — write `reports/broken-loop-review.md`, the
  learner task required by `broken-agent-loop-review.md` (analysis of the
  flawed `while True` / `globals()[response.tool_name]` pseudocode loop).
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: the flawed
  pseudocode and its accompanying description in
  `broken-agent-loop-review.md`, and this project's own implementation
  (`src/operations_agent/agent.py`, `tools.py`, `models.py`) as the point
  of contrast for every risk identified.
- Important proposal or generated change: full draft covering seven
  numbered risk categories (arbitrary `globals()` dispatch and missing
  tool allowlist; uncaught `JSONDecodeError`/`KeyError`/`TypeError` on bad
  input; no `call_id` correlation; no structured trace state; unbounded
  `while True` with no iteration/total-call/repeated-call caps; blanket
  catch-and-retry-forever collapsing not-found/retryable/terminal into one
  path; and `success: True` on any text response regardless of prior tool
  failures) plus a corrected state-transition diagram showing where each
  fix (registry-only dispatch, schema validation, limit checks, explicit
  error categories) sits in the loop.
- Evidence reviewed: `broken-agent-loop-review.md`, `agent.py`, `tools.py`,
  `models.py`, `reports/state-diagram.md`.
- Accepted portions: entire draft accepted by the learner.
- Rejected or corrected portions: none.
- Checks run: none applicable — this is an analysis document, not code;
  confirmed no source files were touched.
- Remaining risk or uncertainty: this review is a static, one-time analysis
  of the given pseudocode snippet; it does not re-run against this
  project's actual code path with an adversarial or malformed live model
  turn, so its claims about this implementation's behavior rest on reading
  the source, not on a new executed test.

## Entry 8

- Date and task: 2026-08-03 — correct `.env.example` after an independent
  AI review (`reports/ai-review.md`) flagged it as inconsistent with the
  actual Bedrock auth path.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: `reports/ai-review.md`
  Important Findings ("Environment-variable documentation is inconsistent
  with the actual Bedrock auth path") and Entry 5 of this log, which states
  `AnthropicBedrock` reads `AWS_BEARER_TOKEN_BEDROCK`/`AWS_REGION` from the
  environment rather than an Anthropic API key. Confirmed by grepping
  `cli.py`/`model.py`: only `ANTHROPIC_MODEL` is ever read via
  `os.environ`; `ANTHROPIC_API_KEY` was never consumed anywhere in the code.
- Important proposal or generated change: replaced `.env.example`'s
  `ANTHROPIC_API_KEY=` line with `AWS_BEARER_TOKEN_BEDROCK=` and
  `AWS_REGION=`, keeping `ANTHROPIC_MODEL=`, so the file documents the
  credentials `ClaudeSession` actually needs.
- Evidence reviewed: `.env.example`, `cli.py`, `model.py`,
  `reports/ai-review.md`, `reports/ai-work-log.md` Entry 5.
- Accepted portions: entire change accepted.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest` (9/9 passed), `uv run ruff check .` and
  `uv run ruff format --check .` (clean), `uv run pyright src` (0 errors)
  — re-run after the edit to confirm a non-code documentation fix caused
  no regression.
- Remaining risk or uncertainty: this fix addresses only the documented
  variable names, not the other items `reports/ai-review.md` raised (no
  test coverage for `TOTAL_CALL_LIMIT`/`EMPTY_TURN`/`MODEL_ERROR` stop
  paths, and no automated case proving an unsupported final answer after a
  terminal/not-found result would be detectable from the trace). Those
  remain open going into mentor review.

## Entry 9

- Date and task: 2026-08-03 — make provider selection (direct Anthropic API
  vs. AWS Bedrock) an environment-variable switch instead of a code edit,
  per the learner's request that not everyone reviewing/running this will
  have Bedrock access.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: `ClaudeSession`
  (`model.py`) previously hardcoded `AnthropicBedrock` as the client with
  no alternative path; the learner asked for something like "load in the
  code and switch models" without a code change.
- Important proposal or generated change: added `_build_client()` in
  `model.py`, which returns `anthropic.Anthropic(...)` if
  `ANTHROPIC_API_KEY` is set in the environment, else falls back to
  `AnthropicBedrock(...)`; `ClaudeSession.__init__` now calls
  `_build_client(timeout_seconds)` instead of constructing
  `AnthropicBedrock` directly. Updated `.env.example` to document both
  paths side by side (`ANTHROPIC_MODEL` required either way; either
  `ANTHROPIC_API_KEY` alone, or `AWS_BEARER_TOKEN_BEDROCK`/`AWS_REGION`).
  No CLI or constructor signature changed — switching providers is now a
  `.env` edit only.
- Evidence reviewed: `model.py`, `cli.py`, `.env.example`,
  `anthropic.Anthropic`'s constructor (reads `ANTHROPIC_API_KEY` natively,
  same pattern as `AnthropicBedrock` reading its own env vars).
- Accepted portions: entire change accepted.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest` (9/9 passed — no test constructs
  `ClaudeSession`/`_build_client`, so this is unverified by CI, same
  live-session gap noted in Entry 5), `uv run ruff check .` and
  `uv run ruff format --check .` (clean), `uv run pyright src` (0 errors,
  confirms the `anthropic.Anthropic | AnthropicBedrock` return type resolves
  cleanly against `messages.create`'s shared interface).
- Remaining risk or uncertainty: provider selection is inferred implicitly
  from which env var is present rather than an explicit
  `ANTHROPIC_PROVIDER=api|bedrock` flag — simpler, but if a learner sets
  both `ANTHROPIC_API_KEY` and Bedrock credentials at once, the direct API
  silently wins with no warning. Still untested by the automated suite,
  same as the rest of `ClaudeSession` (Entry 5, `reports/ai-review.md`).

## Entry 10

- Date and task: 2026-08-03 — close the remaining test-coverage gaps
  `reports/ai-review.md` flagged under Important Findings: no test/scenario
  exercises `TOTAL_CALL_LIMIT`, `EMPTY_TURN`, or `MODEL_ERROR`, and no
  automated case demonstrates that an unsupported final answer (text
  immediately after a `NOT_FOUND`/`TERMINAL_ERROR` result) is actually
  detectable from the trace, as opposed to only claimed in prose.
- Coding agent used: Claude Code (Sonnet 5).
- State, schema, or acceptance criteria supplied first: `reports/ai-review.md`
  Important Findings 1 and 2, `src/operations_agent/agent.py` (to confirm
  exactly where each stop path and the `FINAL_ANSWER`/`TOOL_RESULT` trace
  events are produced), and the existing `fixtures/scenarios.json` shape
  (one full model turn per step via `ScriptedModelSession`), which does not
  fit `EMPTY_TURN`/`MODEL_ERROR`/adversarial-`TERMINAL_ERROR` cases cleanly
  since those need a session that returns an empty turn, raises, or
  sequences turns not tied to a scenario's expected-tool-names shape.
- Important proposal or generated change: added two fake `ModelSession`
  implementations directly in `tests/test_agent.py` —
  `SequenceModelSession` (plays back a fixed list of `ModelTurn`s) and
  `RaisingModelSession` (always raises `ModelGatewayError`) — rather than
  extending `ScriptedModelSession` or `scenarios.json`, since these paths
  are about `run_agent`'s reaction to `ModelSession` behavior, not about
  scripting realistic conversational turns. Added four tests:
  `test_total_call_limit_stops_before_exceeding_the_cap` (three
  distinct-signature calls against `max_total_tool_calls=2`, confirms the
  cap is `TOTAL_CALL_LIMIT`, not `REPEATED_CALL_LIMIT`, and only 2
  `TOOL_RESULT` events exist); `test_empty_turn_stops_when_model_returns_neither_calls_nor_text`;
  `test_model_error_stops_explicitly_instead_of_crashing`; and
  `test_completed_after_terminal_error_is_detectable_from_the_trace`, which
  runs `get_asset("LAP-500")` (the existing `TERMINAL_ERROR` fixture from
  `data/failure_plan.json`) followed by a confident `final_text`, asserts
  `run_agent` still returns `COMPLETED` with a non-`None` answer (proving
  the loop does not itself refuse this), and then asserts the trace slice
  preceding `FINAL_ANSWER` contains no `SUCCESS` tool result — the concrete
  demonstration that the mismatch is checkable after the fact, which
  `reports/final-report.md`'s Unsupported-answer analysis had previously
  only asserted in prose. Updated `reports/final-report.md` to cite these
  four tests in place of the stale "not exercised by the default scenario
  set" language.
- Evidence reviewed: `reports/ai-review.md`, `agent.py`, `models.py`,
  `tools.py`, `data/failure_plan.json`, `data/services.json`, existing
  `tests/test_agent.py` and `tests/test_model.py`.
- Accepted portions: entire change accepted.
- Rejected or corrected portions: none.
- Checks run: `uv run pytest` (14/14 passed, up from 9 — 5 new tests: 4 in
  this entry plus the pre-existing count), `uv run ruff check .` (one
  import-sort/line-length finding, fixed via `ruff check --fix` and
  `ruff format`), `uv run ruff format --check .` (clean after the fix),
  `uv run pyright src` (0 errors).
- Remaining risk or uncertainty: this closes the coverage gap for these
  four specific paths, but does not add a general-purpose evidence
  verifier — `run_agent` still has no code-level check that a `COMPLETED`
  answer is supported, by design (see `reports/final-report.md`'s
  Unsupported-answer analysis and `reports/broken-loop-review.md` section
  7). The new test only proves the trace *permits* detection, not that
  detection happens automatically. `reports/ai-review.md`'s remaining
  open item — whether setting both `ANTHROPIC_API_KEY` and Bedrock
  credentials silently prefers the direct API — is still untouched.
