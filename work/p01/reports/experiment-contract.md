# Experiment Contract

## Decision to support

Whether Claude Sonnet, called via AWS Bedrock, produces incident summaries
reliable enough for this team to use for internal incident digests without
per-summary human rewriting. This project deviates from the course's default
3-provider comparison (OpenAI Responses / OpenAI Chat / Anthropic Messages):
only one model and one API path is available in this environment (Claude
Sonnet via Bedrock, called through pydantic-ai's `BedrockConverseModel`). The
comparison this contract supports is therefore **run-to-run reliability on a
fixed configuration** — not a cross-provider ranking. Flagged to the mentor as
an intentional scope change from PROJECT.md; the recommendation below is
scoped accordingly and does not claim to rank providers.

## Task and audience

Summarize a single incident report into a short internal digest entry for
on-call engineers and leadership. The audience needs to scan a summary in a
few seconds and trust that it does not invent facts.

## Included and excluded examples

- Included: all 8 incidents in `data/incidents.jsonl` (INC-001 through
  INC-008), spanning availability, integration, mobile, payments, network,
  email, security, and analytics domains, including ones tagged
  `distractor` or `uncertainty`.
- Excluded: none. All 8 incidents are used, including the `distractor` and
  `uncertainty`-tagged ones — those tags mark the harder cases this test is
  meant to catch, not cases to filter out.

## Fixed instructions

The following prompt is sent unchanged for every run of every incident
(only `{report}` is substituted):

```
System: You write short internal incident-digest summaries for on-call
engineers and leadership. For the incident report below:
- Identify the affected system or workflow.
- State the confirmed impact and scope.
- State the confirmed cause and mitigation only if the report states them.
- Do not add a cause, impact, or resolution that the report does not state.
- Clearly mark anything uncertain or unconfirmed as such; do not state a
  guess as fact.
- Keep the summary to 2-3 sentences.

User: {report}
```

## Provider and model configuration

- Provider: AWS Bedrock, cross-region inference profile `global` (routes
  dynamically across regions for inference). Client `AWS_REGION=us-east-2`
  (from `.zshrc`) — this sets where the Bedrock API calls originate from,
  not necessarily where the model runs under the `global.` profile.
- Model: Claude Sonnet, model string `bedrock:global.anthropic.claude-sonnet-5`
  (pydantic-ai `provider:model_id` format).
- Client: pydantic-ai `BedrockConverseModel`, not the raw Anthropic SDK.
- Generation parameters: `temperature=0`, `max_tokens=200` (2-3 sentence
  summaries need well under this; generous headroom avoids truncation),
  held identical across every run. Temperature pinned to 0 to maximize
  reproducibility — if variance still appears at temp=0, that is itself a
  finding about the model's non-determinism.

## Factors held constant

- Same incident report text and same fixed instructions across every run.
- Same model ID, same Bedrock region, same client configuration
  (pydantic-ai version, `BedrockConverseModel` settings) across every run.
- Same generation parameters across every run.
- Same run count per incident (see repetition policy).

## Automatic metrics

- Fact recall: fraction of an incident's `fact_checks` whose `any_of`
  phrases appear in the summary (see `Score.fact_recall`).
- Forbidden-claim violations: count of `forbidden_claims` phrases that
  appear in the summary.
- Word count.
- Latency (ms) and token usage, where reported by the API.

These automatic checks are a coarse lexical signal only — they cannot detect
misleading emphasis, wrong certainty language, or claims outside the
supplied deny list.

## Human-review rubric

Each summary is scored 1-5 on each criterion (5 = no issue, 1 = severe
issue):

1. **Unsupported claims** — does the summary state anything (cause, impact,
   resolution) not present in the source report, beyond what the
   forbidden-claims list already catches?
2. **Misleading emphasis** — is anything true but framed with
   disproportionate weight (e.g. a minor detail presented as the headline)?
3. **Incorrect certainty** — does the summary state a suspected/unconfirmed
   detail as fact, or hedge a confirmed detail unnecessarily?
4. **Clarity and usefulness** — could an on-call engineer or leadership
   scan this in a few seconds and understand what happened?

A score of 1-2 on criteria 1-3 in any run is treated as a failure example
for the report's failure-examples section, regardless of average scores.

## Repetition policy

Repetition is the core measurement in this single-model study, not an
afterthought. Each of the 8 incidents is run **3 times** under identical
configuration (same prompt, same `temperature=0`, same `max_tokens`) — 24
total calls — to measure fact-recall and forbidden-claim variance run to
run. Temperature is pinned to 0, so any variance observed across the 3 runs
on the same incident indicates real non-determinism in the model/API path,
not a sampling artifact.

## Failure categories

- Missed required fact (fact_recall < 1.0).
- Forbidden/unsupported claim introduced.
- Wrong certainty framing (states a suspected cause as confirmed, or vice
  versa).
- Off-topic or unusable-length summary.

## Data and privacy rules

- Only the supplied fixtures and `data/incidents.jsonl` are used; no real
  customer or production incident data.
- No API keys, raw live provider payloads, or private response bodies are
  committed to Git. Live outputs are written under `reports/live-raw/`,
  which is gitignored.

## Decision rule

Recommend Claude Sonnet (via Bedrock, this configuration) for **unreviewed**
internal incident-digest use only if, across all 24 runs (8 incidents × 3
repetitions):

- Average `fact_recall` across all runs is **≥ 0.9**, AND
- **Zero** forbidden-claim occurrences appear in any run.

If either condition fails, the recommendation is "human review required
before use" (not "insufficient evidence" — 24 runs across 8 varied
incidents is enough data to judge this specific configuration; it is only
insufficient for claims beyond this one model/setup). Any single run with
a forbidden claim disqualifies unreviewed use regardless of average recall,
since this is an internal digest people will trust — an invented cause or
impact is worse than a merely incomplete summary.

## Known limitations

- Automatic scoring is lexical/substring matching, not semantic
  understanding — it will miss paraphrased facts and can false-positive on
  incidental substring matches.
- 8 incidents is a small sample; results are indicative for this narrow
  summarization task, not a general model quality claim.
- Reference summaries and fact checks were authored for this exercise and
  may themselves have gaps.
- Single model, single provider path — this contract cannot support any
  claim about how Claude Sonnet compares to OpenAI's APIs or to Claude
  called directly (outside Bedrock). It only supports a claim about this
  model's reliability under repeated identical calls.
- TODO — add any limitation specific to your final repetition count or
  configuration choices.
