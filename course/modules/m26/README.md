# M26: Capstone Implementation and Evaluation

## Learning objectives

By the end of this module, you can:

- Deliver an agent system as reviewable, risk-driven vertical slices.
- Evaluate model behavior and deterministic workflow behavior separately.
- Demonstrate durable state, approval, replay, and recovery under failure.
- Improve measured behavior without contaminating the holdout.
- Package and containerize the customer-facing product from a development repo.
- Explain and correct coding-agent output at every critical boundary.

## Entry condition

Do not begin implementation until G9A is approved. The proposal is a controlled
baseline: changes are allowed, but material scope, authority, or evaluation
changes require an architecture-decision update and mentor review.

## Required reading

Revisit the references selected in the proposal, especially:

- [OpenAI Responses, structured outputs, and evals](../../../docs/reference-catalog.md#model-apis-and-application-behavior)
- [FastAPI and integration testing](../../../docs/reference-catalog.md#backend-and-persistence)
- [LangGraph durable workflows](../../../docs/reference-catalog.md#agent-orchestration-and-mcp)
- [GitHub integration](../../../docs/reference-catalog.md#github-integration)
- [Packaging and containers](../../../docs/reference-catalog.md#packaging-and-containers)

## Delivery protocol

### Milestone 1: walking skeleton

Ship one end-to-end fixture-backed case through FastAPI, LangGraph, the provider
boundary, validated output, PostgreSQL state, and a result endpoint. It may be
ugly; it must be observable and testable.

Evidence: sequence trace, one integration test, one evaluation record, and an
architecture-drift note.

### Milestone 2: evidence and failure boundaries

Implement bounded GitHub and second-API adapters, explicit timeouts and error
classification, source citations, redacted correlated logs, and deterministic
policy validation. Add contract tests and failure fixtures before broadening
features.

Evidence: adapter contracts, trust-boundary tests, failure taxonomy, and a
demonstration that untrusted external text cannot grant authority.

### Milestone 3: durability and approval

Add checkpointing, restart behavior, idempotency, human interruption, approval
outside the model-callable surface, and guarded side effects. Redis may carry
progress, coordination, or bounded cache data, but PostgreSQL remains the
durable source of truth unless the proposal defends another design.

Evidence: crash/restart, duplicate delivery, stale approval, and uncertain-write
recovery demonstrations.

### Milestone 4: evaluation and two iterations

Freeze dataset versions and baseline predictions. Diagnose errors by slice,
choose the smallest plausible intervention, and rerun the full development set.
Repeat for a second measured iteration. Do not inspect the mentor holdout.

Record quality, reliability, cost, latency, and regression tradeoffs. A failed
iteration is acceptable evidence when the diagnosis and decision are sound.

### Milestone 5: delivery and red team

Build wheel and source distribution with uv and Hatchling. Install the wheel in
a clean environment. Build the Docker stack, run the external smoke test, and
perform a formal red-team review covering prompt injection, excessive agency,
secrets, retention, tenant boundaries, dependency risk, and operational gaps.

The customer-facing package must not depend on development reports, fixture
paths, local source imports, or repository-only state.

## Coding-agent operating rule

Delegating code is allowed. For each high-risk change, the learner must:

1. state the contract and failure cases before prompting;
2. inspect the patch rather than only the summary;
3. run focused tests, then broader tests;
4. explain selected code without the coding agent;
5. record at least one correction or justified rejection.

The mentor may select any model boundary, state transition, authorization check,
or recovery path for oral explanation and modification.

## Evaluation rules

- Keep development, regression, and mentor holdout data separate.
- Version prompts, schemas, model configuration, datasets, and evaluator code.
- Prefer deterministic checks for contracts, evidence IDs, permissions, and
  state transitions.
- Use model-based grading only for dimensions that require judgment, with a
  calibrated human-reviewed sample.
- Report denominators, uncertainty, missing data, and known blind spots.
- Never tune against the final mentor holdout.

## Formal failure review

At one milestone, stop feature work. The learner and mentor choose at least
three adversarial or operational scenarios, including one consequential-action
case and one restart/replay case. Findings become prioritized issues with an
explicit release decision.

## Comprehension gate: G9B implementation

Passing requires:

- clean automated checks and a clean-install package test;
- a fixture-backed full workflow and documented live-API path;
- success, external failure, validation failure, and recovery demonstrations;
- durable, out-of-band approval before consequential writes;
- baseline plus two measured iterations and an untouched mentor holdout;
- AI and mentor review findings resolved or rejected with evidence;
- an honest prototype-to-production assessment.

## Required GitHub evidence

- Small reviewable pull requests or clearly separated commits.
- Tests and evals added with the behavior they protect.
- Versioned evaluation runs and failure ledger.
- AI work log and review-resolution log.
- Package inventory, clean-install proof, Docker smoke evidence.
- Red-team report and production-readiness assessment.
