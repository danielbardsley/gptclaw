# SPEC-024 implementation acceptance

- **Status:** In progress — local implementation evidence; CI/live/client/merge pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-024](spec.md) · **Design:** [TDD-024](technical-design.md) · **Tasks:** [TASKS-024](tasks.md)
- **Implementation review:** [PR #56](https://github.com/danielbardsley/gptclaw/pull/56)
- **Revision:** Working implementation after `e85105d`; final committed revision to be recorded

The project owner approved the scope and authorized implementation on October 11
with “ok, go ahead and implement the spec.” This includes scoped synthetic checks;
no public exposure, AWS/host package installation or application GitHub repository
creation was performed. This record does not establish merged delivery or client
acceptance.

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | pending | Exact generation and offline observation/path/provenance tests pass; final release/CI checks pending. |
| AC-002 | pending | Actual Python 3.13.16/uv 0.13.0 cold acquisition and warm reuse passed in the real generated Podman workflow; final CI/live record pending. |
| AC-003 | pending | Offline locked preparation, denied inputs, conflict/abort and same-operation interrupted-publication recovery pass. Real uv source-preserving add/update/remove workflow is being completed. |
| AC-004 | pending | Starter API tests pass for typed versioned sample/pagination, safe input failures, health/readiness, OpenAPI/settings. Final generated CI record pending. |
| AC-005 | pending | Shared lifecycle integration and bounded unit/job tests pass; actual managed EC2 service/reload/restart/stop evidence remains. |
| AC-006 | pending | In-process mounted docs/assets/schema and relative/query-preserving hostile-header redirect tests pass. Actual private HTTPS and independent client observation remain. |
| AC-007 | pending | Real starter Black/isort/Ruff/mypy/pytest/coverage/Bandit/audit/build passed. Generated seeded defects, final CI and explicit hook behavior are being verified. |
| AC-008 | pending | Existing offline Next.js/provider/dependency/toolchain/repository/credential regression suites passed. Final combined gate and independent running Next.js check remain. |
| AC-009 | pending | Sanitized recording underway. Review/merge, client/owner acceptance and fixture/rollback disposition remain. |
| AC-010 | pending | Owner-derived guide/config and typed service design are present; standards checks and narrow factory-boy typing adaptation tested. Final gates/review remain. |

## Local verification

The rootless authoring image was built from official pinned Python/uv OCI digests;
actual Python 3.13.16 and uv 0.13.0 were observed. Package candidates came from the
public PyPI registry and Swagger assets from a verified exact npm tarball. Exact
pins are committed in the profile and release metadata; no source hooks were run.

Executed local checks so far:

- `.venv-manifest/bin/python scripts/tests/test_project_python.py`: 21 tests pass,
  including acquisition/reuse, policy, stopped/busy operations, source conflict,
  same-operation publication recovery, read-only guards, hooks and snapshot ownership.
- Pinned-container `scripts/quality.py verify`: Black/isort/Ruff, strict mypy,
  API/quality tests, independent critical statement/branch coverage, Bandit,
  locked-graph pip-audit and build passed in the authoring environment.
- Prepared repository checker: existing suites passed after updating v2 contract
  expectations; the first full attempt also exposed a mistaken mock in the new
  Python runner test, corrected and passing in the focused suite. Final combined
  execution remains pending.
- Bash syntax and Python compilation checks passed for changed controller code.

Real generated-project verification exposed uv's default index-writing behavior;
the policy refused it before publication. Pinned CLI `--raw` was proven to avoid
that behavior in a task-owned fixture. The corrected full workflow is rerunning.
Earlier admission preflight ordering and test-boundary typing failures were
corrected, with passing reruns. These failures are not reported as acceptance.

## Outstanding verification and disposition

Record final command/revision/CI results, cold/warm timings and coverage values;
prove the managed API privately alongside a synthetic Next.js project, source edit
and syntax-error recovery, lifecycle/logs, route refusal and source retention.
Observe the actual HTTPS API/docs from an authorized independent client and trial
older-provider refusal on a stopped owned API. Preserve running fixtures/source
until that observation; remove only identified disposable task verification data.
No Terraform checks are needed because this initiative changes no Terraform or
host bootstrap. Existing backup/reboot/replacement acceptance remains separate.
