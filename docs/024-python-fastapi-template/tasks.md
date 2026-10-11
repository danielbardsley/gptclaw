# TASKS-024: Python FastAPI template

- **Status:** Implementation authorized and in progress; acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-024](spec.md) · **Design:** [TDD-024](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect root/area guidance, documentation index/catalogue, existing
  SYS-002/003 and PRJ-003 designs and actual validator/provider/configuration seams.
  Draft this specification/design/task set in an isolated branch; preserve the
  active checkout's unrelated credential-broker work. Source inspection and
  planning request establish context only, not installed Python capability.
- [x] T-001: Project owner reviews SPEC-024/TDD-024 scope and separately authorizes
  implementation. Record those decisions without treating a planning PR merge
  as permission to implement. No duplicate authorization is needed if already
  supplied in the subsequent session. Authorization: October 11 user instruction
  “ok, go ahead and implement the spec.”

## Dependency-ordered implementation

- [ ] T-002: Resolve one exact stable Linux amd64 Python/uv/framework/check-tool
  combination and Python/uv OCI digests from primary sources. Record supported
  versions/platforms, docs-asset hashes/licenses and acquisition verification.
  Specify and exercise wheel-only sources/hashes, uv no-build/download/config/auth
  controls, lock freshness and owned venv/cache placement. Do not commit floating
  defaults. PYAPI-002, PYAPI-003; AC-002, AC-003. Gate: supported wheel graph and pin-specific
  flags proven before enabling ordinary preparation.
- [ ] T-003: Implement/review bounded project v2 API, Python toolchain/registry v2
  and catalogue v2 contracts plus family-specific validation/dispatch and
  capabilities/errors/results. Preserve v1 schemas, Node legacy mapping and exact
  Next.js release identity/default. Extend immutability checks across catalogue
  versions. Specify quality action and state/receipt compatibility. Validation/
  discovery must not execute/import/fetch project code. PYAPI-001, PYAPI-007, PYAPI-008;
  AC-001, AC-007, AC-008. Gate: positive/negative contract fixtures and legacy regressions.
- [ ] T-004: Implement immutable bounded rootless Python/uv image acquisition,
  exact executable verification, scoped receipts and honest warm reuse/recovery.
  Integrate the selected image/profile with shared jobs. Test bad artifacts,
  wrong platform/versions, missing/corrupt images, concurrent acquisition and
  interrupted ownership. PYAPI-002; AC-002.
- [ ] T-005: Implement the Python dependency-policy adapter for status, locked
  install, typed add/update/remove and recover/abort. Reuse shared locks/limits,
  staged candidate checks, original-hash conflict refusal and publication journal.
  Test stale locks, denied source/config/build/download/auth inputs, concurrent
  edits, partial publish/install and repair without rewriting coherent source.
  Maintain pnpm behavior. PYAPI-003; AC-003. Gate: no dependent ordinary service
  execution until preparation/policy and recovery tests pass.
- [ ] T-012: Bake the owner-supplied standards into the versioned generated guide,
  pyproject/config/CI and AGENTS/README references. Preserve source provenance and
  a disposition for every coding section; review uv/groups, dotenv deferral and
  proposed pip-audit/Safety adaptation before accepting them. Configure Black/
  isort/Ruff without competing fixes, strict types/Google docstrings, complete
  critical statement/branch coverage and Bandit/advisory gates. Prove DI/service
  behavior, safe logs, bounded 429, CORS/headers, versioned pagination and readiness.
  Record review-only design/async/OWASP checks and conditional integration rules.
  Dependencies: T-002/T-003; co-deliver with T-006 before T-008 acceptance. PYAPI-010;
  AC-004, AC-007, AC-010.

- [ ] T-006: Create/register the exact FastAPI release, typed non-secret settings,
  stateless synthetic sample, mounted prefix, health, OpenAPI and self-hosted docs.
  Apply PYAPI-010 and [the owner-derived standards](python-standards.md): src layout,
  injected service objects, versioned/paginated API, distinct readiness, safe JSON
  logs, CORS/headers/admission and documentation. Add Black/isort/Ruff/mypy/pytest/
  coverage/Bandit/audit/pre-commit, build/preflight, verify, pinned CI, metadata and
  examples; T-012 records the detailed standard-to-check mapping. Verify
  generation refuses occupied/unsafe destinations and validates staged output;
  implement no generation hooks. PYAPI-001, PYAPI-004, PYAPI-006, PYAPI-007, PYAPI-010;
  AC-001, AC-004, AC-006, AC-007, AC-010.
- [ ] T-007: Integrate API target selection, preparation/fingerprints, shared
  lifecycle/Quadlet/ports/health/logs and scoped quality CLI jobs. Prove reload
  and syntax-error recovery, stopped-target format/dependency changes, no implicit
  sync/toolchain switch and private prefixed docs/redirect behavior. Include Python
  schemas/policy/code/assets in provider snapshots; preserve selected templates
  through existing repository generation without credential-policy changes.
  PYAPI-005, PYAPI-006, PYAPI-008; AC-005, AC-006, AC-008.
- [ ] T-008: Run generated-container checks and deliberate format/import/lint/
  type/API/docstring/coverage/security failure cases, including missing coverage
  and unavailable advisory data. Record critical statement/branch coverage (each
  at least 80%), scan thresholds and explicit hook behavior. Prove build rejects
  broken imports/app construction and verify propagates each failure. Add
  golden-template and pinned image CI alongside existing Next.js checks; update relevant repository check wiring. PYAPI-007;
  AC-007, AC-010.

## Verification and delivery

- [ ] T-009: Run focused offline manifest, catalogue/release, toolchain, dependency,
  lifecycle/snapshot and repository-generation regressions; run the prepared
  repository checker, changed shell syntax checks where applicable and diff/link
  checks. Submit implementation PR(s), record final-head configured CI and retain
  existing Next.js release/source/state/credential behavior. Record code revisions
  and skipped checks honestly. PYAPI-008, PYAPI-009; AC-001, AC-002, AC-003, AC-007, AC-008, AC-009.
- [ ] T-010: Through the reviewed provider on EC2, exercise a task-owned API and
  independently running synthetic Next.js project. Record acquisition/preparation
  cold/warm timings, exact image/versions, limits/loopback, health, docs/API valid
  and invalid input, queries/redirects, source update/syntax-error recovery,
  lifecycle/logs, busy/interruption and scoped stop/source retention. Obtain an
  authorized client's private HTTPS docs/API/update observation; local loopback
  or CI alone cannot close AC-006. Trial scoped rollback/refusal and document owned
  fixture disposition without broad cleanup. PYAPI-005, PYAPI-006, PYAPI-008, PYAPI-009; AC-005, AC-006, AC-008, AC-009.
- [ ] T-011: Write sanitized acceptance.md with AC-001–010 results, actual local/
  generated CI/live/client evidence, pins/revisions/PRs, rollback/recovery and
  limitations. Update runbooks/index/catalogue only to actual approved/merged/
  accepted state. Project owner accepts the initial standalone API slice after
  implementation merge and all required criteria pass; record deferred AI,
  database and RUN-006 scopes and leave supporting features' wider scopes open.
  PYAPI-009; AC-009.

## Current handover

Planning request: Python/FastAPI is the preferred backend stack; draft TPL-003
before RUN-006. This initiative is planning only. Observed implementation supports
Next.js/Node/pnpm, so the proposal includes its necessary Python execution/policy
and versioned contract extensions. The owner supplied python.md on October 11 and requested incorporation. Its
original content and scoped adaptations are now preserved in this initiative.
Existing source inspection and primary tool documentation inform the draft; no Python app, dependency install, host change,
repository creation or live acceptance was performed.

The project owner authorized implementation on October 11. Current action:
complete implementation verification, CI and scoped live/client acceptance. Exact pins and fixed uv/redirect contracts are implementation tasks,
with measurable gates above. Planning verification and delivery results are
recorded here after execution; implementation tasks remain unchecked.

Initial planning verification on October 11 passed relative-link review for all
181 local links across the original six changed documents, coverage of the original
nine requirement/acceptance IDs, and whitespace checks. The standards amendment
adds PYAPI-010/AC-010 without renumbering earlier requirements/tasks and adds T-012.
Amendment verification results are recorded after execution below. Runtime/
repository test suites and Terraform checks are not required for these documentation
changes; no implementation, live service or feature acceptance is claimed.

Standards-amendment verification on October 11: all 190 relative local links across
the eight planning/source documents resolve, and PYAPI-001–010 / AC-001–010 are
represented in the spec, design and tasks. The archived source matches the supplied
attachment after trailing-whitespace normalization; both original and archived
SHA-256 values are recorded. Implementation/acceptance tasks remain unchecked.
Whitespace checks passed after staging the seven amendment files. No runtime,
repository-suite, Terraform or live checks were run for this documentation change.
