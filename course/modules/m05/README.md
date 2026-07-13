# M05: OpenAI Responses API and Chat Completions Literacy

## Learning objectives

By the end of this module, you can:

- Make a direct OpenAI Responses API call.
- Read and maintain a Chat Completions integration.
- Explain the important differences in request and response handling.
- Avoid assuming every Responses output item is user-facing text.
- Isolate provider-specific details behind a narrow application boundary.

## Prerequisite diagnostic

Inspect one Responses example and one Chat Completions example in the official
documentation. List differences in:

- Input representation.
- Instructions or system context.
- Output extraction.
- Conversation continuation.
- Tool-call representation.

Do not write code yet.

## Required reading

- [Responses references](../../../docs/reference-catalog.md#ref-openai-responses)
- [Chat Completions reference](../../../docs/reference-catalog.md#ref-openai-chat)

## Concept lesson

### Learn the raw API before the framework

Frameworks normalize provider behavior, but production debugging eventually
reaches raw requests, response items, usage, errors, and identifiers. Direct API
literacy makes abstractions easier to evaluate.

### Responses output is a sequence of typed items

Do not assume the first item is always a text message. A response may include
message content, reasoning-related items, function calls, or other typed output.
Use the SDK's convenience text accessor only when the application truly expects
text, and preserve raw metadata for diagnosis.

### Chat Completions remains important literacy

Existing systems and OpenAI-compatible providers frequently expose a
message-list interface. The course uses Responses as the primary OpenAI surface
while teaching Chat Completions well enough to maintain and migrate existing
code.

### Normalize application results, not provider reality

A narrow result object may expose text, model, usage, latency, provider, and raw
identifiers. Do not flatten away tool calls, refusals, finish state, or errors
that the application needs.

## Guided lab

In Project 1:

1. Load one incident.
2. Run it through the offline Responses fixture.
3. Inspect every raw output item.
4. Produce the normalized experiment result.
5. Repeat with the Chat Completions fixture.
6. Compare which provider details are retained.

After offline behavior passes, configure a model through environment variables
and make one live call to each OpenAI API surface.

## Independent challenge

Implement or repair the Project 1 OpenAI adapters. Requirements:

- No API key in source or logs.
- Model identifier supplied by environment or command line.
- Timeout configured.
- Raw response ID retained.
- Usage retained when available.
- Missing text handled explicitly.
- Provider imports do not prevent offline tests from running.

## Failure-analysis exercise

Review code that reads `response.output[0].content[0].text` without checking item
types. Describe at least three ways the assumption can fail and implement a
safer extraction policy.

## Comprehension gate

Trace one Responses and one Chat Completions call from application input to
normalized result. Explain:

- What is provider-specific.
- What is application-specific.
- Which metadata is preserved.
- How missing or non-text output is handled.
- What a migration test must protect.

## Interview questions

1. Why use Responses for new OpenAI application work?
2. Why must an engineer still understand Chat Completions?
3. What can be lost in an overly generic provider abstraction?
4. How would you test a migration between API surfaces?

## Required GitHub evidence

- OpenAI adapter code and offline tests.
- One sanitized live-call transcript per API surface.
- API comparison note.
- Failure-analysis correction.
