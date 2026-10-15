# SPEC-035 acceptance evidence

Status: Implemented in review; managed/private acceptance pending.
Owner: Project owner. Evidence date: 2026-10-15 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)

Tested implementation: `202b7e8778505a6759bba75bc3794ac12928591a` on
`codex/tpl-002-fastify-api`; later status/evidence changes are documentation only.
Review: [PR #82](https://github.com/danielbardsley/gptclaw/pull/82). Initial stateless scope
was explicitly selected by the project owner. PostgreSQL/migrations remain deferred.

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Passed locally and in CI | Five focused platform cases, 28 manifest cases, 27 dependency cases, 31 toolchain cases, 22 mobile cases and three focused Metro reruns passed. Release immutability and the six-job private application CI workflow passed. The complete repository gate passed in development-host CI; local full reruns were stopped after equivalent CI succeeded. |
| AC-002 | Passed locally | Generated starter verify passed in pinned Node 24.21.0 / pnpm 12.10.1 container. Three API/domain/settings tests: 100% lines, 87.10% branches across factory/service/settings; enforced minima 80%. Frozen restore and verify/audit passed for two independent generated projects. Injected lint, type, behavior and construction defects were rejected. |
| AC-003 | Pending managed/private acceptance | Real loopback container checks passed for readiness, prefixed docs/assets/OpenAPI, automatic source updates, syntax-error unavailability/recovery, independent second service and stop/source retention. These do not establish installed Quadlet or private HTTPS acceptance. No infrastructure, Serve configuration or production change was performed. |
| AC-004 | Pending review/merge and owner acceptance | Specification, design, tasks, runbook and CI are present in PR #82. All six private application CI jobs passed on the implementation commit; merge and project-owner acceptance remain outstanding. |

## Executed local verification

- Authoring container command `pnpm format && pnpm verify`, inside
  `localhost/gptclaw-node:24.21.0-pnpm12.10.1` against the new release: final run passed lint, strict typing,
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
- `.venv-manifest/bin/python scripts/tests/test_project_dependencies.py`: 27 cases passed.
- `.venv-manifest/bin/python scripts/tests/test_project_toolchains.py`: 31 cases passed.
- `.venv-manifest/bin/python scripts/tests/test_project_mobile.py`: 22 cases passed.
- Three selected cases in `scripts/tests/test_metro_contract.py` passed: dirty or
  untracked metadata refusal, editor racing atomic publication, historical schema
  opt-in refusal.
- `bash -n scripts/check-repository.sh`, `git diff --check`,
  `git diff --cached --check` and changed-document relative links passed.
- `PATH="/srv/forge/projects/gptclaw/.venv-manifest/bin:$PATH" ./scripts/check-repository.sh`:
  initial full repository run encountered that version assertion and asset hash
  failures while authoring changes were still being sealed. A stable-source rerun
  was started; neither the earlier failed run nor the interrupted rerun is reported
  as a local full-suite pass.

Standalone compiled image build passed, followed by `pnpm verify` as the image
unprivileged user and a loopback smoke test of the default `node dist/server.js`
command (readiness, docs, docs assets and OpenAPI); its container was stopped.

[Private application CI run](https://github.com/danielbardsley/gptclaw/actions/runs/38681962950)
passed all six jobs: TypeScript API, Python API, mobile source, multi-service,
development database and existing template/dependency/toolchain checks. Dashboard
and Tailscale-federation CI also passed.
[Development-host CI](https://github.com/danielbardsley/gptclaw/actions/runs/38681963037)
passed its complete repository security/invariant gate plus Terraform format,
validation, mocked tests and scans. All four workflows passed at `202b7e8`.
The two duplicate local full-suite process groups were interrupted with SIGINT
after this equivalent committed-source CI succeeded; focused local runs and real
container checks completed independently. No local full-suite success is claimed.
Final PR status/evidence commits change documentation only; their fresh CI runs
are separate from this verified implementation commit.

Managed runtime/private HTTPS and project-owner acceptance are unobserved. Local
Terraform checks were skipped because no infrastructure files changed; CI ran its
existing Terraform gates, and protected infrastructure mutations were skipped. No live application
repository or external persistent dataset was created.

## Remaining work and rollback

PR #82 is ready for review. Review/merge and managed/private initial-slice
acceptance remain with the project owner. Unrelated concurrent SPEC-036/index/
catalogue/mobile-sequence edits remain in the workspace and were excluded from
these commits. Rollback uses a reviewed revert/previous provider snapshot while
preserving generated source and published release identities. The template retains
intentional synthetic examples because it is an application starter; generated
products must replace them under their own approved specifications.
