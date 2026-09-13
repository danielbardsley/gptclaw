# SPEC-005 acceptance evidence

- **Status:** Implemented; review, CI, merge, and remote acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-005](./spec.md)
- **Design:** [TDD-005](./technical-design.md)
- **Tasks:** [TASKS-005](./tasks.md)
- **Implementation PR:** [PR #11](https://github.com/danielbardsley/gptclaw/pull/11)
- **Evidence date:** 2026-09-13

Daniel authorized implementation on 2026-09-13. This evidence covers the
implementation changes following planning commit `0640b1e` on
`codex/agt-003-spec`; the PR's commits identify the published revision. The
reviewed/merged revision must be recorded when those gates complete. Local
verification is not evidence of remote instruction loading or feature delivery.

## Acceptance mapping

| Criterion | State and evidence |
|---|---|
| AC-001 | Local content review and static checks complete; Daniel's resulting-policy review pending. Versioned inert template, five examples, and adaptation guide cover the five sections, provenance, placement, budgets, authority, and updates. All example links are checked at their intended synthetic placements. |
| AC-002 | Local source comparison and root-contract regression tests pass; owner review pending. Infrastructure adoption links existing versions, lock, compute replacement, tests, root commands, and CI. Root discovery pointer preserves shared constraints. No Terraform, host-policy source, bootstrap, global settings, workflow, or runtime changes. |
| AC-003 | Passed locally: nine nested tests cover positive/negative contracts, scope/parent boundaries, local links, encoding/size, inert sources, no execution/network/unrelated reads, and fixture placement. The existing ten root-guidance tests still pass. |
| AC-004 | Pending: new task through the supported remote connection directly in `infra/dev-host`, without policy text supplied in the prompt. |
| AC-005 | Pending: fresh root discovery, siblings, deeper specialization, and cross-area behavior. Fixed scenario sources and reproducible helper are ready; content/placement checks are not client behavior evidence. |
| AC-006 | Partial preflight only: shell profile metadata and conservative file budgets below. Remote effective settings, override behavior/restoration, and conflict handling remain pending. Existing unknown settings/files were preserved. |
| AC-007 | Passed locally: isolated adoption/update Git reverts preserved the root policy, unrelated later commit, dirty tracked README, and untracked note. Guide records ownership, independent version updates, targeted live rollback, and fresh-task re-verification. No live rollback was executed. |
| AC-008 | Pending: this record maps every criterion, but resulting-policy review, remote observations, CI results, and merged implementation revision are outstanding. AGT-003 remains Planned. |

## Local verification

Executed from the GptClaw root on 2026-09-13:

- `python3 scripts/tests/test_nested_agents.py`: nine tests passed. The initial
  run found the not-yet-created guide link; after the guide was written, the
  focused suite passed.
- `./scripts/check-repository.sh`: passed repository invariants and 41 tests:
  installer 17, bootstrap 5, root guidance 10, nested guidance 9.
- `bash -n scripts/check-repository.sh`: passed.
- `git diff --check` and `git diff --cached --check`: passed at final validation.
- Relative-link review: 81 local links in 11 changed Markdown files passed
  (fenced/inline code excluded);
  inert example/fixture links validated after materialization by the nested suite.

The shared root validator now accepts explicit section, placeholder, and size
parameters; its original defaults and tests remain unchanged. Validation stats
linked targets but does not read their contents, interpret policy commands, or
fetch external URLs. The nested suite/helper commands use Python's `-B` option
to avoid leaving import caches in the checkout. Human review still owns meaning, command correctness, scope,
and conflict resolution. Fixed fixture Git operations are separate from validation.

The infrastructure policy references the actual root command table, Terraform
version/lock, README, and workflow. Its test-provider distinction was checked
against `tests/host-policy.tftest.hcl` (mock AWS, real cloud-init) and the other
mock-provider test files. Existing workflow filters already cover root guidance,
`templates/agents/**`, `scripts/**`, and `infra/dev-host/**`; no workflow edit
was necessary. Protected plan/apply conditions remain unchanged.

Terraform format/init/validate/test were not run locally: no Terraform code or
behavior changed. No deployment was dispatched, host policy installed, dependency
fetched, application started, or real data used. Existing CI runs its broader
quality job; its outcome is recorded separately after publication.

## Discovery preflight and file budgets

Observed shell metadata, not proof of the remote desktop launch profile:

- `codex-cli 0.153.4`, Python 3.12.3, Bash 5.2.21, Git 2.43.0.
- Shell Codex profile: `/home/forge/.codex`; installed host guidance: 5087 bytes.
- Global, repository-root, `infra`, and `infra/dev-host` override files absent.
  No intermediate `infra/AGENTS.md` or existing area adoption was present.
  Ancestor guidance at `/srv`, `/srv/forge`, and `/srv/forge/projects` was absent.
- `project_doc_max_bytes` and `project_doc_fallback_filenames` were not set at
  top level in the shell profile config. No full configuration or environment
  was printed. Remote profile/launch overrides remain unverified.
- Startup discovery expectations come from the official reference linked in
  [the nested guide](../../templates/agents/nested/README.md), checked for the
  specification on 2026-09-12. Actual client behavior still requires fresh tasks.

| File | UTF-8 bytes | Local budget |
|---|---:|---:|
| Root adoption | 8082 | 8192 |
| Infrastructure adoption | 3431 | 4096 |
| Nested template | 1087 | 4096 |
| Infrastructure example | 1688 | 4096 |
| Mobile example | 1711 | 4096 |
| Backend example | 1628 | 4096 |
| Migrations example | 1675 | 4096 |
| UI example | 1647 | 4096 |

Conservative startup totals include the installed host file plus selected project
files and two newline bytes between files. These are a manual/static budget
inventory, not a loader simulation or proof of effective configuration:

| Entry/scenario | Bytes |
|---|---:|
| GptClaw root | 13171 |
| GptClaw `infra/dev-host` | 16604 |
| Synthetic baseline backend | 7887 |
| Synthetic baseline UI | 7906 |
| Synthetic baseline backend/archive | 9587 |
| Synthetic override UI | 8266 |
| Synthetic conflict backend | 8019 |
| Synthetic conflict backend/archive | 9719 |

Each total is below the documented 32768-byte default. Confirm the effective
remote budget and actual loading before passing AC-006. Other sibling chains in
the override/conflict fixtures are unchanged from baseline. Explicit area reads
by a root-started task must be recorded separately from its startup chain.

## Remaining operator acceptance

Daniel owns review of the resulting policy revision, supported-connection
verification, and merge. The [nested guide](../../templates/agents/nested/README.md#fresh-task-acceptance)
provides a fixed fixture helper, entry points, explanation-only prompts, and a
separate reviewer answer matrix. It covers direct/root starts, siblings, deeper
scope, cross-area work, shadowing/restoration, and unresolved conflicts.

This continuing task already has guidance in its conversation and cannot satisfy
fresh-task acceptance. No new user-owned tasks were created as part of this
implementation request. The approved spec explicitly leaves unexercised remote
entry points pending; no local CLI result substitutes for them. After review,
exercise those scenarios in new tasks through the supported connection and
record sanitized revision/client/profile/entry-point/results for each one.

All temporary projects used by local tests and budget checks were task-owned and
cleaned by their temporary-directory contexts. Remote fixtures have not yet been
created. At experiment expiry, the operator removes only the temporary override
in its confirmed fixture and verifies restored UI guidance in another fresh task.
Clean those confirmed projects only after saving acceptance evidence.

Record CI and the merged revision here when available; mark Delivered only after
all criteria pass. AGT-001 and AGT-002 acceptance remains separate and unchanged.
