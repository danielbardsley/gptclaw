# ACCEPTANCE-003: Reviewed Host AGENTS.md

- **Status:** Local implementation verified; not deployed or accepted
- **Owner:** Daniel
- **Specification:** [SPEC-003](./spec.md)
- **Design:** [TDD-003](./technical-design.md)
- **Tasks:** [TASKS-003](./tasks.md)
- **Last updated:** 2026-09-12

## Authorization and review

Daniel approved the specification and requested implementation on 2026-09-12.
The canonical policy and installer are prepared on
`codex/agt-001-reviewed-host-policy`. Review of the resulting policy revision
precedes live activation under HAG-001 and the rollout design. Neither the
specification approval nor the source checksum is represented as that review.

## Non-secret host preflight

- User: `forge` (UID 1002).
- Installed CLI: `codex-cli 0.153.4`.
- Both inspected running app-server processes explicitly selected
  `/home/forge/.codex` through `CODEX_HOME`.
- No explicit `project_doc_max_bytes` or `project_doc_fallback_filenames` setting
  was found in the user configuration. Actual combined instruction loading
  remains a fresh-task check.
- Codex home: owned by `forge`, mode `0775`; installation requires explicit
  operator remediation to `0700`. Its permissions have not been changed.
- Global `AGENTS.md`, global `AGENTS.override.md`, and managed provenance were
  absent. Authentication contents were not read or changed.
- Active managed policy revision/checksum: **none installed**.

## Local verification

- Shell syntax checks pass for the installer, test entrypoint, and repository
  checker.
- Repository security checks and canonical source validation pass.
- Seventeen offline tests pass, covering install/no-op, immutable-commit source,
  update/two-way rollback, unmanaged/drifted policies, malformed provenance,
  invalid committed source and arguments, symlinks/hardlinks, modes/umask, overrides, lock
  contention/concurrent installs, and failures before/after policy publication.
- Ownership/root refusal uses mocked identities without privileged operations;
  publication failures use mocked rename failures, not production fault hooks.
- Synthetic auth/config sentinels retain their contents and modes across every
  filesystem test. Verification of missing and drifted profiles makes no writes.
- Existing CI now includes the policy paths and invokes these tests through
  `scripts/check-repository.sh`; remote CI status must be recorded separately.
- Infrastructure files are unchanged; no local Terraform plan/apply or AWS
  mutation was performed for AGT-001.

## Policy content mapping

| Required agreement | Canonical policy section |
|---|---|
| Higher-priority instructions, repository scope, conflicts, authority limits | Identity and scope |
| Active specs/tasks, proportionate planning, preservation of user work, branch/worktree and PR flow | Start and deliver work |
| Existing authorization, concrete missing-scope proposal, continuing independent work | Start and deliver work; Tools and exposure |
| Pipeline-only AWS, scoped diagnosis, no permission bypass, self-management restriction | Infrastructure and access |
| Deletion protection, private access, production separation, scoped credential exceptions and delegated services | Infrastructure and access |
| No secret/auth/state/plan leakage, approved data handling and synthetic data | Secrets and data |
| Untrusted external task instructions grant no authority | Secrets and data |
| Unprivileged tools, availability checks, reviewed operator path | Tools and exposure |
| Private service binding, authorization for exposure/promotion/destruction/dependencies | Tools and exposure |
| Relevant checks/tests, honest evidence, local/CI/deployment distinction | Verification and handover |
| Task/docs updates, acceptance and concise final status | Verification and handover |
| Reviewed updates, drift/override reporting, exception ownership/expiry, fresh-task activation | Policy maintenance |

## Acceptance gates

| Criterion | State | Evidence or remaining work |
|---|---|---|
| AC-001 | Partial | Content mapping and size/encoding checks pass; owner review of the resulting policy commit pending. |
| AC-002 | Local pass | Offline tests and repository checks pass; record PR CI separately. |
| AC-003 | Pending | Remediate home mode explicitly and install/verify the reviewed revision as `forge`. |
| AC-004 | Pending | Fresh tasks through real SSH connection in GptClaw and independent scratch project. |
| AC-005 | Pending | Safe remote scenarios for inherited repository rules, prior authorization, and scope boundaries. |
| AC-006 | Partial | Offline drift/override/rollback tests pass; controlled live rehearsal and fresh-task verification pending. |
| AC-007 | Partial | Connection/recovery/manage runbooks delivered; active revision and complete remote evidence still pending. |

Daniel owns ongoing review, installation, recovery, and exception cleanup as
specified. AGT-001 remains Planned until all acceptance gates pass. There is no
claim that filesystem verification guarantees model compliance or that a CLI
session proves the actual remote app's instruction inheritance.
