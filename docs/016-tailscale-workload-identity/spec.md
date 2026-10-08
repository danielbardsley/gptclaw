# SPEC-016: Automatic Tailscale enrollment

- **Status:** Account issuer and trust configured; host deployment and acceptance pending
- **Owner:** Daniel
- **Date:** 2026-10-01 (America/New_York)
- **Design:** [Technical design](technical-design.md)
- **Tasks:** [Tasks](tasks.md)

Daniel authorized “implement that now” after selecting AWS workload identity
federation to eliminate the recurring manual enrollment-key step. Existing
SYS-001/SYS-004 deployment authorization remains valid, subject to recovery and
one-time trust readiness. Account issuer and external trust setup are now recorded
in [acceptance evidence](acceptance.md); fresh-host enrollment remains pending.

## Requirements

- WIF-001: Recreated hosts enroll as `tag:gptclaw-dev` using their EC2 IAM role,
  without static Tailscale credentials or a per-replacement rotation counter.
- WIF-002: Scope token issuance to the exact configured audience and at most
  300 seconds. Preserve EC2-only role trust and deployment-role self-management
  restrictions. Trust in Tailscale must match the exact account issuer and host role.
- WIF-003: Provision account federation only through an isolated protected
  GitHub Actions/HCP Terraform stack. It must not replace compute or alter the
  existing development stack's identities. Preserve the account issuer on removal.
- WIF-004: Refuse unsupported clients, enrollment failures or incorrect tag/state;
  do not publish bootstrap success or fall back to an old secret. Preserve legacy
  secret data during migration without giving the host permission to read it.
- WIF-005: Keep Podman/profile installation, protected project storage and private
  access intact; record local checks separately from deployed acceptance.

## Acceptance

| ID | Required evidence | Requirements |
|---|---|---|
| AC-001 | Rendered cloud-init uses validated non-secret federation configuration and no auth key; offline success/failure/version tests pass. | WIF-001, WIF-004 |
| AC-002 | Exact audience/lifetime IAM assertions and protected-account-stack tests pass; remote plans retain deployment identities and project disk. | WIF-002, WIF-003 |
| AC-003 | Account issuer and exact-role Tailscale trust configured; fresh host joins without key entry; SSM/private access verified. | WIF-001–WIF-004 |
| AC-004 | All profile components including rootless Podman pass deployed receipts; replacement preserves project filesystem/ownership. | WIF-005 |

Daniel owns one-time external trust/credential setup and final acceptance.
Implementation is delivered by PR; no local infrastructure mutation is allowed.
