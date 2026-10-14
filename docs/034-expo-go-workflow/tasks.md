# TASKS-034: Expo Go workflow

- **Status:** Implementation in progress — source/client inspection prepared
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-034](spec.md) · **Design:** [TDD-034](technical-design.md)

## Planning and implementation

- [x] T-000: Review delivered creation/security, SPEC-033 interface proposal,
  catalogue/sequence and official Go/client references; draft this separate consumer
  plan. No Expo Go installation, phone operation, account or launch implementation.
- [x] T-001: Owner reviews bounded Go workflow, proposed platform/freshness matrix
  and acquisition/fallback boundaries, then authorizes implementation. Confirm
  exact device/fixture scope before live acceptance.
- [ ] T-002: After authorization, verify actual SDK/native/client/OS acquisition and
  private transport prerequisites. Consume the security-cleared SPEC-033 spike;
  prove native launch rules and stale-QR/session isolation. Record unsupported
  platforms accurately; any signed-client/account need is a separate MOB-004 scope.
  (GO-001/002/005; AC-001/002/005)
- [ ] T-003: Add a reviewed versioned eligibility profile and source/client/freshness
  invalidation checks, without editing published releases or silently changing SDKs.
  (GO-001/007; AC-001/007)
- [ ] T-004: Implement read-only native launch serializer/local QR and CLI inspection,
  with complete descriptor/generation/expiry/origin/privacy/ownership validation.
  Pin/check the QR dependency and test malformed/wrong/stale/secret payloads and decode.
  (GO-002/003/006; AC-002/003/006)
- [ ] T-005: Add minimum Go-specific dashboard action/detail with accessible copy/QR
  and accurate unsupported/readiness reasons; preserve all existing web/backend
  links and leave full telemetry to MOB-009. (GO-003/006; AC-003/006)
- [ ] T-006: Run relevant profile/URI/QR/CLI/dashboard/worktree/security regressions
  and CI; package and verify installed provider/frozen consumer parity and safe
  launch-capability rollback with Metro/source retained. (GO-001–003/006/007; AC-001–003/006/007)

## Physical acceptance and delivery

- [ ] T-007: On each claimed physical platform, launch both approved source fixtures,
  validate native UI/assets/interaction, restore a demonstrated Fast Refresh edit,
  force reload and exercise network/tailnet/background/compile/Metro interruption
  and intended-session reconnect. Record actual versions and owner confirmation,
  separately from CI/browser/component tests and any coordinated SPEC-033 evidence.
  (GO-004/005; AC-004/005)
- [ ] T-008: Record sanitized profile/device/installed/CI/owner evidence and runbook,
  review/authorized merge and retained fixture disposition. Mark MOB-003 Delivered
  only for the explicitly accepted scope; retain unsupported platform limitations,
  M1 backend/device/product work, signing and MOB-004/009/010/011 as follow-ups.
  (GO-007; AC-007)

## Handover

T-000 and T-001 are complete. Proposed default is physical iOS and Android; a requested
first-platform slice must be labeled. Metro/private transport and runtime security
are SPEC-033 prerequisites. Device/client eligibility and launch rules are not yet
verified; no source upgrade, route, account, signing or phone operation was performed.

The active owner goal authorizes implementation after MOB-002. This records scope
authorization only; no Go implementation or physical acceptance has occurred. Exact
device/client versions and fixture use remain live-test prerequisites.

## Owner client prerequisites (October 14 UTC)

The owner reports Expo Go 57.0.9 supporting SDK 57 on the Android 11 development
tailnet device. This is a prerequisite report, not native acceptance. No iPhone is
currently available. Continue the iOS software path assuming a recent iPhone and
Go 57.0.9 as requested; exact iOS version and all physical iOS checks remain pending.
No platform certification or criteria waiver follows from these assumptions.


## Current implementation checkpoint

Following paired private host protocol verification, T-003/T-004 are in progress.
An exact candidate Go profile binds SDK 57, the locked graph, source policy and static
config/toolchain contract. Read-only `go inspect` reports exact public source input
hashes, caller-reported client/OS, source eligibility and Metro state separately.
Android 57.0.9 / Android 11 remains a reported candidate; iOS has no verified OS or
physical evidence. Neither profile certifies a phone, advertises a launch rule or
returns a launch URL. Native/config/toolchain/lock/client drift is rejected or
reported unsupported/check-required without mutation or account operations.

Fourteen focused eligibility/CLI cases pass. Source and immutable-provider inspection
agree on both actual approved fixtures (0.767 / 1.173 seconds excluding interpreter
startup), with Ready Metro but client check-required/launch unavailable. Stable
installed pointer remains unchanged. T-002's actual Go nonce/manifest behavior,
local QR, launch/frontend, profile certification, installed rollout and physical
acceptance remain open. See [acceptance](acceptance.md).


Local QR selection and pure rendering now have a pinned zero-finding frontend graph,
independent decode and actual rendered-SVG/browser proof. T-004 remains in progress:
validated Go payload production, CLI ownership/expiry and native stale-QR acceptance
remain open. Fifteen inspection cases and thirteen frontend cases pass; type/build
and full portable browser gate pass. The iOS candidate explicitly reports the current
CLI-login prerequisite outside this credential-free scope; no account fallback or
certification is performed. The Android launch-rule owner check remains pending.


Current native checkpoint: the owner’s manual and locally decoded QR query-based
launches failed on Android 11 / Go 57.0.9, including after bundle warmup. Aggregate
diagnostics isolated three generation-guard rejections before any manifest reached
Metro. A guarded session-path entry is implemented and tested; its new physical
launch check remains pending. Runtime/security/route scope is unchanged. No task
or platform is marked accepted from host-only checks. See the latest acceptance
record for exact evidence and limitations.


The slash-normalized path subsequently reached the native manifest, but the owner
received a packager error at an HTTP address on the HTTPS listener. The SDK-57
Android branch confirms a hardcoded HTTP development probe. Exact Go eligibility
now reports this HTTPS incompatibility; physical UI/edit/reload remains unaccepted.
The [transport decision](../034-expo-go-workflow/client-transport-decision.md) is a
reviewable proposal. No transport amendment, listener conversion or MOB-004 build
is authorized by creating it. Independent platform work remains in progress.


The approved HTTP transport amendment is implemented locally with explicit
selection, typed schema 2, retained prior HTTPS ownership and isolated rollback/
protocol/privacy tests. Both approved one-hour HTTP backends are loopback healthy
and Android bundles warm; exact plans are recorded. Operator replacement and
private/native acceptance are still pending. All broader task gates remain open;
no Delivered or physical-certification claim is made. See current acceptance.
