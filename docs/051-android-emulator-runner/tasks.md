# Android runner tasks

Owner: project owner. Date: 2026-10-30. Implementation/provisioning authorized;
runner created; Android bootstrap blocked. [Spec](spec.md) · [Design](technical-design.md)

- [x] **T1:** Inspect existing host, storage, IAM and deployment path. Preserve
  unrelated branch/untracked work in an isolated `codex/` worktree. Record the
  owner's separate-runner and pipeline-only authorization. ER-01,02 / AC-01.
- [x] **T2:** Add bounded bootstrap and immutable Android/Tailscale artifact
  pins, separate forge/KVM setup, private SSH and four-hour stop timer. Preserve
  package license notices and make license acceptance explicit. ER-03–05 / AC-02,03,05.
- [x] **T3:** Add separate protected M7i compute and instance-state resources,
  non-secret outputs and protected workflow state input. ER-01–05 / AC-01,02,05.
- [x] **T4:** Run meaningful synthetic bootstrap tests, Terraform checks and
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
this additional test fix and notes. The original local broad run failed before that fixture correction; it was not
rerun in full locally. Protected plan and apply CI subsequently passed the full
repository and Terraform gates on merged revision `eb0fcec`.

PR #109 merged as `eb0fcec`. The [protected apply](https://github.com/danielbardsley/gptclaw/actions/runs/41205414783)
used runner state **running** and completed with 2 additions, 14 changes and no
destructions. New runner: `i-00eecaeb4e941cf5e`. Existing changes were revision
tags in the reviewed plan; no project-volume or existing-host replacement.

The operator's SSM diagnosis showed `/dev/kvm` present, but cloud-init failed at
`sshd -t`: `Missing privilege separation directory: /run/sshd`. Tailscale was
not installed; both Tailscale and Android services were inactive. AC-03–05 remain
unpassed. Terraform success did not establish a usable emulator.

The follow-up fix creates the root-owned runtime directory before SSH validation
and replaces deprecated cloud-init `sudo: false` with `sudo: null`. Six focused
offline tests pass, including a missing-directory/retry regression using stubs;
no privileged commands execute on the test host. Terraform formatting, validation
and three focused runner tests pass with mocked AWS and real cloud-init rendering;
bootstrap Bash syntax and whitespace checks pass. The full local repository checker
is running; follow-up CI and live recovery remain pending. The [runbook](../../runbooks/android-emulator-runner.md) records a
concrete two-command operator repair proposal; the project owner approved this one-attempt
operator exception and publication of the four-file fix on October 31. The
operator has been given the commands; execution and successful recovery remain
unverified. Source changes alone cannot
repair the existing instance because cloud-init drift is deliberately ignored.

Next: observe the approved operator recovery, verify private access and actual
Android boot, then install Dogstats and test the requested flow. The GitHub connector has no workflow-dispatch capability and the
existing App's grants do not provide Actions dispatch; an owner/operator must
trigger the documented workflow. This access gap does not authorize new
credentials, local apply or direct AWS mutation.
