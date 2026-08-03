# Tool Catalog

## Tool

- Name: `get_service_status`
- Decision supported: "Is this service healthy right now?" — current operational
  state for exactly one named service, so the analyst can decide whether to
  escalate or reassure.
- Description shown to the model: Get the current status of one named service
  by exact name. Returns operational state, region, and a short status detail
  as of the last update. Use this for "is X up / healthy / degraded" questions.
- Argument schema: `GetServiceStatusArgs { service_name: str, min_length=1,
  max_length=80 }`, `extra="forbid"`, `strict=True`.
- Data source: `data/services.json`, matched case-insensitively on `name`.
- Result shape and size bound: single object — `{name, status, updated_at,
  region, detail}`. Bounded because it is always exactly one record, never a
  list.
- Error categories: `not_found` (no service with that name);
  `invalid_arguments` (empty/oversized name, extra fields, wrong type);
  `retryable_error` / `terminal_error` (injected via `failure_plan.json` for
  scenario testing).
- Read or write: read.
- Information intentionally excluded: no historical status timeline, no
  underlying infrastructure/host details, no customer or revenue impact
  figures — those belong to incidents or asset data, not a status check.
- Approval requirement if converted to a write: N/A — this tool is
  deliberately read-only and has no write counterpart; a hypothetical
  "set_service_status" would require a change-management approval step
  (on-call lead sign-off) since it could mask or misreport real incidents.

## Tool

- Name: `search_incidents`
- Decision supported: "What has gone wrong with this service recently, and how
  often?" — bounded historical incident context to support a status answer
  with evidence, not just a current snapshot.
- Description shown to the model: Search historical incidents for one named
  service, most recent first, up to a caller-supplied limit. Use this to
  explain *why* a service is degraded or to show recent incident history.
- Argument schema: `SearchIncidentsArgs { service_name: str, min_length=1,
  max_length=80; limit: int, ge=1, le=5 }`, `extra="forbid"`, `strict=True`.
- Data source: `data/incidents.json`, filtered case-insensitively on
  `service`, deduplicated by `incident_id`, sorted by `started_at` descending.
- Result shape and size bound: list of up to `limit` (max 5) incident objects
  — `{incident_id, service, started_at, status, summary}`. The model-facing
  cap of 5 keeps context small and prevents a single call from dumping a
  full incident history.
- Error categories: `not_found` (no incidents at all for that service —
  distinct from "service has zero incidents ever" only insofar as the data
  set defines it); `invalid_arguments` (bad name, out-of-range limit, extra
  fields); `retryable_error` / `terminal_error` (injected via
  `failure_plan.json`).
- Read or write: read.
- Information intentionally excluded: no root-cause postmortems, no
  customer-identifying detail, no incident owner/assignee — the summary field
  is intentionally short and non-attributional to avoid leaking internal
  blame narratives into a model-composed answer.
- Approval requirement if converted to a write: N/A — no write counterpart
  exists; incident records are owned by the incident-management process, not
  by this agent.

## Tool

- Name: `get_asset`
- Decision supported: "Where is this managed asset, who has it, and is it
  currently in service?" — single-record lookup for a specific inventory
  item by ID.
- Description shown to the model: Get one managed asset by its exact
  asset ID (pattern like `LAP-204`). Returns kind, owner, location, and
  status. Use this only when the user supplies or implies a specific asset
  identifier.
- Argument schema: `GetAssetArgs { asset_id: str, pattern="^[A-Z]+-[A-Z0-9]+$"
  }`, `extra="forbid"`, `strict=True`.
- Data source: `data/assets.json`, matched case-insensitively (normalized to
  upper) on `asset_id`.
- Result shape and size bound: single object — `{asset_id, kind, owner,
  location, status, updated_at}`. Bounded to one record per call by design;
  there is no "list/search assets" tool, so the model cannot enumerate the
  full inventory.
- Error categories: `not_found` (no asset with that ID); `invalid_arguments`
  (ID doesn't match the required pattern, extra fields, wrong type);
  `retryable_error` / `terminal_error` (injected via `failure_plan.json`).
- Read or write: read.
- Information intentionally excluded: no purchase price, no serial numbers
  or vendor warranty detail, no full owner contact info — only what's needed
  to answer "where is it / who has it / is it working."
- Approval requirement if converted to a write: N/A — no write counterpart
  exists; a hypothetical "reassign_asset" or "retire_asset" write would need
  asset-owner and IT-admin approval before execution, since it changes
  accountable custody of physical/logical inventory.

## Why service status and incident search are separate tools

They answer different questions at different time horizons and have
different result shapes. `get_service_status` is a point-in-time snapshot —
always exactly one record, no arguments beyond identity, cheap and safe to
call on every turn. `search_incidents` is a bounded historical query — it
takes a `limit`, returns a list, and is more expensive to reason about
(ordering, deduplication, pagination-style bound). Merging them would force
every status check to carry incident-search parameters (and vice versa),
would blur the two error surfaces (a "not found" service vs. a service with
"no incidents" mean different things), and would prevent the model from
asking a cheap health question without always paying for a heavier incident
search. Keeping them separate also lets the app apply distinct limits and
distinct `strict` argument models per tool, which is required by the
project's validation and limit-enforcement rules.

## Why no write tools exist

The business brief calls for a **read-only** operations analyst assistant:
evidence-backed answers about health, assets, and incidents, not an
execution surface. Every write action here (changing a service's declared
status, reassigning or retiring an asset, editing incident records) has
real operational consequences and an existing human-owned approval process
(on-call escalation, IT asset management, incident command) that this
project does not model. Giving the model any write capability would also
break the stated architecture: "the model may select tools and compose a
final answer; it must never execute tools directly" — a write tool executed
autonomously by a model turn, even through the app's dispatcher, would let a
model-selected action change real state based on unverified reasoning. Until
there is an explicit approval/confirmation step for each write action (noted
per-tool above as a hypothetical), no write tool should be added.
