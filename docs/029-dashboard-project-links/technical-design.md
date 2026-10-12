# TDD-029: Validated destination projection and capability gates

- **Status:** Proposed — no implementation or deployment performed
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-029](spec.md) · **Tasks:** [TASKS-029](tasks.md)

## Interface and existing route evidence

Extend the inventory/status collector protocol with typed destination records keyed by
SPEC-027's opaque row key. Each record has a kind (app, api-docs, repository, logs or
preview), label, availability/reason, validated destination if applicable, observation
and freshness fields, and optional absolute expiry. Frontend URL creation must use the
same reviewed validation rules; do not accept URL overrides in HTTP parameters.

`scripts/private_apps.py:route_info` reports the tailnet hostname, configured prefix
and proposed URL; it can also include an operator command, which must never be projected
into browser data. Current status may report a configured Serve route for a stopped
service. Use SPEC-028 publication/readiness evidence and the owned ingress mapping,
not URL presence alone. Add a reviewed versioned read-only route descriptor reporting
exact origin, app/docs relative paths, ownership/publication and route capabilities.
Older providers return unsupported capability, not guessed links.

Review these existing templates/routing contracts during implementation:

| Supported topology | Candidate destination path to verify against installed capability |
|---|---|
| Single web | `/projects/<id>/` |
| Single FastAPI | `/projects/<id>/docs` for API docs; no web-app link |
| Web/API group, with or without DB | `/projects/<id>/` for web; `/projects/<id>/api/docs` for API docs |

The descriptor must match validated identity/base path and installed template/provenance.
Kind alone cannot prove a custom application's docs route. Do not probe arbitrary app
paths to discover links, and do not enable database, loopback-port or operator URLs.
Group health/publication policy comes from the provider; do not bypass a withdrawn
group route to expose a healthy child independently.

## Repository and optional capability adapters

Normalize repository destinations from the platform metadata described in TDD-027.
Use canonical `https://github.com/<owner>/<repository>` identities with bounded validated
segments; reject additional query/fragment/userinfo/ports and path suffix injection.
Do not read `.git/config`, broker keys or token stores. Clicking opens the repository
using the browser's own authentication; the platform never fetches it to test access.

A future reviewed log viewer advertises a stable same-origin route accepting an opaque
row key and optional validated component enum. Links exist only when that capability
is installed and its target binding matches. In this initial slice the slot is disabled
with a fixed explanation. No log read handler, secret redaction pipeline, placeholder
viewer page or raw `gptclawctl logs` bridge is implemented here.

A future reviewed preview registry supplies bounded versioned records containing
project/root binding, application route class, authoritative HTTPS origin/path, active
state, issued/expiry times and observation freshness. Reject unknown schemas, unsafe
paths, wrong identities and endpoint classes forbidden by exposure policy. Never parse
Serve/Funnel CLI output to infer a public URL or copy private origins into public links.
Use a synthetic adapter for contract tests; an absent real adapter reports unavailable.
Future live integration requires its own accepted registry/exposure evidence. This
feature has no preview lifecycle method or permission.

## URL and freshness validation

Parse destinations structurally. Accept only exact trusted hosts/origins and canonical
validated path forms for each kind. Reject userinfo, non-HTTPS schemes, protocol-relative
forms, backslashes, dot segments, duplicate/ambiguous encodings, control characters,
unexpected ports and query/fragment data. Form origin/path from validated components,
then check the final URL again. For preview URLs, trust only a reviewed registry-bound
origin, not user-entered hostname text. No backend fetch, URL-shortener lookup, arbitrary
redirect endpoint or destination reachability crawler is needed.

Private app/docs links require fresh publication/readiness data within SPEC-028's
30-second stale threshold and currently owned route metadata. Display a stable configured
address as plain text when unavailable; do not create a clickable disabled anchor.
Repository availability uses metadata, independently of runtime health. Logs availability
uses its viewer capability. Each source failure affects only dependent destination kinds.

Proposed preview freshness is at most 30 seconds; expire enabled links at the earliest
of absolute expiry or snapshot freshness deadline. Send collector time and remaining
lifetime with the response; the browser advances it with monotonic elapsed time and
revalidates on focus/visibility changes. Clock anomalies disable the link pending fresh
observation. This prevents client wall-clock skew from extending the displayed active
window. Network revocation is still owned by the exposure service; clicking near expiry
may reach a withdrawn endpoint, which must be explained without renewing it.

## Frontend and operation

Render “Open app”, “API docs”, “Repository”, “Logs” and “Public preview” where applicable,
with textual scope and unavailable reasons. Omit inapplicable web/docs controls rather
than promising nonexistent routes. For public links show expiry with timezone and
remaining time. Use semantic links for enabled navigation and text for unavailable
states. External tabs use `noopener`/`noreferrer`; internal logs destinations stay within
the private dashboard. Do not auto-open destinations or load public previews as embeds.

No separate service, database, route provisioning or project migration is needed. Roll
out this read projection and frontend increment through the existing dashboard release.
On failure disable/roll back the link increment; retain inventory/status/private routing
and optional registries. Rollback must never revoke/create previews or remove project
Serve mappings; those operations retain their own reviewed contracts.

## Verification and traceability

Use synthetic row/status/route/registry fixtures, deterministic time and client clock
skew for URL availability/expiry tests. Exercise origin/path attacks, disabled tab/link
semantics, stale route/health data, forged capability descriptors and secret-like query
values. Verify no backend network fetch or credential/exposure operations occur. Run
relevant provider/collector/frontend checks and review actual UI/routes for scope.

Live initial acceptance opens task-owned web, API and group destinations from the owner's
tailnet browser, plus a configured repository. Verify negative stopped/unrouted cases,
private visibility and unavailable logs/preview prerequisites. No public-preview creation
is part of acceptance. Record local, CI, live/browser results and deferred integration
checks separately. Later logs/preview adapters require actual accepted prerequisite
versions and new live evidence before those integrations are described as complete.

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| LNK-001 | Versioned route descriptor plus identity/health/publication checks | T-002/003 | AC-001/005 |
| LNK-002 | Canonical metadata and capability-gated internal logs slot | T-003/004 | AC-002/005 |
| LNK-003 | Display-only bounded preview adapter and expiry policy | T-004/005 | AC-003 |
| LNK-004 | Typed URL validation, no fetches, safe rendering/navigation | T-002/003/005 | AC-004 |
| LNK-005 | Independent freshness, elapsed-time expiry and accessible reasons | T-003/004/005/006 | AC-001, AC-002, AC-003, AC-005 |

The project owner approves the staged integration scope. Implementation records exact
route-descriptor schema/capability and validation bounds before rollout. Future log and
preview maintainers own compatible destination contracts; until accepted, these slots
remain unavailable without blocking app/docs/repository navigation.
