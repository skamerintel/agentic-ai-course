# Project 2 Reference Notes

The reference implementation is intentionally explicit:

- Pydantic validates JSON shape and local cross-field invariants.
- `validate_policy` compares accepted values to source text and business rules.
- Provider success, refusal, provider failure, schema failure, and policy failure
  are separate outcomes.
- Only retryable provider failures consume another attempt.
- Progress events expose application state without streaming partial JSON.
- OpenAI SDK retries are disabled so course retry behavior remains visible.

The evidence policy is still a heuristic. Exact source excerpts reduce invention
but do not prove that the selected interpretation is correct. Human review and
ground-truth evaluation remain necessary.
