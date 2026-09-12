# TASKS-003: Reviewed Host AGENTS.md

- **Status:** Implemented locally; policy review and live acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-003](./spec.md)
- **Technical design:** [TDD-003](./technical-design.md)
- **Last updated:** 2026-09-12

## Working rules

Daniel approved the specification and authorized implementation on 2026-09-12.
The implementation is prepared for revision-specific policy review and rollout. Recognize authorization already provided; do not
add repeated approval gates for routine work within that scope. Preserve user
changes, authentication, host access, and the AWS pipeline boundary. All live
policy operations run as `forge`; automated tests use isolated directories.

## Phase 0: Review and baseline

- [x] **0.1 Owner:** Review SPEC-003/TDD-003, approve scope and implementation,
  including the proposed file locations, copy-based distribution, size budget,
  update/rollback behavior, and supported remote profile.
- [x] **0.2 Repository:** Inspect Git state and applicable guidance; prepare a
  feature branch or worktree without disturbing existing work.
- [x] **0.3 Operator:** Confirm the actual remote launch profile, Codex/client
  versions, relevant instruction settings, policy/override presence, ownership,
  and modes without dumping environment/configuration or credential contents.
- [x] **0.4 Repository/operator:** Recheck official discovery guidance against
  the installed client. Record profile differences and reconcile the design
  before selecting a live destination. Identify existing-policy migration needs.

**Gate:** Implementation authorized; app-server profile confirmed as
`/home/forge/.codex`. Existing home mode is `0775`; explicit remediation to
`0700` is required before rollout. No global policy or override was present. An
unmanaged policy or unexpected override is preserved pending reconciliation.

## Phase 1: Canonical policy

Depends on phase 0.

- [x] **1.1 Repository:** Create `config/codex/AGENTS.md` with identifier/version
  and the seven content sections described in TDD-003 section 4.
- [x] **1.2 Repository:** Map every security, delivery, authorization, and
  evidence agreement in HAG-003/004/005 to concrete policy wording.
- [x] **1.3 Repository:** Check instructions against accepted platform controls
  and current runbooks. Keep SPEC-002 credential exceptions scoped; do not make
  future tooling or backup acceptance prerequisites for this feature.
- [x] **1.4 Repository:** Keep essential rules standalone and within 8 KiB;
  use stable platform references only for optional detail. Review conflict and
  prior-authorization wording to avoid unsupported authority claims.

**Gate:** Complete, concise policy content ready for owner review (AC-001).

## Phase 2: Installation and verification tooling

Depends on phase 1; follows the interface in TDD-003 section 5.

- [x] **2.1 Repository:** Implement immutable-commit source extraction and
  validation, explicit destination selection, dependency checks, and safe
  path/ownership/mode/override preflight.
- [x] **2.2 Repository:** Implement strict provenance parsing, checksum
  comparison, no-op detection, expected-current checks, and unmanaged/drift
  refusal. Do not infer review authorization from a commit's existence.
- [x] **2.3 Repository:** Add bounded locking, same-filesystem staging, atomic
  policy publication, private metadata, one previous managed version, and
  cleanup restricted to invocation-owned temporary files.
- [x] **2.4 Repository:** Implement read-only verification with documented
  status labels/exit codes, and rollback with checksum validation and locking.
- [x] **2.5 Repository:** Implement failure diagnostics for publication
  interruption and missing/corrupt metadata. Document explicit reconciliation
  and first-install removal; do not silently repair unknown state.

**Gate:** Reviewable local tooling with no root, network, credential, service,
or AWS mutation requirement (HAG-006).

## Phase 3: Tests and operational documentation

Depends on phase 2.

- [x] **3.1 Repository:** Add isolated tests for fresh install, no-op,
  commit-versus-working-tree behavior, update, rollback, and previous-version
  provenance.
- [x] **3.2 Repository:** Cover unmanaged/drifted files, invalid metadata/source,
  wrong checksums, size/encoding failures, symlinks, modes/ownership, overrides,
  concurrency, and interruption around publication.
- [x] **3.3 Repository:** Assert verification makes no writes and synthetic
  auth/config sentinels retain contents and modes throughout all operations.
- [x] **3.4 Repository:** Integrate focused tests and policy validation with
  existing repository checks/CI. Run relevant shell syntax checks, tests,
  repository checks, and diff/relative-link review. Terraform execution is not
  required for a change that leaves infrastructure untouched.
- [x] **3.5 Repository:** Write `runbooks/manage-host-agents.md`: reviewed
  revision selection, profile preflight, unmanaged-policy preservation,
  installation, verification, update, rollback, failed-publication recovery,
  temporary override ownership/expiry, and first-install removal.
- [x] **3.6 Repository:** Update connection and recovery runbooks with policy
  installation and fresh-task checks, including restoration after root-volume
  replacement and preservation of all authentication material.
- [ ] **3.7 Repository:** Prepare a PR describing the final policy/tooling,
  validation, and operational limits. Obtain owner review of the exact policy
  revision used for live installation; record review provenance.

**Gate:** AC-002 local checks pass; AC-001 content mapping is complete, with
owner review of the resulting policy revision still pending. Policy, tests,
and runbooks are reviewable.

## Phase 4: Live rollout and behavior verification

Depends on phase 3 and authorization for the reviewed live installation.

- [ ] **4.1 Operator:** Confirm `forge`, effective remote profile, destination
  state/modes, and lack of shadowing overrides. Resolve any preflight conflict
  explicitly while preserving existing content.
- [ ] **4.2 Operator:** Install from the reviewed full commit SHA. Run read-only
  verification and record revision, checksum, ownership, modes, and timestamp.
- [ ] **4.3 Operator:** Start fresh tasks through the actual ChatGPT SSH
  connection in GptClaw and an independent scratch Git project. Confirm host
  policy inheritance without pasting policy content into prompts.
- [ ] **4.4 Operator:** Run the safe explanation scenarios in TDD-003 section 6
  for AWS workflow, secrets, user changes, evidence, repository guidance, and
  already-granted versus missing authorization. Use disabled tools or verified
  read-only mode; execute no hazardous actions.
- [ ] **4.5 Operator:** Rehearse update/rollback using reviewed policy revisions,
  verify restored hashes and guidance in a fresh task, then reinstall and
  reverify the intended final revision. If no prior reviewed revision exists,
  prepare a harmless reviewed version increment to exercise the cycle.
- [ ] **4.6 Operator:** Remove only task-owned scratch fixtures; preserve
  ongoing sessions and unrelated work. Record unsupported launch paths or any
  behavior that still needs resolution; rerun failed checks after correction.

**Gate:** AC-003 through AC-006 pass on the actual supported remote connection.
A CLI-only result, installed-file presence, or policy self-description alone
cannot replace the complete remote verification.

## Phase 5: Acceptance and handover

Depends on phase 4.

- [ ] **5.1 Repository:** Create `acceptance.md` mapping AC-001 through AC-007
  to sanitized review links, source revision, active checksum, versions,
  filesystem test results, remote scenarios, and rollback evidence.
- [ ] **5.2 Owner/operator:** Confirm Daniel owns future policy review,
  installation, temporary-exception removal, and restoration after replacement.
- [ ] **5.3 Repository:** Update initiative/catalogue status only when every
  acceptance criterion passes. Preserve AGT-002 and later features as separate
  scope. Report outstanding limitations and final Git state honestly.

**Gate:** AGT-001 accepted, active revision identified, and handover complete.

## Traceability

| Requirement | Tasks | Acceptance |
|---|---|---|
| HAG-001 | 1.1, 1.2, 2.1, 2.2, 3.7, 4.2, 5.1 | AC-001, AC-003 |
| HAG-002 | 0.3, 0.4, 2.1, 4.1, 4.3, 4.4 | AC-003, AC-004, AC-005 |
| HAG-003 | 1.1-1.3, 4.4 | AC-001, AC-004, AC-005 |
| HAG-004 | 0.1, 0.2, 1.1-1.4, 4.4 | AC-001, AC-005 |
| HAG-005 | 1.1, 1.2, 3.4, 4.4, 5.1-5.3 | AC-001, AC-004, AC-005, AC-007 |
| HAG-006 | 2.1-2.5, 3.1-3.3, 4.1, 4.2, 4.5 | AC-002, AC-003, AC-006 |
| HAG-007 | 1.4, 3.5, 3.6, 4.5, 5.1-5.3 | AC-001, AC-006, AC-007 |

Current evidence and pending gates: [Acceptance status](./acceptance.md).
