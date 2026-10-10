# SPEC-014 acceptance evidence

- **Status:** Deployed; container smoke checks passed, remaining host acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-10-09 (America/New_York)
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
| AC-001 | passed | Rendered/ordering tests and current CI passed; installed versions/rootless capability receipts were inspected and live Quadlet/container smoke execution succeeded. | Final feature acceptance remains separate; deployment/recovery provenance is tracked in AC-006. |
| AC-002 | pending | October 9 unprivileged image build/run and keep-id bind writes passed; isolated mapping/conflict tests pass. | Reconcile current namespace/non-overlap and repeat-identity evidence before final acceptance. |
| AC-003 | pending | Original filesystem UUID/project ownership match; live synthetic bind-write ownership passed. | Synthetic-source preservation and cache rebuild across replacement remain unproven; do not trigger replacement from this status review. |
| AC-004 | passed | October 9 pinned-base retrieval, container DNS/HTTPS, loopback HTTP and non-loopback refusal passed after the HTTP fixture repair. The fixture/diff changes no ingress policy. | Final feature acceptance remains separate; no managed app routing is inferred. |
| AC-005 | pending | Live Quadlet service and bounded crash restart/HTTP recovery passed October 9. | Independent last-session logout and reboot-before-forge-login observations remain pending. |
| AC-006 | pending | Merged repairs and replacement are recorded; successful receipts, retained UUID/ownership and owner-confirmed SSM access are observed. | Complete protected-run/recovery-point/window evidence and rollback review; no executed rollback is claimed. |
| AC-007 | pending | Live owned-fixture cleanup removed listener and activation; shared cache was retained. Current repository checks and PR #38 CI passed. | Final criterion reconciliation and Daniel's acceptance remain pending. |

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

## Small container smoke test — October 9, 2026 (America/New_York)

Daniel authorized returning to the first-private-app milestone and running a
small container smoke test. Starting `scripts/rootless-fixture.py` at port 18081
on reviewed host revision `6d90105136de55f7932c7e6857ba0bf6415db249` built the image
and passed forge bind-write ownership plus DNS/outbound HTTPS, but user service
startup failed with exit 127: `httpd` was missing. A scoped probe confirmed that
the pinned Alpine base's BusyBox had no HTTP applet. The failed owned fixture
`gptclaw-sys001-62995f275109` was cleaned up using the fixture helper.

The test image now installs exact `busybox-extras=1.37.0-r20` from Alpine v3.22
and checks its HTTP applet during build; both image CMD and Quadlet explicitly
invoke `/bin/busybox-extras httpd`. No host package or configuration change was
made. [Package source](https://pkgs.alpinelinux.org/package/v3.22/main/x86_64/busybox-extras).
The base image remains digest-pinned; package retrieval uses the signed Alpine
repository and is not a claim of a fully immutable dependency closure.

Executed after repair:

- `python3 scripts/tests/test_rootless_toolchain.py`: 22 offline tests passed.
- `python3 scripts/rootless-fixture.py start --port 18081`: passed; fixture
  `gptclaw-sys001-7ce690804176` built/ran rootlessly with DNS/HTTPS, bind ownership
  and loopback HTTP checks.
- `check --directory /srv/forge/projects/gptclaw-sys001-7ce690804176 --non-loopback`
  with an actual assigned host IPv4: passed; listener exclusively loopback and
  connection via the non-loopback address refused.
- `crash --directory /srv/forge/projects/gptclaw-sys001-7ce690804176`: passed;
  bounded systemd restart and HTTP recovery verified.
- `cleanup --directory /srv/forge/projects/gptclaw-sys001-7ce690804176`: passed;
  owned resources/listener/activation removed; shared base/cache retained.

These results supplement AC-002/003/004/005/007; their other obligations remain
pending. No logout, reboot, synthetic-source replacement/rebuild test or full
owner acceptance occurred. At the time of the smoke test, independent CLI SSM
connection was not yet confirmed;
`ssm:DescribeInstanceInformation` for this instance was denied to the development
host role, so no permissions were expanded and no recovery success is inferred.

Repair verification on `codex/first-private-app-plan`: the full
`./scripts/check-repository.sh` passed in the isolated `.venv-manifest` prepared
by the reviewed setup script; `bash -n scripts/check-repository.sh`, Git whitespace,
relative-link and plan traceability checks passed. No Terraform changes were made
and Terraform checks were not run locally. Live smoke execution and offline
checks above are separate from CI and complete host acceptance.

## Independent SSM recovery confirmation — October 9, 2026

Daniel supplied the transcript of an independent CLI connection using
`aws ssm start-session --region us-east-1 --target i-0c42b82d7480123b1`.
The session opened successfully; `whoami` returned `ssm-user` and `hostname`
returned `forge-dev-01`. This is owner-supplied recovery-access evidence, not an
agent-run session. The session identifier is omitted. No permissions were changed.
Logout/reboot persistence and synthetic-source replacement acceptance remain
pending; this connection does not complete those criteria.

## Successful repaired bootstrap - October 8, 2026

The protected replacement at `6d90105136de55f7932c7e6857ba0bf6415db249`
completed bootstrap successfully. Rootless and host-tool receipts passed,
Tailscale enrolled automatically, and authenticated private SSH plus original
project filesystem/ownership were verified. See [SPEC-016 live evidence](../016-tailscale-workload-identity/acceptance.md#fresh-host-enrollment-verified---october-8-2026)
for public workflow references and remaining acceptance limits. This supersedes
the earlier pending bootstrap outcome; full fixture/reboot and final owner
acceptance remain separate.

This earlier verification record was recovered from [PR #35](https://github.com/danielbardsley/gptclaw/pull/35)
on October 10. It preserves the original verifier's observations; enrollment,
replacement and desktop SSH checks were not repeated during this reconciliation.
The referenced protected plan/apply jobs were independently checked through
GitHub and both report success. Current host receipts/storage checks and Daniel's
SSM confirmation above supplement this record.
