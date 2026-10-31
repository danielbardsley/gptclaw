# Private Android emulator runner

Owner: project owner. Date: 2026-10-30. Status: implementation authorized;
replacement Android boot verified; app and lifecycle acceptance pending. The owner requested one additional AWS
runner and explicitly required Terraform through GitHub Actions. This does not
authorize replacing the development host or moving its project volume.

[Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and requirements

Run an accelerated Android emulator that the development agent can actually
operate, screenshot and exercise against Dogstats' existing private backend.
This is a test appliance, not a second complete development environment.

- **ER-01:** Add one Linux x86_64 `m7i.xlarge` (4 vCPU / 16 GiB) with nested
  virtualization enabled, without replacing or resizing existing compute or
  detaching, copying or modifying the persistent project volume.
- **ER-02:** Use the existing protected GitHub Actions → HCP Terraform → AWS
  path for creation and subsequent instance start/stop. No local Terraform apply,
  direct AWS mutation, new public ingress or Tailscale Funnel.
- **ER-03:** Provide private SSH, a loopback-only emulator/ADB control path,
  IMDSv2, encrypted storage and unprivileged `forge` execution with KVM access.
  Reuse the existing development workload identity; never copy credentials or
  Tailscale state from the current host.
- **ER-04:** Install checksum-pinned Tailscale, emulator, platform-tools and API
  36 Google APIs x86_64 image. Test data is synthetic. The project owner accepted
  the Android SDK terms for this test runner on 2026-10-30 in this conversation.
- **ER-05:** Keep SDK, emulator and synthetic test artifacts on the runner's own
  80-GiB encrypted root disk. Preserve them through stop/start. Do not install a
  second backend, credential broker, dashboard or Codex login. Stop after four
  hours per boot with bounded graceful shutdown; storage remains billable.
- **ER-06:** Demonstrate Android boot, screenshots, input, APK installation and
  access to the existing private API and issuer. Android simulation does not
  qualify physical GPS, battery use or background recording.

## Acceptance

| ID | Required evidence | Requirements |
|---|---|---|
| AC-01 | Reviewed remote plan adds only the runner/state resources and expected bootstrap/output changes; existing instance and project attachment unchanged | ER-01,02 |
| AC-02 | GitHub/HCP revision and apply links; encrypted disk, IMDSv2 and zero ingress verified | ER-02,03,05 |
| AC-03 | KVM usable as forge; `sys.boot_completed=1`, launcher screenshot and working input | ER-03,04,06 |
| AC-04 | Dogstats installed; actual app screenshot and private API/issuer connection observed with synthetic account | ER-06 |
| AC-05 | Protected stop/start preserves synthetic app data; stop timer configured and observed stop recorded | ER-02,05 |

Owner authorizes implementation and provisioning in this conversation. Existing
merge/environment gates still apply. Missing access or an unexpected destructive
remote plan blocks deployment, not independent source preparation. App walk-flow
acceptance remains in Dogstats and cannot be inferred from runner acceptance.

## Approved recovery evidence

The October 31 deployment created the runner, but SSH runtime-directory validation
stopped bootstrap before enrollment. The owner requested automatic provisioning
instead of manual repair. A one-time replacement of the failed runner and deletion
of its own 80-GiB root disk completed through the protected pipeline.
The project owner approved the scoped replacement, temporary guard exception and
subsequent guard restoration on October 31. Required gates and remote-plan review
remain. This does not authorize changes to the existing development host or
project volume.
The replacement now has a verified Android boot and inspected launcher screenshot.
The guard-restoration follow-up is pending merge; app and stop/start acceptance
remain pending.
