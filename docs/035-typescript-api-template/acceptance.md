# SPEC-035 acceptance evidence

Status: Delivered — initial stateless slice merged and accepted.
Owner: Project owner. Evidence date: 2026-10-15 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)

Tested implementation: `202b7e8778505a6759bba75bc3794ac12928591a` on
`codex/tpl-002-fastify-api`; later status/evidence changes are documentation only.
Implementation merged in [PR #82](https://github.com/danielbardsley/gptclaw/pull/82)
as `e8e02a60e748ee091d606226ed2fad9ebd4ea8dd`. Final PR revision
`f6ea60a07fd5e465766fca457952ec5e470c3895` passed all four workflows before merge.
Initial stateless scope
was explicitly selected by the project owner. PostgreSQL/migrations remain deferred.

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Passed locally and in CI | Five focused platform cases, 28 manifest cases, 27 dependency cases, 31 toolchain cases, 22 mobile cases and three focused Metro reruns passed. Release immutability and the six-job private application CI workflow passed. The complete repository gate passed in development-host CI; local full reruns were stopped after equivalent CI succeeded. |
| AC-002 | Passed locally | Generated starter verify passed in pinned Node 24.21.0 / pnpm 12.10.1 container. Three API/domain/settings tests: 100% lines, 87.10% branches across factory/service/settings; enforced minima 80%. Frozen restore and verify/audit passed for two independent generated projects. Injected lint, type, behavior and construction defects were rejected. |
| AC-003 | Passed on managed host | Two API instances passed real managed start/status/test/bounded logs/restart/stop/start; private HTTPS docs/assets/OpenAPI/echo/pagination passed. Source reload and syntax-error recovery passed, stop returned 404 while preserving exact source, and B remained ready throughout A operations. Both final instances are ready. Evidence below. |
| AC-004 | Passed | PR #82 merged after final-head CI passed. The project owner accepted the presented private API checks with “Everything looks good” on October 15, 2026. This is owner-reported manual acceptance; automated evidence is recorded separately. |

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

Local Terraform checks were skipped because no infrastructure files changed;
CI ran its existing Terraform gates, and protected infrastructure mutations were
skipped. No live application GitHub repository or external persistent dataset was
created.

## Final-head CI and managed acceptance — October 15, 2026

All four workflows passed on final PR revision `f6ea60a` before merge:

- [Private application workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38682919061).
- [Development-host workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38682919086).
- [Dashboard workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38682919088).
- [Tailscale-federation workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38682919126).

The reviewed repository provider 1.13.0 generated exact `fastify@1.0.0` projects
`/srv/forge/projects/tpl002-acceptance-a` and
`/srv/forge/projects/tpl002-acceptance-b` using `new --template fastify
--template-version 1.0.0 --local-only`. Both validated and initially observed
stopped. Each was started once through `scripts/gptclawctl start --project-root
<root>`, returning ready with configured existing private routes. The installed
stable launcher's actual `--version` interface now reports 1.13.0, manifest 7 and
catalogue 6. The runbook's incorrect `capabilities` command was corrected to
`--version`; no provider behavior was changed in this documentation follow-up.

Both private bases are beneath:
`https://forge-dev-01-4.tail8c3304.ts.net/projects/`.
Use `tpl002-acceptance-a/docs/` and `tpl002-acceptance-b/docs/` for retained
interactive docs. Automated requests verified HTTPS readiness/liveness, docs,
bundled JS, OpenAPI, paginated examples and echo normalization. The project owner
was given the two private docs/health/schema links and echo/invalid-input/list
checks, then reported “Everything looks good.” No unobserved individual browser
interaction is represented as an automated test.

Additional managed checks used only synthetic instance A while B stayed available:

- Edit `src/service.ts` to return a synthetic updated first example; observe the
  update through private HTTPS without a lifecycle restart.
- Introduce a synthetic syntax error; observe non-200 private readiness and managed
  `status` reporting unhealthy. Fetch only bounded `logs --lines 40`.
- Restore the exact original source bytes; observe recovery and the original
  example. Managed `test` returned `tests-passed`.
- Managed `restart` returned ready with distinct recorded stop/start transitions.
- Managed `stop` returned stopped and `source_retained: true`; observe status
  stopped, private route 404, exact source retained and B still ready.
- Managed `start` returned ready again. Both final `status` calls reported ready,
  healthy and no busy operation; private docs/schema/readiness returned 200.

The commands were executed by task-owned helpers
`python3 /tmp/gptclaw-tpl002-managed-acceptance.py` and
`python3 /tmp/gptclaw-tpl002-managed-acceptance-resume.py`, calling the reviewed
CLI with explicit project roots. The first helper incorrectly expected the
managed test success label `passed`; the actual command succeeded with
`tests-passed`. Its receipt was inspected and the helper resumed without repeating
that command. This helper assertion was not a product-test failure.
Sanitized detailed checks and receipts remain in
`/tmp/gptclaw-tpl002-managed-acceptance.json`.

| Managed A action | Operation ID | Result |
|---|---|---|
| test | `45d5fcc8eaa04be2a4c4c37ad52b398b` | tests-passed |
| restart | `2b8c37a7a0364bfcaccd9529da2ed857` | ready |
| stop | `60b6da16725746039da6e37340840376` | stopped |
| start | `159d91d3339247cebce294622784a65c` | ready |

Restored source SHA-256: `4ed1799018f1974ad2d71be2c69e72d84bf4a1095e4fe12f1dff28710e8c8c12`.
A retains loopback port 18100; B retains loopback port 18101. Both managed private
instances remain running for inspection. Their source is retained; no database,
public exposure, production or infrastructure change was introduced.

## Remaining scope and rollback

The approved initial stateless slice has no outstanding acceptance criterion.
PostgreSQL/migrations and service-group integration remain explicitly deferred;
this acceptance does not claim them. The acceptance/status follow-up is
documentation only and does not alter published release assets.

The main workspace's concurrent SPEC-036/index/catalogue/mobile-sequence edits
were preserved; this follow-up uses an isolated worktree. Rollback uses a reviewed
revert/previous provider snapshot while preserving generated source and published
release identities. Intentional synthetic examples remain because this is an
application starter; generated products must adapt them to their own approved
specifications. Retained acceptance instances can be stopped later through the
managed lifecycle without deleting source.
