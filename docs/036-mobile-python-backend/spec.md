# SPEC-036 — Mobile integration with a Python backend

- **Status:** Draft for review; planning requested, implementation not authorized.
- **Owner:** Project owner
- **Date:** 2026-10-15 (America/New_York)
- **Feature:** MOB-010; supporting development-only MOB-005, RUN-006/011,
  TPL-003/004, QLT-008 and Android acceptance slices of MOB-011/QLT-005.
- **Design:** [TDD-036](technical-design.md) · **Tasks:** [TASKS-036](tasks.md)
- **Direction:** [Mobile sequence](../platform/sequence-mobile.md)

## Outcome and scope

An Expo application on the project owner's Android device reads and writes
synthetic notes through a private Python/FastAPI API backed by PostgreSQL.
Records survive backend restart and mobile relaunch. The native interface looks
intentional and interesting, supports comfortable everyday editing, and explains
connection failures without losing an unsaved draft during a transient outage.
This closes M1's backend integration gap when combined with the accepted
creation/Metro/Go workflow; it does not establish iOS or production readiness.

The project owner requested this specification after selecting Python for all
application backends, and requested a good-looking, interesting UI. FastAPI is
the selected backend here and the default recommendation for subsequent mobile
application work. SPEC-035's optional Fastify template remains separate work;
this initiative neither depends on it nor changes its authorization. The owner
requested planning only for this initiative. Review, implementation authorization,
merge, rollout and owner acceptance remain distinct.

Include a reusable API/DB-only project shape and exact immutable starter, an
opt-in bound Expo starter, explicit development configuration, typed API contracts,
a polished synthetic notes experience and real Android end-to-end evidence.
Mobile and backend are separate canonical projects with independent lifecycles.
Preserve existing standalone mobile projects and published starter releases.

Exclude signed clients, iOS acceptance, EAS/accounts/signing, store distribution,
OTA updates, production/local/preview environment execution, public exposure,
real-user authentication/data, offline write queues, conflict resolution, push,
new cloud infrastructure and migration of existing applications or user data.
This is a private shared synthetic demonstration; tailnet access is not per-user
application authorization. Full MOB-005/MOB-011 and production work remain open.

## Observed baseline

- SPEC-031 creation and SPEC-033/034 Metro/Go are delivered for the accepted
  Android-first matrix. Physical acceptance records Android 11 / Expo Go 57.0.9;
  revalidate compatibility and profile freshness before new trials.
- Mobile manifests v5/v6 have no backend binding. Schema v6 supports the owned
  Metro contract; do not extend either published schema in place.
- SPEC-026's `notes-postgres@1.0.0` has FastAPI/PostgreSQL persistence but requires
  web + API + DB. `project_groups.py` uses a fixed API/web order and web fallback
  routing. API/DB-only lifecycle and ingress are proposed extensions.
- Database initialization, role files, migrations, backup and recovery already
  exist. Reuse them; stop retains persistent storage. Source inspection does not
  prove the currently installed provider or live service state.
- SPEC-035 currently occupies proposed project schema 7/catalogue 6 in the dirty
  working tree. Allocate new versions against merged/source state at implementation;
  do not reserve conflicting numbers or make Fastify a runtime prerequisite.

## Requirements

### MB-001 — Explicit mobile/backend binding

Use a new versioned opt-in contract with mobile project ID, backend project ID,
`development` profile, absolute private HTTPS API base URL including its project
prefix, and supported API contract version. Verify the backend's canonical identity
and Python/PostgreSQL capability before managed activation. Reject missing,
conflicting, unsupported, insecure, loopback, credential-bearing or public-target
bindings before network operations. No implicit backend/environment selection.
No arbitrary code or whole environment import is allowed to resolve configuration.
Existing unbound mobile projects remain usable and are not silently upgraded.
Profile changes require validation and an explicit reload/restart; already-loaded
clients must not silently switch backend. Keep private hostnames out of committed
starter defaults and public acceptance evidence.

### MB-002 — Python API and persistent database without a web service

Deliver a strict API/DB-only shape using existing FastAPI/Python/uv and PostgreSQL
profiles, with explicit exact release selection and provenance. No Node API or
unused web server is required. Reuse project locks, private network, resource limits,
receipts and DB ownership/recovery. Initialize explicitly; start DB then API and
publish only when DB/schema/API are ready. Stop removes only owned activation and
routes, retaining source, credentials, records and backups. No automatic migration,
seed, reset or data recreation on start. No published DB port. Existing three-service
and standalone web/API/mobile projects retain their behavior.

### MB-003 — Typed versioned native API contract

Expose prefixed `/api/v1/notes` CRUD with bounded pagination, typed IDs/title/body,
input limits, safe validation/missing-record errors and OpenAPI. Retain health,
readiness and private bundled docs. Produce a deterministic TypeScript client from
Python OpenAPI using reviewed pinned tooling; CI rejects stale client/contract
output. Only public configuration/types enter the mobile bundle. Native requests
use private HTTPS without browser cookie or desktop same-origin assumptions.
Preserve the accepted v1 CRUD contract across the initial compatible schema change;
breaking contract versions fail explicitly rather than corrupting client state.

### MB-004 — Reliable independent operation and recovery

Report Metro session, backend API/database health and client connection separately.
Starting/stopping/restarting Metro never mutates the backend; backend operations
never mutate Metro or unrelated projects. API/DB failures withdraw useful API
availability and yield a recoverable native error. Use bounded requests/cancellation;
no automatic retries of writes or misleading success after an uncertain response.
Retain unsaved editor state through transient request failures, expose retry and
refresh, and reconcile server state after reconnect. Relaunch refetches saved data;
persisting unsaved drafts/offline edits across relaunch is excluded.

### MB-005 — Distinctive, polished native interface

Deliver a designed notes list and full-screen editor, not an unchanged starter or
an unstyled CRUD form. Use an editorial notebook direction: warm paper surfaces,
ink typography, a restrained contrasting accent, strong title hierarchy and
asymmetric card rhythm derived from real note previews. Avoid random decoration,
remote fonts/assets and a web dashboard squeezed into a phone. Provide a visible
create action, useful preview/date metadata, comfortable editing, clear save state
and deliberate delete confirmation. Motion is subtle and respects reduced motion.
Keep list, editor, empty/loading/error/reconnecting states visually coherent;
use skeletons where useful and show success only after the server confirms it.

Use native safe areas, keyboard avoidance, scrollable forms, screen-reader labels,
logical focus order, text scaling and at least 48 dp interactive targets. Normal
text contrast is at least 4.5:1; meaning never relies only on colour. Preserve drafts
when delete is cancelled or requests fail, and distinguish a failed save from an
unsaved edit. Record screenshots of list/editor and exceptional states for owner
visual review on the Android acceptance device. These images supplement actual
interaction/accessibility checks and are not device evidence on their own.

### MB-006 — Safe data and migration compatibility

Use only new owned synthetic fixtures, capped by existing starter limits. Retain
SPEC-026's stopped-writer plan/apply, backup verification, role separation,
retention and recovery controls. Prove saved records survive API source reload,
API/backend restart, Metro restart and mobile relaunch. Test a compatible additive
migration with a previously built v1 client bundle. Provider rollback does not
reverse DB migrations; preserve compatible source/schema and verified recovery
points. Do not change existing applications, source, data, role files or listeners.
No server secrets, DB URLs, request bodies or raw internal errors in bundles/logs.

### MB-007 — Repeatable delivery and honest acceptance

Publish new immutable backend/mobile starter releases, versioned contracts and
provider capabilities with offline generation and installed/source parity tests.
Unselected generation keeps its web default; selecting the mobile backend workflow
uses Python. Include generated guidance, pinned CI, typed-contract checks and
runbooks. Adapt starter UI/routes/tests to this synthetic notes scope: retain notes,
health/docs/security intentionally; remove unrelated counter/echo/demo screens and
update imports, OpenAPI and tests together. Old providers reject new contracts
without execution or mutation. Minimal inventory/API links must handle the new
backend shape honestly; broader dashboard controls/telemetry are excluded.

## Acceptance criteria

| ID | Required observable evidence | Requirements |
|---|---|---|
| AC-001 | Valid explicit bindings resolve the intended Python backend; malformed/profile/version/URL/identity mismatches fail before activation or requests. Old unbound projects and old-provider refusal pass. | MB-001,007 |
| AC-002 | Two new API/DB-only fixtures generate deterministically offline and pass ownership, readiness, lifecycle, routing and existing-stack regressions; no web unit or DB host port is created. | MB-002,007 |
| AC-003 | Generated Python and native quality/contract gates pass; stale types, invalid payload and breaking contract fixtures fail. Prefixed API/docs work over private HTTPS on the device. | MB-003,007 |
| AC-004 | Physical Android creates, lists, opens, edits and deletes synthetic records; empty/paginated results and validation are correct. Restart/reload/relaunch scenarios retain saved records. | MB-003,004,006 |
| AC-005 | Device tests cover offline/network return, API/DB outage and failed/uncertain save with draft retention, explicit recovery and no automatic duplicate writes. Metro/backend stop/restart isolation and unrelated-service preservation pass. | MB-004,006 |
| AC-006 | Owner accepts list/editor visual quality and exceptional-state screenshots; physical checks cover keyboard, large text, TalkBack labels/focus, target sizes, contrast and reduced motion. Starter remnants outside scope are absent from rendered UI and exposed API. | MB-005,007 |
| AC-007 | Stopped-writer compatible migration and previously built v1 client CRUD pass; verified backup/recovery and capable-provider rollback rehearsal retain data/source and refuse incompatible providers. Sanitized bundle/log checks find no server secrets. | MB-001,003,006 |
| AC-008 | Relevant repository/generated CI pass, implementation is reviewed/merged, installed provider parity and scoped rollout are verified, runbooks/evidence are complete and owner accepts Android M1. iOS and other pending work remain labeled. | MB-007 |

## Completion and ownership

Deliver implementation through the repository PR workflow after implementation
authorization. Record local tests, generated CI, platform CI, merge, installed
rollout, physical device and owner acceptance separately in an acceptance record
when evidence exists. MOB-010 becomes Delivered only after merge and AC-001–008;
MOB-005/011 retain their broader scope. The project owner reviews this plan and
accepts the final native experience. The implementation author selects compatible
exact tool pins from existing reviewed profiles and verifies any new client tooling;
no host installation or account changes are implied.
