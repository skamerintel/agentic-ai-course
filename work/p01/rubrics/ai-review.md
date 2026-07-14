# Project 1 AI Review Rubric

The AI reviewer reports findings and questions. It does not assign final pass or
fail status.

## Review instructions

Inspect code, tests, reports, Git diff, and AI work log. Cite a path and line or
artifact for every finding. Separate confirmed defects from questions.

## Criteria

### Experiment integrity

- Is the task contract fixed before conclusions?
- Are provider comparisons run on the same eligible dataset?
- Are configuration differences disclosed?
- Are repeated trials or nondeterminism limitations addressed?
- Are conclusions narrower than or equal to the evidence?

### API correctness

- Are Responses output items handled by type rather than fixed index?
- Is Chat Completions content handled safely?
- Are Anthropic content blocks handled by type?
- Are missing text, usage, identifiers, and errors explicit?
- Can offline tests run without provider packages or keys?

### Evaluation quality

- Are automatic checks described as incomplete signals?
- Does human review inspect unsupported claims and certainty?
- Are reference-summary defects acknowledged?
- Are examples and failure categories included?

### Engineering quality

- Are secrets absent from source, logs, fixtures, and Git history?
- Are timeouts configured for live calls?
- Are provider details isolated behind a narrow boundary?
- Do tests exercise behavior rather than mocks of the unit under test?
- Are logs and result records reproducible and sanitized?

### Learner ownership

- Does the AI work log contain meaningful corrections or rejected proposals?
- Can the report explain tradeoffs without relying on provider marketing?
- Are generated code and conclusions understandable from repository artifacts?

## Output format

1. Critical findings.
2. Important findings.
3. Questions for the learner.
4. Evidence that supports readiness for mentor review.
5. Claims that could not be verified.
