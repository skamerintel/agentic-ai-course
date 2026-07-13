# Project 7 Reference Notes

The reference service keeps its capability surface deliberately small:

- Three bounded read tools.
- One proposal tool that cannot write to GitHub.
- One execution tool that requires a durable out-of-band approval.
- One repository-policy resource.
- No arbitrary REST, shell, file, administration, or approval tool.

The HTTP GitHub adapter owns API headers, timeout, pagination, rate-limit and
permission classification, response normalization, and comment reconciliation.
Approved comments include a proposal marker. If execution is replayed after an
uncertain write, the adapter finds the marker before posting again.

Webhook signatures are checked over raw bytes before JSON parsing. Delivery IDs
and body hashes are persisted in SQLite; identical redelivery is idempotent and
same-ID/different-body delivery is a conflict.

The wheel contains only the runtime package. Tests, fixtures, reports, local
state, and secrets remain development inputs. The multi-stage Dockerfile builds
and installs the wheel, runs as a non-root user, and receives fixture data and
mutable state through Compose mounts.

Production hardening would replace local SQLite with a managed transactional
store, add strong MCP and administrative authentication, use managed secrets,
define tenant isolation, improve write reconciliation, add migrations and
backups, and establish monitoring and incident procedures.
