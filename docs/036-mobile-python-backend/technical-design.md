# TDD-036 — Python-backed native notes

Status: Implemented and merged; Android-first scope accepted October 21 with recorded manual-evidence waivers. Owner: Project owner.
Date: 2026-10-15 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

[Owner closeout](closeout-2026-10-21.md) supersedes the remaining acceptance
gates for this selected scope. The architecture below retains its original
requirements; waived tests are not represented as physical observations.

## Architecture and contracts

Use separate mobile and API/DB canonical roots. The device loads JavaScript through
SPEC-033/034's accepted Metro transport and sends application requests directly to
the existing private HTTPS project ingress. Metro transport exceptions do not permit
HTTP API requests. The backend runs FastAPI and PostgreSQL on its owned rootless
network; only its API is reachable through the loopback gateway/private Serve route.
No new Tailscale listener, AWS resource, host tool or second DB manager is proposed.

Add new strict project contracts for a bound mobile project and an API/DB group.
Keep schemas 1–6 and SPEC-035's pending schema 7 unchanged. Select unused versions
at implementation after reconciling concurrent work. Version provider receipts,
capabilities, catalogue schemas and snapshot inventories wherever their shape changes;
do not merely relax old required-web validation. Inspect installed capability before
rollout; a checkout is not an installed provider.

The mobile contract names the backend project ID, development profile and API
contract major. A restricted ignored local public-config file supplies the exact
private HTTPS origin/base path. Validate it against the selected canonical backend
and the existing approved private ingress identity; reject arbitrary remote URLs,
userinfo, query/fragment, insecure scheme, path escape and project-prefix mismatch.
Materialize only this allowlisted public client configuration into an ignored build
input. Include its hash/profile in job/session fingerprints, avoid concurrent edits,
and require Metro reload/restart after a change. Generated CI uses a non-routable
synthetic HTTPS fixture, never the host's private hostname. An unavailable backend
is a connection state, while invalid configuration blocks launch. Existing unbound
mobile operation remains unchanged; no automatic backend start or binding discovery.

## Backend composition and ingress

Publish a new exact backend starter derived from the accepted PostgreSQL notes API,
its migrations, portable verification and Python standards. Publish a distinct new
mobile notes starter using existing SDK/toolchain policies. Choose final names and
versions at implementation; never edit published release bytes. Generate independently
and bind explicitly, with no automatic repository provisioning in this slice.

Refactor `project_groups.py` and `project_database.py` integration around validated
component sets: legacy web/API(/DB) retains its current order and routes; the new
shape contains exactly API + DB, with DB initialization explicit and DB readiness
preceding API. Derive group readiness from declared components. Extend the gateway
so API/DB groups expose only their own prefixed API/docs/health routes and never
fall through to a nonexistent web upstream. Stale cache, failed database readiness
or an ownership mismatch must not leave useful API routes advertised as ready.
Retain current resource, timeout, lock, receipt and bounded observation behavior.
Adapt database portable tests so their correctness does not depend on a web component.
Inventory and project links must support an API landing/docs destination without
inventing a frontend or client-online status.

Use the existing notes v1 operations: paginated GET/POST collection and GET/PUT/DELETE
by ID, with existing model/input/capacity limits and safe status codes. Preserve
prefix-aware Location, OpenAPI and bundled docs. Keep liveness separate from DB/schema
readiness. No cookie-based browser authentication or permissive CORS is needed for
native clients. Expo web is excluded. This fixture has shared synthetic records and
must not be represented as authenticated multi-user storage.

## Native client and visual design

Generate checked-in TypeScript contract/client output from deterministic FastAPI
OpenAPI without a running DB. Select an exact compatible generator and frozen lock
through existing dependency policy, check its provenance/advisories and verify output
reproducibility before freezing releases. Keep network orchestration in a small typed
adapter with cancellation, a 15-second request deadline and explicit classified errors.
No silent write retries, offline queue or redundant global state framework is needed.
An uncertain save prompts refresh/reconciliation before another create attempt.
CI regenerates and checks a clean diff; an old captured client bundle is retained as
an owned compatibility fixture for the additive migration test.

Use a warm notebook visual system: paper background, ink headings, one cobalt accent,
consistent spacing/corner/elevation tokens and system type. A prominent heading and
record count lead into readable preview cards; note-order metadata and alternating
card emphasis create rhythm without changing reading order. The editor dedicates
space to title/body with a keyboard-aware save action and visible dirty/saving/saved
states. Delete uses an accessible confirmation. Use local assets only if they serve
the experience; do not add decorative package dependencies or remote font loading.

Build reusable list/editor/state components, accessible labels and screen-reader
announcements. Loading, empty, unavailable, validation, reconnect and uncertain-save
states use the same tokens. Preserve draft component state during request errors,
warn before abandoning dirty edits, and fetch saved records after relaunch. Respect
font scaling and reduced motion; verify actual 48 dp targets and colour contrast.
Capture list/editor/empty/error images from the device and obtain owner visual
acceptance alongside native interaction checks. This document chooses a direction;
it does not claim a rendered design or device review already exists.

## Verification, rollout and recovery

Use disposable owned synthetic projects and isolated offline fixtures. Test schema,
URL/admission, identity, tampering, generation, failure stages and route selection
before managed runtime trials. Run repository and generated Python/Expo gates,
contract drift/fault tests, mocked native interaction tests and real API/DB integration
checks. Browser or mocked tests cannot establish Android CRUD or accessibility.

After authorization, verify host capacity and source/installed compatibility, stage
a reviewed immutable snapshot, generate the two projects and initialize their owned
database explicitly. Record exact source/profile/client/schema/config hashes without
private host identities or credentials. Refresh the accepted SDK/client eligibility
before using the available Android device; fail unsupported combinations rather than
installing new host/native tools. Run CRUD, API reload, complete backend restart,
Metro restart, mobile relaunch, offline/reconnect and DB outage scenarios. Verify
unrelated fixture availability and ownership before and after each scenario.

Rehearse one additive schema migration using SPEC-026's stopped-project plan/apply,
verified pre-change backup and existing writer exclusion. Run v1 client CRUD before
and after; require compatible rollback source/schema and a verified recovery point.
Provider rollback stops/reconciles new contracts using the capable provider first,
retains source/role files/data/backups and restores a reviewed snapshot. Older providers
refuse new contracts; they must not reinterpret receipts. Do not downgrade schemas,
reset data or undo migrations by replacing the provider. DB restore remains a separate
reviewed target-specific operation. No destructive operation is authorized by this plan.

Stop only owned trial runtimes and withdraw their routes at closeout. Preserve
synthetic source/history and data until the owner records retention disposition;
no broad prune, listener reset or deletion of existing app state. Record local, CI,
merge, installed, device and owner results independently. No acceptance record with
passed criteria is created during planning.

## Traceability

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| MB-001 | Strict opt-in binding, local public config and activation fingerprints | T2,T3,T8 | AC-001,007 |
| MB-002 | New API/DB contract, declared-component lifecycle and prefixed gateway | T3,T4,T8 | AC-002 |
| MB-003 | FastAPI OpenAPI, pinned generated client and contract drift gates | T4,T5,T8 | AC-003,004,007 |
| MB-004 | Independent lifecycles, deadline/cancellation and recoverable native state | T3,T5,T6,T8,T9 | AC-004,005 |
| MB-005 | Notebook tokens, native list/editor and exceptional/accessibility states | T6,T8,T9 | AC-006 |
| MB-006 | Existing DB controls, persistence and old-client migration rehearsal | T4,T8,T9 | AC-004,005,007 |
| MB-007 | Immutable starters/provider packaging, adaptation, CI and evidence | T2,T7,T8,T9,T10 | AC-001,002,003,006,008 |

Routine implementation choices include unused schema/release numbers and compatible
exact client-generator pins; document them before publication. The project owner
authorized this scope after the planning PR; implementation review is pending. Android-first acceptance follows the
available accepted device; iOS requires a separate observed device matrix. If current
client compatibility or private transport cannot pass within existing contracts,
record the blocker and propose a scoped change without broadening permissions.

## Implementation selections

Provider 1.14.0 selects manifest 8 (API/DB-only), manifest 9 (bound mobile),
API/DB group receipt 4, bound Metro control receipt 3 and catalogue 7. Releases
are `fastapi-postgres@1.0.0` and `expo-notes@1.0.0`. Existing schemas/releases and
the default web selection remain unchanged. The client generator is repository-owned
v1 JavaScript using Node built-ins, frozen with the starter; it requires no new
package/toolchain pin. FastAPI emits the source OpenAPI without connecting to DB,
Python tests detect schema drift and native checks detect stale generated output.
A retained compiled v1 adapter exercises real HTTP CRUD around the isolated additive
migration, without a credential mount. UI motion is deliberately absent, so the
experience does not require animation for comprehension or reduced-motion handling.

The accepted v1 notes API has no timestamps. Cards therefore show real note order
and previews; this slice does not invent per-note dates or add an unrelated schema
change merely for presentation. Actual timestamps can be a later compatible contract
extension. The approved visual direction and Android owner review still apply.


## Preview routing amendment proposed October 15

The earlier two fixtures retain sticky slots after their accepted listener cleanup.
A separate Fieldnotes root cannot reuse their ownership. The requested preview
therefore needs the next private slot, HTTP 8445 to loopback 18605, through the
existing operator path. This amends the original listener-reuse assumption only
after owner approval of [the concrete preview plan](preview-plan.md). Existing
HTTPS API ingress, private access, source/data and unrelated handlers are preserved.

The owner approved the two repository names and exact private route on October 15.
Preserving all four current workflow names requires credential profile schema 5
with a six-name ceiling. Schemas 3/4 keep their two/four-name ceilings. Existing
App grants, one-repository token scope and publication verification are retained.
Update all registered owned helpers to a capable immutable provider before the
profile changes; first-target canary proves publication before reactivation.
