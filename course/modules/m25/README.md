# M25: Capstone Discovery and Architecture

## Learning objectives

By the end of this module, you can:

- Turn an ambiguous workflow problem into measurable user and system outcomes.
- Decide where model reasoning is justified and where deterministic code is safer.
- Define API, data, state, approval, and trust boundaries before implementation.
- Design ground truth and holdout evaluation before seeing system outputs.
- Choose a capstone scope that is substantial but finishable to portfolio quality.
- Defend architecture decisions without hiding behind framework terminology.

## Prerequisite diagnostic

Choose one candidate capstone domain and answer, without proposing features:

1. Who performs the workflow today?
2. What costly decision or handoff should improve?
3. What evidence establishes a correct result?
4. Which external action would require human approval?
5. What would make an LLM unnecessary?

If those answers are vague, remain in discovery.

## Required reading

- [OpenAI Responses and structured outputs](../../../docs/reference-catalog.md#ref-openai-responses)
- [OpenAI evaluation guidance](../../../docs/reference-catalog.md#ref-openai-evals)
- [LangGraph state and durable execution](../../../docs/reference-catalog.md#ref-langgraph-state)
- [GitHub REST integration](../../../docs/reference-catalog.md#ref-github-rest)
- [OWASP LLM application risks](../../../docs/reference-catalog.md#ref-owasp-llm)

OpenAI references in this module were rechecked on **2026-07-13**. Keep model
identifiers configurable and verify current API behavior before implementation.

## Concept lesson

### Start with a decision, not an agent

A useful capstone changes a bounded workflow: it shortens investigation time,
improves evidence coverage, reduces unsafe handoffs, or makes a decision more
consistent. “Build an agent that can use several tools” is an implementation
idea, not a business outcome.

Write the current workflow and proposed workflow as observable steps. Mark the
person responsible, required evidence, input contract, output contract, failure
behavior, and whether each step is deterministic, model-assisted, tool-driven,
or human-controlled.

### Justify every model-assisted step

Use a model for tasks such as interpreting messy text, reconciling conflicting
evidence, or drafting bounded recommendations. Prefer deterministic code for
permissions, identifiers, totals, policy rules, state transitions, retries,
deduplication, and final authorization.

For every model step, state:

- why ordinary code is insufficient;
- the evidence supplied to the model;
- the validated output contract;
- how unsupported claims are detected;
- the fallback when the model fails.

### Architecture is a set of owned boundaries

The capstone uses OpenAI through a provider interface and the Responses API,
LangGraph for a justified durable workflow, GitHub plus another business API,
FastAPI, PostgreSQL, and Redis only where its transient semantics help. FastMCP
is optional and must serve a real interoperability need.

Do not draw these as decorative boxes. For each boundary record authority,
timeouts, retries, rate limits, validation, persistence, idempotency, logging,
test doubles, and expected failure classes.

### Design evaluation before implementation

Define the unit of evaluation, labeling policy, development set, untouched
holdout, metrics, failure slices, and baseline before generating predictions.
The evaluation must measure the workflow outcome and evidence quality, not only
whether output resembles a reference sentence.

At least two measured improvement iterations are required. Preserve the
baseline and failed experiments so the final report shows engineering judgment,
not just the best result.

### Scope by vertical slices

The first implementation milestone should prove one complete path with fixture
APIs, durable state, one model boundary, validation, and one evaluation case.
Do not build every adapter or frontend before proving the workflow.

Good non-goals are explicit: unsupported repositories, automatic writes,
multi-tenant operation, broad web search, autonomous policy changes, or a rich
frontend. A smaller system with strong evidence is more credible than a broad
demo with unclear behavior.

## Guided lab: compare proposals

Review `fixtures/weak-proposal.json` and the mentor-provided exemplar only after
your first critique. For each proposal:

1. Identify the business decision and measurable outcome.
2. Mark unjustified model or framework use.
3. Find authority that is accidentally model-controlled.
4. Test whether the proposed ground truth could prove improvement.
5. Remove at least two features without weakening the outcome.
6. State the smallest end-to-end vertical slice.

Run the proposal validator, but do not substitute its checklist for judgment.

## Independent challenge

Complete the Project 8 proposal, architecture, risk register, evaluation plan,
and milestone plan. Create an initial issue backlog with acceptance evidence for
each issue. Submit the proposal gate as a pull request before product code.

## Failure-analysis exercise

Ask a coding agent to critique the proposal. Classify each finding as correct,
incorrect, unsupported, or useful but out of scope. Record what evidence you
checked and revise only findings you can defend.

Then remove the most technically impressive feature that does not improve the
business outcome or evaluation evidence.

## Comprehension gate: G9A proposal

The learner must defend:

- user, workflow, outcome, success metrics, and non-goals;
- deterministic, model, tool, and human responsibilities;
- provider, graph, API, state, approval, and trust boundaries;
- ground truth, leakage controls, metrics, slices, and baseline;
- a risk-driven test plan and reviewable milestone sequence;
- why the project can reach portfolio quality within its chosen scope.

The mentor changes one constraint during the defense. Passing requires a
reasoned architecture or scope adjustment, not attachment to the original plan.

## Required GitHub evidence

- Approved project brief and architecture decision record.
- Architecture and workflow diagrams.
- Evaluation plan and labeling policy.
- Risk register and trust-boundary sketch.
- Milestone plan and initial issue backlog.
- AI critique log with accepted and rejected findings.
