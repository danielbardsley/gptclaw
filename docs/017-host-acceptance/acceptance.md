# SPEC-017 acceptance evidence

- **Status:** Draft plan; execution pending
- **Owner:** Daniel
- **Evidence date:** 2026-10-09 (America/New_York)
- **Specification:** [SPEC-017](spec.md)
- **Design:** [TDD-017](technical-design.md)
- **Tasks:** [TASKS-017](tasks.md)

## Preliminary observations from this chat

Before drafting this initiative, read-only host inspection ran tool version
commands (`git`, `python3`, `podman`, `aws`, `tailscale`, `codex`), `dpkg-query`
for declared apt packages, receipt reads and canonical profile digest comparison,
`findmnt -no TARGET,FSTYPE,UUID /srv/forge`, ownership metadata, selected
`systemctl is-active` queries, `loginctl show-user forge -p Linger`,
`systemctl --user is-active default.target` and selected fields from
`tailscale status --json`. No authentication files or token traffic were read.

Observed Ubuntu 24.04.5, Git 2.43.0, Python 3.12.3, Podman 4.9.3, AWS CLI 2.37.11,
Tailscale 1.104.1 and Codex CLI 0.162.0. All 26 receipt components passed; the
receipt and completion marker match reviewed profile digest
`f2be7cdc4f4f057fafc908a1d5917ec812ce699cf0ecdd56b8b03e50cd8d294a`
and deployment revision `6d90105136de55f7932c7e6857ba0bf6415db249`.
Provisioning observation time was October 8 at 17:27:48 EDT; these are not new
installation checks. Current apt metadata showed a later sudo package version
than its provisioning receipt, illustrating that receipts do not prove no drift.

Tailscale was Running/online with `tag:gptclaw-dev`; SSM, CloudWatch, Tailscale
and bootstrap services were active. UUID matches the SPEC-016 pre-replacement
baseline; projects/repository UID/GID are 1002, the mount root is root-owned.
Linger is enabled and the user default target active. The rootless receipt
reports rootless=true, overlay, netavark/slirp4netns, crun and cgroup v2/systemd;
no container application test was run. Git SSH authentication and a real branch
push succeeded, and [PR #36](https://github.com/danielbardsley/gptclaw/pull/36)
merged the attributed replacement report.

Daniel reports the instance was recreated and Tailscale connected properly.
Explicit no-manual-key confirmation and protected deployment provenance matching
these receipts still need recording. No independent SSM login, fixture,
logout/reboot persistence or replacement-source/rebuild test is claimed here.

## Criteria

| ID | State | Remaining evidence |
|---|---|---|
| AC-001 | pending | Recheck/capture actual instance, protected deployment/CI and installed policy provenance alongside preliminary matching receipts. |
| AC-002 | pending | Independent CLI SSM and private access evidence; manual-key-free enrollment confirmation. |
| AC-003 | pending | Current mappings and actual fixture bind ownership; reconcile missing historical replacement-source proof. |
| AC-004 | pending | Synthetic build/network/HTTP/limits/crash-restart execution. |
| AC-005 | pending | Independent zero-session and boot-before-login observations in approved window. |
| AC-006 | pending | Actual scoped cleanup, listener/activation removal and unrelated-state preservation. |
| AC-007 | pending | Original criterion reconciliation, evidence review and Daniel's acceptance. |

## Verification and remaining work

This draft contains earlier observations, not completed SPEC-017 execution.
Record future exact commands/results, dates, actual revisions, run links,
limitations and owner acceptance here and in original initiative records.
Do not mark Delivered or replace historical failures with these preliminary
checks. Plan delivery is separate from host acceptance and infrastructure apply.
