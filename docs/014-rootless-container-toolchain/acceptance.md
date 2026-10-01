# SPEC-014 acceptance evidence

- **Status:** Local implementation and CI verified; merge, deployment and host acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-10-01 (America/New_York)
- **Implementation revision:** `c5f6cb27737cff345fbf09e3b6cdebb942763765`
- **Review branch:** `codex/sys-001-rootless-toolchain`
- **Review:** [PR #26](https://github.com/danielbardsley/gptclaw/pull/26)
- **CI:** [Run 81](https://github.com/danielbardsley/gptclaw/actions/runs/36818384744) passed quality checks for `2cf828d34bba07c9959ee52cdbef35bfef3ac2d7`; protected plan/apply jobs were skipped as expected for a PR.
- **Plans:** [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **Operation:** [Rootless toolchain runbook](../../runbooks/manage-rootless-toolchain.md)

## Authorization and observed baseline

Daniel authorized SYS-001 implementation on October 1, 2026. He reiterated that
host changes must be applied through IaC only. No merge, workflow dispatch,
Terraform infrastructure plan/apply, package installation or host reconfiguration
was performed during implementation.

Read-only discovery found `forge` UID/GID 1002, both subordinate mappings
`forge:231072:65536`, cgroup v2, root ext4 storage for `/home/forge`, and separately
mounted ext4 project storage. Podman and its user configuration/storage were absent;
`Linger=no`. These observations justify fixed identity and a clean first-install
path. Subsequent checks confirmed those live settings remained unchanged and the
bootstrap helper was not installed. No authentication files or environment dumps
were inspected.

## Criterion mapping

| Criterion | State | Local evidence | Required remaining evidence/owner |
|---|---|---|---|
| AC-001 | pending | Profile/ordering, prerequisite failure, exact YAML embedding and completion-gate tests pass. Actual distro generator parses the fixture. | Deployed versions, kernel/storage/network capabilities and rootless receipt, operator. |
| AC-002 | pending | Synthetic identity/mapping collision and repeat tests pass; probes explicitly drop to forge; rootful system units are masked before package installation in code. | Real unprivileged build/run and namespace map checks after deployment, operator. |
| AC-003 | pending | Unknown configuration/storage and symlink fixtures are preserved; paths and keep-id write checks are implemented. | Real bind ownership and replacement preservation/rebuild checks, operator. |
| AC-004 | pending | Fixture has a pinned public base, explicit loopback publication and independent DNS/outbound/non-loopback checks; no private route or ingress change. | Run image/DNS/HTTPS/HTTP and non-loopback tests on deployed host, operator. |
| AC-005 | pending | Quadlet generation succeeds; bounded restart/boot activation and mount waiting are declared; no fixture is started by bootstrap. | Actual crash restart, last-session logout and reboot-before-login observations, independent operator. |
| AC-006 | pending | Conflict-safe preflight, system unit masks, repeat and failure tests pass. Recovery/identity rollback constraints documented. | Protected plan, recovery point/window, authorized replacement and post-replacement checks, Daniel/operator. |
| AC-007 | pending | Scoped fixture ownership/cleanup refusal tests and runbook complete; no broad prune/reset. | Actual fixture cleanup, CI/deployment references and Daniel's acceptance. |

All acceptance criteria contain deployed or operator outcomes. Passing local tests
does not pass those unobserved portions or establish that SYS-001 is Delivered.

## Executed checks

Environment: unprivileged `forge`, Python 3.12.3; reused isolated dependencies at
`/tmp/gptclaw-prj001-venv` and Terraform 1.16.1 at
`/tmp/gptclaw-res001-tools/terraform`, with previously initialized locked providers.
No host package setup was needed to run repository or infrastructure tests.

| Command/check | Observed result |
|---|---|
| `source /tmp/gptclaw-prj001-venv/bin/activate && ./scripts/check-repository.sh` | Passed all offline repository checks, including 22 SYS-001 and 19 SYS-004 tests. All provisioning/network/systemd calls in these suites are mocked. |
| `python3 -B scripts/tests/test_rootless_toolchain.py` | 22 passed. |
| `bash -n scripts/check-repository.sh` | Passed. |
| `bash -n infra/dev-host/templates/bootstrap-forge.sh.tftpl` | Passed. |
| Terraform 1.16.1 `fmt -check -recursive` and `validate -no-color`, from `infra/dev-host` | Passed. |
| Terraform 1.16.1 `test -no-color`, from `infra/dev-host` | Final run: 20 passed, zero failed. AWS mocked; real local cloud-init rendering only. Test blocks named `apply` do not apply AWS infrastructure. |
| `git diff --check` and `git diff --cached --check` | Passed. |

An intermediate Terraform run failed three user-data size checks at base64 lengths
23284–23288, above 21844. The fix embeds the remaining bootstrap/policy scripts as
literal YAML inside the existing compressed envelope. Tests assert their exact
decoded contents; the unchanged payload gate and all 20 tests subsequently passed.
No payload was submitted to AWS.

## Package and fixture inspection

Ubuntu package `podman=4.9.3+ds1-1ubuntu0.2` was downloaded into task-owned
`/tmp/sys001-package-inspection` with `apt-get download`, verified against apt
metadata SHA-256
`e5c1c37e387ed14c352a744a75fbb79fb2f82573ca7bf36886e3b7333fc9ef1a`, and extracted
using `dpkg-deb -x`. This does not install a package. Its binary
`extracted/usr/libexec/podman/quadlet --user --dryrun`, with `QUADLET_UNIT_DIRS`
pointing to a temporary rendered fixture, generated the expected service. Checks
confirmed keep-id, loopback publication, memory bounds, mount waiting and restart
configuration. No systemd unit or container was started.

The extracted maintainer script enables rootful Podman system units by default.
Implementation now prepares administrator-owned masks before apt installation and
verifies masked/inactive state afterward. Source inspection of
`deb-systemd-helper` confirmed its unmask operation preserves administrator masks
without its own mask-state file. These scripts were inspected, not executed on
the host. Tests exercise mask creation/conflicts solely under temporary roots.

The Alpine 3.22.2 Linux/amd64 manifest was resolved via public registry metadata:
`sha256:85f2b723e106c34644cd5851d7e81ee87da98ac54672b29947c052a45d31dc2f`.
No image was pulled, built or run; the transient public registry token was not
printed or retained in evidence. The acceptance fixture contains only synthetic
data and copies only its Containerfile into its future build context.

## Remaining work

Review CI and the implementation PR, then obtain a separate authorized pipeline
plan/apply and replacement window. Merges run quality checks only; deployment is
manual `workflow_dispatch` on `main`, through GitHub Actions/HCP Terraform/AWS.
Verify a suitable recovery point, quiesce writes and preserve the protected volume
and fixed identity before replacement. SYS-004's approved upstream exceptions
remain independently bounded through November 1, 2026 (America/New_York).

Perform the runbook's real fixture, logout, reboot, replacement and cleanup checks.
Record exact deployment revision/run links, receipts, sanitized observations and
Daniel's acceptance. Rollback instructions are reviewed but unexecuted; they must
retain compatible UID/GID ownership even when reverting other rootless changes.
No live configuration, deployment, restart/reboot test, replacement or final
acceptance is claimed by this record.
