# Project 7: GitHub Workflow MCP Service

## Business brief

An engineering organization wants a reusable MCP service for bounded GitHub
repository, issue, and pull-request workflows. Read operations may run directly.
Comments must be proposed, approved by a human outside the MCP tool surface, and
then executed idempotently.

The service also receives signed GitHub webhook events, deduplicates deliveries,
ships as a clean Python distribution, and runs through a documented Docker
Compose evaluation path.

## Required architecture

- FastMCP server with typed, bounded tools and a repository-policy resource.
- GitHub gateway with fixture and HTTP implementations.
- Durable SQLite proposals, approvals, execution receipts, and webhook delivery
  records.
- Human approval available through an administrative CLI, not an MCP tool.
- Starlette HTTP application combining MCP, webhook, and health routes.
- uv/Hatchling package build and clean-environment smoke test.
- Multi-stage Docker image that runs the installed wheel as a non-root user.

## Repository assets

- `data/capability-policy.json`: allowed capabilities and approval rules.
- `data/permission-inventory.json`: simulated least-privilege GitHub access.
- `fixtures/github-api.json`: deterministic repositories, issues, and PRs.
- `fixtures/webhooks/`: signed-event payload sources.
- `fixtures/http-scenarios.json`: pagination, rate-limit, permission, and stale
  response cases.
- `fixtures/approval-scenarios.jsonl`: guarded-write acceptance scenarios.
- `broken-tool-catalog-review.md`: over-broad MCP design exercise.
- `broken-delivery-review.md`: unsafe packaging and Docker exercise.
- `rubrics/` and `templates/`: review and portfolio artifacts.

Private mentor holdout scenarios are not copied by `coursectl start`.

## Setup

```bash
python coursectl.py start p07 work/p07
cd work/p07
uv sync
uv run pytest
```

## Required workflow

### 1. Approve the capability surface

Complete `reports/capability-catalog.md` before implementation. Every tool and
resource needs a user, purpose, input bound, output bound, permission, side
effect classification, and approval rule.

### 2. Implement deterministic MCP tests

Use the FastMCP in-memory client to list capabilities, call every read tool,
read the policy resource, and exercise proposal and guarded execution. No model
or network is required.

### 3. Implement the GitHub boundary

Support fixture mode by default. Add HTTP behavior for authentication, API
versioning, pagination caps, rate-limit classification, permission failure,
timeouts, and validated response models.

### 4. Implement signed webhook ingestion

Validate the raw body with `X-Hub-Signature-256`, require delivery and event
headers, then parse and persist. Demonstrate duplicate and conflicting delivery
IDs.

### 5. Demonstrate guarded writes

Propose a comment through MCP, approve it with the administrative CLI, execute
it through MCP, and replay execution. GitHub receives one comment.

### 6. Build and clean-install the package

```bash
uv build
```

Inspect wheel and sdist contents. Install the wheel into a clean temporary
environment and run the public server-factory smoke test outside the checkout.

### 7. Validate container delivery

```bash
docker compose build
docker compose up -d
```

Run the external health, webhook, and MCP smoke checks. Confirm the runtime
image uses the installed wheel and does not contain development reports or
secrets.

### 8. Complete the production review

Present trust boundaries, release blockers, near-term hardening, future scaling,
and explicitly accepted risks.

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pyright src
uv build
docker compose config --quiet
```

## Definition of done

- Capability surface is narrow, typed, and bounded.
- Approval is not model-callable.
- Deterministic client tests cover every MCP capability.
- GitHub text remains untrusted data.
- Pagination and rate-limit behavior are explicit.
- Webhook signatures are validated before JSON parsing.
- Delivery and write replays are idempotent.
- Wheel and sdist inventories are approved.
- Clean-install smoke test passes outside the repository.
- Docker runs the installed wheel as non-root.
- Production gaps are prioritized honestly.

## Comprehension gate

The learner traces a read tool, signed webhook, duplicate delivery, proposed
comment, human approval, executed write, execution replay, clean package install,
and container request. The mentor selects one trust boundary and asks what
authority, validation, persistence, and failure evidence apply.
