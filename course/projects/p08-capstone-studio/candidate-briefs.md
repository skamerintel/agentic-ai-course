# Capstone Candidate Briefs

All organizations, users, records, and metrics in these briefs are synthetic.
The mentor may change constraints during discovery.

## A. Support escalation investigator (recommended default)

### Situation

A platform support lead investigates high-priority customer escalations by
cross-checking ticket history, GitHub issues and pull requests, deployment
status, and public incident data. Evidence is fragmented, and handoffs often
omit uncertainty or the next owner.

### Desired outcome

Produce an evidence-linked investigation packet and proposed follow-up actions
that reduce time-to-triage and missing-evidence errors. Posting a customer note,
opening a GitHub issue, or changing escalation status requires human approval.

### Required systems

- Synthetic support-ticket API.
- GitHub REST API.
- Synthetic service-status API.

### Useful model work

Reconcile narrative symptoms with repository and status evidence, classify
uncertainty, and draft bounded follow-up proposals. Ticket IDs, permissions,
policy, evidence existence, approval, and writes remain deterministic.

### Scope traps

Do not add general customer chat, autonomous remediation, broad internet search,
or a rich support UI.

## B. Incident follow-up coordinator

### Situation

Engineering managers struggle to turn incident timelines, repository changes,
and monitoring events into owned follow-up work. Similar incidents produce
inconsistent action items and weak links back to evidence.

### Desired outcome

Generate an evidence-linked follow-up plan, detect duplicate or unsupported
actions, and propose GitHub issues. Issue creation and ownership changes require
human approval.

### Required systems

- Synthetic incident-management API.
- GitHub REST API.
- Synthetic monitoring-event API.

### Scope traps

Do not build incident detection, paging, root-cause certainty, or automated
production changes.

## C. Dependency-upgrade investigator

### Situation

A platform team evaluates dependency upgrades across several repositories.
Release notes, repository usage, compatibility policy, security advisories, and
test evidence must be reconciled before creating upgrade work.

### Desired outcome

Produce a bounded upgrade recommendation with evidence, affected repositories,
test requirements, and a proposed rollout plan. Pull-request creation or policy
exceptions require human approval.

### Required systems

- GitHub REST API.
- Synthetic package-registry API.
- Synthetic advisory API.

### Scope traps

Do not execute arbitrary package-manager or shell commands, rewrite code
autonomously, or claim compatibility without test evidence.

## D. Compliance evidence coordinator

### Situation

An internal assurance analyst gathers repository controls, review records, and
approved business-system evidence for a recurring control assessment. Manual
collection is slow and conclusions can become detached from source evidence.

### Desired outcome

Assemble a traceable evidence packet, flag missing or stale evidence, and
propose follow-up requests. Submitting an assessment or requesting evidence
from a control owner requires human approval.

### Required systems

- GitHub REST API.
- Synthetic control-catalog API.
- Synthetic evidence-request API.

### Scope traps

Do not claim legal compliance, make final audit determinations, or expose
sensitive evidence through model prompts or logs.

## Selection matrix

Score each candidate from 1 to 5 and defend the evidence behind the score:

| Dimension | Question |
| --- | --- |
| User access | Can the mentor realistically simulate stakeholder decisions? |
| Ground truth | Can correct evidence and actions be labeled consistently? |
| Model justification | Is interpretation needed beyond deterministic rules? |
| Integration depth | Do GitHub and the second API materially affect outcomes? |
| Safety boundary | Is there a meaningful consequential action to guard? |
| Evaluation depth | Are useful metrics and failure slices available? |
| Finishability | Can a polished vertical slice be completed before scope expands? |
| Portfolio distinction | Does it show judgment beyond the earlier projects? |

The highest total is not automatically the best choice. Reject any candidate
with weak ground truth, fake integration, or an unfinishable first slice.
