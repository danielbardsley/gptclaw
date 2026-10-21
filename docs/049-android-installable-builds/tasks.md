# TASKS-049 — Android installable builds

Status: Specification approved; Fieldnotes selected; build preparation in progress, external-operation decisions pending. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning

- [x] P1 — Reconcile current main, mobile closeout, quality delivery and roadmap;
  select MOB-004 with necessary Android MOB-005/006 slices. Preserve accepted
  SPEC-036 waivers and closed tasks. Draft linked spec/design/tasks.
- [ ] P2 — Review app/device/account/custody/budget choices with project owner;
  validate exact tool/native-module matrix and proposed adapter/receipt interfaces.
- [x] P3 — Project owner reviewed and approved SPEC-049 on October 21 and selected
  Fieldnotes. Reversible build preparation proceeds under that approval; external
  account/signing/build/budget and runtime scope remain gated by concrete choices.
  No repeat specification or app-selection approval is required.

## Implementation and external-operation gates

Offline preparation can proceed under P3. Resolve applicable P2 choices before
external account/signing/build actions; record exact versions before dependency changes.

- [ ] T1 — Record concrete account/signing/upload/artifact/budget dispositions and
  exact reviewed source/backend/device inputs before any external job. AB-001/AB-002;
  AC-001/AC-002. Revalidate installed capabilities and preserve historical contracts.
- [ ] T2 — Implement strict identity/environment/native-runtime validation and new
  exact tooling/release as needed, preserving published releases and unsigned quality
  checks. AB-001/AB-003/AB-004; AC-001/AC-003/AC-004. Add meaningful refusal/regression tests.
- [ ] T3 — Implement bounded EAS submission/observation and durable interrupted-job
  recovery; test synthetic credential/upload exclusion, failure, unknown state and
  duplicate refusal. AB-002/AB-005; AC-002/AC-005. Verify authenticated artifact access.
- [ ] T4 — Build/install development client; verify owned private Metro/API access,
  edit/reload, selected native capability and rebuild requirement. AB-003; AC-003.
- [ ] T5 — Build/install standalone preview; with Expo Go absent and owned Metro
  stopped, run physical CRUD/relaunch/persistence/outage/reconnect/uncertain-write/
  accessibility checks. AB-004; AC-004. Retain synthetic data and unrelated services.
- [ ] T6 — Repeat from recorded inputs; exercise interrupted-job and compatible
  corrective-build recovery. Run affected repository/project checks and record exact
  local/CI/remote-build/physical/owner results and limitations. AB-001–AB-005; AC-001–AC-006 (repeatability: AC-006).
- [ ] T7 — Publish implementation PR and sanitized acceptance; merge through reviewed
  workflow, update catalogue for only accepted scope, and clean up only owned active
  fixtures after recording source/data/key retention. No automatic production release.

## Current handover

Planning branch contains documentation only. Fieldnotes source guidance and its
clean Git state were inspected; its current app/package inputs were read without
credentials. No EAS account, key, build submission, installation, runtime, AWS or
production action has been performed. Next action is the remaining P2 account,
signing, budget and device decisions and exact tool/interface validation. Prior mobile and quality task closures stand;
this initiative adds binary-specific evidence rather than reopening those tasks.
