# Project 2 Mentor Review Rubric

Score each category from 0 to 3.

- 0: Missing or fundamentally incorrect.
- 1: Partial or not explainable by the learner.
- 2: Meets the expected standard.
- 3: Strong judgment and evidence beyond the minimum.

## Categories

1. Schema design and optionality decisions.
2. Strict Pydantic validation and extra-field handling.
3. Separation of schema and business policy.
4. Source evidence and prompt-injection handling.
5. Failure taxonomy.
6. Retry and timeout policy.
7. Provider-boundary design.
8. Offline tests and deterministic fixtures.
9. Logging, correlation, and progress events.
10. AI-generated code review and technical defense.

## Critical failure conditions

- A committed credential or private raw payload.
- Default tests require live model calls.
- Invalid or policy-rejected records are emitted as success.
- Refusal or schema errors are retried unchanged.
- Retry attempts are unbounded.
- The learner cannot explain selected Pydantic or retry code.

## Passing guidance

- Minimum total: 20 out of 30.
- No category may score 0.
- Categories 1, 2, 3, 5, 6, and 10 must score at least 2.
- Critical failure conditions override the numeric score.

## Defense prompts

- Classify this unseen output as schema or policy failure.
- Explain one field you deliberately kept optional.
- Show why a particular provider failure is retryable.
- Trace one correlation identifier across three attempts.
- Demonstrate that quoted prompt injection was not accepted as an action.
- Show an AI proposal you rejected.
