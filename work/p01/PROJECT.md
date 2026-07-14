# Project 1: Model API Behavior Lab

## Business brief

A SaaS operations team receives incident reports from support engineers. The
reports contain critical facts mixed with speculation, irrelevant detail, and
status updates. Leadership wants short internal summaries but does not want a
provider recommendation based on one impressive demo.

Your task is to build a reproducible experiment that compares:

- OpenAI Responses API.
- OpenAI Chat Completions API.
- Anthropic Messages API.

The result is an evidence-backed recommendation for this narrow summarization
task, not a universal ranking of providers or models.

## Business requirements

Each summary should:

- Identify the affected system or workflow.
- Preserve critical impact and scope.
- Preserve known cause and mitigation when supplied.
- Avoid adding causes, impact, or resolution not present in the report.
- Distinguish confirmed information from uncertainty.
- Remain concise enough for an internal incident digest.

## Learning goals

- Work directly with three API surfaces before using a framework.
- Preserve raw provider semantics while exposing a useful common result.
- Run controlled experiments rather than compare anecdotes.
- Separate automatic checks from human judgment.
- Review and correct AI-generated code and conclusions.

## Repository assets

- `data/incidents.jsonl`: supplied incident and reference data.
- `fixtures/`: offline provider responses for implementation and tests.
- `starter/`: incomplete learner workspace.
- `rubrics/`: AI and mentor review criteria.
- `templates/`: required report and work-log formats.
- `flawed-comparison-report.md`: failure-analysis input.

## Setup

Materialize a learner workspace from the repository root:

```bash
python coursectl.py start p01 work/p01
cd work/p01
uv sync
uv run pytest
```

The initial test failures identify incomplete normalization, scoring, and live
provider code. Do not ask a coding agent to fix everything immediately. Map the
failures to requirements first.

## Required workflow

### 1. Write the experiment contract

Complete `reports/experiment-contract.md` before implementing live adapters.
Define:

- Task and audience.
- Fixed instructions.
- Dataset and exclusions.
- Automatic and human metrics.
- Repetition policy.
- Configuration held constant.
- Limitations.

### 2. Complete offline normalization

Use fixtures to implement and test extraction from:

- Typed Responses output items.
- Chat Completions message content.
- Anthropic content blocks.

Offline fixtures verify deterministic parsing. They do not establish live model
quality.

### 3. Complete automatic scoring

The supplied fact checks provide a coarse factual-recall signal. They are not a
complete judge. Add human review for:

- Unsupported claims not represented in the simple deny list.
- Misleading emphasis.
- Incorrect certainty.
- Clarity and usefulness.

### 4. Implement live adapters

Required environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
ANTHROPIC_API_KEY
ANTHROPIC_MODEL
```

Never commit keys or raw private responses. Provider packages are imported only
inside live adapter methods so offline tests remain runnable.

### 5. Run the experiment

Begin with the offline fixtures:

```bash
uv run model-api-lab offline --output reports/offline-results.jsonl
```

Then run live providers using the fixed contract. Start with one incident and
inspect the raw and normalized results before running the full dataset.

### 6. Analyze and report

Use `templates/experiment-report.md`. Include:

- Dataset coverage.
- Exact configurations and timestamps.
- Automatic results.
- Human-review method.
- Failure examples.
- Latency and usage observations.
- Variability and reference-data limitations.
- Narrow recommendation or “insufficient evidence.”

### 7. Correct the flawed report

Review `flawed-comparison-report.md`. Create a corrected version that separates
observations, inferences, and unsupported claims.

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
```

Live model calls must not run as part of the default automated test suite.

## Definition of done

- Offline tests pass.
- Live calls have been demonstrated for all three API surfaces.
- Secrets and private payloads are absent from Git history.
- Experiment contract predates the final comparison.
- Results include repeated runs or explicitly justify why a result is
  deterministic.
- The final report does not overstate its conclusion.
- AI and mentor reviews are complete.
- The learner can trace every adapter without assistance.

## Comprehension gate

The mentor selects:

- One raw fixture to normalize by hand.
- One provider adapter to explain line by line.
- One experiment conclusion to defend.
- One failed or ambiguous example to classify.

The project fails the gate if the learner cannot explain generated code or if
the recommendation is stronger than the evidence.
