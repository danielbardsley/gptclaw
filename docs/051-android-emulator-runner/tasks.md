# Android runner tasks

Owner: project owner. Date: 2026-10-30. Implementation/provisioning authorized;
replacement booted; guard restoration and app testing in progress. [Spec](spec.md) · [Design](technical-design.md)

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

## Restart blocker (November 1, 2026)

Guard restoration merged in PR #112 as `7b5fe51`. The protected
[restart plan](https://github.com/danielbardsley/gptclaw/actions/runs/41313415827)
passed quality checks, then refused Android-instance destruction under
`prevent_destroy`. No apply ran. The narrow correction ignores observed
public-IP association drift while retaining the creation setting, existing
guards and explicit state resource. Pinned provider/AWS behavior supports this
likely cause, but the failed plan omits the specific replacement field and live
read-only inspection was denied by the host role. Permissions were not changed.

Local pinned Terraform format/validation, all 31 mocked Terraform cases, six
offline runner tests and whitespace checks pass. The broader repository gate
is still pending. The additional mocked stop/restart runs check instance identity
retention; they cannot prove AWS refresh behavior. T5/AC-05 remain open: a fresh reviewed zero-destruction remote
plan, protected apply and actual retained-data restart are required.

## Earlier evidence (October 31, 2026)

- [PR #109](https://github.com/danielbardsley/gptclaw/pull/109) introduced the
  runner. The project owner approved public publication and SDK terms. Its first
  boot failed before Tailscale installation at `sshd -t` because `/run/sshd` was
  missing. The operator confirmed that exact failure through SSM.
- [PR #111](https://github.com/danielbardsley/gptclaw/pull/111), merged as
  `379fc9f`, creates the SSH runtime directory before validation and uses supported
  cloud-init `sudo: null`. The owner superseded the manual repair proposal with
  an approved one-time runner/root-disk replacement through the protected pipeline.
- Local six-test bootstrap suite, Terraform format/validate, all 29 mocked-AWS
  tests with real cloud-init rendering, Bash syntax and whitespace checks passed.
  The broad local checker completed exit 0, but source changed during that run;
  this is diagnostic evidence rather than a frozen-final-head claim. Exact-head
  protected CI on PR #111, the plan and apply passed the full repository and
  Terraform checks. Unchanged generated-template dependency audit failures remain
  separate; no advisory suppression or exception renewal was introduced.
- [Remote plan](https://github.com/danielbardsley/gptclaw/actions/runs/41218238098)
  and [apply](https://github.com/danielbardsley/gptclaw/actions/runs/41223764115)
  used `379fc9f`, state **running**, with 2 additions, 14 tag-only updates and 2
  destructions: the failed Android instance and its Terraform state resource.
  HCP [apply run](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-WBWyfSrF2cVmyEsc).
  Failed instance `i-00eecaeb4e941cf5e` was removed; replacement is
  `i-0128be3340461d289`. Existing host and project storage were not replaced.
- Replacement enrolled privately as `forge-android-01.tail8c3304.ts.net`.
  Unprivileged SSH verified forge's KVM read/write access, active emulator service,
  `sys.boot_completed=1`, loopback-only emulator/ADB ports and scheduled stop timer.
  An actual Android launcher screenshot was captured and inspected locally.
  No screenshots containing credentials/private data were published. Fresh SSH
  host-key trust used first-use enrollment on the private node; subsequent SSH
  requires that key.
- The one-replacement lifecycle exception has expired. This follow-up restores
  destruction/user-data drift guards, pending its merge. No further apply until
  those guards are restored on main. Live APK/core-flow testing is now the next
  activity; stop/start retention, timer shutdown and app acceptance remain pending.

T5 remains open because retained-data stop/start and observed automatic shutdown
have not been demonstrated. T6 requires actual Dogstats interaction and private
API/issuer observations; Android boot alone does not complete it. Physical GPS,
battery and background qualification are not established by this emulator.
