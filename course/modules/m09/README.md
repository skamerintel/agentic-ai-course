# M09: Tool Design and Function Calling

## Learning objectives

By the end of this module, you can:

- Decide when a model needs a tool instead of more prompt text.
- Design narrow read-only tools with typed, validated arguments.
- Write tool names and descriptions that distinguish similar capabilities.
- Separate tool selection from deterministic tool execution.
- Classify success, not-found, retryable, terminal, and invalid-argument results.
- Identify write operations that require explicit approval.

## Prerequisite diagnostic

For each proposed capability, decide whether it should be one tool, multiple
tools, or no model-selected tool:

1. Look up the current status of one named service.
2. Search historical incidents for a service.
3. Read and update every field on an asset record.
4. Add two numbers.
5. Restart a production service.

State what the model decides and what deterministic code decides.

## Required reading

- [OpenAI function-calling references](../../../docs/reference-catalog.md#ref-openai-structured)
- [OpenAI agent references](../../../docs/reference-catalog.md#ref-openai-agents)
- [Anthropic tool-use references](../../../docs/reference-catalog.md#ref-anthropic-tools)
- [OWASP agent-risk references](../../../docs/reference-catalog.md#ref-owasp-llm)

## Concept lesson

### A tool is a controlled application boundary

The model proposes a tool name and arguments. Application code validates the
proposal, executes deterministic code, and returns a bounded result. The model
does not receive arbitrary code execution or direct access to databases merely
because a function schema exists.

### Use tools for facts and actions outside the model

Tools are appropriate when the application needs:

- Current or private data.
- Deterministic calculations.
- External APIs or databases.
- Controlled side effects.
- A result that must be independently testable.

Do not create a tool for every local helper function. Tool surfaces are model
interfaces, not mirrors of the codebase.

### Narrow tools improve selection and authorization

Compare:

- `operations(query: str, action: str, payload: dict)`
- `get_service_status(service_name: str)`
- `search_incidents(service_name: str, limit: int)`
- `get_asset(asset_id: str)`

The narrower tools have clearer descriptions, schemas, permissions, tests, and
failure behavior. Broad tools invite ambiguous selection and excessive agency.

### Typed arguments remain untrusted

Model-generated JSON can be malformed, omit required fields, include unknown
fields, or use invalid values. Validate arguments before dispatch. Return a
structured error to the model when correction is possible; do not let a parsing
exception crash the loop.

### Errors are part of the tool contract

Useful result categories include:

- `success`: bounded data is available.
- `not_found`: the lookup completed but no matching data exists.
- `invalid_arguments`: the model can correct its call.
- `retryable_error`: a later identical call may succeed.
- `terminal_error`: repeating the call unchanged will not help.
- `unknown_tool`: the requested capability is unavailable.

The model may decide what to do next, but the application defines these
categories.

### Read and write tools deserve different treatment

Project 3 is read-only. For write tools, additionally consider:

- Authentication and authorization.
- Narrow permissions.
- Idempotency.
- Preview or dry-run output.
- Human approval.
- Audit records.
- Compensation or recovery.

## Guided lab

Inspect Project 3's service-status, incident-search, and asset tools.

For each tool, document:

- Decision it supports.
- Arguments and validation.
- Data source.
- Maximum result size.
- Error categories.
- Whether it reads or writes.
- Information intentionally excluded.

Then compare tool selection across supplied scenarios.

## Independent challenge

Review the supplied broad `operations_lookup` proposal and replace it with the
smallest useful tool set. Write strict argument models and result examples
before implementing handlers.

Ask a coding agent to critique ambiguity between `get_service_status` and
`search_incidents`. Revise descriptions only when the critique is supported by
scenario evidence.

## Failure-analysis exercise

Identify defects in a generated tool that:

- Accepts arbitrary SQL.
- Can read or delete records through one `action` argument.
- Returns unlimited rows.
- Treats missing records as an exception.
- Retries every error internally.
- Does not disclose side effects in its description.

## Comprehension gate

The learner must defend every Project 3 tool, then classify unseen results as
not-found, retryable, terminal, or invalid arguments. The learner must also
identify where an approval gate would be required if a read tool became a write
tool.

## Interview questions

1. What makes an LLM tool different from an ordinary Python function?
2. How do tool descriptions affect reliability?
3. Why should tool argument validation happen outside the model?
4. When should a tool error be returned to the model rather than retried by the
   application?

## Required GitHub evidence

- Tool catalog and decision record.
- Tool-schema tests.
- Selection scenario matrix.
- Review of the broad-tool anti-pattern.
- AI work-log entry documenting a tool-design correction.
