# M04: Operational Mental Model for LLM Applications

## Learning objectives

By the end of this module, you can:

- Discuss tokens, context, nondeterminism, hallucination, latency, and cost as
  application concerns.
- Distinguish instructions from untrusted data.
- Design a controlled comparison instead of relying on one impressive output.
- Describe model capability differences without invoking low-level architecture.
- Explain why fluent text is not evidence of factual correctness.

## Prerequisite diagnostic

Answer before reading the lesson:

1. If the same prompt produces two different answers, which one is “the real”
   output?
2. If a model follows formatting instructions, does that show the content is
   correct?
3. Why might adding more context reduce answer quality?
4. What must stay constant in a useful model comparison?

## Required reading

- [OpenAI Responses references](../../../docs/reference-catalog.md#ref-openai-responses)
- [Anthropic Messages references](../../../docs/reference-catalog.md#ref-anthropic-messages)
- [Context engineering references](../../../docs/reference-catalog.md#ref-context-engineering)

## Concept lesson

### Models generate; applications decide

Your application decides what data enters the request, what tools exist, what
output is accepted, what evidence is required, and what happens after failure.
Reliability is a property of this entire system, not the model response alone.

### Nondeterminism requires distributions, not anecdotes

One output can reveal a failure but cannot establish a stable success rate. For
tasks that vary across runs, repeat representative examples and report the
distribution of outcomes. Retain exact inputs, configuration, model identifier,
timestamp, and evaluation method.

### Context is finite and competitive

Relevant instructions, examples, source data, tool results, and conversation
history all compete for attention. More context may introduce contradictions,
stale data, or irrelevant patterns. Context engineering is deciding what the
model needs now and how that information should be represented.

### Hallucination is an application failure mode

Do not ask whether the model “hallucinates” in the abstract. Define what claims
the task permits, what evidence is available, and how unsupported claims are
detected. A safe outcome may be refusal, uncertainty, or “insufficient evidence.”

### Compare capabilities on the actual task

Model comparisons should hold the task, dataset, rubric, and application
behavior constant while changing one factor. Measure quality, latency, usage,
format adherence, and failure categories. Avoid universal conclusions from one
narrow benchmark.

## Guided lab

Use three supplied Project 1 incidents. Run repeated summaries with the same
task contract. Record:

- Facts preserved.
- Facts omitted.
- Unsupported claims.
- Format deviations.
- Latency and usage.
- Variation across runs.

Offline fixtures can teach the scoring workflow, but live repeated calls are
required before drawing conclusions about model behavior.

## Independent challenge

Write an experiment contract for Project 1 before implementing providers. It
must define:

- Exact task and audience.
- Fixed instructions.
- Dataset inclusion criteria.
- Metrics and failure categories.
- Number of repetitions and why.
- Factors held constant.
- Known limitations.

Ask a coding agent to critique the contract. Accept only corrections you can
justify.

## Failure-analysis exercise

Critique this conclusion:

> Model A is more intelligent because its one summary sounded more professional
> and used fewer words than Model B.

Identify missing evidence, confounding variables, and a better claim that could
be supported.

## Comprehension gate

Present the experiment contract and answer:

- What result would falsify your preferred conclusion?
- Which metric can be automated and which needs human judgment?
- What does the experiment not establish?
- How will you detect unsupported facts?

## Interview questions

1. Why are LLM evaluations task-specific?
2. How can additional context make output worse?
3. What does temperature or sampling variability mean operationally?
4. How would you compare two models fairly?

## Required GitHub evidence

- Experiment contract.
- Initial scoring worksheet.
- Coding-agent critique and accepted/rejected findings.
- Gate notes.
