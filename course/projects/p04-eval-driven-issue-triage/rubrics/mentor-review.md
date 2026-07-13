# Project 4 Mentor Review Rubric

Score each category from 0 to 3.

1. Labeling policy and adjudication.
2. Dataset versioning and leakage controls.
3. Metric correctness.
4. Slice selection and interpretation.
5. Failure taxonomy and ledger.
6. Controlled experiment design.
7. Retrieval-only evaluation.
8. Context strategy and evidence.
9. Development versus holdout conclusions.
10. AI-generated analysis review and oral defense.

## Critical failure conditions

- Ground truth is included in model context.
- Hard examples or labels are changed to improve a score without disclosure.
- Holdout data is used during tuning.
- Metric implementation is incorrect or untested.
- Retrieval and generation failures are conflated.
- The learner cannot trace a reported metric to source examples.

## Passing guidance

- Minimum total: 20 out of 30.
- No category may score 0.
- Categories 1, 2, 3, 6, 7, 9, and 10 must score at least 2.
- Critical failure conditions override the numeric score.

## Defense prompts

- Recompute this metric for three examples by hand.
- Explain why this owner prediction is acceptable despite not matching one label.
- Identify the layer responsible for this duplicate failure.
- Show the fingerprint proving two experiments used the same dataset.
- Explain one slice regression hidden by the aggregate.
- Defend one rejected experiment.
