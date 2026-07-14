# Project 1 Mentor Review Rubric

Score each category from 0 to 3.

- 0: Missing or fundamentally incorrect.
- 1: Partial; learner cannot reliably explain or demonstrate it.
- 2: Meets the project's expected standard.
- 3: Strong evidence, judgment, and explanation beyond the minimum.

## Categories

1. Experiment contract and controlled comparison.
2. OpenAI Responses API understanding.
3. Chat Completions understanding and migration literacy.
4. Anthropic Messages API understanding.
5. Provider-boundary design.
6. Automatic and human evaluation design.
7. Failure classification and handling.
8. Test quality and offline reproducibility.
9. Report accuracy and limitation disclosure.
10. AI-generated code review and learner ownership.

## Critical failure conditions

The project cannot pass while any condition remains:

- A committed credential or sensitive raw payload.
- Live model calls required by the default test suite.
- A universal provider claim based on the course experiment.
- The learner cannot explain a selected adapter or evaluation function.
- Results were manually edited without retaining source records.
- Different providers received materially different task information without
  disclosure and justification.

## Passing guidance

- Minimum total: 20 out of 30.
- No category may score 0.
- Categories 1, 2, 4, 6, 9, and 10 must score at least 2.
- Critical failure conditions override the numeric score.

## Mentor defense prompts

- Normalize this unseen raw fixture by hand.
- Show one case where the reference summary is debatable.
- Explain why an automatic fact score is incomplete.
- Identify a provider detail your common result deliberately preserves.
- Defend one retry or timeout decision.
- Show an AI-generated proposal you rejected.
