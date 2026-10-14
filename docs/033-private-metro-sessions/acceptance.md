# SPEC-033 acceptance tracking

- **Status:** In progress — private HTTP, installed rollout and Android edit/recovery verified; final owner/delivery gates pending
- **Owner:** Project owner
- **Observed:** October 14, 2026 UTC
- **Specification:** [SPEC-033](spec.md) · **Design:** [TDD-033](technical-design.md) · **Tasks:** [TASKS-033](tasks.md)
- **Context:** Main fd6566426e0f18f16bc19150edcc113902da3e84;
  planning commit 66c19a26eb9fba81812165b6c7bda3d390e776ed / [PR #77](https://github.com/danielbardsley/gptclaw/pull/77).
  Installed implementation is on codex/mobile-metro /
  [draft PR #78](https://github.com/danielbardsley/gptclaw/pull/78); implementation CI and runtime rollout pass; merge and final acceptance remain pending.

## Criterion mapping

| Criterion | State | Current evidence and remaining action |
|---|---|---|
| AC-001 | Passed | Schema-6 opt-in, canonical/input denial, versioned capabilities/receipts and installed parity pass. Historical contracts and immutable releases are preserved. |
| AC-002 | In progress | Real independent sessions, idempotence, SSM reconnect, crash restart, mutation/input drift denial and bounded expiry pass. The repeated physical stop/isolation check now passes: app one is unavailable while unchanged app two remains usable. The earlier both-failed result remains recorded; intended-session restart/crash/expiry checks remain pending. |
| AC-003 | Passed (Android-first) | Private manifests, >2 MiB native bundles, assets/maps and both WebSocket paths pass. Owner verifies Android 11 / Go 57.0.9 native load, local assets, Fast Refresh and reload. Owner selected Android-first delivery; iOS remains explicitly unsupported/follow-up. |
| AC-004 | In progress | Approved HTTP conversion, exact route readback, preserved HTTPS handlers/Funnel off and owner-reported off-tailnet denial pass. All devices on this tailnet are owner-permitted. Exact operator-owned listener-removal readback remains pending. |
| AC-005 | Passed | Installed CLI/collector distinguish readiness/expiry and withdraw launch targets; typed generation/origin/expiry, source parity and Go-only rollback/roll-forward pass. No device-online/backend-health claim is made. |
| AC-006 | Passed | Exact runtime disposition, effective mounts/resource/environment predicates, bounded sanitized records, tested exception/version/expiry denials and live lock/environment-file admission shutdown pass. A separate allowed source-exclusion probe proves the synthetic private canary file is absent from the SDK view and native bundle; failed forbidden-dotenv probes remain recorded. |
| AC-007 | Passed | Offline bind/route/health/interruption/foreign-lease boundaries, real owned crash recovery, bounded expiry/reconciliation, actual private renewal, capable refresh/rollback and older-provider rejection pass. Source/data and the existing app baseline are preserved; preexisting group degradation is not reported as healthy. Physical reconnect remains tracked in AC-002/003 and SPEC-034 AC-005. |
| AC-008 | In progress | Implementation CI passes at 92119fb; documentation CI passes at ca460b5. Installed rollout/parity/rollback and Android owner evidence are recorded separately. Final matrix, device recovery, owned listener removal, review/authorized merge and delivery remain pending. |

## Actual local verification

- Eight cases in `python3 -B scripts/tests/test_metro_security.py` passed.
- Twenty-one cases in `python -B scripts/tests/test_metro_spike.py` passed using the
  prepared Python 3.12 manifest environment. Synthetic offline fixtures only.
- `metro_spike.py --project-root /srv/forge/projects/mob001-accept-one --origin
  https://forge-dev-01-4.tail8c3304.ts.net:8443 --seconds 300` returned approval-pending,
  a read-only plan with ten filtered source files, and no route operation.
- The same command with `--apply` returned exit 1 / blocked at the absent owner
  runtime approval, before lock/store/container/network writes.
- `./scripts/check-repository.sh` completed with exit 0 using the prepared manifest
  environment. This checkpoint ran the full offline repository suite; subsequent
  protocol integration was verified with the focused tests below.
- Ten cases in `python -B scripts/tests/test_metro_protocol.py` passed against
  task-owned loopback HTTP fixtures: a 3 MiB stream, byte/header/deadline limits,
  redirects, foreign/credential URLs and malformed/truncated manifests. An initial
  deadline-test revision exposed an EOF/socket-close bug; the corrected revision
  passed all ten cases. These are synthetic protocol tests, not an SDK/phone result.
- Diff whitespace, checker shell syntax and new relative-link review passed.
  All 59 focused security/spike/protocol/opt-in cases are registered in the checker.
  This includes a real host-identity denial case and explicit opt-in recovery tests.
  The full local gate completed with exit 1 from the two obsolete manifest-test
  assumptions described below. Every other suite passed. The corrected complete
  28-case manifest suite passed separately, and CI then passed at fb7f4b2.

The initial preparation had no Metro startup. Subsequent owner approval enabled
two bounded loopback SDK spikes; see [SDK evidence](sdk-spike.md). No private
route, phone client or installed rollout was executed. Source-check audit containers are covered by the existing source-only
scope and do not prove runtime acceptance. Terraform/deployment checks are not
applicable to this source preparation.

## Owner reports and remaining work

An authorized owner relay reports Android 11 on the development tailnet, with
Expo Go described as up to date. Exact model and OS build remain unknown; the owner subsequently reported Expo
Go 57.0.9 supporting SDK 57. No actual native load/interaction/reload was
reported for this initiative.
No iPhone is confirmed. Both platform criteria remain pending.

Use only the approved retained mob001-accept-one/two synthetic roots within the
recorded runtime scope, preserving their Git history/source. Shelfmark, Trailboard, existing app
routes/data and immutable starter releases have not been changed. Security approval,
SDK spike, provider/transport, exact operator scope, physical evidence and merge
remain distinct gates; the active goal stays open.

## Source-contract progress

The source provider now reports development version 1.12.0, source manifest schemas
1–6, `metro_actions: [enable]`, an empty Metro session-schema list, and runtime
manifest schemas 1–4. Schema 6 is not advertised as a working runtime. Existing
schema-5 generation and immutable releases are preserved. Frozen provider bundling
includes the new validator/migration; no new snapshot was selected for live operation.

The final opt-in fixture suite passed 18 cases, including exact toolchain/profile
fingerprints and wrong-toolchain denial. Initial failures were fixture assertions that overlooked
creation's existing identity lock; assertions now compare against the actual initial
store. The full regression run found two outdated manifest-test assumptions: schema 6
was still listed as unsupported, and a proposed sixth cache slot exceeded the
existing five-entry test bound. Unknown-version coverage now uses schema 7; the
five-entry cache bound was preserved. Both focused cases passed after correction.
The completed full run had no other failures. Its exit 1 is retained rather than
reported as a clean rerun. The complete corrected 28-case manifest suite passed
and the new-head CI quality jobs later passed.
A canonical read-only plan for retained mob001-accept-one succeeded with no apply,
service or route change. Current stable launcher remains provider snapshot
48a1131521aae5c2e6671faec8b3a1701c56976de6a3099f1d1d0887a4f5a5ba / version 1.10.1.

That actual installed provider rejected a task-owned schema-6 fixture via `validate`
with exit 1 and `version`; the fixture was unchanged and no runtime was started.
Only the owned temporary fixture was removed. This is installed backward rejection
evidence, not installation or session/rollback acceptance for 1.12.0.

At 319925ab20653fc6ee14d9ca2f579c7ad493adf2, the private application workflow
[passed](https://github.com/danielbardsley/gptclaw/actions/runs/38480679547). The dev-host
and Tailscale-federation workflows failed in repository checks because the new
simulation tests incorrectly hit forge's UID-1002 guard on the runner. The test
boundary now mocks operator admission only for simulated jobs; a separate negative
case proves the actual foreign/root UID guard remains enforced. There was no apply,
permission change or genuine Metro job. Final CI at the new revision remains pending.

## CI and final source-job guard checkpoint

At fb7f4b20185905a0f5b355a4640c584aff8396f1 all four workflows passed:
[private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38484536211),
[dev-host checks](https://github.com/danielbardsley/gptclaw/actions/runs/38484536150),
[Tailscale-federation checks](https://github.com/danielbardsley/gptclaw/actions/runs/38484536222),
and [dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38484536162).
Protected infrastructure plan/apply were skipped, not executed. Source creation,
legacy apps/database/dashboard and invariant/format/validate/test/scan results
remain separate from Metro/native acceptance.

A final review added source-job admission before opt-in publication: checking or
unknown source jobs block before container commands; any extant job container
blocks even when its saved phase is idle. Only an explicitly absent job permits
publication. The two added cases and the existing normal-upgrade case passed
(three focused cases). No real job/container was stopped or started; stale state
and both metadata copies were preserved. The 18 prior opt-in cases plus these two
new cases, 21 preflight cases, eight admission cases and ten protocol cases cover
59 focused scenarios. Final CI for this small additional guard remains pending.

The pinned SDK flag conflict was corrected after bounded terminal failures, preserving
all source and unrelated services. Both approved fixtures now passed actual loopback
native manifest/bundle delivery and owned cleanup. Full lifecycle/private/native
acceptance remains pending. Twenty-two preflight and ten protocol cases passed after
nonpersistent diagnostic/argv corrections; final CI for those changes is pending.

Extended actual SDK probes subsequently passed existing-icon delivery (99 bytes,
exact retained-file hash), source maps (11,366,406 iOS / 12,348,753 Android bytes)
and /message + /hot WebSocket upgrades/ping-pong on both unchanged fixtures.
Source hashes and exact owned cleanup were verified again. These results do not
establish sustained native reload/private TLS or phone acceptance. Fourteen pure
state-boundary cases now verify independent readiness/freshness/expiry/ownership
projection; live state wiring and installed capability remain pending. [Details](sdk-spike.md)

Controller implementation checkpoint: fourteen offline cases cover separate sticky
leases, wrong-root/registry/resource denial, owned cleanup, unknown source mutation
guards, bounded user-unit configuration, simulated expiry and security withdrawal.
Historical schema-5 mobile suite: 22 cases passed. The updated schema-6 contract
case passes for early admission/no-runtime-write, no fabricated HTTP components
and truthful not-started observation. Live user-service, concurrent sessions,
restart/disconnect, proxy/private routing and device proof remain pending.

## Controller recovery checkpoint

The prepared source controller now freezes the provider for an exact forge user
unit, checks unit file/FragmentPath/drop-in ownership and binds sticky paired slots.
Read-only status separates process/protocol/private-route observations. Source
mutation checks reject an activating/automatically restarting unit even if a receipt
says failed and no container happens to exist at that instant.

Twenty-eight isolated controller cases passed, including expiry/revocation,
pre-execution revocation with orphan cleanup, invalid-metadata receipt recovery,
stop timeouts, partial/foreign cleanup, foreign-unit preflight before writes,
bounded secret-free event retention and exact read-only/idempotent revocation.
An early test revision used future fixture timestamps with the real wall clock;
its receipt failures were corrected by a deterministic fixture clock. No live user
unit or policy revocation marker was created by these synthetic tests.

Source `metro recover-stop` requires exact registry/root/canonical/generation and
unit proof; it does not execute invalid app config. Unknown start/stop outcomes
remain recovery-required rather than reporting a process down. Event logs retain
only enumerated lifecycle metadata, up to 256 events/64 KiB/seven days. SDK output
remains ephemeral. The admission audit timeout is capped by remaining session TTL.
A read-only real user-manager query for the selected absent fixture unit returned
LoadState=not-found, ActiveState=inactive and empty FragmentPath/DropInPaths.

All four workflows passed at committed 62603d4 (before this controller checkpoint).
The broader local gate passed the mobile/admission/spike/protocol/opt-in/state/
controller suites. Its template snapshot fixture lacked the newly bundled reviewed
Metro policy and failed one case; the fixture now copies that provider input and
asserts controller/policy byte parity, and the complete 21-case template suite passed.
The full local gate subsequently completed 36 suites / 672 cases with exit 1
from that single fixture error; every other suite passed. The corrected complete
21-case template rerun passed. This is not reported as a clean full-gate rerun.
At implementation head 80e28eb, dashboard CI passed and the other three workflows
were still running; final CI remains separate. No private listener, installed pointer,
retained app metadata or phone acceptance changed. Live concurrent user units,
streaming proxy, route readback, cache/renewal bounds, installed recovery and actual
Android/iOS remain pending. Session/runtime capability remains unadvertised.

A fresh frozen review snapshot `1e52db1e7ff3e72d9fe798051d4d98be88746db08995cc4c2648d4c32587128d`
was prepared and its controller/state/protocol/worktree bytes matched source. Its
CLI readback reports 1.12.0, source manifest schemas 1–6, worktree receipt schema 1,
no Metro session schemas and runtime schemas 1–4. This did not select it as the
installed launcher: the stable pointer still resolves to the original 1.10.1
snapshot. Frozen byte/capability readback is distinct from installed lifecycle.

The completed broad command was
`PATH=/srv/forge/projects/gptclaw/.venv-manifest/bin:/usr/local/bin:/usr/bin:/bin ./scripts/check-repository.sh`.
Its synthetic offline suites included mobile, canonical worktrees, repository/
credential ownership, web/API/group/database and dashboard regressions. No local
Terraform apply, infrastructure mutation, production use or host package setup
ran. Whitespace, Python/shell syntax and changed relative-link checks passed.
Private streaming transport is the next open implementation step; the pinned
URL-builder limitation is recorded in [SDK evidence](sdk-spike.md).


## Proxy integration checkpoint

Nineteen real task-owned loopback tests passed: 3 MiB exact-byte delivery, streaming
before upstream EOF, chunked/EOF framing, bounded/malformed/foreign/credential
requests, generation/freshness/inactive denials, fixed header forwarding and
discarded device/identity data, byte/header/connection/deadline limits, expiry,
masked ping/fragmented reload frames, malformed/oversized WebSockets, receipt
change, bind failure and release of an in-flight listener on stop. Initial tests
exposed a bind-ready race and Python 3.12 wait_closed ordering with active clients;
both were corrected and all 19 cases passed without resource warnings.

The 28 controller cases passed with proxy start/stop wiring; 13 protocol and
22 original spike cases passed, preserving strict direct-SDK port validation
while adding explicit generation-bound odd-port proxy probing. Frozen packaging
regressions passed all 21 template cases. Whitespace and syntax checks passed.
All four CI workflows passed at 8278e54, before this proxy integration; the new
integration revision still requires its own CI result.

Read-only opt-in revalidation on both retained fixtures returned eligible
300-second plans and clean Git status. Neither was applied at this checkpoint.
No live supervised unit, private route, phone operation or installed pointer
change has occurred. Actual SDK-through-proxy, two concurrent lifecycle/recovery,
operator readback, private transport and iOS/Android remain pending.


## Actual owned user-service and proxy rehearsals

Both approved retained fixtures were explicitly adopted on separate
codex/metro-session-contract branches, with lifetime 300 seconds. Their source
verify commands passed format checking, lint, types, tests, SDK, existing source
security and JS/assets build. Only tracked .gptclaw/project.yaml changed.
Previous metadata remains in owned migration journals; bootstrap PRs are intact.
Metadata PRs: [fixture one #2](https://github.com/danielbardsley/mob001-accept-one/pull/2)
at 56ca4196a198eda7cca9b43fa6995962e6a4d2c1 and
[fixture two #2](https://github.com/danielbardsley/mob001-accept-two/pull/2)
at 294f26fb7a60b33fe2f68de1445dba244bdf36f9. Both are draft, not merged.

The first real managed session (generation 7736c436c17a4752af7c06bd477426dd)
started under its owned forge user unit and reported route-pending with unavailable
origin. Through its odd-port loopback proxy, both manifests, iOS bundle 5,737,192 B,
Android bundle 6,441,778 B, 99 B icon, 11,366,406/12,348,753 B maps and both /message
plus /hot upgrades/ping-pong passed. Evidence contains hashes/counts, not bodies.
Private route and physical client flags remain false. Actual controls were
1,610,612,736 B memory, 100000 CPU quota, 256 PIDs, read-only root and only
127.0.0.1:18600 publication. The supervisor unit had 192 MiB/25% CPU/64 tasks and
NoNewPrivileges=yes. It survived the initiating CLI process exit; actual SSM
disconnect still requires separate evidence. Automatic expiry passed: inactive/dead
unit, absent SDK/network, process down and both loopback ports released.

A paired rehearsal used independent 18600/18601 and 18602/18603 leases. Both real
starts were idempotent with unchanged generations. Stopping one removed only its
SDK/network/proxy; the other stayed owned/running. Restarting one produced a new
generation without changing the other's identity. The second SDK-proxy sampler
hit a socket/compile timeout rather than passing; that session subsequently expired
to recovery-required. Exact inspection later found SDK, audit, network and proxy
already absent; generation-bound recover-stop confirmed stopped/inactive state.
The precise initial shutdown failure was not retained by that revision. Fixed
sanitized stage/code records are now added for the next reproduction; this edge
case is unresolved and is not reported as a clean expiry pass.

The remaining first session was stopped by exact generation; SDK/network were
absent and its proxy released. No temporary session remains running. Source mount
identities are now recorded in internal control schema 2 and rechecked before
publication/while running, preventing silent stale serving after directory
replacement. Ordinary file edits remain a separate Fast Refresh check. Current
controller/proxy tests pass; new mount/failure-record source still needs CI.

Installed launcher remains 1.10.1. Tailscale 1.104.1 readback showed only TCP 443 and
Funnel off. Help flags are on stderr as well as stdout; combined help confirms
--https and --bg support. No Serve/access-policy change, private TLS, native phone
load, signing, production, AWS mutation or existing app/data change occurred.
All four workflows passed at source 5de817a before the current guarded-mount changes.
Operator, sustained reload, native generation/URI, cache/renewal, crash/recovery/
rollback, installed/collector and physical iOS/Android criteria remain pending.

## Corrected proxy deadline and private-route preparation (October 14 UTC)

Current-state readback confirms fixture one stopped and fixture two cleanly expired.
The latter generation 5824188a7675496db3da5dbc06d700e2 passed the full real SDK
sample through its owned loopback proxy: iOS bundle 5,737,192 B, Android 6,441,778 B,
source maps 11,366,406 / 12,348,753 B, the 99 B retained icon and both /message
and /hot upgrade/ping-pong checks. Its evidence explicitly records private-route
and physical-client flags false. Automatic expiry returned passed, with no failure
record, SDK/network absent and proxy released. Earlier 90/120-second bounded
rehearsals also expired cleanly; the 120-second cold sampler timed out.

The probe previously allowed only two seconds between body reads and capped the
response-header wait at 60 seconds despite a longer bounded cold-transform deadline.
It now respects the caller's finite header deadline and permits at most 30 seconds
between streamed reads, using read1 so a slow body cannot hide deadline checks
inside a multi-read call. This fixes observed probing behavior, not a proven cause
of the older recovery-required case; that historical initial failure remains unknown.

Local focused results at this checkpoint: 14 protocol, 20 proxy, 30 controller,
20 private-route and 21 packaging cases passed (105 cases). The first new proxy
expiry test incorrectly changed an immutable fixture expiry after constructing the
proxy; corrected fixture setup passed the full suite. A real stalled-upstream test
now proves expiry cancellation before headers. Route fixtures cover absent/unowned/
changed listeners, digest races, preserved dashboard/projects handlers, coexisting
owned origins, default TLS trust, stale/wrong session and expired/stopped denial.

Both actual read-only route plans succeeded against Tailscale 1.104.1, with current
baseline digest d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539.
The [exact operator plan](operator-plan.md) proposes only 8443→18601 and 8444→18603.
No Serve or access-policy mutation ran. The supervisor's route observer is separate
from process/protocol readiness; actual HTTPS and phone ACL access remain unverified.

All four GitHub workflows passed at da9cdd8bc9561b9fa86d84a494c695a8038efba1:
[private apps](https://github.com/danielbardsley/gptclaw/actions/runs/38502791680),
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38502791684),
[dev-host](https://github.com/danielbardsley/gptclaw/actions/runs/38502791727) and
[Tailscale federation](https://github.com/danielbardsley/gptclaw/actions/runs/38502791798).
These precede the route/deadline changes; new-head CI remains separate.
Exact Android Go and iOS/device prerequisites were requested again, with no
physical outcome inferred. Stable provider remains 1.10.1; no existing app/data,
production, signing, infrastructure or host security change occurred.

Readback of the old first-fixture unit was terminal failed (exit status 1), despite
the reconciled stopped/passed receipt; all SDK/audit/network handles were absent
and the proxy released. This is not reported as an inactive-success unit. The
new-controller bounded rehearsal and its own expiry result are recorded separately.

The subsequent new-supervisor 120-second loopback rehearsal passed on fixture one,
generation 7f82a86bd5b84698964eafd13abd36ca. It returned route-pending with no launch
origin, independently recorded a pending route timestamp, then expired/passed.
The exact unit was inactive/dead with Result=success, ExecMainStatus=0 and no
automatic restarts; SDK/network were absent and proxy released. The saved owned
evidence explicitly marks private-route and physical-client verification false.
No Serve/access-policy operation occurred. The final process/protocol publication
ordering adjustment was checked separately by all 30 controller cases; this live
snapshot preceded that small ordering adjustment.

## Full offline gate and real crash recovery (October 14 UTC)

The existing repository gate completed with exit 0:
PATH=/srv/forge/projects/gptclaw/.venv-manifest/bin:/usr/local/bin:/usr/bin:/bin ./scripts/check-repository.sh
All registered offline suites passed, including historical web/API/group/database,
source mobile, canonical worktrees, repository/credential ownership, dashboard,
new route boundaries, templates and immutable release integrity. The final
process/protocol-before-route publication ordering was separately verified by the
complete 30-case controller suite. This is local source evidence, not installed,
private-network, physical-device or deployment acceptance.

A real 120-second loopback crash/recovery rehearsal then passed on fixture two,
generation a1c4be043994442cb9dbe631783961f9. After proving the exact SDK/container
and user-unit ownership, the test killed only that fixture's SDK. The owned unit
automatically restarted once, using the same session generation and original
expiry, repeated admission and returned to running. It then expired/passed with
Result=success, ExecMainStatus=0, inactive/dead unit, absent SDK/audit/network and
released proxy. The bounded source inventory before/after was identical.
The terminal unit resets its NRestarts counter; the live observation recorded one
restart before expiry. Owned evidence records the successful automatic recovery
and explicitly false private-route/physical-client flags. Both fixtures are now
terminal with resources absent; no operator route, ACL or installed pointer changed.

Runtime/protocol/route source is published at 7f7e5a8ea0d1513a0fb823c9403237afa1c02f03.
Dashboard CI passed at that revision; its other three workflows were still running
at the last verified poll, so final CI remains pending. Exact private listener
approval was requested against the published operator plan, separately from
device/client prerequisite information. All remaining acceptance rows stay pending.

## Renewal, bounded retention and owner prerequisites (October 14 UTC)

The owner reports Android 11 with Expo Go 57.0.9 supporting SDK 57. No physical
native result is inferred. No iPhone is currently available; the owner authorized
continuing the iOS development path assuming a recent iPhone and the same Expo
version. Actual iOS OS/client acquisition and physical acceptance remain pending.

The owner approved exactly 8443→127.0.0.1:18601 and
8444→127.0.0.1:18603 through the existing SSM operator path. No ACL change is
included. Operator execution/readback, permitted/denied access and private TLS
remain pending. The two source fixtures may use a reviewed one-hour finite
lifetime within the previously approved bounded private-session disposition.

Source renewal is read-only by default and digest-confirmed on apply. It requires
current exact generation, valid inputs/security, owned active process/unit and a
verified private route. It stops the old owned generation and starts a freshly
admitted new generation; no running timeout is extended. Active status now removes
transport availability immediately when security admission is unavailable.

Runtime retention admits at most 1 GiB generated source copies, 10 MiB artifacts,
65,536 entries and 128 copies per project. Pruning requires an inactive current
session and digest confirmation, and selects only marker/hash/inode-proven inactive
generated copies. Current, unresolved, edited, unknown and older pre-marker copies
are preserved. Known inactive metadata retires after seven days; protocol/acceptance
evidence remains. A batch is limited to 32 copies and 64 metadata records. Interrupted
or racing cleanup retains staging for reconciliation rather than deleting unknown
content. This is runtime-store cleanup, not project source/data deletion.

Focused suites passed: controller 44, retention 21, packaging 21, route 20 and
source mobile 22 (128 cases). Real 90-second generation
577139d24fc74400a0ad3a6de6e8be5b sealed its 449,737 B source copy, denied renewal
while route-pending without stopping it, then expired successfully. A second
60-second generation 80c127edecd94529bcdb8b8ac25e5a66 expired successfully and its
confirmed inactive prune removed only that older proven 449,737 B duplicate.
Four pre-marker copies and the current copy remained; canonical source inventory
was identical. Both runs ended with inactive/success units, SDK/audit/network absent
and proxy released. Private-route and physical-client flags were false. Positive
private renewal and full interruption/recovery acceptance remain pending.

All four CI workflows passed at published head
7fa418cdd539544d44e5c085f5904222d571d2c2:
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38574054530),
[Tailscale federation](https://github.com/danielbardsley/gptclaw/actions/runs/38574054247),
[dev-host](https://github.com/danielbardsley/gptclaw/actions/runs/38574054079) and
[private apps](https://github.com/danielbardsley/gptclaw/actions/runs/38574054153).
These precede the renewal/retention changes; their full local gate and new-head CI
are separate checks. Installed provider remains 1.10.1. No Serve/ACL mutation,
physical acceptance or feature completion is claimed.

## Approved private-backend preparation

The recorded route plans were applied locally without changing Serve. Retained
fixture metadata now declares 3,600 seconds through each existing draft PR #2,
with validation, clean status and publication verified. Both source-managed
backends started with fresh audit, exact unit/container ownership and generation/
expiry loopback health. Source inventory was preserved. Their generations are:

- one: 0f8032ae4b374f13af583145c6a4b75d
- two: a462a926bcea436a8c1cfa178d3b8210

Both initially reported route-pending with no available launch origin. Exact
operator commands were sent for the already approved listeners; operator readback,
ACL/device/private-protocol acceptance remains pending.

The sampler now supports only this node's exact owned private origin/port with
default-trust HTTPS and WebSocket TLS/SNI. A guarded private sample requires current
generation/security/unit/container and verified route before and after streaming;
bounded output contains hashes/counts rather than native bodies or identity. All
20 protocol cases passed, including wrong host/port/mode, certificate denial,
default trust/SNI and route drift. Actual private TLS sampling is pending operator
execution. This change followed the full-gate protocol checkpoint and has focused
verification; CI remains a separate final-head gate.

## Current verification checkpoint

The complete offline repository gate for the renewal/retention integration finished
with exit 0 using the prepared Python 3.12 environment. All registered suites passed,
including controller 44, retention 21, route 20, proxy 20, packaging 21 and legacy
web/API/database/dashboard/worktree/credential behavior. The later private TLS
sampler was checked separately by the complete 20-case protocol suite; the broader
run had already passed its earlier protocol checkpoint before that addition.

A real guarded private sample was attempted on both active fixture generations:
each denied route-pending before native retrieval, retained its owned SDK and
reported transport unavailable. No Serve or ACL change ran. Both one-hour sessions
remain bounded to their original expiries (one 15:55:24 UTC, two 15:55:54 UTC).
Latest-head CI is still running; no installed/private/device completion is inferred.

## Minimal native collector and dashboard integration

The source collector now schedules schema-6 native observations only when its
provider declares runtime schema 6 and Metro session schema 1. Schema-5 and older/
missing capability retain source-only behavior. Native observations have no fake
web/API/DB component, app/docs publication or native launch target. Minimal details
show separate process/protocol/private-route timestamps, finite expiry, independent
source quality and unverified native-client acceptance. Freshness, clock anomalies,
bad identity, malformed projection and expiry never preserve a fresh ready claim.

Affected Python suites passed: native projection 8, inventory 13, observation 10,
status cache 8, collector 5 and packaging 21 (65 cases). The first added inventory
fixture lacked required static app.json and was corrected; the complete rerun
passed. Nine frontend tests, typecheck and production build passed. The existing
portable rootless check then passed frozen install, tests/types/build, actual socket/
HTTP boundary and browser checks, including schema-5 source-only labels, native
route-pending details, absence of native anchors/fake components and foreign native
project rejection. Existing design/responsive/keyboard/status/link checks passed.
Only task-owned browser containers/fixtures were removed.

Actual read-only source observations of the two active fixture generations returned
route-pending, process up/protocol ready, components empty, publication unavailable
and source clean. Durations were 0.439 s and 0.341 s, within the collector budget.
The first live test supplied an incomplete filesystem identity and was correctly
denied; the corrected test used the existing dev/inode/uid identity contract.
These are source observations, not installed collector or owner-browser acceptance.

The provider bundle includes the native projection with byte-parity coverage.
Installed launcher and live dashboard/collector are unchanged; their compatible
rollout/parity and rollback remain pending. Runtime capability is still not
advertised ahead of private-adapter verification. No Go profile/link/QR or device
telemetry is implemented by this minimum observation slice.

The actual format command returned exit 1 for each active fixture. Their canonical
source inventories/Git status and exact owned generations/SDKs remained unchanged.
The active-session guard separately returned busy for both without writes. An
initial live harness wrongly expected conflict; the corrected expectation passed.
These are real mutation-conflict checks; private/operator/installed/device evidence
remains pending.

## Cold-bundle supervision investigation

A new cold Android bundle request on the original first-fixture generation timed
out before any source edit. Both sources remained clean. The first owned unit
automatically restarted once in its original generation/lifetime; the second
remained running with no restart. Typed failure was supervision/health, and bounded
SDK events showed exit 0 during cleanup rather than evidence of a container OOM.
The current process readback was running with OOM false; the original initial
failure mechanism is not proven solely by those events.

Source inspection identified a definite controller flaw consistent with this
failure: after the initial startup deadline, every protocol probe error raised a
fatal health failure even for an established live SDK. The source now records
protocol failure/unavailable and retries in place, retaining the live process,
generation and original expiry. Initial readiness still has a finite deadline.
All 48 controller cases passed. A corrected live cold-load/edit rehearsal remains
pending; this is not phone Fast Refresh acceptance.

The corrected-controller first-fixture generation
7a04519f8dec4aeb891951d4c506f4ce successfully served its cold Android bundle
(6,441,560 B) without requiring a source reset. The immediate edit test returned
the same bundle hash; its finally block restored the exact source and preserved
the second fixture. This did not pass rebuild or Fast Refresh acceptance.

Pinned CLI source then established the specific watcher defect: instantiateMetro.js
isWatchEnabled returns false for env.CI. Supervised SDK sessions inherited CI=1
from the audit/spike container defaults, so reload watching was disabled.
Runtime-only watch opt-in now uses CI=false with explicitly closed stdin/non-TTY
piped output; audit/spike defaults remain CI=1. All existing offline/resource/
readonly/privacy bounds remain. The 24 spike and 48 controller cases passed.
Corrected actual rebuild proof remains pending; no physical result is inferred.

## Corrected watch-enabled edit loop and CI portability

The bounded watch-enabled paired refresh passed, preserving both canonical sources
and exact approved listener bindings. Current first generation is
5863c80222c346e18e49c0f4ea59ba21; second is
cbe287fcd42e4cfbbb18d2981be4853f. They have original finite expiries
16:52:14 / 16:52:49 UTC on October 14 and initially reported route-pending.

The corrected first-fixture source rehearsal passed. Its baseline Android bundle
was 6,441,560 B / SHA-256
6c44f58dd8835cfb37f298db8acb14d1a7742ffbde70ecbcfbc871920cef9bc8.
A guarded display-text edit produced 6,441,572 B / SHA-256
5fce307db1f76a756740dfa9389bba92748ca2a6497d05d0bfe69c869884d329.
The exact restoration returned the original bundle hash. Both Git/source inventories
were clean, both owned generations/SDKs survived and the second source remained
unchanged. This proves actual loopback source watching/rebuild, not native phone
Fast Refresh or private TLS. The initial edit harness used the directory form of
the file-identity helper and stopped before writes; that harness was corrected.
The later cached-bundle failure was separately diagnosed as the pinned CI-mode
watcher disablement and its finally block restored source.

At 28f6fb006f854b0dd78de58ce1954e8d854e95b8,
[dashboard CI](https://github.com/danielbardsley/gptclaw/actions/runs/38589057843)
and [private app CI](https://github.com/danielbardsley/gptclaw/actions/runs/38589057905)
passed. [Dev-host](https://github.com/danielbardsley/gptclaw/actions/runs/38589057806)
and [federation](https://github.com/danielbardsley/gptclaw/actions/runs/38589058158)
failed their repository checks. Log evidence identified simulated renewal/prune CLI
tests reaching the real forge-UID guard on the runner (exit 2), not a production
permission failure. Those two tests now substitute only the CLI identity adapter,
preserving real filesystem ownership checks. New explicit root/foreign-UID denial
coverage confirms no runtime dispatch. The 49 controller and 21 retention cases
passed. Final-head CI and the updated full gate remain separate checks.


## October 14 private access and SSM reconnect evidence

The owner executed the approved 8443/8444 Serve commands and supplied the exact
JSON readback. Independent inspection confirms both reviewed root handlers and
preserves the original 443 dashboard/projects baseline digest
`d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539`.
Funnel remains off. The agent did not administer Tailscale or change policy.

Both current generations passed the full default-trust private TLS sample:

| Project | Generation | iOS bundle / map bytes | Android bundle / map bytes |
|---|---|---|---|
| mob001-accept-one | 5863c80222c346e18e49c0f4ea59ba21 | 5,737,500 / 11,366,453 | 6,441,560 / 12,348,959 |
| mob001-accept-two | cbe287fcd42e4cfbbb18d2981be4853f | 5,737,192 / 11,366,406 | 6,441,778 / 12,348,753 |

Both retained icons match SHA-256
`41c5028d232c20672121818fc63796242b6da381a985716b0a357e2eaff459bb`.
Both `/message` and `/hot` upgraded with HTTP 101 and passed masked ping/pong.
The second fixture's initial cold iOS HTTP probe failed without stopping/restarting
its SDK; a subsequent 200 response and the complete repeated sample passed in the
same generation. The initial response status/cause was not captured and is unknown.
These probes validate host transport, not a physical Expo Go client.

After the owner reported exiting and reconnecting SSM, independent inspection at
16:25 UTC confirmed the original generations above, unchanged expiry (16:52:14 /
16:52:49 UTC), exact owned unit/container, active/running state, zero restarts and
verified private health. No lifetime extension occurred.

The owner reports that neither health URL can be reached with Tailscale disconnected
or connected under a different identity. Record this as owner-reported off-tailnet
and different-identity denial; the agent did not run the laptop tests. Authoritative
relevant ACL/grant selectors were not supplied and remain pending. No policy change
is requested or performed. Physical permitted-client checks remain pending.

At source 9308e0b, dashboard, development-host and federation CI passed. Private-app
CI passed its mobile-source/database/Python/group jobs but the template job failed
one existing repository-credential fixture during synthetic repository bootstrap.
Its failed job is being retried; no success is inferred from other jobs. The local
complete gate returned exit 1 despite all reported test suites passing; its nonzero
result remains unresolved and is not recorded as a pass.


## Supplied access policy supersedes the denial interpretation

The owner supplied the active console policy containing the grant
`{"src":["*"],"dst":["*"],"ip":["*"]}` and tag ownership
`{"tag:gptclaw-dev":["autogroup:admin"]}`. This permits all same-tailnet
sources/destinations/ports, including TCP 8443/8444; tag ownership controls tag
assignment and is not a traffic restriction. The supplied policy is owner-provided
readback, not an independently authenticated console/API read by the agent.

The earlier different-identity failure therefore cannot establish an ACL-enforced
unpermitted same-tailnet-device denial. It may be a different-tailnet/non-routable
identity; that membership remains unknown. Off-tailnet denial remains owner-reported.
AC-004's scoped permitted/unpermitted-device evidence is not complete. No ACL/grant
change is authorized or performed. A selective policy would need a separately
reviewed concrete source selector and preservation of other intended traffic; adding
a narrower grant alone cannot override the existing wildcard allow.


## Accepted whole-tailnet scope and positive private renewal

The owner explicitly confirmed that all devices on this development tailnet should
have host access. This resolves the access-policy decision: the supplied wildcard
grant is accepted unchanged. No same-tailnet device is designated unpermitted.
Denied-access evidence is the owner-reported off-tailnet failure. This supersedes
the earlier selective-policy requirement; it does not establish physical Go success.
The specification/design/operator plan reflect the confirmed boundary.

An actual digest-confirmed renewal of mob001-accept-one passed through the owner
controller: generation 5863c80222c346e18e49c0f4ea59ba21 was stopped and replaced by
aba2b3b0b860477bbfd1d1f3da0f0bc3 after fresh admission. TTL is exactly 3,600 seconds,
expiry 17:30:08 UTC. The new session became Ready with verified private route; the
old-generation entry returned HTTP 503 through default-trust private HTTPS. The
second generation/expiry and exact owned SDK remain unchanged, and both source Git
checkouts remain clean. This is host renewal/stale-entry evidence, not proof that
Expo Go preserves the nonce or reloads correctly on a physical device.

The source provider now advertises schema-6 runtime and session descriptor schema 1,
following paired private protocol verification. Schema 5 remains source-only, and
no Expo Go launch capability or physical certification is advertised. The stable
installed provider remains unchanged until reviewed parity/rollout verification.


The failed private-app template job at 9308e0b passed on its scoped retry; all four
workflows are now successful at that revision. No production source was changed
to mask the synthetic credential-bootstrap failure. Later capability/Go inspection
changes require their own CI. The traced local diagnostic retry was interrupted by
editing its shell script while Bash was still reading it (exit 2); this is a harness
interruption, not a passing complete gate. Subsequent full checks use a frozen copy
of the completed checker to prevent that concurrent-read failure.


## Private expiry, bind denial and pre-rollout baseline

The second private generation cbe287fcd42e4cfbbb18d2981be4853f reached its original
16:52:49 UTC expiry. Independent inspection confirmed terminal expired state, absent
exact owned SDK/network, released loopback ports, clean source and default-trust HTTPS
entry HTTP 502 (no backend). It was not auto-renewed. An exact task-owned temporary
loopback socket then occupied its proxy port; start denied with conflict before receipt
publication. The prior receipt/source and first live generation were preserved; the
temporary socket was released. No foreign listener was adopted or removed.

The installed and candidate frozen providers independently report identical current
Shelfmark/Trailboard observations: API/DB healthy, web unknown with observation-
inconsistent, aggregate degraded. That pre-existing web observation limitation is
not presented as healthy app acceptance. The first comparison harness used a source
launcher with the wrong interpreter and was corrected to the exact frozen launchers;
no application runtime or data changed. Existing backend status parity is recorded
before platform rollout.

All four workflows at 73913b3 passed after the isolated template-job retry. The two
intermittently failing credential-bootstrap cases passed four additional isolated
local repetitions (eight cases total) with non-secret require-location diagnostics;
no failure was reproduced or production guard bypassed. The full local frozen-checker
process later terminated with SIGTERM/exit 143 during the worktree suite, after prior
reported suites passed; cause is unknown and no complete local pass is claimed.
CI's complete repository gates at the exact revision remain separate successful
checks. Subsequent QR/profile changes need their own relevant gates/CI.


## Android launch failure and transport correction (October 14 UTC)

The owner’s Android 11 / Expo Go 57.0.9 launch of the exact 8443 query-based URL
failed with `java.io.IOException: Failed to download remote update`. The phone
browser could reach the private health endpoint. Warming the unchanged generation’s
6,441,560-byte Android bundle reduced the host download to 2.398 seconds, but the
owner’s retry still failed; cold compilation alone is not an explanation or fix.

A fresh bounded diagnostic generation, 4778c48ab0fc418eb19c6c0dc034797e, then used
a locally rendered QR, independently decoded before presentation. The owner
reported the same error. Before that attempt, no resources or rejections were
counted. Afterwards, there were exactly three `stale-launch` rejections and zero
forwarded manifest/bundle/asset requests. All other fixed rejection counts were
zero. The failure reaches the proxy and fails the generation guard before Metro;
this does not establish an SDK, account, TLS or bundle failure. No request URL,
query, header, token, IP or device identifier was captured.

The adapter now accepts only the exact current session-bound path
`/_gptclaw/metro-session/GENERATION/` and maps that entry to the SDK’s `/` manifest
route. SDK bodies, MIME boundaries, signatures and origin-root resource URLs are
unchanged. Old/wrong/malformed paths, conflicting generation queries and unbound
`/manifest` or `/index.exp` aliases fail closed. The previous exact query entry
remains available for historical host probes; it is not a verified Go launch rule.
Twenty-five real loopback proxy tests and twenty protocol tests pass at this
checkpoint. Native success, two-project interaction and reload acceptance remain
pending until the corrected path is actually tested on the owner’s device.

Diagnostics are bounded in-memory aggregate counters, exposed only through the
existing private origin at `/_gptclaw/metro-transport`. Keys are fixed rejection
enums, resource categories and HTTP status classes; counters saturate at 2^53−1.
Health response shape is unchanged. Nothing is persisted and no per-request
identity or raw payload is logged. Reading counters is not device-online evidence.
The first diagnostic session was replaced through its reviewed owner controller
with fresh security admission; the second project and shared routes were preserved.


### Normalized path follow-up

The owner also reported the same download error for the slash-terminated session
path on generation 99e19c05970a41e69a8ce781adc6cef7 (expiry 18:47:43 UTC). Before
that attempt, agent probes had one successful manifest and four deliberately
rejected stale/alias entries. Afterwards, stale-launch rose from four to eight,
with no additional forwarded resource. This candidate did not pass native launch.

Targeted inspection of Expo’s public Android
[Kernel.getManifestUrlFromFullUri](https://github.com/expo/expo/blob/11342ecad05c78851da27ca0ea587f3f214af361/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/kernel/Kernel.kt#L506)
found explicit removal of nonreserved query parameters and the final trailing
slash. This explains both rejected candidate forms; it is source evidence, not
an exact binary fingerprint of the owner’s app. The adapter now accepts the exact
current generation path with or without one trailing slash. New candidates/probes
use the form without a trailing slash. Both map only to the SDK root; old/wrong
generations, extra segments or duplicate/conflicting generation queries remain
rejected. Twenty-five proxy cases pass, including both normalized forms with
unchanged multipart body and signing header. Native retry remains pending.


## Native manifest reached; SDK-57 development probe uses HTTP

On generation 5eb678adae594bab80daac2d9bd5be92 (expiry 18:56:37 UTC), the owner
reported that the app opened, then “Packager is not running.” The reported address
is `http://forge-dev-01-4.tail8c3304.ts.net:8443`. Agent comparison shows one new
successful manifest and no forwarded bundle/status request. The native entry-path
guard is passed; counter/navigation/assets, edit and reload are not accepted.
The agent's HTTPS `/status` probe returns 200 and exactly `packager-status:running`;
the manifest's launch asset is HTTPS on the owned origin and the SDK is running.

The official SDK-57 Android branch at 0607af7a70d0ea3e58a6d55824aac5cfd3e78613
uses HTTP unconditionally for its development packager probe. The newer main-source
HTTPS-origin fix cannot be assumed present in the owner’s installed client. Go
inspection therefore now reports the exact Android client unsupported for the
approved HTTPS transport, with no launch certification or implicit fallback.
Sixteen focused eligibility/CLI cases pass, including refusal to bypass this known
transport prerequisite. [The concrete transport decision](../034-expo-go-workflow/client-transport-decision.md)
records alternatives; no listener/profile transport change or client build is applied.

At c8d03a1, the prepared immutable dashboard release is
8950b4549e6ad51b827eb374a3c628062ec5a37e0309f98a12783586cacad3ec, with provider
b99f07397268d3e4d4793a64220c9a2d405fd9349cfdce63e25c0d9a03b2597c. Both fixtures'
source/frozen inspection behavior matches, excluding only separately measured
command duration (one 0.587/0.822 s; two 0.788/1.242 s). The initial strict full-JSON
comparison failed because elapsed durations differ; the corrected behavior check
passes. One is Ready, two is Expired, and launch availability is false. This snapshot
precedes the newly recorded Android incompatibility; its new profile still requires
frozen parity. Stable launcher and active dashboard were not selected or restarted.


The normalization correction c8d03a13ce7105f3f4738fa7fa8540d2278d0547 now has
all four CI workflows passing: dashboard 38611095207, development host 38611094360,
private applications 38611094365 and Tailscale federation 38611094314. No protected
AWS deployment/apply was invoked. The later unsupported-client profile is verified
with sixteen local eligibility/CLI cases and immutable-provider behavior parity on
both actual approved fixtures at provider
0d693ff3f11fb696e5f7b0840b876e1a6fffb9d5824ab92d0c7dccb226ce3b98. That profile’s
CI is not inferred from c8d03a1. Source and snapshot both report Android unsupported
for the current HTTPS boundary, with launch unavailable; one remains Ready and two
Expired. Active dashboard and stable launcher remain unchanged.


## Approved HTTP implementation and loopback preparation

The owner explicitly approved Metro-only private HTTP over encrypted Tailscale.
Source now has an explicit `--metro-transport tailnet-http` lifecycle selection,
schema-2 HTTP receipts/descriptors/route approvals, strict same-node/scheme resource
validation, HTTP-aware health/WebSocket probes and native collector projection.
Legacy HTTPS stays schema 1; old providers reject schema 2. Exact conversion retains
the original HTTPS approval and history, rejects unowned bindings, keeps private
readiness false before operator execution and gates rollback recording until HTTP
is removed/replaced. No native launch certification follows from host tests.

Focused checks pass: 26 proxy, 22 protocol, 49 controller, 15 state, 24 route, 17 Go
inspection, 9 native collector and 22 mobile-source cases. The first new collector
case used the wrong function name; correcting the test to the existing `project`
function gives all nine passes. This is local verification; latest HTTP CI remains
pending. The previous normalization revision's four CI workflows passed separately.

An actual attempt to change the running first session's transport in place was
rejected with conflict and preserved its generation. Through the owner lifecycle,
only that SDK was stopped and replaced; the expired second SDK was independently
started. Fresh admitted one-hour HTTP loopback sessions are:

| Project | Generation | Expiry UTC | Android bundle bytes | Bundle SHA-256 |
|---|---|---|---:|---|
| mob001-accept-one | 788e407115ff4ad3802c475453062cd3 | 20:04:04 | 6441558 | 207c54fa52af4c5734b680baca48d932e1ab6f646095d6558c53ecc8253e95c8 |
| mob001-accept-two | 9d717649f4c64a56b7b3a96fa9575e97 | 20:05:42 | 6441558 | 5a452b481fa7a893548e9851bc7c5f1806e36270c254e19f2a820f0932b6c4c1 |

Both session-path manifests are 200 / 1,299 bytes over the owned loopback proxies,
with advertised HTTP bundle targets. Both Android bundles are warm. Exact conversion
plans are recorded (one 9aa9584e17457e51775ca5332b17b1cb00cc6a195625c994cb63213714f774c6;
two 3db774203ca5f7f48a35f04938ccded8c534f8364f8274563a4eafd7e3914cb1).
Current Serve remains HTTPS; private HTTP route state is therefore unavailable as
expected. Baseline handlers and Funnel-off state are independently verified.
Operator conversion, private HTTP/device checks, source/frozen final parity,
installed rollout/rollback, full Go consumer implementation and delivery remain open.


## Operator HTTP conversion and independent private readback

On October 14 the project owner reported execution of the exact approved two-port
SSM conversion. Independent readback verifies HTTP on TCP 8443/8444, their exact
owned loopback proxies, unchanged original dashboard/project baseline digest
`d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539`, and Funnel off.
Both current generations retain their original expiry and report Ready. Private
HTTP native manifests return 200 / 1,299 bytes for each project. Fresh `exp://`
path-bound candidates were sent for physical Android acceptance; that owner check
is pending. This establishes private transport readback, not native UI acceptance.


## Android native acceptance and bounded Go consumer (October 14 UTC)

The project owner confirms both current private HTTP candidates opened correctly
in Expo Go 57.0.9 on Android 11, including the requested native counter, navigation
and local icon checks. On each app, the agent changed only the heading in
`src/app/index.tsx`; the owner confirmed automatic Fast Refresh while count 3
was retained. Exact hash-guarded originals were restored and each checkout is
clean. The owner confirmed full reload restored the normal heading and count 0.
An owner-supplied screenshot corroborates the restored native starter screen;
it is not a binary fingerprint or additional platform certification.

On app two the owner confirms background/foreground, Wi-Fi/mobile-data transition
with Tailscale connected, failed reload while disconnected, and successful intended
app reload after reconnect. A brief task-owned syntax error in app one produced
the native compile error while app two remained usable; exact source restoration
and native reload/counter recovery were confirmed. These are owner reports,
separate from agent protocol checks. Physical restart/stale QR/expiry checks,
installed rollout/rollback and final delivery remain pending.

Both sessions also pass agent private HTTP probes for iOS/Android manifests,
bundles over 2 MiB, local icon, source maps, and `/message` and `/hot` WebSocket
upgrade/ping-pong. Android bundles are 6,441,558 bytes; iOS bundles 5,737,498 bytes;
source maps are 12,348,959 / 11,366,453 bytes. iOS host-protocol checks do not
establish physical iOS support. The sampler's prior fixed label said private TLS
for these HTTP probes; transport was independently verified HTTP and the label
is corrected in source.

The reviewed Android profile now records actual physical validation at `2026-10-14T19:33:39.053597+00:00`,
expiring `2026-10-21T19:33:39.053597+00:00` (seven days). It binds the unchanged exact SDK/source policy,
locked graph, static public config/toolchain contract, Android 11, Go 57.0.9 and
approved private HTTP. New source/client/config/transport or stale/future evidence
withdraws launch eligibility. iOS remains uncertified and reports its CLI-login
prerequisite outside this credential-free scope; no device/version assumption
is treated as acceptance. No automatic recertification or SDK migration occurs.

Source implements explicit read-only `go launch --generation`, exact owned-origin/
generation/expiry serialization, finite profile freshness and minimum dashboard
Open/copy/local-QR controls. No launch operation starts Metro, provisions a route,
logs into Expo or collects phone identifiers. Stale collector/layer/session/profile
states withdraw links and QR. Existing app/API/repository links remain covered.

Local checks pass 26 Go, 6 Go collector, 9 native collector, 10 observation and
21 provider-packaging cases. The dashboard portable gate passes 17 frontend tests,
typecheck, production build, independent rendered SVG decode and browser UI checks
including native Go controls and stale/hostile payload withdrawal. The first decode
check failed because its expected payload retained the old query form; both the
producer and independent assertion now use the proven session path and pass.
The full local repository gate was attempted but terminated with SIGTERM/143
after its completed suites passed; it is not recorded as a full pass. CI at
885a4d9 passes dashboard 38622460470 and private applications 38622460506.
Development-host 38622460480 and federation 38622460457 failed solely because
the Metro capability assertion still expected `[1]` instead of `[1,2]`; that
assertion is corrected. Latest consumer CI remains pending. No protected apply ran.

Source/frozen Go behavior matches on both real approved roots at provider
`9f574ef13547d7b83cd0370719a4cd076765c2514feb5316c18d06984deeda6e` (before
the subsequent consistent-reason validation). App one is compatible/stopped with
launch unavailable; app two is compatible/Ready and its exact generation-bound
payload matches. Elapsed command duration is excluded from behavioral equality.
The retained HTTP-capable, Go-disabled rollback provider is
`a99e4012c3b0232ddf0dffc3ef7161e34f2eed20976ac9a6bcf9bd11a812963c`.
Stable launcher/dashboard remain unchanged at this checkpoint.


## Installed collector correction, rollout and recovery checkpoint

All four CI workflows pass at implementation 78a9d45b344cd3655c72ef719ebb4c88e178d79b:
dashboard 38627048749, private applications 38627048657, development host
38627048864 and federation 38627048631. No protected AWS apply ran. Later
collector/cleanup corrections below require their own final CI.

Actual installation exposed two missed boundaries: the collector entrypoint
hard-coded only schemas 1–4, and provider observation sent a reduced native
projection where StatusStore expected the typed descriptor. Source now reads
capabilities from its bundled read-only CLI and hands the typed session descriptor
to the collector; the public native projection remains unchanged and removes
origin/transport details. Six collector cases and ten observation cases pass,
including CLI-capability parity and the real provider-to-StatusStore handoff.
Nine native projection and six Go projection cases also pass. The portable
dashboard install/test/type/build/socket/QR/browser gate passes again (17 frontend
cases). Earlier readiness harness attempts failed; the harness also initially
assumed a non-null observation and an inactive session whose old TTL had not
elapsed. Those task-harness assumptions are corrected and not product successes.

New immutable paired candidates retain the original snapshots unchanged: Go
provider 4791d30c239a6b145ea108d564b259c69b2b34102f355d3e96515f47c2c53959 /
dashboard a17ec4fb9f9b5ba6dba0cd5bc872eb2848abd30818947b70f2eba83d0bd40a35,
and HTTP-capable Go-disabled provider cc9850dcbc31cc30d838e99ad9ed6600a60db2f713cbce9be61e42f3f0a1ab2d /
dashboard 833e14ab9ccf727ff97824f73646b10187cd452d879e504bdb2981f55e95dfd5.
The disabled candidate is a new snapshot built from a task-owned copy of the
previous HTTP provider plus the two collector corrections; no old snapshot was
modified. Actual install → Go enable → Go-only rollback → roll-forward passed.
Installed CLI launch, live collector Ready/Go launch and withdrawal during rollback
were verified. Both session generations/expiries, canonical sources, group behavior,
original HTTPS handler baseline and Funnel-off state were preserved throughout.

Effective metadata on the owned second SDK verifies read-only source/dependency
mounts/rootfs, 1 CPU/1536 MiB/256 PIDs, loopback-only publish, internal network,
log driver none and offline/no-dotenv/no-telemetry/ephemeral HOME predicates.
Only necessary metadata and boolean fixed-environment predicates were inspected;
no environment, credential, control token or SDK-output dump was recorded.

The original second generation 9d717649f4c64a56b7b3a96fa9575e97 expired normally
at its one-hour bound with absent SDK/network/proxy and clean source. A subsequent
explicit ten-minute installed-test generation e18a2397bd4f4acc8f914f8453a969fd
ended recovery-required with sanitized owned-cleanup/conflict, although all resources
and listeners were independently absent. Exact owned recover-stop reconciled the
receipt. An inspect/auto-removal race is a possible cause, not a proven trace.
Cleanup now accepts a failed removal command only after independent absence is
proven, while foreign/unknown replacements still block. All 51 controller cases
pass, including both absence and foreign-replacement regressions. A new-runtime
expiry check remains required before claiming that intermittent path fixed live.

The owner later reported neither old app link could download. At that time app
one was intentionally stopped and app two's original URL was obsolete after its
finite expiry/rehearsal replacement; this is not confirmation that the other app
remained usable during the earlier stop window. Following that response, app one
was explicitly restarted (ed16a0fa76ca4e879505c670d3a03c9e, expiry 21:25:12 UTC).
The second bounded rollout generation is b015056fcff54f35a85a7f92393a87c9,
expiry 20:32:13 UTC. Both Android bundles are warm and unchanged at 6,441,558 bytes.
Cold compilation briefly made the first protocol layer unavailable; subsequent
process/protocol/route observations are Ready. Current dashboard QR/copy and
intended native restart confirmation have been requested; no owner result is
assumed. Stable Go installation at this checkpoint precedes the cleanup race fix.


## Final corrected source verification checkpoint

At 92119fb3f4a699e9c2c9a4b444e183f2d369ccf9 all four CI workflows pass:
dashboard 38632684998, development host 38632685434, private applications
38632685022 and federation 38632685026. Protected plan/apply did not run.
The final source is installed as combined provider
69061bff1ab378e044a4684090ead61f6a94cd87f4899b475beb61ede98cb473 with dashboard
1ac5111f34b77a179a88ffe5ce014358a1a573d34a4f8e86e8779ea062fda2c4.
Actual installed collector verifies the current first app Ready with its exact
generation-bound Go action. Source and installed inspection are identical on
both real fixtures excluding command duration: one Ready/launch available;
two Expired/launch unavailable.

After exact owned reconciliation of the prior second receipt, one explicit
120-second updated-runtime rehearsal ran at generation
9ece4e2f6a604fffbc354ad0d77b58f4. It became Ready, then automatically ended
Expired / operation passed. SDK container, isolated network and both loopback
listeners were independently absent. The original canonical source is clean;
first-session generation/expiry and the original HTTPS/Funnel baseline are
unchanged. This is a real successful updated-cleanup expiry case; the two
earlier ambiguous cleanup outcomes remain recorded above.

The project owner has been asked to confirm refreshed dashboard QR/copy and
intended first-app native restart. The first session remains bounded until
21:25:12 UTC; no response is assumed. The previous second-app QR prompt expired
with its stated 20:32 UTC session; test only a current available dashboard action.
An Android-first matrix decision is also pending: iOS remains unverified with
its CLI-login prerequisite outside this scope. Final owner acceptance, operator
owned-listener removal evidence, review/merge and delivery records remain open.
No catalogue entry is marked Delivered.


## Admission drift and environment-file denial (October 14, 20:58 UTC)

One explicit 300-second session on app two, generation
`b95669116cdc47318e8e28211056971a`, became Ready. A task-owned comment changed
only its locked graph hash. Within the bounded supervision check it became
Failed / supervision / conflict, with its owned SDK/network/proxy absent.
The exact original lockfile was restored in a guarded finally block; source Git
status, app-one generation/expiry and the HTTPS/Funnel baseline were preserved.
The unit later re-admitted the restored inputs within its original finite lifetime
and ended Expired / passed. This proves input invalidation shutdown and bounded
re-admission; it is not a global-policy revocation test. No approval/marker changed.

The attempted synthetic private-input bundle check created only a task-owned
root `.env` file on app one. The SDK source snapshot excluded it, but bundle
requests returned 502. Inspection identified the intentional `private_apps.target`
forbidden-file guard: both attempts caused Failed / supervision / invalid and an
owned automatic restart after exact fixture removal. The same generation and
21:25:12 UTC expiry were retained; two restarts were observed. Neither attempt is
counted as a successful marker-free bundle check or uninterrupted availability.
No policy was relaxed. The task-owned file is absent and both fixture checkouts
are clean. A subsequent current private Android manifest probe passed; app one
is Ready. App two is expired with launch unavailable.

All four workflows also pass at documentation commit ca460b5. Final device QR/
restart/isolation, platform matrix, operator removal, review/merge and delivery
remain pending; no owner response is assumed.


## Private source-exclusion canary (October 14, 21:05 UTC)

A separate task-owned `.gptclaw-private-acceptance.env` file tested private source
exclusion without adding a forbidden root `.env` or relaxing policy. Its random
synthetic marker was not printed or persisted as evidence. The reviewed root-file
allowlist omitted the file from the existing SDK snapshot. The current private
Android bundle returned HTTP 200, identity encoding, 6,441,558 bytes, SHA-256
`207c54fa52af4c5734b680baca48d932e1ab6f646095d6558c53ecc8253e95c8`;
bounded streaming proved the marker absent across chunk boundaries. Only that
exact owner/content-checked task file was removed in finally; canonical Git
status is clean. Generation/expiry remain unchanged and NRestarts remains 2,
with active unit / ExecMainStatus 0. This is a successful source/bundle exclusion
check, distinct from the failed forbidden-dotenv attempts above. SDK output and
environment were not dumped; persistent SDK logs remain disabled.


## Positive private renewal and finite replacement (October 14, 21:14 UTC)

A read-only 300-second renewal plan on current app one passed, preserving its
lifecycle/ownership/input fields and pending device-test link. An initial harness
incorrectly compared the whole receipt while supervision independently updated
observation timestamps; the corrected comparison permits only those observations
to change. No renewal was applied to app one.

The approved app-two HTTP listener was independently still present before an
explicit 300-second rehearsal, generation `c285dba54490414290227ca2003ccdf9`.
Actual digest-confirmed renewal used fresh admission and replaced it with
`9ed1f8bfa9e843a78386d158d3ea5613`, keeping schema 2 / private-tailnet-http and the
same owned origin. The new generation had an explicit 120-second bound, expiry
21:14:07 UTC. Its native private Android manifest passed; the old generation's
entry returned 503. This verifies renewal preserves the approved transport and
invalidates the earlier copied payload rather than extending its running timeout.

The renewed session then ended Expired / passed. SDK/network and both loopback
listeners were independently absent. Canonical source is clean, app-one generation/
expiry/input/unit identity are unchanged, and the original HTTPS/Funnel baseline
is preserved. No Tailscale route operation or device acceptance occurred.

At documentation head 3c0b0f4 dashboard CI passed (38637236845). Private-application
CI (38637236901) initially failed one synthetic credential-recovery case; that
individual case and the complete 58-case suite passed locally, and the failed
job's rerun passed the complete workflow. No production credentials or remote
repositories were used by these local fixtures. Development-host and federation
runs 38637239492 / 38637237136 remain running at this checkpoint; no new full-pass
claim or infrastructure apply is made.


## Owner resumed device checks and selected Android-first delivery

On October 14 the owner requested fresh sessions and inline QR codes after other
work delayed the earlier prompts. The owner explicitly selected Android-first
release with iOS retained as a follow-up. Prior expired QR prompts are not counted
as physical evidence. Two fresh one-hour sessions are being prepared under the
existing exact runtime/private-listener scope. The owner did not report execution
of the listener-removal command; defer that operator step until device checks
finish and independently read back its result. No Tailscale mutation or new
permission is inferred from the reply.


## Fresh owner-requested QR sessions (October 14, 21:22 UTC)

The owner requested fresh sessions and direct QR images. Both canonical fixtures
were explicitly started with the approved one-hour bound and private HTTP, after
reconciling their prior exact generations. Each current Android bundle returned
200 / 6,441,558 bytes before launch publication. The Go serializer independently
validated current ownership/generation/origin/client/profile/freshness twice.

| Project | Current generation | Expiry |
|---|---|---|
| mob001-accept-one | c5ad655350a04e11a5b478c45e0a9ceb | 22:17:52 UTC |
| mob001-accept-two | dc40a59da6f1445e838fabf899c55b41 | 22:19:44 UTC |

Each PNG was rendered offline from the same pinned `localQr` encoder used by the
dashboard and independently decoded to the complete current payload with jsqr.
No external QR service, credential or owner device data was used. Both source
checkouts are clean; the existing HTTPS/Funnel baseline is unchanged. The owner
receives the QR images directly; native QR/restart results remain pending.
The prior inline/manual payloads are obsolete and not acceptance for these sessions.


## Owner QR acceptance and failed reload isolation (October 14, 5:57–6:08 p.m. Eastern)

The project owner confirms both fresh QR images open the correct native home,
local icon, navigation and working counter after restart on the selected Android
matrix. This is physical QR/restart evidence for generations c5ad655350a04e11a5b478c45e0a9ceb
and dc40a59da6f1445e838fabf899c55b41, separate from local PNG decode.

Before the isolation mutation, both host route observations intermittently failed
while their owned SDKs remained up with zero restarts. Aggregate diagnostics showed
connection-bound rejections and established proxy socket counts 7/8, without
recording peer/device identities or request data. Only app one was then stopped:
its SDK/network/proxy were absent, while app two's generation, expiry, input/unit
identity and original HTTPS/Funnel baseline were unchanged. App-two private manifest
probes failed. The owner confirms both native reloads failed with “Failed to download
remote update.” App one's failure is expected; app two's failure means this physical
isolation check fails and is not accepted as other-app availability.

A capacity correction keeps eight total active slots, limits forwarded native
requests to seven and reserves a slot for fixed health/diagnostic work. Under
pressure it reclaims only proxy-owned incomplete-header connections older than one
second, before any SDK request is forwarded, and rechecks the shared bound after
cancellation. Complete requests are preserved. Diagnostics expose bounded aggregate
capacity counts only. Twenty-eight proxy tests pass, including native saturation,
idle-header reclamation, resource bounds and privacy; 51 controller and 22 protocol
cases pass. This fix is prepared, not yet counted as installed/native acceptance.

All four CI workflows pass at prior documentation head e67ce44: dashboard
38639886338, private applications 38639886322, development host 38639886301 and
federation 38639886350. Protected infrastructure actions were skipped. The capacity
fix needs new-head CI, installed verification and repeated device isolation/recovery.


## First capacity correction did not recover native launch

Provider 15b5491fef90cbc337a1aabeae279d8664419cce24b4a89a13c00e68122aef66
was installed through the owned provider path. Both new sessions served warm
6,441,558-byte Android bundles and fixed health/diagnostic responses. Six consecutive
private app-one health probes passed. The owner nevertheless reports the same
remote-update failure from the new app-one QR, including after force-stopping Expo Go.
That native result fails; healthy host probes are not treated as native acceptance.

Aggregate diagnostics after the new QR attempts show seven additional accepted
WebSocket requests per attempt, capacity rejections, and no additional manifest or
bundle response beyond the agent's warmup. Reserving health capacity alone still
lets reconnecting WebSockets monopolize all seven forwarded native slots. The
correction now separately caps WebSockets at four, preserving three native HTTP
slots and one health slot within the unchanged eight-slot total. Complete requests
remain protected; diagnostics contain aggregate counts only. New regression keeps
four WebSockets open while proving the current manifest and health return 200,
with excess WebSockets rejected. Installed/native revalidation is still required.


## WebSocket reservation installed; device retry pending (October 14)

At implementation head `22a458b`, the proxy retains eight total connections,
reserves one for control requests and limits WebSockets to four within seven
forwarded native slots. The regression holds four upgraded WebSockets while the
current manifest and health requests succeed; all 29 proxy cases pass. Its first
run exposed a missing test-server behavior, corrected before installation; that
failed run is not counted as success.

Immutable provider `960457be4f02e2aef1bc604009a8e79a901557ba751ce3445345601a7943d96b`
was selected through the reviewed provider path. Both fresh one-hour sessions
serve 6,441,558-byte Android bundles through the private HTTP listeners. A real
private app-one check held four upgraded WebSockets open concurrently: its current
Android manifest and diagnostics returned 200, with active=5, native=4,
websockets=4 and limit=8. All four test connections were closed afterward. This
proves the installed capacity reservation; it does not prove the phone failure
is resolved.

Fresh app-one generation `06f4d67221ff4d26bf2d14d12b433d35` expires at
7:32 p.m. Eastern; app-two generation `00b5662918864f26829652ccb881412e`
expires at 7:34 p.m. Eastern on October 14. Both locally rendered QR PNGs were
independently decoded to their complete current launch payloads. Source checkouts
and the original HTTPS/Funnel baseline remain unchanged. Phone scan/reload,
repeated isolation/recovery, owned listener removal and final CI/review/delivery
remain pending; neither feature is marked Delivered.


## Owner confirms fresh native loading after capacity correction

On October 14 at approximately 6:42 p.m. Eastern, the project owner confirms
“Both apps work again” for the exact app-one generation
`06f4d67221ff4d26bf2d14d12b433d35` and app-two generation
`00b5662918864f26829652ccb881412e`. This accepts native loading/operation
with the revised installed proxy on the selected Android matrix. Aggregate
transport observations independently show additional successful manifest and
bundle responses for both sessions, with unchanged generations/expiry and no
stale-launch, foreign-origin or credential-header rejection. Bounded connection
rejections still occur; successful loading is not evidence that every reconnect
request succeeds.

The owner's statement does not separately confirm Expo Go Reload, stop/isolation,
crash or expiry recovery. Those checks remain pending and the earlier failed
isolation result remains recorded. No completion, merge or Delivered claim follows
from this loading confirmation.


## Owner responds to the corrected-session Reload check

At approximately 6:47 p.m. Eastern on October 14, the project owner responds to
the explicit request to use Expo Go Reload in each current app: “Both apps still
appear to work.” This is the owner's reported Reload result for generations
`06f4d67221ff4d26bf2d14d12b433d35` and
`00b5662918864f26829652ccb881412e`; it does not independently report a
specific counter value or establish stop/isolation, crash or expiry recovery.
The app-one-only stop check proceeds separately, with app two's existing
session retained.


The repeated app-one-only stop completed at 6:47 p.m. Eastern with phase stopped,
operation_result passed and the owned SDK, network and both loopback listeners
absent. App two retains generation `00b5662918864f26829652ccb881412e`,
expiry, input digest and unit digest; its transport remains available and three
private Android manifest probes pass. The original HTTPS/Funnel baseline is
preserved. This is host evidence only; the corresponding device isolation result
remains pending.


## Owner confirms stopped-project isolation after the correction

On October 14 at approximately 6:50 p.m. Eastern, in response to the explicit
Reload check for stopped app one and unchanged app two, the project owner reports:
“Ok app one no longer works, app two still does.” This accepts the intended
physical isolation result: stopped generation
`06f4d67221ff4d26bf2d14d12b433d35` is unavailable, while running generation
`00b5662918864f26829652ccb881412e` remains usable. No additional counter
value or interaction detail is inferred. This successful repeat supersedes the
current isolation failure state without erasing the earlier failures.
A new app-one-only finite restart/reconnect and subsequent expiry check remain;
app two's existing session and expiry are retained.


App one was restarted separately into generation
`8989c4bc00f749c6b3712439415aae76`, with a 15-minute lifetime expiring at
7:06 p.m. Eastern. Its private Android manifest and 6,441,558-byte bundle pass;
the former generation entry returns 503. App two retains its existing generation,
expiry, input/unit digests and available private transport. Existing HTTPS/Funnel
handlers remain unchanged. The new physical reconnect and expiry checks are
pending; host payload rejection alone is not native evidence.
