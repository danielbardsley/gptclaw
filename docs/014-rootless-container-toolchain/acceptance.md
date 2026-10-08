# SPEC-014 acceptance evidence

- **Status:** Implementation merged; replacement bootstrap blocked; host acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-10-08 (America/New_York)
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

## Authorized deployment preparation (October 1, 2026)

Daniel requested review, necessary fixes, and the protected plan/apply deployment
of SYS-001 and SYS-004. PR #26 merged as
`e59d14bec30cfed287dc0a6f54aa9362acfc5976`; its final CI run 82 passed.
The [first protected plan](https://github.com/danielbardsley/gptclaw/actions/runs/36818874361)
reported 2 additions, 15 updates and 2 destroys: compute and its volume attachment
replace, while the project volume is retained with a revision-tag update.
Thirteen updates were tags; two were deferred HCP identity policy renderings.
Do not apply that superseded plan.

The repair renders the same IAM statements with local JSON expressions instead
of deferred provider data sources. It preserves exact resource scopes and the
apply role's prohibition on modifying deployment identities. A mocked initial
apply followed by a revision-only plan verifies the policies remain known.
The code-managed enrollment counter advances from 4 to 5, and compute waits for
the secret version before boot. Daniel must set a fresh tagged one-use key in
HCP's sensitive `tailscale_auth_key` variable before apply; he asked to be reminded
later. Do not paste keys into chat or create an HCP override for the code counter.

Review confirms all 26 profile components flow through install and version checks,
including Podman and eight rootless prerequisites; rootless capability and final
profile verification gate the completion receipt. This is source/test evidence,
not evidence of installed packages. The revised protected plan, completed backup
metadata, fresh enrollment key, apply and post-bootstrap verification remain
pending. The current connector exposes workflow reads and reruns but no dispatch;
no local AWS CLI or operator identity was available for backup inspection.

Repair validation: Terraform 1.16.1 formatting and validation passed; all 22
Terraform tests passed (mock AWS only), including revision-only policy planning
and rendered IAM mutation boundaries. The full offline repository checker passed.
Shell syntax and Git whitespace checks passed. No infrastructure apply or
package installation was performed by these checks.

## Enrollment approach superseded

Daniel subsequently authorized [SPEC-016](../016-tailscale-workload-identity/spec.md).
Its federation implementation supersedes the fresh-key/counter instructions in
the earlier deployment-preparation record. Actual deployment remains pending
one-time issuer/trust setup and the reviewed protected plan/apply.

## Rootless storage parent ownership repair - October 8, 2026

[Protected apply](https://github.com/danielbardsley/gptclaw/actions/runs/37841684250)
and [HCP run](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-W6sxoPo2JcG2xH2G)
succeeded at `c94ac9f02d563e063524015e8515fe9eea0c271d`, creating replacement
`i-05db973e028285c47`. This proved infrastructure replacement, not bootstrap or
Tailscale acceptance. Daniel subsequently authorized host commands for debugging;
Terraform plans and applies must remain in CI/CD.

SSM diagnostics verified the earlier absent-package repair: base packages, SSM,
AWS CLI, forge identity and project-volume phases passed. The protected volume
mounted as ext4 at `/srv/forge` with original UUID
`680fdc21-378e-466b-8b3f-8fa947eabc8d`. Bootstrap failed in `rootless-toolchain`
at 16:49:17 EDT; no completion or rootless capability receipt existed. The
Tailscale service was absent and enrollment had not been attempted.

The bounded Podman probe reported permission denied creating
`/home/forge/.local/share`. `namei` and `stat` verified `.local` was `root:root`
mode 755 while `.local/bin` was `forge:forge` mode 755. GNU install's directory
ownership flags applied only to the explicit leaf operand; its implicit parent
remained owned by the root bootstrap caller. The bootstrap now explicitly creates
both `.local` and `.local/bin` with forge ownership, without recursive ownership
changes, extra packages, or privilege changes.

A disposable diagnostic storage directory allowed the installed Podman 4.9.3 to
prove rootless operation, v2/systemd cgroups, netavark, slirp4netns, crun and overlay.
Observed UID and GID maps both matched `(0, 1002, 1), (1, 231072, 65536)`.
The task-owned temporary storage was removed. This did not change the deployed
configuration, initialize the intended engine graph, pull an image or produce an
acceptance receipt. User manager/linger were active and rootful units remained
masked/inactive.

The bootstrap ownership regression failed against the old template and passed
after the fix. Four focused host-tool tests passed with Python 3.12 on Windows;
bootstrap shell syntax and Git whitespace checks passed. The full Linux repository
and pinned Terraform checks are delegated to PR CI because this desktop's WSL
runtime is unavailable and its default Terraform version differs from the pin.
Deployment and actual bootstrap/enrollment acceptance of this repair remain pending.

## Successful repaired bootstrap - October 8, 2026

The protected replacement at `6d90105136de55f7932c7e6857ba0bf6415db249`
completed bootstrap successfully. Rootless and host-tool receipts passed,
Tailscale enrolled automatically, and authenticated private SSH plus original
project filesystem/ownership were verified. See [SPEC-016 live evidence](../016-tailscale-workload-identity/acceptance.md#fresh-host-enrollment-verified---october-8-2026)
for public workflow references and remaining acceptance limits. This supersedes
the earlier pending bootstrap outcome; full fixture/reboot and final owner
acceptance remain separate.
