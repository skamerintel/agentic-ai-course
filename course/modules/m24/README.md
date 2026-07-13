# M24: Prototype-to-Production Review

## Learning objectives

By the end of this module, you can:

- Identify trust boundaries and release blockers.
- Assess prompt injection, excessive agency, and output validation risks.
- Review secrets, retention, tenant isolation, dependency, and deployment gaps.
- Separate required hardening from future scaling work.
- Produce a prioritized roadmap under budget constraints.
- Avoid calling a tested container automatically production-ready.

## Prerequisite diagnostic

Project 7 has tests, typed tools, a wheel, and a Docker image. List at least ten
questions that still need answers before operating it for multiple teams with
real GitHub write access.

## Required reading

- [OWASP LLM application references](../../../docs/reference-catalog.md#ref-owasp-llm)
- [GitHub REST references](../../../docs/reference-catalog.md#ref-github-rest)
- [Docker references](../../../docs/reference-catalog.md#ref-docker)

## Concept lesson

### Production readiness is contextual

A prototype can be well engineered and still lack authentication, tenant
isolation, managed secrets, migrations, backup, monitoring, incident response,
availability targets, or a scaling plan. State the intended operating context
before scoring readiness.

### Draw trust boundaries

Project 7 crosses MCP clients, model-controlled arguments, GitHub text, webhook
HTTP, approval administration, durable state, GitHub writes, package supply
chain, and container runtime. Validate and authorize at each boundary.

### Prompt injection is not solved by a system prompt

GitHub content remains untrusted. Restrict tools and permissions, preserve
source evidence, require approval, constrain outputs, and prevent content from
granting new authority.

### Excessive agency is architectural

A broad token plus arbitrary API tool plus model-accessible approval creates
danger even if individual schemas validate. Reduce capability and privilege
before adding prompt warnings.

### Prioritize findings

- Release blocker: unsafe or unreliable for the stated context.
- Near-term hardening: needed before wider use.
- Future scaling: important only after demand or reliability targets justify it.

Tie every recommendation to impact, likelihood, effort, and evidence.

## Guided lab

Apply the Project 7 readiness scorecard. Produce a trust-boundary sketch and
classify findings into blockers, near-term hardening, and future scaling.

## Independent challenge

Given a fictional two-engineer, six-week budget, select the highest-value
hardening work and explicitly defer lower-value improvements.

## Failure-analysis exercise

Challenge an AI-generated review declaring the service production-ready because
tests pass, schemas are typed, and the image runs. Identify missing operational
and security evidence.

## Comprehension gate

The learner presents the readiness scorecard and defends priorities under a
changed budget or operating context. Honest limitations are required to pass.

## Required GitHub evidence

- Trust-boundary and threat sketch.
- Production-readiness scorecard.
- Prioritized hardening roadmap.
- Explicitly accepted risks and deferred work.
