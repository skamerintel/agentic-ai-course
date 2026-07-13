# Capstone AI Review Rubric

The AI reviewer advises; it does not pass a gate. Require file, test, trace, or
evaluation evidence for every finding.

## Review dimensions

Score 0-3 and explain the evidence:

1. Business outcome and scope.
2. Deterministic versus model-assisted design.
3. Typed provider, tool, API, and data boundaries.
4. LangGraph state, transitions, persistence, and recovery.
5. GitHub and second-API depth.
6. Consequential-action authority and idempotency.
7. Ground truth, metrics, slices, leakage control, and iterations.
8. FastAPI, PostgreSQL, justified Redis, and optional FastMCP design.
9. Unit, integration, contract, recovery, and adversarial tests.
10. Logging, privacy, prompt injection, and excessive-agency controls.
11. uv/Hatchling packaging, clean install, Docker, and smoke evidence.
12. Documentation, reproducibility, portfolio claims, and production gaps.

## Required challenge

- Identify the strongest unsupported claim.
- Identify one unnecessary feature.
- Identify one authority or replay path that needs direct evidence.
- Propose one changed constraint and trace its architectural impact.
- Select code the learner must explain without AI assistance.

## Learner response

For each material finding record: accepted, corrected, rejected, or deferred;
evidence checked; resulting patch or rationale; and regression checks run.
