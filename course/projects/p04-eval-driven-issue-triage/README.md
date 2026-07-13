# Project 4: Eval-Driven Issue Triage Engine

## Business brief

An engineering organization wants assistance triaging incoming GitHub issues.
The system recommends category, urgency, owning team, labels, duplicate
candidates, and missing-information questions. It does not write to GitHub.

Your primary deliverable is not a prompt. It is an evaluation-driven engineering
process that demonstrates what the system does well, where it fails, and why an
accepted change should generalize.

## Required decisions

For each issue, produce:

- Category.
- Urgency.
- Owning team.
- Recommended labels.
- Up to three duplicate candidates.
- Missing-information questions.
- Evidence identifiers or excerpts.

## Repository assets

- `data/issues-dev.jsonl`: visible development issues.
- `data/ground-truth-dev.jsonl`: adjudicated development labels.
- `data/annotator-labels.jsonl`: seed labels containing disagreement.
- `data/ownership-rules.json`: deterministic team ownership.
- `data/known-issues.jsonl`: historical candidate corpus.
- `data/retrieval-queries.jsonl`: retrieval-only benchmark.
- `fixtures/baseline-predictions.jsonl`: initial system output.
- `fixtures/improved-predictions.jsonl`: candidate improvement output.
- `rubrics/`: AI and mentor review criteria.
- `templates/`: labeling policy, failure ledger, experiment manifest, context
  decision, and final report.
- `leaky-experiment-report.md`: invalid improvement exercise.

The mentor holdout set is stored outside the learner workspace and is not copied
by `coursectl start`.

## Setup

```bash
python coursectl.py start p04 work/p04
cd work/p04
uv sync
uv run pytest
```

## Required workflow

### 1. Approve labels before tuning

Complete `reports/labeling-policy.md`. Review annotator disagreements and write
an adjudication note. Do not edit ground truth merely because a prediction looks
reasonable.

### 2. Run and interpret the baseline

```bash
uv run issue-triage evaluate \
  --predictions fixtures/baseline-predictions.jsonl \
  --output reports/baseline.json
```

Report category, urgency, owner, label-set, duplicate-ranking, and follow-up
metrics with sample counts and slices.

### 3. Build a failure ledger

Classify individual failures as labeling, ownership, retrieval, context,
generation, schema, or policy failures. Prioritize by simulated business impact.

### 4. Evaluate retrieval separately

```bash
uv run issue-triage retrieval --output reports/retrieval.json
```

Measure hit rate and reciprocal rank before using retrieved candidates in final
triage. Compare no context, full historical context, and bounded retrieval.

### 5. Run controlled experiments

Complete at least two experiments and one rejected experiment. Each manifest
must retain dataset fingerprints, one primary hypothesis, configuration, target
metric or slice, outcome, and regressions.

### 6. Request holdout evaluation

Only the mentor runs the holdout command after the learner freezes the candidate
system. Holdout examples and labels must not enter prompts, retrieval corpora, or
coding-agent context.

### 7. Demonstrate a live structured-output path

Use OpenAI Responses structured output for one or more development issues. The
default tests and evaluator must remain provider-independent and offline.

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
```

## Definition of done

- Labeling policy and adjudication are documented.
- Dataset fingerprints are recorded.
- Baseline and candidate use the same development examples and evaluator.
- Multiple metrics and meaningful slices are reported with counts.
- Retrieval quality is evaluated independently.
- Two controlled improvements and one rejection are documented.
- A mentor holdout report exists.
- Leakage and changed-dataset checks pass.
- AI and mentor reviews are complete.
- The learner can explain why accepted changes should generalize.

## Comprehension gate

The mentor selects one aggregate result, one slice regression, one retrieval
miss, and one ambiguous label. The learner must trace each from source example
through metric computation and defend the final experiment decision.
