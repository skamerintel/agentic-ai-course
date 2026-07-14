# Instructor Handbook

## Purpose

This handbook defines how a human mentor operates the self-paced LLM
application and agent engineering course. The curriculum, project brief,
project-specific rubric, and executable evidence remain authoritative. This
handbook supplies the common review process around them.

The mentor's job is not to provide the implementation. The mentor protects the
learning sequence, tests technical ownership, introduces realistic ambiguity,
controls private evaluation evidence, and makes the final gate decision.

## Operating principles

1. **Evidence before confidence.** Require a file, test, trace, metric, commit,
   or demonstration for material claims.
2. **Ownership before completion.** Working code does not pass when the learner
   cannot explain or safely modify it.
3. **Blocking conditions do not average away.** A high rubric total cannot
   compensate for leaked credentials, uncontrolled authority, holdout leakage,
   or an unexplained critical path.
4. **AI review is advisory.** The AI reviewer identifies concerns and asks
   questions. It cannot approve a gate.
5. **References are comparison material.** A learner implementation may differ
   and pass when its behavior and tradeoffs are well defended.
6. **Holdouts test generalization.** They are not examples to tune against.
7. **Prototype claims stay honest.** Tests, packaging, and Docker do not by
   themselves prove production readiness.

## Instructor setup

From a clean course checkout:

```bash
uv sync --only-group dev --frozen
uv run --no-sync python scripts/validate_course.py
python coursectl.py status
```

Keep `course.toml` in `gated` mode for normal learner operation:

```toml
[course]
solution_access = "gated"
```

Copy the progress template only when the first reference must be unlocked:

```bash
cp course/progress.example.toml .course-progress.toml
```

The gate and reference mechanism is an honor-system learning control, not a
security boundary. If the learner can read this entire repository, they can
also locate instructor assets. For truly blind assessment, keep
`course/instructor/evaluation/` in a private instructor checkout or separate
private repository and expose only the required input at evaluation time.

Never place real customer records, production credentials, private source code,
or sensitive interview material in course fixtures, model prompts, logs, or
mentor records.

## Roles and decision authority

### Learner

- Produces code, tests, evaluation evidence, reports, and Git history.
- Runs the project AI-review rubric and responds to findings.
- Leads demonstrations and technical explanations.
- Identifies coding-agent contributions, corrections, and rejected proposals.
- Requests gate review only after completing the gate preflight.

### AI reviewer

- Applies the checked-in AI rubric.
- Cites files, tests, traces, and unsupported claims.
- Separates blocking findings from recommendations.
- Challenges assumptions and asks follow-up questions.
- Does not assign final approval or unlock references.

### Human mentor

- Confirms that submitted evidence is reproducible.
- Applies the project mentor rubric and blocking conditions.
- Selects unseen cases, code, and changed constraints.
- Tests learner ownership without coding-agent assistance.
- Records `pass`, `revise`, or `stop-and-repair` as the gate decision.
- Controls reference access and private holdouts.

## Recommended mentor cadence

The course is mastery-based, so cadence follows artifacts rather than a fixed
calendar.

### Course opening

Conduct one baseline session for M00-M03:

- Confirm environment and Git workflow.
- Review the learner's repository inventory and first pull request.
- Establish expectations for AI work logs and review resolution.
- Explain that intentional test failures are learning gates, while dependency or
  collection failures are setup defects.
- Agree on how the learner requests reviews and how quickly the mentor normally
  responds.

### Each smaller project

Use three checkpoints:

1. **Design checkpoint:** brief artifact review before broad implementation.
2. **Pull-request preflight:** asynchronous review after automated and AI checks.
3. **Gate defense:** live demonstration, unseen case, code explanation, and
   decision.

The design checkpoint may be asynchronous for P1-P4. P5-P7 generally benefit
from a short live review because state, authority, and recovery mistakes become
expensive when discovered late.

### Capstone

Use the explicit Project 8 sequence:

- G9A proposal and changed-constraint defense.
- Walking-skeleton review.
- Evidence and integration-boundary review.
- Durability, approval, replay, and recovery review.
- Baseline and two measured-iteration review.
- Package, container, red-team, and readiness review.
- G9C portfolio and technical interview defense.

Do not allow frontend polish, extra tools, or framework expansion to replace a
weak vertical slice or evaluation plan.

## Gate map

| Gate | Primary course evidence | Typical project |
| --- | --- | --- |
| G0 Engineering baseline | Repository analysis, Git workflow, tests, oral ownership | M00-M03 |
| G1 Model API literacy | Responses implementation and provider comparison | P1 |
| G2 Reliable model boundary | Strict structured output, resilience, failure taxonomy | P2 |
| G3 Agent mechanics | Hand-built loop, tool contracts, termination evidence | P3 |
| G4 Evaluation practice | Ground truth, metrics, slices, measured iteration | P4 |
| G5 Backend service | FastAPI, PostgreSQL, justified Redis, correlated diagnosis | P5 |
| G6 Durable orchestration | LangGraph state, interrupt, restart, replay, approval | P6 |
| G7 MCP and integration | FastMCP, GitHub boundaries, webhooks, guarded writes | P7 |
| G8 Delivery | Wheel/sdist, clean install, Docker smoke, readiness review | P7 |
| G9 Capstone | Proposal, implementation evidence, portfolio, full defense | P8 |

The module and project rubric define the exact evidence. This table is routing,
not a substitute for those requirements.

## Standard gate protocol

### 1. Learner preflight

The learner provides:

- Pull request or immutable commit under review.
- Passing required automated checks, with expected exclusions identified.
- Required reports and diagrams.
- Completed AI review and response to every material finding.
- AI work log or equivalent ownership evidence.
- Demonstration commands and fixture path.
- Known limitations and requested mentor decisions.

Reject the review request as incomplete when the repository cannot be run from
its own instructions or the learner has not read the rubric.

### 2. Mentor evidence review

Before the live defense:

1. Read the business brief and current rubric.
2. Inspect the diff and commit sequence, not only the final files.
3. Run the documented deterministic checks.
4. Confirm no credential, generated state, or private holdout was committed.
5. Select one important success path, one failure path, and one code region.
6. Prepare an unseen input or changed constraint.

Do not reveal the selected code or scenario early when surprise is part of the
ownership test.

### 3. Learner-led defense

The learner should:

- State the problem and accepted scope.
- Trace the important data and authority boundaries.
- Run the success and failure demonstrations.
- Explain the selected code without an AI assistant.
- Predict behavior for the unseen case before running it.
- Respond to one changed requirement by tracing contract, state, test, and
  evaluation impact.
- Distinguish demonstrated behavior from production assumptions.

The mentor may permit documentation and source inspection. Do not permit the
coding agent to answer oral ownership questions or generate the changed design
during the defense.

### 4. Gate decision

Use one of three decisions:

- **Pass:** all required evidence is present, no blocking condition remains, and
  the learner demonstrates ownership. Non-blocking improvements may be recorded.
- **Revise:** the approach is recoverable, but required evidence, behavior, or
  explanation is incomplete. Specify observable resubmission conditions.
- **Stop-and-repair:** an integrity, safety, or foundational issue invalidates
  the evidence, such as holdout leakage, committed credentials, uncontrolled
  authority, fabricated metrics, or inability to explain the core implementation.

Avoid “conditional pass.” Either the required gate is demonstrated or it is not.
Record the decision using
`course/instructor/templates/gate-decision.md`.

### 5. Resubmission

For `revise`:

- Keep the original decision and evidence links.
- Require a focused patch and regression checks.
- Re-test the failed dimensions; do not repeat unrelated ceremony.
- Use a new unseen example when the prior answer has been disclosed.
- Record whether the correction generalizes beyond the demonstrated case.

For `stop-and-repair`, return to the prerequisite concept or earlier gate before
resubmission.

## Applying project rubrics

Projects 1-4 use scored rubrics with critical failure conditions. Enforce the
published minimum, required category scores, and the absence of critical
failures. Do not adjust scores to manufacture a pass.

Projects 5-8 use blocking conditions, review sequences, and required evidence.
Treat each blocking condition as binary until the learner supplies contrary
evidence. Add project-specific questions, but do not quietly remove published
requirements during review.

When a rubric item is ambiguous:

1. Return to the business brief and learning outcome.
2. Prefer demonstrable behavior over implementation style.
3. Accept a different design when contracts and tradeoffs are sound.
4. Record the interpretation so later reviews remain consistent.

## AI-review protocol

The learner should give the AI reviewer the project brief, rubric, changed
files, known limitations, and commands already run. Use
`course/instructor/templates/ai-review-request.md` as the reusable prompt.

Reject AI reviews that:

- Report generic best practices without repository evidence.
- Invent files, test results, or runtime behavior.
- Treat framework presence as proof of correctness.
- Declare the project passed or production-ready.
- Ignore the project scope and recommend a rewrite.
- Expose or request private holdout answers.

The learner classifies each material finding as accepted, corrected, rejected,
or deferred and supplies evidence. The mentor reviews the learner's reasoning,
not whether they agreed with the AI.

## Private holdout administration

### General rules

- Freeze holdout inputs and expected evidence before the learner's final tuning.
- Keep development and holdout identifiers distinct.
- Record the commit, dataset fingerprint, configuration, and command used.
- Do not help the learner tune against a disclosed holdout failure.
- After disclosure, use a new or rotated case for the next generalization check.
- Report the failure category and required remediation; withhold expected answer
  details unless they are needed for instruction after the decision.

Use `course/instructor/templates/holdout-run-record.md` for each run.

### P1-P3

Create a small unseen input that targets the project's core contract rather
than trivia. Ask the learner to predict and trace behavior before execution.

### P4

Keep `holdout-ground-truth.jsonl` private. Run the learner's frozen prediction
path against `holdout-issues.jsonl`, then evaluate the resulting predictions
against the private truth. Review overall metrics, slices, and individual
failures. Do not copy truth into the learner workspace.

### P5-P8 executable holdouts

From the frozen learner workspace, the mentor may run the relevant test file:

```bash
uv run pytest /path/to/agent-course/course/instructor/evaluation/p05/test_holdout.py
```

Substitute the project number as needed. These tests import the learner's
installed package, so verify the current working directory and environment
before trusting the result.

For course-maintainer reference verification, use:

```bash
uv run --no-project --python 3.13 python scripts/verify_reference.py p08
```

That command evaluates the reference, not the learner submission.

## Reference unlocking

References may be unlocked after a passed gate or after a documented attempt
when the mentor decides comparison will improve learning.

1. Create `.course-progress.toml` from the example if needed.
2. Set only the relevant project to `true`.
3. Confirm access:

```bash
python coursectl.py status
```

4. Materialize the reference outside the learner's working branch:

```bash
python coursectl.py solution p03 /tmp/p03-reference
```

5. Ask the learner to compare contracts, behavior, and tradeoffs rather than
   copying files.

Do not switch `course.toml` globally to `reference` for ordinary learner use.
Do not merge reference files into the learner submission. A later learner patch
should cite what changed after comparison and why.

## Technical-defense protocol

Use `course/instructor/templates/technical-defense-record.md`.

Select questions across five dimensions:

1. **Problem and scope:** user, outcome, non-goals, and simplest alternative.
2. **Contracts and authority:** schemas, tools, permissions, approvals, trust.
3. **State and reliability:** transitions, retries, idempotency, replay, recovery.
4. **Evaluation:** ground truth, metric limits, slices, regressions, leakage.
5. **AI collaboration:** generated code, detected error, correction, ownership.

At least one question should require a small changed constraint. At least one
should use selected code. The goal is not memorized syntax; it is accurate
reasoning through consequences.

## Common troubleshooting

### `coursectl start` refuses the destination

The destination must be absent or empty. Choose a new path rather than deleting
an active learner workspace.

### Initial tests fail

Read `START_HERE.md`. Documented TODO failures are expected. Dependency
resolution, imports during collection, missing commands, or unrelated failures
are setup problems.

### `uv` uses the wrong environment

Confirm the current directory and inspect `.venv`. A warning that
`VIRTUAL_ENV` points at another project usually means the shell was activated in
the wrong workspace. Deactivate it and rerun `uv sync` from the intended root.

### Live calls appear during default tests

Stop the run. Default tests must be fixture-backed. Inspect test imports and
module-level code for accidental provider calls, then remove credentials while
diagnosing.

### Docker checks are unavailable

Run all offline checks and static Compose validation. Record the Docker smoke as
unverified and do not pass a gate that explicitly requires the live container
demonstration until an appropriate environment is available.

### A holdout import resolves the reference package

Check `pwd`, `which python`, and the installed editable package. Run the holdout
from the learner workspace environment and record the learner commit.

### The learner saw holdout answers

Invalidate that case for final assessment. It may still be used as a teaching
example. Create or rotate an unseen case before making the gate decision.

### The learner cannot explain generated code

Do not let the coding agent explain it during the gate. Mark the relevant
ownership dimension incomplete, require simplification or study, and select a
new code region at resubmission.

## Record keeping

Store mentor records outside a public learner repository when they contain
private evaluation details, interview notes, or personal information. Public
gate records should contain the decision, evidence links, required revisions,
and technical rationale—not private expected answers or subjective personal
commentary.

Recommended records:

- Mentor session notes.
- Gate decisions and resubmissions.
- Holdout run records.
- Technical-defense records.
- Pilot observations.
- Course release record.

Templates live in `course/instructor/templates/`.

## Course completion

The learner completes the course only when:

- Required gates G0-G9 pass.
- Required smaller projects and capstone evidence are reviewable.
- The capstone success and failure demonstrations pass.
- Evaluation claims are reproducible and honestly limited.
- Selected AI-generated code is explainable and modifiable.
- Portfolio claims match repository evidence.
- The learner can state what remains before production use.

Completion is a mentor judgment supported by evidence, not a count of finished
readings or repositories.

## Maintainer handoff

Before assigning the course to a new learner, complete the
[release checklist](release-checklist.md). During the first learner run, use the
pilot observation template and treat confusion as course feedback rather than a
learner defect until the instructions have been tested from a clean clone.
