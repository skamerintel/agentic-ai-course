# Leaky Experiment Report

## Claim

Prompt v4 achieved 100% on every triage metric and is ready for production.

## Method

The development ground-truth JSON was placed in the model context as examples so
the model could “learn the expected format.” The evaluation examples were then
run against the same context. Three issues that still failed were removed as
unrepresentative. One owner label was changed to match the model because the
prediction sounded plausible. The report does not include the new dataset
fingerprint, removed issue IDs, prompt, model configuration, slice metrics, or a
holdout result.

## Learner task

Create `reports/leaky-experiment-review.md` that identifies every validity
failure, reconstructs what evidence remains usable, and proposes a clean
experiment that could support a narrower conclusion.
