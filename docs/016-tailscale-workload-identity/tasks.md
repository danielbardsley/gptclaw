# TASKS-016: Automatic enrollment

- [x] T-000: Record Daniel's authorization and verify AWS/Tailscale support and account prerequisite.
- [x] T-001: Implement isolated account stack, host IAM and bounded enrollment helper (WIF-001–WIF-004).
- [x] T-002: Add offline tests and update migration/runbooks/workflows; run repository and Terraform checks (AC-001/AC-002).
- [ ] T-003: Deliver reviewed PR and CI; configure account issuer and external Tailscale trust, then protected dev-host plan/apply (AC-002/AC-003).
- [ ] T-004: Verify replacement access, storage, package/rootless receipts and automatic enrollment; record acceptance (AC-003/AC-004).

Account issuer plan/apply and external Tailscale trust setup completed on
October 8, 2026; the client ID is saved in the development workspace. T-003
remains incomplete until the protected development-host plan/apply. The
development HCP workspace still needs its version set to 1.16.5. No host
replacement or package deployment has run.

Local verification: [acceptance record](acceptance.md). Account setup evidence is recorded; host deployment and live acceptance remain pending.
