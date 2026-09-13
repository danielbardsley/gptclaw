# ACCEPTANCE-003: Reviewed Host AGENTS.md

- **Status:** Policy installed on existing host; fresh-task and provisioning acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-003](./spec.md)
- **Design:** [TDD-003](./technical-design.md)
- **Tasks:** [TASKS-003](./tasks.md)
- **Last updated:** 2026-09-12

## Authorization and review

Daniel approved the specification and requested implementation on 2026-09-12.
Daniel reviewed PR #6 and authorized its merge on 2026-09-12.
[PR #6](https://github.com/danielbardsley/gptclaw/pull/6) merged as
`e6aa908ef51b2dd0daa2f241418d2bedfb411c73`, containing reviewed policy source
`a287d7c9712817fd9f318a11f28041cfc6b5ad06`. The PR CI run #49 passed.
Daniel subsequently requested Terraform bootstrap integration; that follow-up
is prepared separately on `codex/agt-001-bootstrap-policy`.

## Non-secret host preflight

- User: `forge` (UID 1002).
- Installed CLI: `codex-cli 0.153.4`.
- Both inspected running app-server processes explicitly selected
  `/home/forge/.codex` through `CODEX_HOME`.
- No explicit `project_doc_max_bytes` or `project_doc_fallback_filenames` setting
  was found in the user configuration. Actual combined instruction loading
  remains a fresh-task check.
- Original Codex home mode was `0775`; after rechecking ownership and absence
  of policy/overrides, only that directory was changed to `0700` on 2026-09-12.
- Global `AGENTS.md`, global `AGENTS.override.md`, and managed provenance were
  absent. Authentication contents were not read or changed.
- Installed and verified on 2026-09-12 at 22:33:04 UTC as `forge`.
- Active source revision: `a287d7c9712817fd9f318a11f28041cfc6b5ad06`.
- Active SHA-256: `0f6ae760595870c82d387d68a904730c31652f88e11bf4766748eacdce580fad`.
- Installer verification reports `current`, validating exact source bytes,
  provenance, ownership and modes. Fresh-task loading is not yet demonstrated.

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
  `scripts/check-repository.sh`; PR #6 CI run #49 passed; follow-up CI status is recorded separately.
- The follow-up changes Terraform bootstrap code; no live Terraform apply or
  AWS mutation was performed. Local Terraform tests mock AWS.

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
| AC-001 | Pass | Content mapping and validation pass; Daniel reviewed PR #6 and authorized merge. |
| AC-002 | Local pass | Offline tests and repository checks pass; record PR CI separately. |
| AC-003 | Pass | Approved source installed as `forge`; exact bytes, provenance, paths and modes verified. |
| AC-004 | Pending | Fresh tasks through real SSH connection in GptClaw and independent scratch project. |
| AC-005 | Pending | Safe remote scenarios for inherited repository rules, prior authorization, and scope boundaries. |
| AC-006 | Partial | Offline drift/override/rollback tests pass; controlled live rehearsal and fresh-task verification pending. |
| AC-007 | Partial | Runbooks and active revision recorded; fresh remote behavior evidence remains pending. |
| AC-008 | Pass locally | Five offline bootstrap tests plus three focused Terraform tests pass; follow-up PR CI recorded separately. |
| AC-009 | Pending | No new EC2 instance provisioned with bootstrap version 4; review replacement plan and verify first boot during a future approved creation/replacement. |

Daniel owns ongoing review, installation, recovery, and exception cleanup as
specified. AGT-001 remains Planned until all acceptance gates pass. There is no
claim that filesystem verification guarantees model compliance or that a CLI
session proves the actual remote app's instruction inheritance.

Provisioning follow-up validation: all 18 mocked Terraform tests pass, including
the three first-boot tests using real local cloud-init rendering. Terraform
formatting and validation, 22 offline installer/bootstrap tests, repository
checks, and documentation link checks pass. No infrastructure apply was run.
