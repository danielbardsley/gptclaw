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

## Current evidence

[PR #109](https://github.com/danielbardsley/gptclaw/pull/109) publishes the runner
source. Owner separately approved public repository publication and SDK terms.
Local Terraform 1.16.5 formatting/validation and all 29 mocked-AWS tests pass;
cloud-init was rendered locally. Five offline installer tests, real pinned archive
inventory checks, Tailscale checksum/layout, YAML structure and Bash syntax pass.
The three runner tests also pass with the workflow's running-state environment.
None of this establishes deployed Android behavior.

The broader checker found five Metro spike test errors: live policy expired on
October 28. Identical failures reproduced on isolated main `ea8d126`. A test-only
fixture correction now passes all 24 spike tests; the real runtime policy and its
expiry enforcement are unchanged. The owner explicitly approved publication of
this additional test fix and notes. The original broad run continues, and fresh
CI remains required. No full repository-check success is claimed.

No AWS resource has been created. Next: finish gates/review, then protected remote
plan/apply. The GitHub connector has no workflow-dispatch capability and the
existing App's grants do not provide Actions dispatch; an owner/operator must
trigger the documented workflow. This access gap does not authorize new
credentials, local apply or direct AWS mutation.
