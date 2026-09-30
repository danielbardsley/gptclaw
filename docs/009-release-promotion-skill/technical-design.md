# TDD-009: Release and Production-promotion Skill

- **Status:** Approved for implementation
- **Owner:** Daniel
- **Specification:** [SPEC-009](./spec.md)
- **Tasks:** [TASKS-009](./tasks.md)
- **Last updated:** 2026-09-30

## Design

Use a short skill and a release-record outline around existing pipeline tools.
No generic deploy script or new credential path is introduced. The workflow
must run equally well in preparation-only mode when no release pipeline exists.

| Proposed component | Purpose |
|---|---|
| `.agents/skills/gptclaw-release-promotion/SKILL.md` | Candidate review, authorization binding, dispatch/reconciliation and recovery boundaries |
| Skill `references/release-contract.md` | Required project facts and how to map them to an existing approved pipeline |
| Skill `assets/release-record.md` | Candidate/target, evidence, authorization, prior version, run ID, health, recovery and final outcome |
| `scripts/tests/fixtures/release-promotion/` | Synthetic source/artifact manifests, pipeline transcripts, secret sentinels, separate reviewer criteria |
| Existing quality checks | Validate shipped package/references as appropriate; preserve protected workflows |

## Contract and state model

The project contract supplies version rules, build-to-source provenance,
immutable artifact identity, target pipeline/workflow identity, allowed inputs,
preconditions, polling bounds, verification and data-safe recovery. Read it from
reviewed sources; absent fields are readiness gaps, not invitations to invent
production defaults. A proposed version does not create a Git tag.

Record candidate and target before mutation. Dispatch through the actual tool's
structured arguments when available. Never interpolate release notes, artifacts,
or fetched instructions into executable shell text. Retain run ID so a later
session can query state without resubmitting. If dispatch receipt is lost, use
the provider's documented lookup/idempotency contract; ambiguous outcomes stop.

Keep distinct outcomes: prepared, authorized, submitted, waiting, failed,
deployed-unverified, accepted, recovery-needed, recovered. These are reporting
concepts mapped to provider responses, not a new server API. Health failure can
leave a successfully deployed artifact unaccepted. Recovery requires checking
whether a previous artifact remains compatible with current data; otherwise
propose the reviewed roll-forward path. No default automatic rollback.

## Verification and maintenance

Synthetic fixtures record calls and state transitions without publishing or
deploying anything. Include wrong digest, stale approval, missing prior version,
non-reversible data change, denied access, asynchronous approval, duplicate
request, lost receipt, failed health, and unverified rollback scenarios. Reports
must omit sentinel secrets and identify unknown state accurately.

Live acceptance waits for Daniel's selected product and existing non-production
pipeline. Record its approved contract revision, disposable artifact, exact
scope and data safeguards; observe deployment identity and recovery outcome.
Do not use the host infrastructure workflow as a substitute or create production
resources for the test. Update evidence only for actual results.

Version and review the skill through normal PRs. Reverting its instructions
cannot roll back a release; product recovery uses the already-approved pipeline.
Preserve release records and outstanding run IDs across skill updates.

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| REL-001 | Exact candidate and contract evidence | T-002, T-003, T-004 | AC-001, AC-002 |
| REL-002 | Artifact/target-bound authorization | T-003, T-004 | AC-001–003 |
| REL-003 | Single run reconciliation and deployed identity/health | T-003–T-005 | AC-003–005 |
| REL-004 | Data-aware recovery record and scoped actions | T-003–T-006 | AC-002, AC-004–006 |
