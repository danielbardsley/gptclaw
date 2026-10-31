# Private Android runner

[Scope/approval](../docs/051-android-emulator-runner/spec.md) ·
[Design](../docs/051-android-emulator-runner/technical-design.md)

One separate M7i instance runs Android; Dogstats remains on the existing host.
Only synthetic test data belongs on this appliance. No project volume, backend,
credentials or Tailscale state are copied.

## Provision and start/stop

After review/merge, open the [Terraform development host workflow](https://github.com/danielbardsley/gptclaw/actions/workflows/terraform-dev-host.yml).
Run on **main**, operation **plan**, Android runner state **running**. Inspect
the HCP plan: expected additions are `aws_instance.android_runner` and
`aws_ec2_instance_state.android_runner`, cloud-init/output changes and ordinary
revision tags. Reject unexpected existing-host replacement, project-volume
resize/detach/destruction, ingress or IAM expansion. Then dispatch **apply**,
state **running**, confirmation **gptclaw-dev-host**, with existing environment
approvals. Retain the revision and GitHub/HCP links. Never apply locally.

For later start/stop use that same plan/apply path with **running** or **stopped**.
Default dispatch state is **stopped**, including unrelated future applies. A
four-hour boot timer stops Android and shuts down the runner, allowing up to 90
seconds for graceful exit. The encrypted disk survives stop/start; storage and
applicable IPv4/network charges remain. The timer is not a hard billing cap.

## First-boot SSH runtime-directory failure

The October 31 apply created runner `i-00eecaeb4e941cf5e`, but cloud-init
stopped at `sshd -t` with `Missing privilege separation directory: /run/sshd`.
KVM existed; Tailscale had not been installed and Android had not started.
The bootstrap now explicitly creates the root-owned 0755 runtime directory
before validating SSH, including on images using socket activation.

Updating ignored cloud-init source does **not** repair an existing instance.
The owner subsequently requested automatic machine setup instead of the proposed
manual SSM repair. Do not run the earlier two commands; that recovery path has
been superseded. No successful manual repair has been observed.

### Proposed one-time Terraform replacement — approval pending

The repair branch temporarily permits replacement of **only**
`aws_instance.android_runner` and allows its corrected user-data to trigger it.
It uses create-before-destroy so the failed runner is not removed before EC2 has
created the replacement. This does not prove the replacement has bootstrapped.
The new runner's original 80-GiB root disk is deleted with the failed instance;
there is no Dogstats installation or app data observed on that failed first boot.
The existing development host, its root disk and persistent project volume keep
their existing guards and configuration. No SSM permissions or public ingress
are added. The previous instance never enrolled, so its Tailscale state is not
copied or reused.

Before publication/merge/apply, obtain explicit approval for this expanded source
scope and the failed runner/root-disk replacement. Use the protected workflow
**plan**, state **running**, on main after merge. Inspect the HCP diff: replacement
is limited to the Android instance and its state resource, plus revision tags.
Reject any other destruction/replacement, IAM change, ingress or project-volume
change. Then use **apply**, state **running**, confirmation `gptclaw-dev-host`,
retaining existing environment gates. Never use local apply or direct EC2 mutation.

Owner of the proposed temporary guard exception: project owner. Reason: consume
corrected bootstrap after a failed first boot. Scope: the named failed runner
only. Expiry: completion of this one replacement; it is not standing permission
to replace future runners. Immediately prepare a follow-up PR restoring
`prevent_destroy = true` and `ignore_changes = [ami, user_data_base64]`, removing
`create_before_destroy` and retiring these active recovery instructions while
retaining evidence. Do not perform another apply while the guard is relaxed.
If replacement fails, preserve the new instance/disk and stop for diagnosis.

Verify tailnet enrollment, KVM, Android boot and app interaction before claiming
success. If bootstrap fails again, diagnose it and prepare a separate reviewed
repair; do not loop replacements or repeat manual repair commands.

## Connect and verify

Bootstrap downloads approximately 2.3 GB of pinned Android archives. Terraform
success does not establish bootstrap, tailnet enrollment or Android readiness.
Confirm the fresh `forge-android-01` node/tag and verified SSH host fingerprint.
If bootstrap fails, use reviewed SSM/operator diagnosis; never open public ingress
or grant forge sudo. The owner accepted Android SDK terms for this runner on
October 30, 2026; bootstrap records `/home/forge/android/license-accepted`.

From the development host, leave this tunnel running (use the actual tailnet DNS
name if the short hostname is not resolved):

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -i /srv/forge/projects/dogstats/.local/android/emulator-runner-access/id_ed25519 \
  -L 127.0.0.1:15555:127.0.0.1:5555 forge@forge-android-01
```

Connect using Dogstats' pinned `platform-tools/adb connect 127.0.0.1:15555`;
always select serial `127.0.0.1:15555` for subsequent commands. Check `sys.boot_completed`
equals **1**, inspect a launcher screenshot and exercise input. As forge on the
runner, verify `/dev/kvm` is readable/writable, `emulator -accel-check` succeeds,
`systemctl list-timers gptclaw-android-stop.timer` shows the stop timer, and `ss -ltn`
shows only loopback emulator/ADB listeners. Confirm any authorization prompt
belongs to this dedicated emulator; don't control an unrelated phone.

Install the inspected APK; verify version, actual app screens and Android access
to `forge-dev-01-4.tail8c3304.ts.net` API/issuer ports 8443/8444. Test synthetic
sign-in → walk → stops/notes → End → Save → History/reopen against the original
design. Don't capture credentials, inbox action links or real private locations.
Emulated GPS does not establish physical-device recording/battery acceptance.

Stop only this runner through Terraform when finished; close its SSH tunnel.
Preserve the disk on failure. Removal/replacement requires a reviewed change to
its destruction guard. The private key stays in ignored Dogstats local storage;
retiring the public key in source alone does not revoke an already provisioned
authorized_keys entry. Source rollback likewise does not roll back disk data.
