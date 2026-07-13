# M06: Anthropic Messages API Comparison

## Learning objectives

By the end of this module, you can:

- Make a direct Anthropic Messages API call.
- Explain content blocks, system instructions, usage, and tool-use shape.
- Compare Anthropic and OpenAI on a controlled task.
- Decide which semantics should remain provider-specific.
- Make a narrow recommendation supported by measured evidence.

## Prerequisite diagnostic

Before implementing the adapter, identify from the official documentation:

- Where system instructions are supplied.
- How message content is represented.
- How text is extracted from content blocks.
- How usage is reported.
- How tool use differs from plain text output.

## Required reading

- [Messages API references](../../../docs/reference-catalog.md#ref-anthropic-messages)
- [Anthropic tool references](../../../docs/reference-catalog.md#ref-anthropic-tools)
- [Anthropic streaming reference](../../../docs/reference-catalog.md#ref-anthropic-streaming)

## Concept lesson

### A second API reveals hidden assumptions

Code that appears clean with one provider may depend on that provider's message,
tool, usage, or streaming semantics. Implementing one second API is enough to
expose those assumptions without forcing every course project to support every
provider.

### Content is structured

Treat message content as typed blocks rather than assuming one string. Extract
the block types your task supports and handle unsupported types explicitly.

### Provider-neutral does not mean lowest common denominator

Share application concepts such as task input, normalized text result, latency,
and evaluation records. Preserve provider-specific capabilities when they
affect behavior. An abstraction that hides important differences creates false
portability.

### Compare the system, not the brand

Use the fixed Project 1 dataset, task contract, and rubric. Record model and API
configuration. Report results for this task only. Do not turn a small course
benchmark into a claim about all workloads.

## Guided lab

In Project 1:

1. Parse the offline Anthropic fixture into the common experiment record.
2. Inspect all content blocks rather than selecting by index alone.
3. Retain provider usage and request identifiers when available.
4. Run the same incident through all three API adapters.
5. Compare normalized results and raw provider metadata.

## Independent challenge

Implement or repair the Anthropic adapter, then run the complete Project 1
experiment. The final report must include:

- Task-specific quality results.
- Unsupported-claim and omission counts.
- Format adherence.
- Latency and usage observations.
- Variability limitations.
- A provider recommendation or a justified “insufficient evidence” conclusion.

## Failure-analysis exercise

Review an abstraction that returns only `str` from every provider. List what is
lost. Redesign it to preserve the information needed by Project 1 without
exposing the entire SDK object to the rest of the application.

## Comprehension gate

The learner must:

- Trace a Messages request and response.
- Explain what the common result object preserves and omits.
- Present the controlled comparison.
- Correct at least two unsupported claims in the supplied flawed report.
- State what the experiment cannot conclude.

Passing this gate completes Project 1.

## Interview questions

1. What design problems appear when supporting multiple model providers?
2. What should a provider adapter normalize?
3. When is a provider-specific capability worth exposing?
4. How do you prevent a benchmark from overstating its conclusion?

## Required GitHub evidence

- Anthropic adapter and offline tests.
- Sanitized live-call evidence.
- Final experiment report.
- Corrected flawed report.
- Project 1 pull request, AI review, and mentor review.
