# Project 2 AI Review Rubric

The AI reviewer reports evidence-backed findings and questions. It does not
grant final approval.

## Schema and validation

- Are enums, optional fields, strictness, and extra-field behavior justified?
- Can wrong types or unknown fields pass silently?
- Are schema and business policy separated?
- Are refusal and missing parsed output handled explicitly?

## Policy integrity

- Are identifiers compared to the source request?
- Are requester contacts and evidence checked against source text?
- Are missing-information and follow-up rules consistent?
- Can quoted prompt injection become an accepted action?
- Are urgency rules explained and tested?

## Resilience

- Are only eligible provider failures retried?
- Are attempts bounded?
- Is the correlation identifier stable across attempts?
- Can partial or invalid records be published?
- Are timeout and unknown-outcome limitations documented?

## Engineering quality

- Can tests run without API credentials or live calls?
- Are provider SDK details isolated?
- Are logs sanitized?
- Do tests cover success, refusal, provider, schema, and policy outcomes?
- Are progress events useful and non-sensitive?

## Learner ownership

- Does the work log document rejected schema or retry proposals?
- Can the learner's report explain why each failure category matters?
- Are conclusions consistent with fixture and live evidence?

## Output format

1. Critical findings.
2. Important findings.
3. Questions for the learner.
4. Evidence supporting mentor review.
5. Claims that could not be verified.
