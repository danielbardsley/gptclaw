# TASKS-031: Reliable Expo / React Native creation

- **Status:** Delivered — all tasks and acceptance complete
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md)

## Planning and scope

- [x] T-000: Read the mobile sequence, catalogue, current creation/resolver, dependency/
  toolchain/job, repository and inventory contracts; draft this planning set. The
  owner requested MOB-001 planning October 13. Official Expo guidance was consulted;
  no implementation, package setup, app generation or service operation ran.
- [x] T-001: Project owner reviews SPEC-031's creation-only scope and supporting
  slices, then separately authorizes implementation. Record the disposition;
  do not infer mobile runtime/backend/build authorization from planning approval.
- [x] T-002: After authorization for the preparation work, propose and verify exact
  SDK/package/toolchain pins, pnpm layout, native package/script compatibility and
  bounded resource profile in owned rootless fixtures. Recheck version-5 availability.
  Record sources/digests/outcomes and resolve any necessary policy/resource change
  with the owner before release freeze. Routine exact pin choices are recorded in
  the implementation PR rather than a separate approval request. (EXPO-001/004; AC-001/004)

## Dependency-ordered implementation

- [x] T-003: Add strict mobile manifest/catalogue/policy contracts, capability metadata,
  development identity rules and compatibility validation. Preserve schemas 1–4,
  published catalogues and web default. Author the minimal native starter/standards
  without automatic upstream agent/plugin adoption or dynamic app config.
  (EXPO-001/002/005/007; AC-001/002/005/007)
- [x] T-004: Integrate exact release selection and generation into the shared resolver;
  add typed config substitutions/provenance, no-overwrite staging/publication and
  normalized-source golden tests. Cover invalid/tampered/occupied/symlink/race/
  concurrent/interrupted cases and deterministic offline local-only creation.
  (EXPO-001/003; AC-001/003)
- [x] T-005: Extend exact toolchain/dependency selection for the chosen mobile policy;
  verify executable/image pins, frozen install, SDK compatibility checks and safe
  staged add/update/remove/recovery. Reject unsupported native/config-plugin changes
  and preserve concurrent edits and legacy policy behavior. (EXPO-004; AC-004)
- [x] T-006: Implement mobile quality jobs through shared owned-job/lock/receipt
  mechanisms without HTTP reservations. Add format/lint/type/test/security/SDK
  checks, interaction/navigation tests and separate iOS/Android JS/assets exports.
  Exercise intentional defects, cold/warm preparation, timeouts and job recovery.
  (EXPO-005; AC-005)
- [x] T-007: Extend broker/repository plan fingerprints and generated source publication
  for exact mobile identities/inputs. Exercise local-only, private initial PR,
  protection/readback, denial, changed-plan and ambiguous/interrupted resume cases
  with synthetic adapters before authorized live provisioning. (EXPO-006; AC-006)
- [x] T-008: Add pinned least-permission generated CI, README/architecture/mobile
  standards, adaptation guidance and an Expo-creation runbook. Review retained
  synthetic examples and remove unrelated upstream demos/configuration. Explicitly
  document bundle versus binary output and unsupported Metro/backend/device/release
  operations; do not advertise unimplemented commands. (EXPO-007; AC-007)
- [x] T-009: Update safe inventory/provider capability handling for mobile source rows;
  distinguish quality support from absent runtime support, keep repo links available
  and reject mobile lifecycle/DB calls without side effects. Add collector/frontend
  regression tests and prepare the required frozen dashboard consumer update.
  (EXPO-008; AC-008)
- [x] T-010: Package schemas/release/policies into immutable providers and extend
  source/installed parity, release immutability and older-provider rejection tests.
  Run full relevant repository, frontend and generated-project gates and configured
  final-head CI. Resolve failures before activation; document exact revisions.
  (EXPO-009; AC-009)

## Installed and owner acceptance

- [x] T-011: With implementation/private scope authorized, record the exact provider/
  dashboard releases, two synthetic project/repository names and retention plan.
  Refresh only the owned provider/collector/frontend through reviewed interfaces.
  Create two apps through source/installed local-only and activated-broker paths;
  verify normalized source, identities, preparation, every quality gate and generated
  PR CI. Show actual private inventory/repo destinations and unchanged observations
  for existing projects. Rehearse scoped failure/recovery and provider/dashboard
  rollback with source retained. Record local/CI/installed behavior separately in
  acceptance.md. (EXPO-001–009; AC-001–009)
- [x] T-012: Project owner confirms the repeatable creation/edit/check/repository
  workflow. Complete review/merge under its applicable gate, record merged revision
  and accepted evidence, and mark only MOB-001 Delivered. Keep TPL-004 native-device
  acceptance, M1 and other mobile features incomplete. Update catalogue/sequence/
  index/runbooks; stop any owned temporary jobs and retain/archive source/repositories
  per the recorded fixture plan. Never delete existing app data or remote repos as
  incidental cleanup. (EXPO-009; AC-009)

## Current handover

T-000–012 are complete. The approved four-name profile, two private repositories,
final stable provider/dashboard and preserved archived bindings are recorded in
[acceptance.md](acceptance.md). Corrective immutable starter 1.0.1, actual generated
workflow/guidance CI, all 540 local cases, four implementation workflows, both
private final-head quality jobs and both managed verification runs passed. Compatible
provider/dashboard rollback/restoration passed with six unchanged application
containers and both existing groups Ready/current afterward.

PR #73 merged as `f40a7f33f6ba8a1f1880b10463cace88f6d88a45` with owner authorization.
The owner subsequently replied “Confirmed” to the dashboard repository-link/runtime
message and creation/edit/check workflow acceptance on October 13. MOB-001 is
Delivered; all criteria pass. This documentation closeout preserves TPL-004's full
native-device scope, MOB-002/003 transport, MOB-010 backend binding and mobile
milestones as follow-ups. Retain both private starter PRs/source and task-owned
verification evidence. The approved advisory exceptions still require removal or
fresh disposition before their recorded October 27 expiry.
