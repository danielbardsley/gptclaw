# TDD-033: Metro lifecycle and private transport

- **Status:** Implementation authorized — not installed capability
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-033](spec.md) · **Tasks:** [TASKS-033](tasks.md)

## Approach and ownership boundary

Extend the mobile adapter with a Metro session adapter; preserve non-HTTP quality
receipts. Proposed Metro receipts live outside source under the runtime store,
separate from mobile job.json, with typed schema, canonical project/root, ownership
token, generation, exact SDK/lock/toolchain/config hashes, unit/container identity,
port leases, selected origin, lifecycle/operation outcome, start/expiry timestamps
and route readback. Do not store client credentials or device identity. Stop preserves
source, dependencies and caches. Web/backend receipts retain their existing meaning.

Schema 6 was vacant and is selected for explicit opt-in. It preserves the schema-5
source fields and adds only `metro: {adapter: metro-v1, mode: expo-go, ttl_seconds: N}`
with an integer lifetime of 60–28800 seconds (default 7200). Schema 5 and published
templates remain unchanged; no host, port, environment or URL is project-declared.
Source validation capability includes schema 6 separately from actual runtime
capability. The development provider is 1.12.0; installed 1.10.1 is unchanged.
Provide a reviewed opt-in upgrade/validation operation for existing canonical source;
reject dirty/concurrently changed metadata and preserve source/provenance.
Migration reuses PRJ-006 canonical identity/configuration checks, requires tracked
clean metadata and exact mobile toolchain/dependency inputs, and revalidates under
the project lock. Atomic exchange retains displaced metadata in an owned journal
archive. A racing edit or unknown publication leaves both copies recoverable and
blocks further migration until reconciliation. Commit the reviewed manifest before
using it; the source plan digest grants neither runtime nor security permission. A new exact
starter release is needed only if reviewed source/SDK inputs change. Later MOB-004
can consume the generic transport descriptor without this spec creating its client.

Proposed CLI uses existing lifecycle verbs after mobile dispatch, with explicit
Metro enablement and a finite lifetime. Existing schema-5 behavior remains unsupported
for lifecycle. Exact flag/schema syntax is finalized and tested during implementation;
the lifecycle/transport interfaces remain pending. The implemented source command
`metro enable --project-root ROOT` emits a read-only plan; `--apply --confirm-plan
DIGEST` explicitly upgrades metadata and starts no session. A supported provider
will advertise session/runtime capability only after the adapter is available. Logs and observation
use bounded read-only provider calls; state changes stay in lifecycle/recovery paths.
Require the main-branch PRJ-006 canonical-root guard even though the installed launcher
observed at planning was older. Do not add worktree runtime previews or auto-integration.

## Session execution and bounds

Use a rootless Podman user unit with the reviewed Node/pnpm image and the project's
locked Expo CLI. Explicit frozen preparation precedes admission. A finite noninteractive
server command has explicit port/mode and disables global downloads, dotenv and
telemetry; verify pinned CLI behavior rather than copying tutorial npx invocations.
Container-internal binding may use its isolated interface; host publishing is loopback
only. Source/dependencies are read-only to the runtime, with narrowly owned writable
Expo/Metro caches and temporary files proven to support watching/transforms. Keep
CLI .expo state ephemeral and discard it at session end; persistent transform-cache
allowlists must exclude devices.json and other client-identity state. Exclude
credential stores, Git internals, private environment material and backend data; no
engine socket or forge home mount. Validate effective mounts and full URL/config output.

Proposed initial bounds: 1 CPU, 1536 MiB, 256 PIDs; session TTL 8 hours with explicit
bounded renewal, startup deadline 300 seconds, stop deadline 20 seconds and at most
three automatic restarts in five minutes. Renewal requires the same owner, current
security/inputs and route, never a disconnected phone heartbeat. Record stopped/expired
state and invalidate launch availability. Propose a 1 GiB cache ceiling per session and 10 MiB log retention per session,
with seven-day retention for stopped-session logs; never evict active source or
unknown cache directories. Keep cleanup explicitly owned and source-preserving;
measure cold transforms and request load before freezing numerical limits. A changed
ceiling needs documented scope disposition; no host resize or unbounded retry.

Reuse the shared registry lock to allocate Metro and proxy port leases atomically,
checking existing web/API reservations and actual listeners. Session-specific locks
coordinate preparation, dependency/format/integration mutations and recovery. Two
sessions require independent leases, containers and caches; unknown leftover ownership
blocks reuse. Source edits can trigger transforms; dependency/toolchain/config changes
require controlled restart and input revalidation. Do not silently restart another app.

## Private transport proposal and protocol spike

Prefer one origin-root private HTTPS listener per session, forwarding to a bounded
loopback Metro proxy; dedicated origins avoid relying on Expo accepting a web-style
path prefix. Select an exact finite listener pool after checking the installed
Tailscale version, Serve support, current occupancy and owner access policy. No ports
are assumed free or configured by this draft. Keep existing HTTPS-443 handlers intact.
Do not reuse the buffered web ingress as-is. A path-prefix alternative is acceptable
only if the pinned SDK and actual devices prove every advertised URL/endpoint and
cross-session isolation; record the final reviewed choice before productionizing it.

The proxy derives allowed upstream/origin from owned receipts, checks Host/path/header
bounds and refuses caller-supplied targets. Use streaming/backpressure, a proposed
64 MiB per-response ceiling, eight connections per session, 16 KiB header bounds,
finite connect/handshake/idle timeouts and shutdown cancellation; measure representative
bundles/assets before freezing bounds. WebSocket lifetime cannot exceed session expiry.
Verify reconnect after idle closure and compile activity; a transport health endpoint
is not proof that a bundle compiles or a native client renders.

Before adapter implementation, run an authorized security-cleared spike with the
exact SDK. Capture sanitized manifest/bundle/asset/source-map origins, redirect rules,
request/response headers necessary for native delivery, and HMR/reload WebSocket
behavior. Verify whether pinned CLI supports the advertised proxy origin correctly;
do not rewrite signed payloads or ignore TLS/signature failures. Use manual launch
with an eligible existing native client for the spike if available; the product's
Go compatibility/QR UX belongs to SPEC-034. Desktop protocol probes alone do not close
physical acceptance. If Expo Go cannot supply a client, a separately accepted MOB-004
client is a dependency, with no automatic account/build fallback.

Operator handoff specifies exact new listeners/targets, access selectors and existing
config hash/readback. Forge installs only owned loopback units and emits route-pending
status until private readback/probes pass. The reviewed operator adds/removes only
owned Serve targets, preserving unrelated listeners. Expiry/stop closes the loopback
proxy and descriptor; stale operator config cannot expose a new project through a
recycled lease. Reassignment requires explicit lease/listener generation reconciliation.

## Security and observation

The delivered source-only advisory exceptions cannot authorize Metro. Preparation
collects fresh exact audit/package evidence and runtime threat analysis; patched pins
or an explicitly approved runtime disposition precede even a network spike. Keep a
separate enforced runtime admission record with owner/scope/expiry/removal; don't edit
published policy files or widen the source exception. Check again on start/renewal,
and use a bounded supervision check to revoke an expired approval during a session.
Existing expiry never grants permission to run until the session's nominal TTL.

Expose process, protocol and private route freshness independently through safe
observation. A typed descriptor includes generation, canonical project, approved mode,
private origin, supported targets, observed time/expiry and eligibility reasons.
It has no fake web app URL or device count. Minimal dashboard source/session rendering
may consume that capability after a frozen collector refresh; build/install/device
telemetry remains MOB-009. SPEC-034 alone generates Go launch payloads from it.

## Verification, rollout and traceability

| Requirements | Mechanism / task | Acceptance |
|---|---|---|
| MET-001/002 | Contract/canonical guard, typed receipts, atomic leases, user units; T-003/004 | AC-001/002 |
| MET-003/004 | Security-cleared SDK spike, streaming proxy, exact operator plan; T-002/005 | AC-003/004 |
| MET-005 | Safe observation/descriptor and minimum inventory changes; T-006 | AC-005 |
| MET-006 | Fresh runtime security/admission, mount/log/environment checks; T-002/004 | AC-006 |
| MET-007 | Reconciliation, capable snapshot rollback and fixtures; T-007/008 | AC-007/008 |

Local/CI fixtures exercise contracts, collision/drift, lifecycle transitions, expiry,
concurrent mutation, large responses, long-lived/idle WebSockets, hostile origins,
TLS failures and cleanup with no secrets. Real rootless integration measures limits
and two-session independence. Operator readback, permitted/denied network tests and
actual physical iOS/Android loads/reloads remain separate required evidence. Specify
exact synthetic roots/retention before live work; preserve existing groups and source.
Install a reviewed combined provider, then any required frozen collector/UI release.
Rollback stops/reconciles new sessions and revokes owned routes before selecting an
older snapshot; keep a capable snapshot for receipt recovery and retain caches/source.

Decisions before implementation: final schema/CLI encoding and current provider
compatibility (implementation author); runtime advisory disposition (project owner
after concrete evidence); origin/listener/access plan (operator/project owner after
spike); verified per-platform client and physical devices (project owner/implementer).
Other contracts/tests can be drafted while these are unresolved; no service starts
from planning or an unapproved runtime policy.

Primary references checked October 13:
[Expo CLI](https://docs.expo.dev/more/expo-cli/) documents local serving and advertised
proxy origins; these are candidates requiring exact-version/native tests, not proof
of this design. [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)
describes private serving; actual listener/access configuration still needs reviewed
operator ownership. [SPEC-031 security scope](../031-expo-project-creation/security-review.md)
excludes Metro and is the authoritative limit on existing exceptions.

## State boundary implementation checkpoint

`metro_state.py` now validates a separate receipt schema 1 with exact project/root/
canonical key, ownership token and generation, immutable image/input/policy/unit
hashes, bounded paired ports/origin, finite lifetime and independent process/protocol/
route timestamps. Its pure descriptor hides an origin on expiry, stale/future
observations, input drift, pending/failed route, unknown operation and inactive phase.
It reports transport readiness separately from source quality and native-client
acceptance; it emits no Go URI, web app link, credential or device-online claim.
This boundary is bundled for the forthcoming controller. It is not yet connected
to live lifecycle/collector observations and adds no installed session capability.

## Controller source checkpoint

Source lifecycle now freezes the provider in an exact forge user service, with
sticky per-project Metro/proxy slots and independently observed protocol state.
The unit definition/readback must match the receipt with no drop-ins. Mutating
source jobs also require a confirmed inactive unit, preventing automatic restart
races. A registry-bound `metro recover-stop` uses the exact generation and unit
proof even if app metadata is invalid. Partial outcomes preserve owned receipts
and prior generations; they do not kill foreign resources or claim shutdown.

The source log interface exposes enumerated lifecycle events only, bounded to
256 records/64 KiB/seven days, with no persistent raw SDK output. Exact policy
revocation has a read-only plan and explicit marker publication; frozen supervisors
check the shared marker. Fresh audit execution is bounded by remaining session
lifetime. These are tested source mechanics, not completed installed/live evidence.
Streaming private proxy, operator readback, persistent cache/renewal measurements,
collector/native presentation and actual two-session/device acceptance remain open.


## Streaming proxy source checkpoint

The source supervisor now owns its paired loopback proxy in the same user-service
process. The adapter binds only 127.0.0.1 and derives upstream/origin/generation
from the typed receipt. Eight concurrent forwarded connections, 16 KiB headers,
64 MiB response/WebSocket bounds, bounded symbolication input, fixed forwarded
headers and deadlines protect each session. It streams Content-Length, chunked
and EOF responses with drain/backpressure rather than buffering a full bundle.
Manifest bodies and signing headers are preserved; no manifest/signature rewriting.

Host/Origin/credential/traversal/framing/redirect inputs reject before forwarding.
Device/identity headers are discarded. HTTP launch at the origin root currently
requires the exact generation query; SDK bundle/assets/maps and /hot plus /message
keep their verified root paths. This host-side stale-launch guard still requires
actual native-client URI/query preservation evidence in SPEC-034; no launch/QR
capability or working phone claim follows from the synthetic test.

WebSocket handshake/accept, mask direction, opcodes, continuation/control framing,
size and expiry are checked before bounded forwarding. Shutdown closes both
transports and cancels in-flight work before waiting for the Python 3.12 listener
to release. Exact policy revocation is checked through the live receipt loader.
Private route readiness remains pending; no operator listener is created.

## Implemented private route boundary

metro_routes.py produces read-only plans bound to the canonical registry,
sticky HTTPS origin and exact odd-port loopback target. Digest-confirmed local
recording rechecks current configuration under the registry lock and runs no
Tailscale mutation. Occupied unrecorded listeners block; only previously recorded
exact targets can be subtracted when comparing preserved baseline handlers across
two sessions. Wrong targets, extra handlers, Funnel, unknown configuration or
baseline drift fail closed.

The owned supervisor independently observes Serve readback plus default-trust
HTTPS health matching project/generation/expiry every ten seconds. Config
readback alone cannot establish readiness; host TLS verification alone cannot
establish phone access/native rendering. Existing process/protocol freshness remains
separate. Operator commands/access selectors and rollback are documented in the
[concrete plan](operator-plan.md); actual operator/device acceptance is pending.
