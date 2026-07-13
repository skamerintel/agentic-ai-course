# Project 4 AI Review Rubric

The AI reviewer reports evidence-backed findings and questions. It does not
grant final approval.

## Dataset and labels

- Are labeling instructions and adjudication documented?
- Are acceptable alternatives represented?
- Are dataset fingerprints retained across experiments?
- Did any examples or labels change without disclosure?
- Is holdout material absent from prompts and retrieval data?

## Metrics and slices

- Do metrics match category, label-set, owner, ranking, and follow-up outputs?
- Are sample counts reported?
- Are important slices visible?
- Are zero-denominator and ambiguous cases handled explicitly?
- Does the report avoid collapsing everything into one score?

## Experiments

- Does each experiment have one primary hypothesis?
- Are configuration and context changes recorded?
- Are regressions and rejected experiments included?
- Could an apparent improvement come from leakage or dataset change?
- Is holdout evidence used only after candidate selection?

## Retrieval and context

- Is structured ownership lookup separated from duplicate retrieval?
- Are hit rate and ranking measured before generation quality?
- Are metadata filters and context bounds explicit?
- Are irrelevant but similar candidates analyzed?

## Learner ownership

- Can the learner trace metric calculations to examples?
- Are conclusions narrower than the evidence?
- Does the work log show corrections to AI-generated labels or analysis?

## Output format

1. Critical findings.
2. Important findings.
3. Questions for the learner.
4. Evidence supporting mentor review.
5. Unverified claims.
