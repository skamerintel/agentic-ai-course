# M07: Structured Outputs and Pydantic Validation

## Learning objectives

By the end of this module, you can:

- Design a Pydantic model from business requirements rather than sample output.
- Explain the difference between structured generation and runtime validation.
- Use strict validation, forbidden extra fields, enums, field constraints, and
  cross-field checks deliberately.
- Separate schema errors from business-policy violations.
- Treat model output as untrusted even when the provider promises a schema.

## Prerequisite diagnostic

For each rule, decide whether it belongs primarily in a type, field constraint,
cross-field validator, or application policy:

1. Urgency must be one of four named values.
2. `source_id` must match the input request identifier.
3. An email address must not be invented.
4. `requested_action` cannot be blank.
5. A request with missing required information must require follow-up.

If every rule goes into one giant validator, revisit separation of concerns
before proceeding.

## Required reading

- [Pydantic references](../../../docs/reference-catalog.md#ref-pydantic)
- [OpenAI structured-output references](../../../docs/reference-catalog.md#ref-openai-structured)
- [Pydantic strict-mode reference](https://docs.pydantic.dev/latest/concepts/strict_mode/)

## Concept lesson

### A schema is an application contract

Start with what downstream code needs to know and reject. Do not begin with a
large JSON example and infer that every observed field is useful.

A good schema communicates:

- Allowed concepts through enums and discriminated types.
- Required versus genuinely optional information.
- Bounds and formats.
- Whether unknown fields are rejected.
- Which absence is acceptable and which requires follow-up.

### Structured output is not complete validation

Provider-constrained output can improve syntactic and schema adherence. Your
application must still handle:

- Refusal or missing parsed output.
- A provider or transport failure.
- A schema that is too permissive or incorrect.
- Semantically unsupported values that fit the schema.
- Cross-field contradictions.
- Business policy that changes independently of the transport schema.

### Pydantic and static typing solve different problems

Static checking reasons about annotated code before execution. Pydantic checks
runtime data. LLM output, JSON payloads, environment values, and external API
responses remain runtime inputs even when your Python code is fully typed.

### Strictness is a choice

Coercion can be convenient at human-facing boundaries, but it may hide model or
integration defects. Decide explicitly whether values such as `"3"`, `3`, and
`3.0` should be equivalent. In this project, structured model output is parsed
from JSON under strict validation so unexpected types fail visibly.

### Separate shape from policy

Pydantic should establish a valid record shape. A policy layer should compare
the record to source text and changing business rules. Examples:

- Evidence must appear in the original request.
- A critical urgency recommendation needs supporting language.
- Access requests need an affected system or a missing-information marker.
- Output identifiers must match the input record.

This separation makes failures easier to classify and policies easier to test.

## Guided lab

Open the Project 2 starter and inspect the supplied service requests before
editing the schema.

1. List downstream decisions the normalized record must support.
2. Identify truly optional fields.
3. Define enums for category, urgency, channel, and missing-information codes.
4. Reject unknown fields.
5. Add constraints for non-empty actions and bounded evidence.
6. Write invalid examples before adding validators.

Ask a coding agent to critique the schema for overuse of optional fields. Do not
let it rewrite the schema until you evaluate each finding.

## Independent challenge

Complete Project 2's output model and validation function. It must distinguish:

- Valid structured output.
- Pydantic schema failure.
- Business-policy failure.
- Provider refusal.
- Provider or transport failure.

Add at least three adversarial outputs that fit JSON syntax but should not be
accepted.

## Failure-analysis exercise

Review the supplied weak schema. It allows every field to be optional, accepts
unknown fields, coerces urgency from arbitrary values, and trusts evidence that
does not occur in the source request. Explain how each choice can create a
plausible but unsafe downstream record.

## Comprehension gate

The learner must defend:

- Every required field and enum value.
- Every optional field.
- Strictness and extra-field behavior.
- The boundary between Pydantic and application policy.
- One generated schema proposal that was rejected.

The mentor supplies an unseen output containing one shape defect and one policy
defect. The learner must classify both correctly.

## Interview questions

1. Why is valid JSON insufficient for a production LLM application?
2. When should Pydantic use strict validation?
3. What belongs in a model validator versus a service policy?
4. How do structured outputs change, but not eliminate, failure handling?

## Required GitHub evidence

- Schema decision record.
- Valid and invalid example matrix.
- Pydantic and policy tests.
- AI work-log entry documenting schema review.
- Project 2 pull-request checkpoint.
