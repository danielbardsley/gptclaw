# SPEC-016 acceptance evidence

- **Status:** Locally verified implementation; CI and external setup pending
- **Owner:** Daniel
- **Date:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-016](spec.md)
- **Design:** [TDD-016](technical-design.md)
- **Tasks:** [Tasks](tasks.md)
- **Branch:** `codex/tailscale-workload-identity`

## Criteria

| Criterion | State | Evidence / remaining work |
|---|---|---|
| AC-001 | passed locally | 11 offline enrollment tests cover success, retry, version/config/state/tag failures, timeout, credential isolation and migration; rendered helper/no-key/payload assertions pass. |
| AC-002 | pending remote | Local IAM bounds, exact subject and account-stack tests pass. Both protected remote plans and account trust ownership still need inspection. |
| AC-003 | pending | Issuer setup, exact-role tailnet trust and fresh-host enrollment have not run. |
| AC-004 | pending | Existing Podman/profile tests pass; actual package receipts, private access and preserved storage must be checked after replacement. |

## Executed verification

- `./scripts/check-repository.sh` with the existing isolated manifest environment:
  passed, including all existing suites and 11 federation tests.
- Terraform 1.16.1 `fmt`, `validate`, `test` in `infra/dev-host`: passed,
  24 tests, mocked AWS and real local cloud-init rendering; user-data size passes.
- Terraform 1.16.1 backend-free, read-only-lock initialization, validation and
  tests in `infra/tailscale-federation`: passed, 2 mocked AWS tests.
- The first account-root initialization rejected an unrelated copied cloud-init
  lock entry; removed that unused entry while retaining the existing signed AWS
  provider selection/checksums, then read-only initialization passed.
- `bash -n` for the repository checker and bootstrap template: passed.
- Git whitespace checks: passed.
- Source inspection confirmed Tailscale's JSON status mode returns successfully
  for a not-yet-enrolled node. Documentation establishes >=1.94 audience discovery
  and persistent/preauthorized client-ID parameters; no client enrollment was run.

No local package install, token request, AWS mutation or external trust write was
performed. Mock test blocks named `apply` do not provision AWS resources. No
credentials, live tokens, state or plans are included in this evidence.

## Remaining setup

Follow [the runbook](../../runbooks/manage-tailscale-federation.md): isolated HCP
workspace/environment and scoped operator session, account issuer plan/apply (or
reuse an already-owned issuer), one-time Tailscale exact-role trust and non-secret
client ID, then development plan/apply with recovery readiness. Existing GitHub
connector tools cannot dispatch workflows and no Tailscale connector is available;
operator actions remain necessary. This replaces the earlier fresh-key reminder.
Rollback is documented, not executed; never disable the account issuer as part
of routine host rollback. Delivered status is not claimed.
