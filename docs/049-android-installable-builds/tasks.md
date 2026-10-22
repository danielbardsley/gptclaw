# TASKS-049 — Android installable builds

Status: Approved free Fieldnotes builds in progress; development APK finished, preview queued, phone acceptance pending. Owner: Project owner.
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

- [x] T1 — Record concrete account/signing/upload/artifact/budget dispositions and
  exact reviewed source/backend/device inputs before any external job. AB-001/AB-002;
  AC-001/AC-002. Revalidate installed capabilities and preserve historical contracts.
  Recorded October 22: account/project/Free quota, PRIVATE access setting, remote
  key custody and exact reviewed input provenance; actual artifact/phone acceptance
  remains a separate check, not implied by this preparation task.
- [x] T2 — Implement strict identity/environment/native-runtime validation and new
  exact tooling/release as needed, preserving published releases and unsigned quality
  checks. AB-001/AB-003/AB-004; AC-001/AC-003/AC-004. Add meaningful refusal/regression tests.
  First-app scope passed source/identity/profile/upload checks in Fieldnotes PR #2;
  no immutable published starter, historical schema or installed provider changed.
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

## Current handover — October 22

The owner approved Fieldnotes, Expo account `bardsley`, Expo-managed Android keys,
free-only builds and the exact temporary native-tool exception through October 28
midnight Eastern. Authentication and PRIVATE internal-artifact access are verified.
No repeat approval is needed for this scope; paid usage, production and store
submission remain outside it.

Fieldnotes PR #2 implements deterministic upload/configuration and durable job
receipts with tested quota/expiry/duplicate/unknown-outcome refusals. The first
cloud attempt failed strict dependency-install admission. The correction preserves
package-age checks and explicitly refuses two install hooks; fresh normal frozen
installation, disposable Android native generation and corrected-source CI passed.

Development job `c789df30-82ca-4849-ad8d-e1a2f1b4ebe5` is FINISHED. Official
authenticated APK retrieval and package/manifest/DEX/signing-block checks passed;
anonymous artifact lookup was denied. Preview job
`d580a4b0-09df-4cd1-bc67-43d8f8b30c71` is queued after a fresh preflight showing
14 free Android builds remaining. Preserve its intent and reconcile before any
retry. No simultaneous or paid build was submitted.

T3 has implemented/tested submission recovery and development artifact access;
preview completion/access remain to verify. T4/T5 cloud and physical gates are
separate: neither phone installation nor Metro/API/native-module/CRUD/recovery/
accessibility behavior has been observed. T6/T7 repeatability, merge and owner
acceptance remain open. See [acceptance](acceptance.md) and the
[tooling review](build-tool-review.md) for exact provenance and limitations.

The initial provider 1.17.0 read-only check found Fieldnotes API/database stopped.
The owner subsequently requested startup: one start operation passed and an
independent status confirmed both ready/healthy, with the private route configured.
See acceptance for the operation receipt; physical phone access remains pending. Prior mobile/quality acceptance and
waivers remain closed; SPEC-049 adds binary-specific evidence. No feature is
marked Delivered from cloud-build success alone.
