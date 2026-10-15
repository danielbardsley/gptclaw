# SPEC-035 acceptance evidence

Status: Local implementation verification in progress; no delivery claim.
Owner: Project owner. Evidence date: 2026-10-15 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)

Tested source: feature branch `codex/tpl-002-fastify-api`, based on the repository
main checkout; exact review revision will be the PR commit. Initial stateless scope
was explicitly selected by the project owner. PostgreSQL/migrations remain deferred.

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Pending final regressions | Five focused platform tests passed: exact generation/dependency policy, unknown-version/provider refusal, manifest safety, loopback unit guard and provider snapshot contents/parity. Existing release immutability passed. Broader final-source suite still required. |
| AC-002 | Passed locally | Generated starter verify passed in pinned Node 24.21.0 / pnpm 12.10.1 container. Three API/domain/settings tests: 100% lines, 87.10% branches across factory/service/settings; enforced minima 80%. Frozen restore and verify/audit passed for two independent generated projects. Injected lint, type, behavior and construction defects were rejected. |
| AC-003 | Pending managed/private acceptance | Real loopback container checks passed for readiness, prefixed docs/assets/OpenAPI, automatic source updates, syntax-error unavailability/recovery, independent second service and stop/source retention. These do not establish installed Quadlet or private HTTPS acceptance. No infrastructure, Serve configuration or production change was performed. |
| AC-004 | Pending | Specification, design, tasks, runbook, generated CI and source integration are present. PR, remote CI, merge and project-owner acceptance remain separate. |

## Executed local verification

- `podman run ... localhost/gptclaw-node:24.21.0-pnpm12.10.1 sh -c 'pnpm format && pnpm verify'`
  against the new release during authoring: final run passed lint, strict typing,
  API tests/coverage, compile/construction preflight and npm audit (no known
  vulnerabilities). An initial formatting pass needed a second normalization;
  strict Fastify error typing was corrected before the passing run.
- `.venv-manifest/bin/python scripts/tests/check_fastify_template.py /tmp/gptclaw-tpl002-generated --engine podman --image localhost/gptclaw-node:24.21.0-pnpm12.10.1`
  passed two-project frozen restore, verify, injected-defect rejection and real
  private loopback container behavior. Test containers were stopped. Synthetic
  source remains in the task-owned temporary directory.
- `.venv-manifest/bin/python scripts/tests/test_project_fastify.py`: five tests passed.
- `.venv-manifest/bin/python scripts/check-template-releases.py`: baseline release
  integrity and immutability passed after sealing the new release. Authoring
  caches were removed from the new release source and excluded from its inventory.
- `.venv-manifest/bin/python scripts/tests/test_project_manifest.py`: 28 tests passed
  after updating the unknown-version assertion from 7 to 8.
- Initial full repository pass encountered that version assertion and asset hash
  failures while authoring changes were still being sealed. A stable-source rerun
  is required; this record does not treat the earlier pass as successful.

Standalone compiled container build is being checked separately. Remote CI,
managed runtime/private HTTPS and project-owner acceptance are unobserved. Terraform
checks are not applicable: no infrastructure files changed. No live application
repository or external persistent dataset was created.

## Remaining work and rollback

Finish final local regressions and standalone image verification, create the
review PR and record actual CI. Merge and initial-slice acceptance belong to the
project owner. Rollback uses a reviewed revert/previous provider snapshot while
preserving generated source and published release identities. The template retains
intentional synthetic examples because it is an application starter; generated
products must replace them under their own approved specifications.
