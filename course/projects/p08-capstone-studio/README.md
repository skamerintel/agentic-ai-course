# Project 8: Capstone Studio

## Purpose

Project 8 is the course capstone process, not a pre-solved application. You will
select a realistic workflow domain, defend the proposal, build the system, prove
its behavior, and convert the repository into credible hiring evidence.

The supplied studio provides candidate briefs, strict proposal and artifact
contracts, milestone gates, rubrics, templates, validator tooling, private
mentor challenges, and a gated exemplar. It intentionally does not provide a
complete capstone product implementation.

## Candidate domains

Start with `candidate-briefs.md` and `data/capstone-options.json`:

- Support escalation investigation across tickets, GitHub, and a status API.
- Engineering incident evidence collection and follow-up coordination.
- Dependency-upgrade investigation and approval.
- Compliance evidence gathering from repositories and a business system.

A custom domain is allowed when it satisfies the same constraints. The
recommended default is support escalation investigation because it has a clear
business user, conflicting evidence, meaningful GitHub use, a second API, and
consequential follow-up actions without duplicating Project 7.

## Required product shape

The capstone must:

- solve a workflow problem and not be primarily a chatbot;
- use OpenAI via a provider boundary and the Responses API;
- use structured, validated model output and typed tool contracts;
- use LangGraph for justified durable, multi-step behavior;
- integrate GitHub and at least one additional external API;
- expose a FastAPI backend;
- persist durable workflow state in PostgreSQL;
- use Redis only for a justified transient concern;
- include FastMCP only if a real client or interoperability need exists;
- keep consequential approval outside the model-callable surface;
- include correlated, redacted logging;
- include realistic ground truth, holdout separation, failure slices, a
  baseline, and at least two measured iterations;
- include unit, integration, contract, and recovery-oriented tests;
- build a clean uv/Hatchling wheel and source distribution;
- run through Docker Compose with an external smoke test;
- document security, privacy, cost, latency, and production gaps.

## Start the studio

```bash
python coursectl.py start p08 work/p08
cd work/p08
uv sync
uv run pytest
```

The `start` command prints these next steps and creates `START_HERE.md` with the
expected baseline and first proposal task.

The starter tests that exercise proposal and artifact validation fail until the
two validator functions are implemented. The studio package is development
tooling; your selected capstone product should live in its own repository or a
clearly separated product directory with its own package and Docker stack.

## Gate 1: discovery and proposal

1. Compare candidate domains with the selection matrix.
2. Interview the mentor as the simulated stakeholder.
3. Complete the project brief, workflow map, architecture decision, evaluation
   plan, risk register, and milestone plan.
4. Encode the approved design as `proposal.json` using the Pydantic contract.
5. Implement `validate_proposal` and run:

```bash
uv run capstone-studio validate-proposal proposal.json
```

6. Open a proposal-only pull request and pass the M25 defense.

## Gate 2: implementation milestones

Deliver five reviewable milestones:

1. Fixture-backed walking skeleton.
2. Evidence, API, and failure boundaries.
3. Durable state, approval, replay, and recovery.
4. Baseline plus two measured evaluation iterations.
5. Package, container, red-team, and production-readiness review.

Use `data/milestone-gates.json` as the minimum contract. Each milestone needs a
demo, automated evidence, AI review, learner resolution, and mentor decision.

## Gate 3: portfolio and defense

Complete every item in `data/required-artifacts.json`, encode the evidence in
`artifact-manifest.json`, implement `validate_artifact_manifest`, and run:

```bash
uv run capstone-studio validate-artifacts \
  artifact-manifest.json data/required-artifacts.json
```

Then perform the fixture-backed demo, private mentor scenario, code explanation,
changed-constraint exercise, and mock interview.

## Ground-truth rules

- Label synthetic data explicitly.
- Define the evaluation unit and policy before generating predictions.
- Keep development, regression, and mentor holdout sets separate.
- Do not inspect or tune against the mentor holdout.
- Version prompts, schemas, dataset fingerprints, model configuration, and
  evaluator code with each run.
- Report denominators and important slices, not only aggregate scores.
- Preserve baseline and failed iterations.

## Coding-agent rules

Claude Code, Codex, or a VS Code coding agent may implement large portions of
the system. You remain responsible for contracts, acceptance evidence, patch
review, tests, security boundaries, and oral explanation.

For every high-risk boundary, record one accepted, corrected, or rejected AI
suggestion. The mentor may select generated code for explanation or a small
change during the final defense.

## Definition of done

- G9A proposal, G9B implementation, and G9C final defense pass.
- Clean-clone setup, checks, package build, clean install, and Docker smoke work.
- A success path and at least two failure/recovery paths are demonstrated.
- Evaluation contains a baseline, two measured iterations, slices, and holdout.
- Consequential actions require durable out-of-band approval and are idempotent.
- AI and mentor findings are resolved or rejected with evidence.
- Portfolio claims are reproducible and production limitations are explicit.
