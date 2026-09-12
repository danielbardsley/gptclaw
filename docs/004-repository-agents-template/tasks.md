# TASKS-004: Repository AGENTS.md Template

- **Status:** Implemented locally; review and remote acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-004](./spec.md)
- **Technical design:** [TDD-004](./technical-design.md)
- **Last updated:** 2026-09-12

## Phase 0: Planning and review

- [x] **0.1** Inspect repository guidance, AGT-002, architecture, prior initiative
  status, and existing check commands; preserve unrelated work.
- [x] **0.2** Draft spec, design, and dependency-ordered tasks; link the initiative
  and mark AGT-002 Draft in the catalogue.
- [x] **0.3 Owner:** Approve scope and authorize implementation, including the
  GptClaw first adoption, manual distribution, file budgets, and focused checks.

**Gate:** Daniel approved the specification and authorized implementation on
2026-09-12. No repeat implementation approval is required. Review of the resulting
policy revision, merge, and remote acceptance remain distinct completion gates.

## Phase 1: Baseline and reusable contract

Depends on phase 0 approval.

- [x] **1.1** Recheck Git state, applicable guidance, overrides, current command
  sources, and supported-client discovery behavior; record only necessary
  non-secret metadata. Preserve unknown policies/settings.
- [x] **1.2** Write the versioned stack-neutral template and guide covering all
  required sections, placeholder resolution, and explicit applicability.
- [x] **1.3** Review authority, data boundaries, file budgets, portability, and
  independence from future platform tooling against RAG-001–005.

**Gate:** Template and adaptation procedure are ready for real adoption.

## Phase 2: GptClaw adoption and isolated verification

Depends on phase 1.

- [x] **2.1** Populate GptClaw root guidance from checked-in commands, layout,
  version sources, active-planning discovery, and existing data/product rules.
- [x] **2.2** Create a synthetic project fixture with distinct project facts,
  a harmless verification command, real links, and no external dependencies.
- [x] **2.3** Add focused offline validation and meaningful negative cases,
  including proof that policy command text is never executed by validation.
- [x] **2.4** Integrate checks and path triggers with the existing quality
  workflow, preserving all protected deployment behavior.
- [x] **2.5** Run focused tests, repository checks, diff/relative-link checks,
  and applicable safe commands; record exact results and skipped operations.
- [x] **2.6** Rehearse targeted Git rollback in the synthetic project and prove
  preservation of unrelated later edits. Document update ownership/provenance.
- [ ] **2.7** Prepare implementation PR and obtain review of the resulting
  repository guidance; update documentation links.

**Gate:** AC-001–004 and AC-006 have concrete local/review evidence; no host,
infrastructure, credentials, or runtime changes are required.

## Phase 3: Fresh-task acceptance and handover

Depends on phase 2 and approved repository adoption.

- [ ] **3.1** Verify fresh tasks through the supported remote connection in
  GptClaw and the synthetic project without pasting policy content; record
  project/host guidance, command selection, and data-boundary responses.
- [ ] **3.2** Resolve missing/shadowed guidance through reviewed changes and
  repeat affected checks. Preserve AGT-001's separate pending acceptance items.
- [ ] **3.3** Record sanitized AC-001–007 evidence in `acceptance.md`, including
  revision, review/merge links, client/profile metadata, checks, and limitations.
- [ ] **3.4** Clean only task-owned fixtures. After merged implementation and
  all criteria pass, mark AGT-002 Delivered and link evidence in the catalogue.
  Otherwise record the actual pending state; hand over Git status and ownership.

**Gate:** All acceptance criteria pass; a merged PR or static file check alone
is insufficient.

## Traceability

| Requirement | Tasks | Acceptance |
|---|---|---|
| RAG-001 | 1.2, 1.3, 2.1–2.3 | AC-001, AC-003 |
| RAG-002 | 1.1, 2.1, 2.5 | AC-002 |
| RAG-003 | 1.1, 1.3, 2.7, 3.1, 3.2 | AC-004, AC-005 |
| RAG-004 | 1.3, 2.1, 2.2, 3.1 | AC-004, AC-005 |
| RAG-005 | 1.2, 2.6, 2.7 | AC-001, AC-006 |
| RAG-006 | 2.3–2.5, 3.1–3.4 | AC-003, AC-005, AC-007 |

## Current handover

Template, guide, GptClaw adoption, ten focused tests, and workflow integration
are implemented. The isolated rollback preserves unrelated committed and
uncommitted work. Implementation review/merge and fresh-task remote acceptance
remain pending. [Acceptance evidence](./acceptance.md) records the exact checks
and separates local evidence from AC-005 and final completion.
