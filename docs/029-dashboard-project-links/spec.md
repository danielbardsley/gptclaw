# SPEC-029: Dashboard project links

- **Status:** Approved for implementation — implementation and acceptance in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Primary feature:** DSH-003
- **Design:** [TDD-029](technical-design.md) · **Tasks:** [TASKS-029](tasks.md)
- **Dependencies:** [Inventory foundation](../027-dashboard-project-inventory/spec.md), [live status](../028-dashboard-live-service-status/spec.md), [private app routing](../../runbooks/manage-private-apps.md), [API route design](../024-python-fastapi-template/technical-design.md), [group route design](../025-multi-service-projects/technical-design.md)

## Outcome and authorization

Let the project owner open each project's private UI or API documentation and repository
from its dashboard entry, with clear availability and destination labels. Provide a
stable internal logs destination when a reviewed log viewer exists, and display an
active public-preview URL only when an authoritative reviewed registry supplies it.

The October 12 request authorizes this separate planning set and reviewable planning
PR. Specification approval and implementation authorization are recorded below; acceptance remains pending. Opening
an existing destination is distinct from starting services, creating previews or
changing exposure; no new exposure or preview lifecycle is authorized here.

## Scope and existing readiness

Include typed link projection, private project/API-doc links, repository links, honest
unsupported/unavailable states, safe browser navigation and expiry-aware display-only
preview integration. Use the SPEC-027 row identity/metadata contract and SPEC-028
freshness/health where available; basic repository links do not depend on live health.

The current provider returns a configured private Serve URL, but that alone does not
prove the project is currently published or healthy. Single API docs are mounted under
`/projects/<id>/docs`; group API docs use `/projects/<id>/api/docs`. Treat these as
reviewed provider/template route capabilities, not universal paths for any manifest.
No public-preview registry or dashboard log viewer is currently supplied by the provider.

Logs are an explicit destination slot: use a stable same-origin project/component logs
route only when a reviewed DSH-006 viewer capability is installed. Until then show
“Log viewer not available”; do not implement log reads/streaming in this feature. Public
previews likewise show “Preview registry not available” until the separately reviewed
NET-108/exposure contract exists. Initial acceptance must prove these unavailable states;
actual viewer/preview integration needs real evidence when those prerequisites arrive.
Do not mark those dependent features Delivered through this initiative.

Exclude public-preview creation/renewal/revocation, Funnel controls, lifecycle buttons,
log content/streaming, external link crawling, remote Git authentication, database/admin
links, arbitrary URL inputs, production and secret-bearing destinations. The dashboard
itself and logs/admin/metrics/database endpoints remain forbidden Funnel targets.

## Requirements

### LNK-001 — Typed private project and API-doc links

Generate project links only from a validated inventory identity, trusted tailnet origin,
and observed owned private route state. Require current publication/readiness evidence
for an enabled private app/docs link; retain the stable address with a clear unavailable
label when stopped, stale, degraded, conflicted or not routed. Never make an unavailable
URL an enabled launch action or imply that a configured Serve prefix proves app health.

Show “Open app” for supported web/group UI and “API docs” only for an observed supported
API docs capability. Resolve single/group paths from a reviewed route descriptor.
Do not infer docs support solely from kind, and do not link to unpublished container
ports or local host addresses. A never-started project can show the expected private
path as text but cannot claim an observed configured address.

### LNK-002 — Repository and logs destinations

Offer a canonical credential-free HTTPS repository link from SPEC-027's validated
platform metadata; absent metadata shows “Repository not recorded”. Repository access
uses the browser's existing GitHub session, with no dashboard-issued credentials.

Provide an internal logs link keyed by opaque project/component identity only when a
reviewed same-origin log viewer capability exists. Otherwise disclose its absence.
Stopped services may still have historical logs when the viewer reports that support;
service health alone does not disable repository/log destinations. No shell command,
file URL or raw journal/container endpoint is substituted for a missing viewer.

### LNK-003 — Authoritative active public-preview links

When a reviewed registry is available, show only a validated active application HTTP
preview for the exact project/route identity, with absolute expiry and remaining time.
Exclude expired/revoked/stale/conflicted entries; show their reason without an enabled
link. Registry observation is display-only and cannot create, extend or revoke exposure.
Missing registry support must not be described as “No active previews” unless a fresh
successful registry result establishes that fact.

The initial implementation can prove this adapter with synthetic registry fixtures and
show unavailable in the live dashboard. Real preview display stays capability-gated
until its separately authorized registry/exposure prerequisite is accepted. An expired
UI link is not proof of network revocation; exposure enforcement remains that service's
responsibility. Do not publish the dashboard, logs, API admin or database endpoints.

### LNK-004 — Safe destination and navigation boundary

Allow only typed destinations: configured private tailnet HTTPS origin and reviewed
project paths, canonical GitHub HTTPS repository URLs, same-origin logs paths, or a
registry-owned HTTPS preview origin/path bound to an approved application route.
Reject credentials/userinfo, secret tokens, unsafe schemes, protocol-relative URLs,
unexpected ports/hosts, query/fragment injection, traversal and encoded-path confusion.
No arbitrary redirect target, backend URL fetch or browser-provided URL is accepted.
Validate again at the rendering boundary and treat labels as plain text. External tabs
must prevent opener access; label private, repository and public destinations clearly.

### LNK-005 — Freshness and usable unavailable states

Show each unavailable reason and observation age independently from other link types.
Repository links remain available during runtime/registry outages. Withdraw enabled
private/preview links when their authoritative snapshots become stale. Preview links
expire locally at the registry's absolute expiry even between polls; refresh must never
revive an expired/revoked entry from old cache. Use collector time plus bounded browser
elapsed time, rather than trusting the client's wall clock for expiry decisions.
All link controls and unavailable explanations are keyboard and screen-reader usable.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirement IDs |
|---|---|---|
| AC-001 | Single web/API and group fixtures produce exact reviewed private app/docs destinations only when capability, identity, publication and health evidence agree; stopped/stale/conflicted/unrouted targets are disabled with reasons. | LNK-001/005 |
| AC-002 | Recorded/missing repository metadata behaves honestly; repository links survive runtime failure; a supported logs adapter yields correct opaque internal destinations while absent viewer support has no enabled logs link or log-reading side effect. | LNK-002/005 |
| AC-003 | Synthetic registry fixtures cover active, expired, revoked, absent, unavailable, stale, wrong-project and forbidden endpoint entries; only valid active app previews are enabled and expire between polls despite client clock skew. Live initial acceptance shows unavailable registry support; no exposure is created. | LNK-003/005 |
| AC-004 | Security fixtures reject unsafe schemes, userinfo, injected hosts/ports, query tokens, path traversal/encoding and redirects; execution/network spies show no crawling, credentials, mutations or exposure operations. Plain-text rendering and safe external-tab attributes pass. | LNK-004 |
| AC-005 | Owner browser acceptance opens a task-owned ready private web app, standalone API docs and group API docs at their correct prefixes; repository destination is correct where recorded. Keyboard/unavailable/failure/recovery checks pass. Record local/CI/live/owner evidence separately and dependent logs/preview integration limitations explicitly. | LNK-001/002/003/005 |

## Dependencies and decisions

Implement identity/private hosting after SPEC-027 and readiness freshness after SPEC-028.
Settle a versioned route-capability descriptor with the provider: current source URL
fields are insufficient to prove docs capability or publication by themselves. Keep
repository navigation useful without status; keep logs/public-preview slots honest
without their future implementations. The project owner reviews this staged scope;
acceptance of initial DSH-003 must state that live logs/preview integration is pending
its separately accepted prerequisites. No extra authorization is inferred from fixtures.

## Implementation authorization

On October 12 the project owner instructed: “In order implement the specs for
DSH-001, DSH-002 and DSH-003. Finish once all acceptance criteria have been met.”
This approves the specified scope and defaults and authorizes implementation and
necessary reversible private runtime verification. Existing operator, review/merge,
public-exposure and production gates remain in force. Acceptance is still unproven.
