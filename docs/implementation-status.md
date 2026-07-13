# Implementation Status

Updated: **2026-07-12**

## Complete

- Formal course specification.
- Curriculum roadmap and seven-project sequence.
- Official reference catalog.
- M00-M08 lesson materials.
- M01 generated Git conflict lab.
- M02 flawed-test exercise, mentor acceptance tests, and reference repair.
- M03 local HTTP failure simulator and tested reference async client.
- Project 1 business brief, eight-record incident dataset, offline provider
  fixtures, starter workspace, tests, rubrics, templates, and flawed report.
- Project 1 reference normalization, scoring, aggregation, and live provider
  adapters.
- Project 2 business dataset, mentor ground truth, deterministic provider
  sequences, starter workspace, tests, rubrics, and review templates.
- Project 2 reference strict Pydantic schema, source-aware policy validation,
  classified retry pipeline, progress events, and live OpenAI structured-output
  adapter.
- `coursectl.py` project materialization and configurable honor-system solution
  access for Projects 1 and 2.

## Verification completed

- Root `unittest` suite passes.
- Repository Python files pass Ruff lint and format checks.
- JSON, JSONL, and TOML assets parse successfully.
- Markdown local links resolve.
- M02 reference passes its learner and mentor acceptance tests plus Pyright.
- M03 reference passes success, transient-retry, invalid-request, and timeout
  tests against a local HTTP server.
- Project 1 reference passes Ruff, format checking, 10 pytest tests, Pyright, and
  the offline experiment command.
- Project 1 learner starter fails only at the intended normalization and scoring
  TODOs.
- Project 2 reference passes Ruff, format checking, 12 pytest tests, Pyright,
  strict OpenAI JSON Schema conversion, and the offline batch command.
- Project 2 learner starter fails only at the intended weak-schema checks and
  policy/pipeline TODOs.

## Deliberately not verified

- Live OpenAI and Anthropic requests require learner credentials and selected
  current model identifiers. They are a required learner gate, not part of the
  repository's default automated verification.
- GitHub pull-request and mentor-review workflows require the learner's remote
  repository and cannot be completed by repository tests.

## Next vertical slice

- M09: Tool design and function calling.
- M10: Build an agent loop without a framework.
- Project 3: Operations Tool Agent.
