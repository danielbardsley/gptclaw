# Android runner tasks

Owner: project owner. Date: 2026-10-30. Implementation/provisioning authorized;
no live runner claimed. [Spec](spec.md) · [Design](technical-design.md)

- [x] **T1:** Inspect existing host, storage, IAM and deployment path. Preserve
  unrelated branch/untracked work in an isolated `codex/` worktree. Record the
  owner's separate-runner and pipeline-only authorization. ER-01,02 / AC-01.
- [x] **T2:** Add bounded bootstrap and immutable Android/Tailscale artifact
  pins, separate forge/KVM setup, private SSH and four-hour stop timer. Preserve
  package license notices and make license acceptance explicit. ER-03–05 / AC-02,03,05.
- [x] **T3:** Add separate protected M7i compute and instance-state resources,
  non-secret outputs and protected workflow state input. ER-01–05 / AC-01,02,05.
- [ ] **T4:** Run meaningful synthetic bootstrap tests, Terraform checks and
  existing repository gates. Review complete source diff and open PR. Local
  checks and CI are distinct. ER-01–05 / AC-01–03,05.
- [ ] **T5:** Review/merge using existing gates; inspect protected remote plan,
  apply only the additive runner changes, and verify private access/KVM/Android,
  stop/start and retained fixture data. Record sanitized revision/run/evidence
  links. ER-01–06 / AC-01–05.
- [ ] **T6:** Install Dogstats and capture actual screens against the original
  design. Return to simplifying and repairing the core walk flow; do not add
  general runner/platform features. ER-06 / AC-04.

No infrastructure has been created. Next action: finish repository checks and publish the reviewed source, then
inspect CI and the protected plan before deployment. No local apply/direct AWS
mutation is authorized or needed.
