# Project 7 Mentor Review Rubric

## Blocking conditions

- Arbitrary GitHub request or shell tools are exposed.
- Human approval is an MCP tool or can be supplied by model arguments.
- Webhook JSON is parsed before signature validation.
- Delivery IDs or write executions are deduplicated only in memory.
- Raw GitHub text can grant new authority.
- Default tests require a live GitHub repository.
- Wheel includes secrets, reports, tests, or local state.
- Container executes repository source instead of the installed wheel.
- Production readiness is claimed without stated limitations.

## Review sequence

1. Approve the capability and permission inventory.
2. Run deterministic MCP client tests.
3. Exercise pagination and rate-limit fixtures.
4. Validate, duplicate, and conflict a webhook delivery.
5. Propose, approve, execute, and replay a comment.
6. Inspect wheel and sdist contents and clean-install result.
7. Validate or run the container smoke path.
8. Apply one private holdout scenario.

## Passing evidence

The learner can trace every read and write boundary, explain package and image
contents, distinguish prototype safeguards from production hardening, and defend
deferred risks honestly.
