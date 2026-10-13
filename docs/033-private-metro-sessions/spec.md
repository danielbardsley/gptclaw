# SPEC-033: Owned private Metro sessions

- **Status:** Draft — planning requested; implementation not authorized
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Feature:** MOB-002 — Physical-device development
- **Supporting slices:** RUN-002/003/004/005; NET-104 and Metro-specific NET-102; minimal inventory compatibility
- **Design:** [TDD-033](technical-design.md) · **Tasks:** [TASKS-033](tasks.md)
- **Dependencies:** [MOB-001 acceptance](../031-expo-project-creation/acceptance.md), [PRJ-006](../032-branch-worktree-policy/spec.md), [mobile sequence](../platform/sequence-mobile.md)

## Outcome and scope

A canonical Expo/React Native project can start, inspect, stop and restart an owned
Metro development session on the forge host. A permitted physical device reaches
its manifest, native JavaScript, assets and reload channel over the private tailnet.
Sessions survive an operator terminal disconnect and remain isolated from other
projects and backend lifecycles. Stopping Metro stops development delivery, not an
installed application's existence or an independently managed API/database.

The project owner requested separate MOB-002 and MOB-003 specs. This authorizes
planning and a reviewable PR only. This spec owns lifecycle, protocol transport,
operational readiness and a typed endpoint descriptor. [SPEC-034](../034-expo-go-workflow/spec.md)
owns Expo Go compatibility, user launch/QR presentation and the supported client loop.
MOB-002 can use a compatible existing native client during its protocol spike; it
adds no signed client creation. Its provider/interface must precede MOB-003, while
physical-device acceptance may be coordinated across both initiatives. MOB-003 does
not require an already Delivered label when it supplies joint device evidence.

Include standalone mobile projects without a backend, two independent sessions,
reviewed private routing/operator handoff, bounded resources/logs/lifetime, recovery,
source-only worktree safeguards and honest source/session readiness. Exclude EAS,
Expo/Apple/Google credential setup, native compilation/signing, public tunnels/Funnel,
production, backend binding (MOB-010), parallel worktree previews, web export, and full
device/build/release dashboard telemetry (MOB-009). No backend CRUD or full M1 claim
is made by this slice. Proposed iOS and Android coverage requires real devices for
both; an owner-selected first-platform slice must be explicitly labeled.

## Observed baseline and constraints

MOB-001 is Delivered: schema 5, immutable expo-react-native@1.0.1, SDK 57.0.28,
React Native 0.86.3, React 19.2.3, Node 24.21.0/pnpm 12.10.1 and source-quality jobs.
Mobile lifecycle remains unsupported. Main now includes PRJ-006/provider 1.11.0,
but the stable launcher observed during planning reports 1.10.1. This is a source/
installed difference, not an instruction to replace either version during planning.
Implementation must preserve the newer worktree contracts and publish a compatible
combined snapshot; runtime admission is canonical-root-only.

The current web ingress recognizes /projects/, requires web/group ready receipts,
buffers responses with a 2 MiB limit and forwards WebSockets. That is not accepted
Metro transport: native bundles/assets and origin-root URLs need their own verified
contract. Existing private /projects/ and /dashboard/ handlers must be preserved.
Forge cannot administer Tailscale; host security/access changes use the reviewed
operator path, and AWS changes, if ever needed, use the protected IaC pipeline.

MOB-001's node-forge/braces exceptions are source-check/export-only and explicitly
exclude Metro. They grant no runtime permission. A patched reviewed graph or a fresh,
concrete runtime security disposition is required before a Metro spike or rollout.

## Requirements

### MET-001 — Explicit supported contract

Add a versioned, opt-in Metro runtime contract/capability for validated mobile source.
Keep source/quality, host Metro readiness, private transport readiness and native
client acceptance distinct. Existing schema-5 source projects remain valid and
unsupported until explicitly enabled; never fabricate a web/API service. Validate
static public configuration, exact tools/lock/policies and canonical checkout identity
before writes. No automatic SDK upgrade, package install script or native generation.

### MET-002 — Owned lifecycle and bounded operation

Reuse project/registry locks, owned containers/user units, toolchain/dependency
preparation and durable receipts. Start is idempotent for matching inputs; drift,
occupied ports, concurrent jobs or unknown outcomes fail with owned recovery guidance.
Two projects have distinct ports/units/cache scopes. Stop/restart acts only on the
selected session. Service supervision, bounded restart attempts and explicit session
expiry survive shell disconnect without leaving an unmanaged terminal process.
Running Metro conflicts with mutating dependency/toolchain/format/integration jobs;
status and read-only operations remain available. Ordinary approved app source edits
support Fast Refresh. Managed task worktrees are source-only and cannot activate,
retarget or silently operate the canonical runtime.

### MET-003 — Private complete native transport

Provide tailnet-only TLS access to all required manifest/bundle/asset/source-map and
WebSocket endpoints for the selected SDK. Advertised URLs must resolve to the owned
origin, never host/container loopback, an unapproved LAN address or a public relay.
Handle large responses by bounded streaming, backpressure and cancellation; isolate
per-session capacity so development traffic cannot starve web/API/dashboard services.
Devices use the approved tailnet access policy. Explicitly verify permitted-device
access and denied external/unpermitted access. No automatic tunnel, Funnel, LAN
listener, certificate bypass or arbitrary proxy target/Host rewriting.

### MET-004 — Operator route ownership

Separate loopback running from private-route readiness. Produce an exact reviewed
operator plan for absent private Serve listeners and access-policy changes, including
conflict readback, ownership, rollback and narrowly scoped removal. Forge performs no
privileged administration. An occupied/unowned listener blocks; never reset Serve,
replace /projects/ or /dashboard/, weaken host controls or broaden credentials.
Stopping or expiring a session must make its published endpoint unavailable even
when an operator-created listener remains; removal is a separate owned operator action.

### MET-005 — Truthful observation and launch descriptor

Expose bounded CLI status/logs and a versioned native endpoint descriptor with project,
session generation, mode eligibility, origin, freshness and expiry. Running process,
protocol readiness and private reachability are separately observed; no claim that a
phone is online follows from a healthy Metro process. Unready/stale/expired sessions
have no available launch target. Keep native session state separate from existing
web/backend status. Inventory may show a minimal Metro state without adding fictitious
components, web Open app links or MOB-009 device/build telemetry. Expo Go QR belongs
to SPEC-034; do not present an unverified transport as a supported client workflow.

### MET-006 — Security and source/data protection

Require an exact runtime threat/dependency review before first execution/exposure.
Runtime exceptions, if needed, name advisory/package/version, owner, mitigation,
expiry and removal; unexpected findings/expiry block start and report running-session
revocation rather than silently extending approval. Runtime shutdown on revocation
must preserve source and unrelated services. No signing, GitHub broker, backend or
production credentials/home/engine socket/data volumes are mounted or forwarded.
Allow only reviewed public environment values; dotenv/telemetry and public tunnel
fallback remain disabled. Sanitize bounded logs/receipts and avoid persisting device
identifiers, request headers, tokens or full manifests. Source/native directories,
persistent data, immutable templates and approved source-only policies are preserved.

### MET-007 — Recovery, rollout and rollback

Reconcile start/stop timeout, crash, expired session, ingress failure and stale owned
leases from exact receipts. Never kill unknown processes or reuse an unresolved port.
Retain recoverable caches/source, stop orphaned owned jobs only after proof of ownership,
and report partial outcomes. Package the same contracts in source/installed providers
and frozen collector releases. Before older-provider rollback, stop/reconcile sessions
with a capable snapshot, revoke routes and preserve receipts/source; older snapshots
must explicitly reject unsupported runtime contracts. Existing app/data/credential
behavior must remain intact through refresh and rollback.

## Acceptance criteria

| ID | Required evidence | Requirements |
|---|---|---|
| AC-001 | Versioned opt-in/capabilities validate; historical contracts/source remain valid; invalid config, wrong-root/worktree and unsupported SDK inputs cause no writes. | MET-001/002 |
| AC-002 | Two real owned rootless sessions start idempotently, survive SSM disconnect, stop/restart separately and expire; colliding/drifting/concurrent/unknown ownership cases preserve other source/services/leases. | MET-002 |
| AC-003 | Permitted physical native client loads manifest, a bundle larger than 2 MiB, assets and sustained reload/WebSocket traffic over the selected private origin; large/slow/malformed/foreign-origin traffic is bounded. iOS/Android results are recorded independently. | MET-003 |
| AC-004 | Operator plan/readback proves owned route/access policy, denied outside/unpermitted access, preserved handlers and Funnel off. Stop/expiry disables the endpoint; removing only owned listeners preserves others. | MET-003/004 |
| AC-005 | CLI/collector distinguish loopback running, route pending, ready, failed, stale and expired; descriptor has correct origin/generation/expiry and unavailable launch on failure. No device-online or backend-health inference. | MET-005 |
| AC-006 | Exact runtime security disposition precedes execution; exception/version/expiry and secret/config/admission denials pass; logs/source/bundles contain no fixture secrets or persistent device identity. | MET-006 |
| AC-007 | Crash, bind/route/health failure, interruption and lease recovery are rehearsed; compatible refresh/rollback and older-provider rejection retain source/data and existing apps. | MET-007 |
| AC-008 | Local/CI protocol and regression checks, installed operations, operator and physical-device evidence are separate; owner accepts lifecycle/private device behavior, implementation merges and retention/runbook records are complete. | MET-001–007 |

## Completion and decisions

Deliver implementation, meaningful ownership/protocol/security tests and a reviewed
Metro runbook through a PR after approval/implementation authorization. Runtime
security and exact private operator route scope are separate concrete decisions;
planning alone changes neither. Synthetic targets/retention are selected before live
work; Shelfmark, Trailboard and existing data remain untouched. Keep MOB-002 Draft
until disposition, and mark Delivered only after merge and AC-001–008 pass. Physical
native acceptance cannot be replaced with desktop HTTP/WebSocket tests; if a compatible
client is unavailable, record Implemented/pending device evidence and address MOB-003
or separately approved MOB-004 rather than claim completion or open a public tunnel.
