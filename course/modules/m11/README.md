# M11: Ground Truth and Evaluation Design

## Learning objectives

By the end of this module, you can:

- Convert a business task into explicit evaluation dimensions.
- Create versioned examples, labels, rubrics, and meaningful slices.
- Distinguish deterministic metrics from human or model-graded judgments.
- Measure classification, set-valued, ranking, and follow-up decisions.
- Explain label disagreement and what an evaluation cannot prove.
- Protect a held-out regression set from prompt and tuning leakage.

## Prerequisite diagnostic

Suppose an issue-triage system gets 90% “accuracy.” List at least five questions
you need answered before deciding whether that number is useful.

Your questions should include what was scored, which examples were included,
who created labels, how ambiguous cases were handled, and whether important
slices are hidden by the aggregate.

## Required reading

- [OpenAI evaluation references](../../../docs/reference-catalog.md#ref-openai-evals)
- [pytest references](../../../docs/reference-catalog.md#ref-pytest)

## Concept lesson

### Start with the decision, not the metric

Project 4 recommends issue category, urgency, owning team, duplicate candidates,
and missing-information questions. These are different decisions and should not
be collapsed into one vague score.

Define for each decision:

- Allowed outputs.
- Acceptable alternatives.
- Cost of false positives and false negatives.
- Whether exact matching is appropriate.
- Which examples are ambiguous.
- Who adjudicates disagreement.

### Ground truth is governed data

Ground truth is not automatically true because it is in a file. Record:

- Labeling instructions.
- Annotator identity or role.
- Disagreements.
- Adjudication decisions.
- Dataset version and fingerprint.
- Changes and reasons.

Some examples may allow multiple owning teams or duplicate candidates. Represent
acceptable alternatives rather than forcing false precision.

### Use metrics that match the output

- Single category: exact accuracy and confusion matrix.
- Labels: precision, recall, and F1 over sets.
- Owner: membership in acceptable owners.
- Duplicate ranking: hit rate or reciprocal rank at a fixed `k`.
- Follow-up decision: precision and recall for asking questions.
- Free-text quality: rubric or human review with examples.

### Slices expose hidden failures

Useful slices may include repository, team, severity, ambiguous requirements,
prompt-injection content, sparse descriptions, and duplicate-present versus
duplicate-absent issues.

An aggregate can improve while a critical slice gets worse. Always report sample
counts beside slice metrics.

### Development and holdout sets serve different purposes

Use the development set to inspect failures and choose changes. Use a held-out
set to check whether the chosen changes generalize. Do not copy holdout labels or
examples into prompts, retrieval corpora, or coding-agent context.

## Guided lab

Inspect Project 4's seed labels from two annotators. Identify disagreements and
possible label mistakes, then apply the supplied labeling policy to produce an
adjudication note.

Run the baseline evaluator and answer:

- Which metric is worst?
- Which slice is worst?
- Which metric has too few examples to trust?
- Which error would matter most to the simulated business owner?

## Independent challenge

Add three development examples:

- One ambiguous owner.
- One issue with insufficient information.
- One issue where a semantic duplicate should not be treated as a true
  duplicate.

Update labeling guidance, dataset version, and evaluator tests. Do not alter
existing labels merely to improve a prediction score.

## Failure-analysis exercise

Critique a report that uses ten happy-path examples, calls exact-match category
accuracy “agent accuracy,” omits sample counts, and reports only the best prompt
on the same examples used to design it.

## Comprehension gate

The learner must defend:

- Dataset inclusion and exclusion rules.
- Every metric and slice.
- How disagreement is represented.
- Development versus holdout usage.
- What the evaluation does not establish.

The mentor supplies a new output type and asks the learner to choose an
appropriate metric.

## Interview questions

1. How do you create ground truth for an ambiguous LLM task?
2. Why can aggregate accuracy be misleading?
3. What is evaluation leakage?
4. When would you use precision, recall, F1, or ranking metrics?

## Required GitHub evidence

- Labeling policy and adjudication log.
- Versioned development dataset.
- Metric and slice definitions.
- Evaluator tests.
- Baseline report.
