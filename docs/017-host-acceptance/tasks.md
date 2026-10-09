# TASKS-017: Development host acceptance

- **Status:** Draft; execution pending scope and interruption readiness
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Specification:** [SPEC-017](spec.md)
- **Design:** [TDD-017](technical-design.md)
- **Evidence:** [Acceptance record](acceptance.md)

## Planning and authorization

- [x] T-000: Read existing specs, acceptance records, fixture interface and
  runbooks; draft the coordinated plan requested by Daniel. Earlier read-only
  host observations are attributed in the acceptance record.
- [ ] T-000A: Daniel reviews the plan and authorizes the desired execution scope.
  Reuse any existing explicit scope; agree independent observation and the
  logout/reboot window/operator path before dependent interruption tests.

## Execution in dependency order

- [ ] T-001: After T-000A, capture actual deployment/CI provenance, matching
  receipts, tools/policy and storage/identity/mapping baseline. Preserve unrelated
  state; resolve conflicts before fixture work. (HA-001, HA-003; AC-001, AC-003)
- [ ] T-002: Establish independent CLI SSM access; verify private access and
  tagged online node; obtain attributed manual-key-free enrollment confirmation.
  Require recovery access before dependent tests. (HA-002; AC-002)
- [ ] T-003: After T-001/T-002, inspect and run the existing fixture on a free
  loopback port; record build, namespace, bind ownership, DNS/HTTPS, HTTP,
  non-loopback refusal, limits and crash/restart evidence. Retain printed owned
  path for subsequent checks and cleanup. (HA-003, HA-004; AC-003, AC-004)
- [ ] T-004: After T-003 and observation readiness, coordinate closing all forge
  sessions; independent operator records continued service/HTTP with no forge
  session. Retain recovery connection. (HA-005; AC-005)
- [ ] T-005: After T-004, in the approved window with backup/write readiness,
  reboot through the reviewed operator path. Independently capture changed boot
  ID and active service/HTTP before any new forge login, then verify reconnection.
  Stop on failure; record scoped recovery. (HA-005, HA-006; AC-005, AC-006)
- [ ] T-006: Export evidence; use fixture cleanup to remove only owned resources;
  verify no listener or boot activation and preservation of unrelated state.
  If testing stops early, disposition owned resources without broad deletion.
  (HA-006; AC-006)
- [ ] T-007: Reconcile original criteria and missing historical evidence,
  especially SPEC-014 synthetic-source preservation/rebuild across replacement.
  Do not repeat replacement or waive criteria. Update acceptance/tasks/catalogue
  only to proven status, review evidence PR and obtain Daniel's final acceptance.
  (HA-003, HA-007; AC-003, AC-007)

## Current handover

This request produces planning documents and a review PR. No fixture, session
closure, reboot, AWS mutation or acceptance execution has been performed for
SPEC-017. Preliminary read-only observations do not complete the tasks above.
Next: Daniel reviews scope; the operator supplies independent recovery access
and interruption readiness. Missing historical replacement evidence may leave
SYS-001 acceptance pending even after current-host tests pass.
