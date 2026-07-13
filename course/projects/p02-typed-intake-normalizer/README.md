# Project 2: Typed Intake Normalizer

## Business brief

An internal operations team receives service requests through email, forms, and
chat. The messages are inconsistent, incomplete, and sometimes contain quoted
or malicious instructions. Downstream workflows need a trustworthy typed record
without silently inventing requester details, systems, actions, or due dates.

Build a batch normalizer using OpenAI structured outputs and Pydantic. The
pipeline must classify every request as:

- Successful normalized record.
- Provider refusal.
- Retryable or terminal provider failure.
- Schema validation failure.
- Business-policy failure.

## Business requirements

The normalized record must capture:

- Source request identifier.
- Category and urgency.
- Known requester identity and contact information.
- Affected system when known.
- Requested action when known.
- Due date when unambiguous.
- Missing information and whether follow-up is required.
- Short evidence quotations from the source request.

The system must not:

- Invent identity, contact, system, action, or date information.
- Treat quoted prompt injection as application instructions.
- Retry refusal, schema, or policy failures unchanged.
- Publish partially validated records.
- Log full customer messages or credentials by default.

## Repository assets

- `data/requests.jsonl`: raw multi-channel service requests.
- `data/ground_truth.jsonl`: mentor-reviewed expected records.
- `fixtures/provider_sequences.json`: deterministic provider outcomes.
- `starter/`: incomplete learner workspace.
- `rubrics/`: AI and mentor review criteria.
- `templates/`: schema decision, failure taxonomy, and final report.
- `weak-schema-review.md`: failure-analysis input.

## Setup

From the course repository root:

```bash
python coursectl.py start p02 work/p02
cd work/p02
uv sync
uv run pytest
```

Initial failures identify incomplete schema hardening, policy checks, retry
behavior, and the live provider boundary.

## Required workflow

### 1. Approve the data contract

Complete `reports/schema-decision.md` before asking a coding agent to implement
the final schema. Document required fields, optional fields, enums, strictness,
extra-field behavior, and policy checks.

### 2. Write invalid examples first

Add examples for:

- Unknown urgency.
- Extra output field.
- Wrong JSON type.
- Unsupported evidence.
- Missing system without a missing-information marker.
- Follow-up mismatch.
- Ambiguous due date.

### 3. Complete the Pydantic boundary

Use strict JSON validation and reject unknown fields. Keep business comparison
to the source request in a separate policy function.

### 4. Complete deterministic resilience behavior

Use fixture sequences to demonstrate:

- Transient failure followed by success.
- Exhausted transient failures.
- Terminal provider failure.
- Refusal.
- Schema failure.
- Policy failure.
- Stable correlation ID across attempts.

### 5. Implement the live OpenAI adapter

Required environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
```

Use the Responses API structured parsing helper with the Pydantic output model.
Disable hidden SDK retries so the course retry policy remains observable. Do not
run live calls in the default test suite.

### 6. Run offline and live workflows

```bash
uv run intake-normalizer offline --output reports/offline-results.jsonl
uv run intake-normalizer live REQ-001 --output reports/live-result.json
```

Start with one live request. Inspect the parsed object, usage, identifiers, and
policy result before running additional examples.

### 7. Analyze failures

Complete the failure taxonomy and final report. Do not combine schema and policy
failures under a generic “model error.”

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
```

## Definition of done

- Pydantic and policy tests pass.
- Offline fixtures exercise every required outcome class.
- Retries are bounded and only retryable failures are repeated.
- Progress events preserve one correlation identifier.
- Live structured output has been demonstrated and sanitized.
- Ground truth is used for evaluation, never included in model input.
- AI and mentor reviews are complete.
- The learner can explain every schema and retry decision.

## Comprehension gate

The mentor supplies an unseen request and three candidate outputs. The learner
must identify:

- Which output fails schema validation.
- Which output passes schema but fails business policy.
- Which output is acceptable and what remains uncertain.

The learner must also trace a transient provider failure through retry and final
success without coding-agent assistance.
