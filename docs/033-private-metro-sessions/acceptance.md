# SPEC-033 acceptance tracking

- **Status:** Pending — private TLS and reconnect evidence recorded; installed/device acceptance outstanding
- **Owner:** Project owner
- **Observed:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-033](spec.md) · **Design:** [TDD-033](technical-design.md) · **Tasks:** [TASKS-033](tasks.md)
- **Context:** Main fd6566426e0f18f16bc19150edcc113902da3e84;
  planning commit 66c19a26eb9fba81812165b6c7bda3d390e776ed / [PR #77](https://github.com/danielbardsley/gptclaw/pull/77).
  Local runtime preparation is on codex/mobile-metro /
  [draft PR #78](https://github.com/danielbardsley/gptclaw/pull/78); merge/CI/runtime are pending.

## Criterion mapping

| Criterion | State | Current evidence and remaining action |
|---|---|---|
| AC-001 | Pending | Schema-6 opt-in/strict input validation, canonical guarded metadata migration and older-provider rejection have local evidence; session capability/descriptor and installed rollout remain pending. |
| AC-002 | Pending | Real two-session start/idempotence/independent stop/restart and clean expiry recorded below; SSM disconnect/reconnect preserved both generations and expiries; remaining recovery and physical evidence still required. |
| AC-003 | Pending | Two sequential SDK loopback spikes served iOS/Android manifests and >2 MiB bundles; Existing assets, source maps and WebSocket handshake/ping passed on both fixtures; Private default-trust TLS manifests/bundles/assets/maps and both WebSocket paths now pass on both fixtures; physical native reload and iOS/Android remain required. [Measured evidence](sdk-spike.md). |
| AC-004 | Pending | Owner executed the exact approved two-listener plan; independent readback preserves the original baseline and Funnel off. Owner reports denial both off-tailnet and under a different identity. Owner explicitly accepts the supplied wildcard grant and all same-tailnet devices. Off-tailnet denial is owner-reported; permitted physical-client and owned removal/expiry evidence remain pending. |
| AC-005 | Pending | Typed independent state/descriptor and source CLI controller are prepared; private route observations, collector and installed parity remain pending. |
| AC-006 | Pending | Fresh audit, owner-approved exact runtime admission, bounded real SDK spikes and offline safety tests recorded in [security proposal](security-review.md); real managed-runtime revocation/secret checks remain; exact owner disposition is recorded. |
| AC-007 | Pending | Offline absent/foreign ownership cleanup passes; actual crashes, leases, compatible provider refresh/rollback and app regression evidence remain. |
| AC-008 | Pending | Local source/admission/protocol evidence and all four CI workflows passed at fb7f4b2. All four CI workflows also passed at 62603d4; new controller CI and actual Metro/installed operations, operator/device acceptance and merge remain required. |

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
