# Weak Generated Schema Review

An AI coding agent proposed this design:

```python
class IntakeRecord(BaseModel):
    source_id: str | None = None
    category: str | None = None
    urgency: str | int | None = None
    requester_email: str | None = None
    affected_system: str | None = None
    requested_action: str | None = None
    due_date: str | None = None
    missing_information: list[str] | None = None
    evidence: list[str] | None = None
```

The agent explained that optional fields make the model less likely to fail and
that accepting strings or integers for urgency improves flexibility. Unknown
fields are allowed so future models can add useful information. Any record that
parses is written to the database. If parsing fails, the exact request is
retried five times.

## Learner task

Create `reports/weak-schema-review.md` covering:

1. Which business requirements are not represented.
2. Which coercions or optional fields can hide defects.
3. Why unknown fields matter.
4. Which rules belong in Pydantic and which belong in policy.
5. Why unchanged schema failures should not be retried.
6. A revised schema proposal and remaining limitations.
