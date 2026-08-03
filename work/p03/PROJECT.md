# Project 3: Operations Tool Agent

## Business brief

An internal operations analyst needs evidence-backed answers about current
service health, managed assets, and historical incidents. Build a read-only
tool-using agent without LangGraph or another orchestration framework.

The application must own tool execution, validation, correlation, limits,
tracing, and stopping. The model may select tools and compose a final answer; it
must never execute tools directly.

## Available tools

- `get_service_status`: current state for one named service.
- `search_incidents`: bounded historical incidents for one service.
- `get_asset`: one managed asset by identifier.

All tools are read-only and use deterministic local data for offline work.

## Required behavior

- Validate every tool call against a strict Pydantic argument model.
- Reject unknown tools and malformed argument JSON without crashing.
- Return bounded, structured tool results with the original `call_id`.
- Distinguish success, not found, invalid arguments, retryable error, terminal
  error, and unknown tool.
- Support multiple tool calls in one model turn.
- Preserve a complete trace.
- Enforce maximum iterations, total tool calls, and repeated-call limits.
- Stop explicitly rather than loop indefinitely.
- Return insufficient evidence when tools cannot support an answer.

## Repository assets

- `data/`: service, asset, incident, and failure-plan fixtures.
- `fixtures/scenarios.json`: scripted model turns and expected outcomes.
- `starter/`: incomplete learner workspace.
- `rubrics/`: AI and mentor review criteria.
- `templates/`: tool catalog, state diagram, final report, and work log.
- `broken-agent-loop-review.md`: failure-analysis input.

## Setup

```bash
python coursectl.py start p03 work/p03
cd work/p03
uv sync
uv run pytest
```

The starter provides data loading and scripted model infrastructure. The learner
completes tool registration, execution, loop control, and the live OpenAI
session.

## Required workflow

### 1. Approve the tool catalog

Complete `reports/tool-catalog.md` before implementing handlers. Explain why
service status and incident search are separate and why no write tools exist.

### 2. Draw the state machine

Complete `reports/state-diagram.md`. Include model request, tool validation,
dispatch, result return, final answer, and every stop limit.

### 3. Implement and test tools independently

Do not begin with the agent loop. Prove tool schemas, handlers, error categories,
result bounds, and duplicate-incident behavior without a model.

### 4. Implement the scripted loop

Use `fixtures/scenarios.json` to demonstrate:

- Sequential and parallel tool calls.
- Invalid arguments followed by correction.
- Retryable tool error followed by model-directed retry.
- Terminal error.
- Not found.
- Repeated-call limit.
- Iteration limit.

### 5. Implement the live OpenAI session

Required environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
```

Use Responses function calls and return each tool result as a
`function_call_output` with the matching `call_id`. Use `previous_response_id`
for continuation. Live calls are excluded from default tests.

### 6. Analyze traces

Every scenario must produce a JSON trace. The final report should identify why
the loop stopped and whether the final answer was supported by tool evidence.

## Commands

```bash
uv run operations-agent offline --output reports/offline-results.jsonl
uv run operations-agent scenario S01
uv run operations-agent live "Is checkout healthy? Include recent incidents."
```

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
```

## Definition of done

- Tools pass independent deterministic tests.
- Scripted scenarios cover every required stop and error path.
- All call IDs remain correlated.
- Limits are enforced by code, not prompts.
- The live OpenAI session has been demonstrated and sanitized.
- No framework owns the loop.
- AI and mentor reviews are complete.
- The learner can narrate selected traces without running the code.

## Comprehension gate

The mentor selects one scenario trace and one unseen model turn. The learner
must predict validation, tool execution, next input, and stop behavior. The gate
fails if the learner cannot explain generated loop code or if unsupported final
answers are accepted as successful evidence.
