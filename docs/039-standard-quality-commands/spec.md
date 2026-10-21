# SPEC-039 — Standard quality commands (QLT-001)

- **Status:** Draft for review; implementation not authorized by this planning request.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-001
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Every newly generated supported application has a consistent, documented way to format,
lint, type-check, test, build and verify its source. Failures mean the same thing
locally and in pull-request CI, while stack-specific behavior remains explicit.

The proposed common verbs are format (explicit source-writing action), lint (including
formatting checks), typecheck, test, build and verify. Verify runs all applicable
read-only quality gates, including existing security/contract gates, without calling
format. Build may write ignored output. Mobile build means deterministic source/bundle
validation, not native signing. A check with no applicable meaning must be documented
and reported as not applicable; it must not silently become a successful empty script.

This request authorizes drafting the specification, design and tasks. Specification
approval, implementation authorization, PR review/merge, rollout and acceptance remain
separate. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

Manifest v1 exposes build/start/test only. Later API and mobile contracts already
require broader command vectors; Fastify has package scripts, FastAPI has
scripts/quality.py, and Expo has checks/quality.cjs. Next.js and grouped projects still
need a reviewed common interface. Existing checks are a starting point, not evidence
that every template meets this standard.

Build on SPEC-019/020 dependency/toolchain selection and SPEC-021 immutable generation;
coordinate CI invocation with QLT-002 and regression coverage with QLT-009.

Source/previous-record evidence, not a new runtime verification:

- [docs/project-manifest.md](../../docs/project-manifest.md)
- [scripts/project_manifest.py](../../scripts/project_manifest.py)
- [scripts/project_templates.py](../../scripts/project_templates.py)
- [templates/apps/releases/fastify/1.0.0/package.json](../../templates/apps/releases/fastify/1.0.0/package.json)
- [templates/apps/releases/fastapi/1.0.0/scripts/quality.py](../../templates/apps/releases/fastapi/1.0.0/scripts/quality.py)
- [templates/apps/releases/expo-react-native/1.0.1/checks/quality.cjs](../../templates/apps/releases/expo-react-native/1.0.1/checks/quality.cjs)

## Requirements

### QLT-001-R01 — Command semantics

Expose and document all six verbs, their prerequisites, outputs, network needs and
failure statuses for each supported stack and component; verify aggregates applicable
gates without rewriting source.

### QLT-001-R02 — Versioned discovery

Declare quality command vectors through a reviewed versioned manifest contract where
missing. Validation must remain offline and must not execute commands; existing schemas
retain their behavior.

### QLT-001-R03 — Coding standards

Ship TypeScript/JavaScript conventions for formatting, naming, organization and
idiomatic usage, with enforceable formatter/linter rules and explanatory guidance;
retain Python and mobile standards.

### QLT-001-R04 — Portable execution

Run identical source gates in reviewed pinned containers locally and in CI, using frozen
lockfiles and bounded resources. Advisory/network checks identify unavailable services
as incomplete or failed, never passed.

### QLT-001-R05 — Safe adoption

Generate new immutable releases with matching catalogue hashes and document explicit
adoption for existing apps; group results identify failed components and mobile limits.

## Acceptance criteria

All criteria are pending; drafting does not establish implementation acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-001-AC01 | A clean generated project passes each applicable verb; injected format, lint, type, test and build faults each make verify fail, with tracked source unchanged by verify. | QLT-001-R01 |
| QLT-001-AC02 | Old schema fixtures remain valid; a new fixture exposes the verbs; unknown fields/versions and unsafe vectors fail without executing a sentinel command. | QLT-001-R02 |
| QLT-001-AC03 | Representative enforceable style violations fail lint; format fixes only formatting; generated guidance explains organization/naming and matches the actual configuration. | QLT-001-R03 |
| QLT-001-AC04 | Local and CI reports identify the same revision/toolchain/gates; lock mismatch and unavailable advisory-service fixtures cannot yield an all-passed verify result. | QLT-001-R04 |
| QLT-001-AC05 | New releases generate successfully; historical release integrity checks pass; a group with one failing component fails overall; mobile docs do not claim a signed build. | QLT-001-R05 |

## Decisions and completion

Project owner reviews the initial supported-template matrix and command/schema proposal
before implementation. Use existing API/mobile conventions where compatible; allocate
any new schema versions at implementation time.

This is a proposed default, not a recorded owner decision. The project owner reviews the
open decision before dependent implementation; source discovery and planning review can
proceed meanwhile. Implementation should recheck current source versions, supported
templates and applicable guidance rather than assume this snapshot establishes installed
capability.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.