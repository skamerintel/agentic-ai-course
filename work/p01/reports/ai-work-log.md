# Project 1 AI Work Log

For each material interaction, record:

- Date and task.
- Coding agent used.
- Requirement or acceptance criteria supplied.
- Important proposal or generated change.
- Evidence reviewed.
- Accepted portions.
- Rejected or corrected portions and why.
- Checks run.
- Remaining uncertainty.

Do not paste full conversations unless a short excerpt is needed to explain a
decision.

## 2026-07-15 — Fix Bedrock adapter, drop OpenAI scope, run repetition experiment

- **Coding agent:** Claude Code (Sonnet 5).
- **Requirement:** `call_anthropic_messages` had a pyright error
  (`result.response`/`result.usage` called as methods); project scope had
  already been narrowed to Anthropic-only (no OpenAI credentials available)
  per `reports/experiment-contract.md`; then run the contract's required
  3x-repetition live experiment (8 incidents x 3 runs = 24 calls).
- **Proposed/generated changes:**
  1. `providers.py`: confirmed `response`/`usage` are properties on
     pydantic-ai's `AgentRunResult` (verified via
     `inspect.getsource`/`__dict__` inspection, not assumption), fixed the
     call sites. Added explicit `region_name="us-east-2"` via
     `BedrockProvider` after a live call failed with `NoRegionError` —
     `AWS_REGION` in `.zshrc` is not read by boto3 by default (only
     `AWS_DEFAULT_REGION` is).
  2. Removed `call_openai_responses`/`call_openai_chat`,
     `normalize_openai_responses`/`normalize_openai_chat`, their tests, CLI
     `responses`/`chat` choices, and `fixtures/openai_*.json` — dead code
     for a scope this project no longer supports. Updated
     `test_experiment.py`'s expected record count from 9 to 3.
  3. Ran the offline fixture pipeline and a live 24-call sweep (3 reps x 8
     incidents) via `model-api-lab live anthropic <id>`, writing results to
     `reports/live-raw/` (gitignored).
- **Evidence reviewed:**
  - Static: `inspect` on `AgentRunResult.response`/`.usage`
    (`property`), `ModelResponse.provider_response_id`,
    `RunUsage.input_tokens`/`output_tokens` field presence.
  - Live: one smoke call against real Bedrock before and after the region
    fix; full 24-call sweep; manually read the 3 summaries each for
    INC-005 and INC-008 (the two lowest fact_recall incidents) against
    their source reports.
- **Accepted:** all code changes above; region fix, OpenAI removal.
- **Rejected/corrected:** none required — the region-fix approach (explicit
  `region_name` matching the user-supplied working sample) was accepted
  as-is over alternatives (e.g. exporting `AWS_DEFAULT_REGION`) per user
  choice.
- **Checks run:** `ruff check .`, `ruff format --check .`, `pytest`,
  `pyright src` — all clean after each change. Live smoke test and full
  24-call sweep executed and inspected manually (not by the coding agent
  alone — user ran/confirmed the live commands per the workflow used).
- **Key finding surfaced by manual review:** avg fact_recall across the 24
  live runs was 0.842 (below the contract's 0.9 bar), but spot-checking
  INC-005/INC-008 by hand found every "missed" fact was actually present
  in the summary, just phrased differently than the fact-check's exact
  substring list (e.g. "no inventory records lost" vs. required "no
  inventory records were lost"; "expired service account secret" vs.
  required "expired secret"). This means the 0.842 number understates true
  recall and the automatic scorer's known lexical limitation (documented
  in the contract) has real, non-trivial impact on this dataset — not just
  a theoretical caveat.
- **Remaining uncertainty:** true semantic fact-recall is not yet measured
  (only a 2-of-8-incident manual spot check was done, not a full rubric
  pass across all 24 runs); whether the run-to-run variance seen in 4 of 8
  incidents at `temperature=0` is genuine model non-determinism or partly a
  scoring-boundary artifact is undetermined.
