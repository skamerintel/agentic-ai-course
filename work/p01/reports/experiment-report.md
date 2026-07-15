# Model API Behavior Lab Report

## Executive summary

Claude Sonnet 5, called via AWS Bedrock's `global` cross-region inference
profile using pydantic-ai's `BedrockConverseModel`, was run 3 times each on
all 8 incidents in `data/incidents.jsonl` (24 live calls total) under a fixed
system prompt, `temperature=0`, and `max_tokens=200`. Average lexical fact
recall across all 24 runs was **0.842**, below the contract's 0.9 threshold
for unreviewed use. Zero forbidden-claim occurrences appeared in any run.
Manual inspection of the lowest-scoring runs (INC-005, INC-008) found that
most of the "missed" facts were present in the summary but phrased
differently than the fact-check's exact substring list — the automatic
scorer's known lexical limitation, not an actual omission. Because the
automatic score cannot be trusted at face value, and because true recall
could not be fully confirmed without a semantic check, the recommendation is
**human review required before use**, on different grounds than a naive read
of the 0.842 number would suggest.

## Narrow recommendation

Do not use this model/configuration for **unreviewed** internal
incident-digest summaries. Per the experiment contract's decision rule, that
requires avg fact_recall ≥ 0.9 and zero forbidden claims; recall fell short.
This recommendation is scoped to this exact configuration (Claude Sonnet 5,
Bedrock `global` profile, this system prompt, temp=0) and does not extend to
other models, providers, or prompts. It also does not claim the model is
unreliable at stating facts — see Failure analysis — only that the
automatic-scoring pipeline as built cannot certify it without human
spot-checking.

## Experiment contract

Committed at `eae30c5` (`reports/experiment-contract.md`), before this
experiment was run.

## Dataset

All 8 incidents in `data/incidents.jsonl` (INC-001–INC-008), spanning
availability, integration, mobile, payments, network, email, security, and
analytics domains. No exclusions — incidents tagged `distractor` or
`uncertainty` were included by design, since they represent the harder cases
this test is meant to catch.

## Provider and model configurations

- Provider: AWS Bedrock, cross-region inference profile `global`.
- Client region: `AWS_REGION=us-east-2` (origin of the API call, not
  necessarily where inference runs under the `global` profile).
- Model: `global.anthropic.claude-sonnet-5`.
- Client: pydantic-ai `BedrockConverseModel` (not the raw Anthropic SDK).
- Generation parameters: `temperature=0`, `max_tokens=200`, fixed system
  prompt from `src/model_api_lab/prompting.py`, identical across all 24
  calls.

## Automatic results

24 live calls (8 incidents × 3 repetitions):

| Metric | Value |
|---|---|
| Avg fact_recall | 0.842 |
| Min fact_recall (single run) | 0.6 |
| Forbidden-claim violations | 0 / 24 |
| Avg word count | ~67 words |
| Avg latency | 3172 ms |
| Avg input tokens | 328 |
| Avg output tokens | 157 |

Per-incident fact_recall across the 3 runs:

| Incident | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| INC-001 | 0.8 | 0.8 | 0.8 |
| INC-002 | 1.0 | 0.8 | 1.0 |
| INC-003 | 1.0 | 1.0 | 1.0 |
| INC-004 | 1.0 | 0.8 | 0.8 |
| INC-005 | 0.6 | 0.8 | 0.6 |
| INC-006 | 1.0 | 1.0 | 1.0 |
| INC-007 | 0.8 | 1.0 | 0.8 |
| INC-008 | 0.6 | 0.6 | 0.6 |

Offline fixture run (3 fixed Anthropic Messages payloads, for comparison,
not part of the live decision): avg fact_recall 0.80, 0 forbidden claims.

## Human-review method and results

Manual read of all 3 runs for the two lowest-scoring incidents (INC-005,
INC-008), comparing summary text against the source report and against each
missed fact-check phrase. Every "missed" fact on those two incidents was
present in the summary in substance; none were absent, invented, or
misstated. No run scored 1-2 on the rubric's unsupported-claims, misleading-
emphasis, or incorrect-certainty criteria in this spot check. A full 1-5
rubric pass across all 24 runs was not completed — this is a documented gap,
see Follow-up experiments.

## Failure analysis

- **Scorer false negative, verb form (INC-005):** report says "No inventory
  records were lost"; summary says "no inventory records lost" — same fact,
  the scorer's exact-phrase match fails on missing "were".
- **Scorer false negative, inserted words (INC-008):** report says
  "a service account secret expired"; summary says "expired service account
  secret" — same fact, but the required substring "expired secret" doesn't
  match because "service account" sits between the two words.
- **Scorer false negative, paraphrase (INC-008):** report's "still in
  progress" fact check is written by the model as "still under assessment
  and unconfirmed" — semantically equivalent, no exact-phrase match.
- **Scorer false negative, reordering (INC-005):** report's cause
  ("maintenance notice named building A only") is restated as "the
  maintenance notice incorrectly named only Building A" — same fact, word
  order defeats the substring check.
- No unsupported claims, no forbidden-claim occurrences, and no obvious
  certainty errors were found in the runs inspected. This is a spot check of
  2 of 8 incidents, not exhaustive.

## Latency and usage observations

Latency ranged roughly 2500–4400 ms per call, averaging ~3.2s, with no
correlation observed between latency and fact_recall in this data (e.g.
INC-005 run 2 had the highest latency in its group, 4424 ms, and the highest
recall of the three, 0.8). Input tokens were stable per incident (as
expected — identical prompt), output tokens varied by ~15-90 tokens run to
run at temp=0, consistent with the fact_recall variance below.

## Variability

Despite `temperature=0`, 4 of 8 incidents produced different fact_recall
scores across their 3 repetitions (INC-002, INC-004, INC-005, INC-007); the
other 4 were identical across all 3 runs (INC-001, INC-003, INC-006,
INC-008). This is a genuine non-determinism finding: pinning temperature to
0 did not guarantee identical outputs or identical scores run to run for
this API path. Some of that apparent variance may itself be a scoring
artifact (a paraphrase crossing the substring-match boundary differently
run to run) rather than the model varying which facts it states — this
was not disentangled in this pass.

## Reference-data limitations

Reference summaries and fact-check phrase lists were authored for this
exercise and were not exhaustively validated against every plausible valid
paraphrase before running the experiment — the false negatives found in
Failure analysis suggest the phrase lists are narrower than the space of
correct restatements a capable model will produce.

## Confounding variables

- The `global` Bedrock inference profile may route each call to a different
  underlying region/data-center; no per-call region or trace metadata was
  captured to confirm whether variance correlates with routing.
- All 24 calls were made in a single sitting; no check for time-of-day or
  backend-version effects was possible with this sample size.

## What the experiment establishes

- On this dataset, this model, via this Bedrock path, produced zero
  forbidden/unsupported claims across 24 runs — a meaningfully clean safety
  signal for this narrow risk.
- Lexical fact-recall scoring alone is not sufficient to certify summary
  quality for this task; multiple genuine facts were scored as missing due
  to paraphrase, word order, and verb-form mismatches.
- Temperature 0 did not produce fully deterministic fact-recall outcomes for
  half the incidents tested.

## What the experiment does not establish

- Whether the *true* semantic fact recall (as opposed to the lexical proxy)
  meets or exceeds the 0.9 bar — a human rubric pass across all 24 runs, not
  just the 2-incident spot check done here, would be needed to know this.
- Anything about how this model/path compares to OpenAI's Responses or Chat
  Completions APIs, or to Claude called outside Bedrock — this project is
  scoped to a single model/provider path (see experiment contract).
- Whether the routing behavior of the `global` inference profile explains
  the run-to-run variance observed.

## Follow-up experiments

- Run the full 1-5 human rubric across all 24 runs (not just 2 incidents)
  to get a trustworthy semantic recall estimate independent of the lexical
  scorer's false negatives.
- Expand each fact check's `any_of` list with the paraphrases actually
  observed in this run (e.g. add "secret expired" variants, "still under
  assessment") and re-score the same 24 outputs to see how much of the 0.842
  → expected-higher gap the scorer fix alone closes.
- Repeat the 24-call sweep once more (e.g. 3 more repetitions per incident)
  to see whether the temp=0 variance pattern (4/8 incidents varying) is
  stable or itself noisy at this small a sample.
