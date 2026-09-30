# SPEC-009: Release and Production-promotion Skill

- **Status:** Draft; approval and implementation authorization pending
- **Owner:** Daniel
- **Feature:** AGT-007
- **Design:** [TDD-009](./technical-design.md)
- **Tasks:** [TASKS-009](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 6, 15–17
- **Last updated:** 2026-09-30

## Outcome

Prepare a traceable release candidate and, when separately authorized, invoke
an existing project-owned promotion pipeline for the exact artifact and target.
The agent can explain what will ship, why it is eligible, who authorized the
action, how success is verified, and what recovery is permitted.

A request to prepare release notes produces a draft, not a tag or deployment.
A request to promote an approved candidate uses the identified immutable artifact
and preserves existing protected-environment approvals.

## Scope and readiness

Include a repository skill, release-record outline, project release-contract
reference, synthetic pipeline scenarios, and evidence. Support preparation,
readiness review, authorized dispatch, bounded observation, and recovery handoff.
Version conventions come from the selected product; no universal SemVer policy.

Exclude building a registry, production architecture, workflow, IAM role, HCP
workspace, credentials, secrets, database migration system, or rollback engine.
No direct AWS mutations, local Terraform apply, permission broadening, automatic
publishing, or blanket production authorization. Do not change the GptClaw host
pipeline into an application-release pipeline. Tags, releases, package publication,
production dispatch, and destructive recovery need their own concrete scope.

A real promotion requires an approved product-specific release contract,
artifact provenance, target pipeline and recovery/health checks. PRD-001–004,
PRD-008/009 or approved equivalents provide these; they are not implemented by
this skill. GptClaw's host-infrastructure pipeline is not proof of product
promotion readiness. Build and test the skill synthetically now after approval;
real-product acceptance waits for a selected pipeline. No AGT-006/008/009/010
feature is a hard dependency; ordinary project docs supply required facts.

## Proposed defaults and decision

Skill: `.agents/skills/gptclaw-release-promotion/`, scoped initially to GptClaw,
with normal selection and explicit invocation. Preparation is read-only except
requested local release records. No global installation or automatic bootstrap
distribution. Daniel must select the first product, immutable artifact contract,
pipeline identity, environment, and permitted validation/recovery operations
before live acceptance. Each actual promotion has its own authorization.

## Requirements

### REL-001: Resolve an exact release candidate

Identify project/repository, approved source revision, version convention,
artifact digest or equivalent immutable identifier, build provenance, tests,
release notes, target environment, current deployed version, and relevant data
compatibility constraints. Mark absent evidence unknown; do not create a tag,
rebuild an artifact, or infer a successful build from a branch name. Refuse a
mutable-only artifact identifier or source/artifact mismatch for promotion.

### REL-002: Separate preparation, approval, and dispatch

Prepare a reviewable record of exact artifact, environment, pipeline operation,
expected effects, health criteria and recovery path before missing approval is
requested. Honor authorization already supplied for that exact candidate and
target. If either changes, establish whether the new operation is authorized;
do not reuse approval for a different artifact or environment. Preserve pipeline
branch, role and environment gates. A release-note request cannot authorize a
remote release, Git tag, or deployment.

### REL-003: Observe one promotion accurately

Invoke only the reviewed pipeline with validated fixed inputs and record its
run/operation ID. On lost response or timeout, query that run or the documented
reconciliation endpoint before any retry. Do not dispatch duplicates or cancel
unrelated runs. Distinguish queued, awaiting approval, running, failed, cancelled,
and succeeded. Pipeline success is separate from post-deploy acceptance; verify
that the reported deployed identity matches the candidate and required health
checks pass before calling it accepted.

### REL-004: Recovery and evidence

Before dispatch, establish the prior artifact, rollback/roll-forward procedure,
data compatibility or backup prerequisites, and owner for irreversible steps.
If recovery prerequisites are absent, block promotion and state what is missing.
On failure, perform only recovery already authorized for that scope; otherwise
prepare a concrete recovery proposal. Record actual actions, sanitized run links,
checks and unresolved state. Never claim rollback from a requested rollback job
alone or read production secrets to populate a report.

## Acceptance

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Preparation fixtures produce accurate records with missing facts explicit; release-note-only requests cause no tags, releases, dispatches or production access. | REL-001, REL-002 |
| AC-002 | Mutable/mismatched artifacts, changed targets, missing recovery, denied permissions and unmet protected gates stop promotion without bypass or credential expansion. | REL-001, REL-002, REL-004 |
| AC-003 | Existing exact authorization is honored; timeout/lost-response/concurrent-run fixtures reconcile one operation without duplicate dispatch or unrelated cancellation. | REL-002, REL-003 |
| AC-004 | Failed health after pipeline success stays unaccepted; rollback/roll-forward proposals preserve data constraints and distinguish authorization from actual recovery. | REL-003, REL-004 |
| AC-005 | After dependency readiness and specific operation authorization, a fresh-client rehearsal against an existing product's isolated non-production pipeline promotes an immutable synthetic artifact and exercises the contract's failure/recovery path with actual identity/health evidence. | REL-001–004 |
| AC-006 | Tests, reviewer inspection, actual CI, merge, and limitations are recorded; documentation does not portray the non-production rehearsal as a production deployment. | REL-001–004 |

## Completion

Daniel approves this feature and its implementation separately from any product
release. AC-005 validates orchestration in non-production; it grants no standing
production permission and does not establish that every product is release-ready.
Deployed can describe the available skill; Delivered requires all criteria.
Production use always follows that product's approved contract and exact scope.
