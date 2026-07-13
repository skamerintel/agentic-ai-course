# M12: Failure-Driven Agent Improvement

## Learning objectives

By the end of this module, you can:

- Build a failure taxonomy from observed traces and outputs.
- Separate prompt, schema, retrieval, policy, tool, and label failures.
- Run controlled experiments with one primary change at a time.
- Detect improvements caused by leakage, changed labels, or removed hard cases.
- Maintain regression examples and rejected experiments.
- Explain why a change should generalize beyond visible examples.

## Prerequisite diagnostic

A new prompt raises overall owner accuracy from 70% to 80%. Before accepting the
change, list the evidence needed to rule out:

- Dataset changes.
- Label changes.
- Different model configuration.
- Leakage.
- Regression on an important repository.
- Random variation.

## Required reading

- [OpenAI evaluation references](../../../docs/reference-catalog.md#ref-openai-evals)
- [Python logging references](../../../docs/reference-catalog.md#ref-python-logging)

## Concept lesson

### Improvement starts with a named failure

Avoid “the output looks weak.” Classify failures such as:

- Category confusion.
- Unsupported urgency.
- Owner lookup missing or stale.
- Duplicate retrieval miss.
- Semantically similar false duplicate.
- Missing-information question omitted.
- Schema or parsing failure.
- Ground-truth disagreement.
- Prompt injection followed.

A taxonomy turns random prompt edits into testable hypotheses.

### Separate system layers

If duplicate ranking fails, determine whether:

- Retrieval missed the relevant issue.
- Retrieval returned it but the model ignored it.
- The context was truncated or confusing.
- The label is wrong or ambiguous.

Changing the generation prompt cannot repair a retriever that never supplied the
relevant evidence.

### One experiment, one primary hypothesis

Record:

- Baseline identifier.
- Dataset fingerprint.
- Model and configuration.
- Prompt, schema, context, or code change.
- Predicted effect and target slice.
- Result by metric and slice.
- New regressions.
- Decision: accept, reject, or investigate.

Bundling prompt, model, dataset, and retrieval changes makes the result difficult
to interpret.

### Preserve rejected experiments

A rejected experiment is valuable evidence. Record why it failed. This prevents
future agents or engineers from repeating the same attractive mistake.

### Watch for counterfeit improvement

Common causes include:

- Deleting hard examples.
- Editing labels to match predictions.
- Including ground truth in context.
- Selecting the best run without reporting variance.
- Changing scoring code.
- Reporting only improved metrics.

## Guided lab

Compare Project 4's baseline and improved fixture predictions. Build a failure
ledger before reading the experiment description. Identify which errors the
improved system fixed and which slice regressed.

Then inspect the supplied leaky experiment and explain why its perfect score is
invalid.

## Independent challenge

Complete two controlled improvement iterations:

1. One context or ownership-rule improvement.
2. One retrieval or triage-instruction improvement.

Also record one rejected experiment. Run all three against the unchanged
development set and then request mentor evaluation on the holdout set.

## Failure-analysis exercise

The dataset fingerprint changed between baseline and candidate, but the report
claims the prompt alone improved accuracy. Trace the change, identify affected
examples, and rewrite the conclusion.

## Comprehension gate

The learner presents the failure ledger, two accepted experiments, one rejected
experiment, development results, holdout results, regressions, and limitations.
The learner must explain why each accepted change should generalize.

## Interview questions

1. How do you improve an agent without prompt thrashing?
2. How do you distinguish retrieval failure from generation failure?
3. Why preserve rejected experiments?
4. What evidence suggests an apparent improvement is leakage?

## Required GitHub evidence

- Failure taxonomy and ledger.
- Experiment manifests.
- Dataset fingerprints.
- Before-and-after reports with slice metrics.
- Rejected experiment record.
