# M20: MCP Concepts and FastMCP Implementation

## Learning objectives

By the end of this module, you can:

- Explain MCP client, server, tool, resource, prompt, and transport roles.
- Design a small, typed capability surface around a business API.
- Distinguish tools from resources and read operations from writes.
- Test a FastMCP server deterministically without a model.
- Choose in-memory, stdio, or HTTP transport deliberately.
- Reject broad or ambiguous AI-generated tool catalogs.

## Prerequisite diagnostic

Given a GitHub integration, classify each capability as a tool, resource, or
out-of-band administrative action:

1. List open pull requests.
2. Read repository operating policy.
3. Propose an issue comment.
4. Approve a consequential write.
5. Execute an approved comment.

Explain why exposing approval as a model-callable tool weakens the safety gate.

## Required reading

- [FastMCP concepts and client references](../../../docs/reference-catalog.md#ref-fastmcp)
- [FastMCP testing and deployment references](../../../docs/reference-catalog.md#ref-fastmcp-operations)

## Concept lesson

### MCP standardizes capability discovery and invocation

An MCP server publishes named tools, resources, and optional prompts. A client
discovers those capabilities and invokes them using the protocol. A model may
sit above the client, but deterministic applications and tests can use the same
client directly.

### Tool names and schemas are part of the product contract

Prefer narrow names such as `list_open_pull_requests` over vague tools such as
`github_action`. Inputs need bounded strings, identifiers, and result limits.
Outputs should be structured and small enough for clients to inspect.

### Resources are read-oriented context

Project 7 exposes repository capability policy as a resource. Reading policy is
different from executing an operation. Do not turn every static or queryable
document into a side-effecting tool.

### Keep approval outside model authority

The server can expose `propose_issue_comment` and
`execute_approved_comment`. A human approves the proposal through an
administrative command that is not listed as an MCP tool. The model cannot
satisfy its own approval requirement.

### Test the server without a model

Use the FastMCP client with an in-memory transport to list capabilities, call
tools, read resources, and inspect structured results. Network transport tests
are a separate, smaller layer.

### Transport follows the deployment boundary

- In-memory: deterministic tests and embedded clients.
- Stdio: local process integration and desktop tools.
- HTTP: centralized multi-client service with network security concerns.

Transport does not change tool authorization requirements.

## Guided lab

Connect a FastMCP client to a supplied in-memory server. List its tools and
resources, call one bounded read tool, and add one typed resource template.

## Independent challenge

Design Project 7's capability catalog before implementation. For every tool,
record its user, side effects, input bounds, output contract, permissions, and
approval requirements.

## Failure-analysis exercise

Refactor an AI-generated server with one `github` tool accepting arbitrary
method, URL, headers, and JSON. Replace it with the minimum typed capabilities
required by the business scenario.

## Comprehension gate

The learner explains the MCP lifecycle, calls every capability without a model,
and defends why approval is not exposed as a tool. The mentor proposes one new
capability and asks whether it belongs in this server.

## Required GitHub evidence

- Tool and resource catalog.
- Transport decision.
- In-memory client tests.
- Rejected broad-tool review.
