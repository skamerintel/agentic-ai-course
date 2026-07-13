# Simulated API Requirements

## Client behavior

The client submits one issue-triage request with a caller-generated idempotency
key. It may retry the identical request after a timeout. It polls status and
recent progress, may request cancellation, and retrieves a result only after a
successful terminal state.

## Business rules

1. The first valid submission returns `202 Accepted`.
2. An identical idempotent retry returns the existing job and `200 OK`.
3. Reusing an idempotency key for a different issue is a conflict.
4. Job state and idempotency survive process and Redis restarts.
5. Progress may expire without changing durable state.
6. A cancellation committed before completion wins and discards the result.
7. A cancellation after a terminal state returns that state unchanged.
8. Provider failures create a failed attempt and classified job failure.
9. HTTP clients never receive raw provider exception text.
10. Logs correlate request, job, and provider attempt without logging issue
    bodies.

## State model

Allowed states are:

`queued -> running -> succeeded`

`queued -> cancelled`

`running -> cancel_requested -> cancelled`

`running -> failed`

Terminal states are `succeeded`, `failed`, and `cancelled`.

## Non-goals

- Authentication and multi-tenant authorization.
- A distributed production queue.
- Exactly-once model execution.
- Full observability-platform integration.
- Frontend specialization.
