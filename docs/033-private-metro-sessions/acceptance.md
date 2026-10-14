# SPEC-033 acceptance tracking

- **Status:** Pending — implementation in progress; no Metro/device acceptance
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
| AC-002 | Pending | Offline ownership/deadline/fixture guards pass; real two-session lifecycle/disconnect/expiry still required. |
| AC-003 | Pending | Two sequential SDK loopback spikes served iOS/Android manifests and >2 MiB bundles; Existing assets, source maps and WebSocket handshake/ping passed on both fixtures; actual private TLS, sustained native reload and physical iOS/Android remain required. [Measured evidence](sdk-spike.md). |
| AC-004 | Pending | No Serve changes performed; exact operator plan/readback and permitted/denied private access still required. |
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
Expo Go described as up to date. Exact model, OS build and client version remain
unknown; no actual native load/interaction/reload was reported for this initiative.
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
