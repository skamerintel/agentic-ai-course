# Project 3 Mentor Review Rubric

Score each category from 0 to 3.

1. Tool boundaries and descriptions.
2. Strict argument validation.
3. Error and result contracts.
4. Agent state and transition design.
5. Call-ID correlation.
6. Iteration, total-call, and repeated-call controls.
7. Complete and useful traces.
8. Offline scenario coverage.
9. Live Responses function-calling integration.
10. AI-generated code review and oral defense.

## Critical failure conditions

- Arbitrary function dispatch or unvalidated arguments.
- Missing call-ID correlation.
- No enforced stop limits.
- Tool or model failures reported as successful evidence.
- Default tests require live model calls.
- The learner cannot narrate the selected loop code.

## Passing guidance

- Minimum total: 20 out of 30.
- No category may score 0.
- Categories 2, 4, 5, 6, 7, and 10 must score at least 2.
- Critical failure conditions override the numeric score.

## Defense prompts

- Predict the result of this malformed tool call.
- Explain why these two call signatures are or are not repeats.
- Trace two parallel calls and their outputs.
- Show where a retryable tool error becomes model input.
- Explain one stop reason from a JSON trace.
- Show an AI proposal you rejected.
